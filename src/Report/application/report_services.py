# src/Report/application/report_services.py
import os
import csv
import asyncio
import numpy as np
from datetime import datetime
import cv2  # para grabar el frame
from zipfile import ZipFile
from uuid import UUID
from Report.domain.ReportEntry import ReportEntry
from Report.domain.SessionSummary import SessionSummary
from Report.ports.inbound.report_services_port import ReportServicesPort
from Report.ports.outbound.report_storage_port import ReportStoragePort
from Report.ports.outbound.report_notification_controller_port import ReportNotificationPort

class ReportServices(ReportServicesPort):
    """
    Core del módulo de reporte:
      - add_result: persiste y notifica
      - list_sessions, get_entries: consultas
      - get_summary: cálculos, PDF/CSV/ZIP
    """
    # Aquí se llenará en startup de FastAPI
    MAIN_LOOP: asyncio.AbstractEventLoop = None

    def __init__(self,
                 storage: ReportStoragePort,
                 notifier: ReportNotificationPort,
                 frames_dir: str):
        self.storage = storage
        self.notifier = notifier
        self.frames_dir = frames_dir

    def add_result(self,
                   session_id: str,
                   frame: np.ndarray,
                   label: str,
                   timestamp: datetime) -> None:
        """
        1) Reordena e normaliza array para cv2.imwrite
        2) Guarda frame como PNG
        3) Persiste metadato en BD
        4) Notifica por WebSocket
        """
        img = frame

        # --- a) Si viene en formato (C,H,W), lo pasamos a (H,W,C)
        if img.ndim == 3 and img.shape[0] in (1, 3, 4):
            img = np.transpose(img, (1, 2, 0))

        # --- b) Si es float, comprobar rango antes de escalar
        if img.dtype in (np.float32, np.float64):
            mx = float(img.max())
            if mx <= 1.0:
                img = (img * 255).clip(0,255).astype(np.uint8)
            else:
                img = img.clip(0,255).astype(np.uint8)

        # --- c) Asegurar canales válidos
        if img.ndim == 2:
            pass  # grayscale
        elif img.ndim == 3 and img.shape[2] == 1:
            img = img[:, :, 0]
        elif img.ndim == 3 and img.shape[2] == 4:
            img = img[:, :, :3]
        elif img.ndim == 3 and img.shape[2] == 3:
            pass  # BGR okay
        else:
            raise ValueError(f"Unsupported frame shape {img.shape} dtype={img.dtype}")

        # --- 2) Guardar en disco
        session_folder = os.path.join(self.frames_dir, session_id)
        os.makedirs(session_folder, exist_ok=True)
        fname = timestamp.isoformat().replace(":", "-") + ".png"
        frame_path = os.path.join(session_folder, fname)
        if not cv2.imwrite(frame_path, img):
            raise IOError(f"cv2.imwrite failed for {frame_path}")

        # --- 3) Persistir
        entry = ReportEntry(session_id, frame_path, label, timestamp)
        self.storage.save_entry(entry)

        # --- 4) Notificar
        #self.notifier.notify_entry(entry)
        # Encolamos la notificación para que corra en el loop principal
        asyncio.run_coroutine_threadsafe(
            self.notifier.notify_entry(entry),
            ReportServices.MAIN_LOOP
        )


    def list_sessions(self):
        return self.storage.list_sessions()

    def get_entries(self, session_id: UUID):
        return self.storage.fetch_entries(session_id)

    def get_summary(self, session_id: UUID,
                    operator: str, location: str,
                    job_order: str = None) -> SessionSummary:
        entries = self.storage.fetch_entries(session_id)
        if not entries:
            raise ValueError(f"No hay entradas para {session_id}")

        # Cálculos básicos
        start = entries[0].timestamp
        end = entries[-1].timestamp
        duration = (end - start).total_seconds()
        total = len(entries)
        fps = total / duration if duration>0 else 0

        # Conteo por etiqueta
        counts = {}
        for e in entries:
            counts[e.label] = counts.get(e.label, 0) + 1

        # Detección de eventos (cambios de estado)
        events = 0
        longest_normal = 0
        curr_run = 0
        first_anom = None
        last_anom = None
        prev_label = entries[0].label
        for e in entries:
            if e.label != prev_label:
                events += 1
                prev_label = e.label
            if e.label == "NORMAL":
                curr_run += 1
            else:
                longest_normal = max(longest_normal, curr_run)
                curr_run = 0
                if first_anom is None: first_anom = e.timestamp
                last_anom = e.timestamp
        longest_normal = max(longest_normal, curr_run)

        summary = SessionSummary(
            session_id=session_id,
            start_time=start,
            end_time=end,
            duration_seconds=duration,
            total_frames=total,
            fps=fps,
            counts_by_label=counts,
            total_events=events,
            longest_normal_run=longest_normal,
            first_anomaly_time=first_anom,
            last_anomaly_time=last_anom
        )

        # 1) Generar PDF, CSV y ZIP de imágenes
        self._generate_assets(summary, entries, operator, location, job_order)

        # 2) Notificar cierre con resumen y metadatos
        meta = {"operator": operator, "location": location, "job_order": job_order}
        # Encolamos la notificación para que corra en el loop principal
        # Notificar el summary también en el loop principal
        asyncio.run_coroutine_threadsafe(
            self.notifier.notify_summary(summary, meta),
            ReportServices.MAIN_LOOP
        )

        return summary

    def _generate_assets(self, summary: SessionSummary,
                         entries, operator, location, job_order):
        sess = str(summary.session_id)
        out_dir = os.path.join(self.frames_dir, sess + "_report")
        os.makedirs(out_dir, exist_ok=True)
        # -- CSV
        csv_path = os.path.join(out_dir, "report.csv")
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["session_id","frame_path","label","timestamp"])
            for e in entries:
                writer.writerow([e.session_id, e.frame_path, e.label, e.timestamp.isoformat()])

        # -- CSV de summary
        summary_csv = os.path.join(out_dir, "summary.csv")
        with open(summary_csv, "w", newline="") as f2:
            writer = csv.writer(f2)
            # encabezado
            writer.writerow(["field","value"])
            for field, val in summary.__dict__.items():
                writer.writerow([field, val])

        # -- Imágenes referenciales: inicio, medio, fin
        for idx in [0, len(entries)//2, -1]:
            src = entries[idx].frame_path
            dst = os.path.join(out_dir, f"ref_{idx}.png")
            if not os.path.exists(dst):
                os.link(src, dst)

        # -- ZIP de todo
        # Empaquetar **afuera** del folder para no “repetir”
#        zip_path = os.path.join(self.frames_dir, f"{sess}_report_pack.zip")
#        with ZipFile(zip_path, "w") as zf:
#            zf.write(csv_path, os.path.basename(csv_path))
#            for fname in os.listdir(out_dir):
#                if fname.startswith("ref_"):
#                    zf.write(os.path.join(out_dir, fname), fname)

            # -- PDF con metadata, tabla y miniaturas
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        pdf_path = os.path.join(out_dir, "report.pdf")
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        # Título y metadatos
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, height-50, f"Reporte Sesión {sess}")
        c.setFont("Helvetica", 10)
        c.drawString(40, height-70, f"Operador: {operator}")
        c.drawString(40, height-85, f"Ubicación: {location}")
        if job_order:
            c.drawString(40, height-100, f"Orden de trabajo: {job_order}")

        # Tabla de métricas
        y = height-130
        for field, val in summary.__dict__.items():
            c.drawString(40, y, f"{field}: {val}")
            y -= 12
            if y < 100:
                c.showPage()
                y = height-50

        # Tres miniaturas: inicio, medio y fin
        thumb_positions = [(40, y-100), (200, y-100), (360, y-100)]
        for idx, pos in zip([0, len(entries)//2, -1], thumb_positions):
            img_p = entries[idx].frame_path
            c.drawImage(img_p, pos[0], pos[1], width=150, height=100, preserveAspectRatio=True)

        c.save()

