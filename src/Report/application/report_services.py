# src/Report/application/report_services.py
import os
import csv
import asyncio
import numpy as np
from datetime import datetime
import cv2  # para grabar el frame
from zipfile import ZipFile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import shutil
from uuid import UUID
from Report.domain.ReportEntry import ReportEntry
from Report.domain.SessionSummary import SessionSummary
from Diagnostic.domain.InferenceLabel import InferenceLabel
from Report.ports.inbound.report_services_port import ReportServicesPort
from Report.ports.outbound.report_storage_port import ReportStoragePort
from Report.ports.outbound.report_notification_controller_port import ReportNotificationPort

class ReportServices(ReportServicesPort):
    """
    Módulo de reportes que:
      - add_result: guarda y notifica SOLO en cambios de estado
      - list_sessions, get_entries: consultas
      - get_summary: calcula estadísticas avanzadas, genera CSV/PDF
    """
    MAIN_LOOP: asyncio.AbstractEventLoop = None  # asignado en startup de FastAPI

    def __init__(self,
                 storage: ReportStoragePort,
                 notifier: ReportNotificationPort,
                 frames_dir: str):
        self.storage = storage
        self.notifier = notifier
        self.frames_dir = frames_dir
        # Lleva el último label visto por sesión para detectar cambios
        self._last_label: dict[str, InferenceLabel] = {}

    def _to_enum(self, raw_label) -> InferenceLabel:
        """Convierte un label crudo (int, '0', 'NORMAL') a InferenceLabel."""
        if isinstance(raw_label, InferenceLabel):
            return raw_label
        if isinstance(raw_label, int):
            return InferenceLabel(raw_label)
        if isinstance(raw_label, str):
            try:
                return InferenceLabel[int(raw_label)]  # str numérico
            except Exception:
                return InferenceLabel[raw_label]       # nombre del enum
        raise ValueError(f"Label inválido: {raw_label!r}")

    def add_result(self,
                   session_id: str,
                   frame: np.ndarray,
                   label:str | int | InferenceLabel,
                   timestamp: datetime) -> None:
        """
        1) Mapea label a Enum
        2) Sólo si es el primero o cambió de estado:
           a) normaliza y guarda imagen
           b) persiste metadato
           c) notifica
        """
        label = self._to_enum(label)
        prev = self._last_label.get(session_id)

        # Si no cambia, no hacemos nada
        if prev == label:
            return

        # Actualizamos el último estado
        self._last_label[session_id] = label

        # --- Normalización de la imagen para OpenCV
        img = frame
        # Si viene en (C,H,W) a (H,W,C)
        if img.ndim == 3 and img.shape[0] in (1,3,4):
            img = np.transpose(img, (1,2,0))
        # Float [0,1] o [0,255]
        if img.dtype in (np.float32, np.float64):
            mx = float(img.max())
            if mx <= 1.0:
                img = (img * 255).clip(0,255).astype(np.uint8)
            else:
                img = img.clip(0,255).astype(np.uint8)
        # Canales: ignorar alpha, convertir grayscale
        if img.ndim == 3 and img.shape[2] == 4:
            img = img[:,:,:3]
        elif img.ndim == 3 and img.shape[2] == 1:
            img = img[:,:,0]

        # --- Guardar en disco
        session_folder = os.path.join(self.frames_dir, session_id)
        os.makedirs(session_folder, exist_ok=True)
        fname = timestamp.isoformat().replace(":", "-") + f"_{label.name}.png"
        path = os.path.join(session_folder, fname)
        if not cv2.imwrite(path, img):
            raise IOError(f"Falló cv2.imwrite para {path}")

        # --- Persistir en base de datos
        entry = ReportEntry(session_id, path, label.name, timestamp)
        self.storage.save_entry(entry)

        # --- Notificar via WebSocket en el loop principal
        asyncio.run_coroutine_threadsafe(
            self.notifier.notify_entry(entry),
            ReportServices.MAIN_LOOP
        )

    def list_sessions(self):
        return self.storage.list_sessions()

    def get_entries(self, session_id: UUID):
        return self.storage.fetch_entries(session_id)

    def get_summary(self,
                    session_id: UUID,
                    operator: str,
                    location: str,
                    job_order: str = None) -> SessionSummary:
        """
        1) Carga todas las entradas almacenadas (cambios de estado)
        2) Calcula:
           - tiempos globales y por estado
           - fps, total_events, counts_by_label
           - longest normal run en segundos
           - métricas nuevas: tiempo por estado, % anomalía, intervalo medio entre anomalías, anomalías por minuto
        3) Genera CSV y PDF con todo
        """
        entries = self.storage.fetch_entries(session_id)
        if not entries:
            raise ValueError(f"No hay entradas para {session_id}")

        # --- Tiempos globales
        start = entries[0].timestamp
        end   = entries[-1].timestamp
        total_duration = (end - start).total_seconds()
        total_events = len(entries) - 1  # cada entrada > primer frame es un cambio
        fps = len(entries) / total_duration if total_duration > 0 else 0.0

        # --- Conteo de transiciones por label
        counts_by_label = {}
        for e in entries:
            counts_by_label[e.label] = counts_by_label.get(e.label, 0) + 1

        # --- Tiempo total por estado (suma de duraciones entre cambios)
        time_per_label = {lbl: 0.0 for lbl in counts_by_label}
        for i, e in enumerate(entries):
            t0 = e.timestamp
            t1 = entries[i+1].timestamp if i+1 < len(entries) else end
            delta = (t1 - t0).total_seconds()
            time_per_label[e.label] += delta

        # --- Porcentaje de tiempo en anomalía vs normal
        normal_time = time_per_label.get(InferenceLabel.NORMAL.name, 0.0)
        anomaly_time = total_duration - normal_time
        pct_anomaly = (anomaly_time / total_duration * 100) if total_duration>0 else 0.0

        # --- Intervalo medio entre anomalías (solo eventos != NORMAL)
        anom_times = [e.timestamp for e in entries if e.label != InferenceLabel.NORMAL.name]
        if len(anom_times) >= 2:
            intervals = [
                (anom_times[i+1] - anom_times[i]).total_seconds()
                for i in range(len(anom_times)-1)
            ]
            mean_interval = sum(intervals) / len(intervals)
        else:
            mean_interval = 0.0

        # --- Anomalías por minuto
        anomalies_per_minute = (len(anom_times) / (total_duration/60)) if total_duration>0 else 0.0

        # --- Longest run continuo de NORMAL (en segundos)
        longest_normal_run = 0.0
        run_start = None
        for e in entries:
            if e.label == InferenceLabel.NORMAL.name:
                if run_start is None:
                    run_start = e.timestamp
            else:
                if run_start:
                    run = (e.timestamp - run_start).total_seconds()
                    longest_normal_run = max(longest_normal_run, run)
                    run_start = None
        # si al final quedó un run abierto
        if run_start:
            run = (end - run_start).total_seconds()
            longest_normal_run = max(longest_normal_run, run)

        # --- Primera y última anomalía global
        first_anom = anom_times[0] if anom_times else None
        last_anom  = anom_times[-1] if anom_times else None

        # --- Primera/última ocurrencia por label
        first_by_label = {}
        last_by_label = {}
        for e in entries:
            lbl = e.label
            if lbl not in first_by_label:
                first_by_label[lbl] = e.timestamp
            last_by_label[lbl] = e.timestamp

        summary = SessionSummary(
            session_id=session_id,
            start_time=start,
            end_time=end,
            duration_seconds=total_duration,
            total_frames=len(entries),
            fps=fps,
            counts_by_label=counts_by_label,
            total_events=total_events,
            longest_normal_run_seconds=longest_normal_run,
            first_anomaly_time=first_anom,
            last_anomaly_time=last_anom,
            first_occurrence_by_label=first_by_label,
            last_occurrence_by_label=last_by_label,
            time_per_label=time_per_label,
            pct_anomaly=pct_anomaly,
            mean_interval_between_anomalies=mean_interval,
            anomalies_per_minute=anomalies_per_minute
        )

        # Generación de CSV/PDF/… (idéntico al ejemplo anterior)
        self._generate_assets(summary, entries, operator, location, job_order)

        # Notificar resumen
        meta = {"operator": operator, "location": location, "job_order": job_order}
        asyncio.run_coroutine_threadsafe(
            self.notifier.notify_summary(summary, meta),
            ReportServices.MAIN_LOOP
        )

        return summary
    
    def _generate_assets(self,
                         summary: SessionSummary,
                         entries,
                         operator: str,
                         location: str,
                         job_order: str):
        """
        Genera:
          - report.csv
          - summary.csv
          - report.pdf con miniaturas basadas en ref_<tag>.png
        """
        sess = str(summary.session_id)
        out_dir = os.path.join(self.frames_dir, sess + "_report")
        os.makedirs(out_dir, exist_ok=True)

        # 1) CSV de entries
        with open(os.path.join(out_dir, "report.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["session_id","frame_path","label","timestamp"])
            for e in entries:
                w.writerow([e.session_id, e.frame_path, e.label, e.timestamp.isoformat()])

        # 2) CSV de summary
        with open(os.path.join(out_dir, "summary.csv"), "w", newline="") as f2:
            w2 = csv.writer(f2)
            w2.writerow(["field","value"])
            for field, val in summary.__dict__.items():
                w2.writerow([field, repr(val)])

        # 3) Prepara imágenes de referencia en out_dir
        refs = [(entries[0].frame_path, "start")]
        for lbl, ts in summary.last_occurrence_by_label.items():
            fp = next(e.frame_path for e in entries if e.label==lbl and e.timestamp==ts)
            refs.append((fp, lbl))
        refs.append((entries[-1].frame_path, "end"))

        for src_fp, tag in refs:
            dst = os.path.join(out_dir, f"ref_{tag}.png")
            if not os.path.exists(dst):
                try:    os.link(src_fp, dst)
                except: shutil.copy(src_fp, dst)

        # 4) Genera el PDF
        pdf_path = os.path.join(out_dir, "report.pdf")
        c = canvas.Canvas(pdf_path, pagesize=letter)
        W, H = letter

        def draw_header():
            c.setFont("Helvetica-Bold", 16)
            c.drawString(40, H-50, f"Reporte Sesión {sess}")
            c.setFont("Helvetica", 10)
            c.drawString(40, H-70, f"Operador: {operator}")
            c.drawString(40, H-85, f"Ubicación: {location}")
            if job_order:
                c.drawString(40, H-100, f"Orden: {job_order}")

        draw_header()

        # 4.1) Imprime métricas verticalmente
        y = H - 130
        lh = 12
        bottom = 60
        c.setFont("Helvetica", 9)

        def new_page_if_needed(lines=1):
            nonlocal y
            if y - lines*lh < bottom:
                c.showPage()
                draw_header()
                y = H - 70
                c.setFont("Helvetica", 9)

        for field, val in summary.__dict__.items():
            if isinstance(val, dict):
                new_page_if_needed()
                c.drawString(40, y, f"{field}:")
                y -= lh
                for k, v in val.items():
                    new_page_if_needed()
                    c.drawString(60, y, f"- {k}: {v}")
                    y -= lh
                continue
            disp = val.isoformat() if hasattr(val, "isoformat") else val
            new_page_if_needed()
            c.drawString(40, y, f"{field}: {disp}")
            y -= lh

        # 4.2) Toma solo los ref_*.png y ordénalos coherentemente
        files = [f for f in os.listdir(out_dir) if f.startswith("ref_") and f.endswith(".png")]
        def sort_key(fn):
            tag = fn[4:-4]
            if tag == "start":
                return (0, "")
            if tag == "end":
                return (2, "")
            return (1, tag)   # todos los labels van en el medio, orden alfabético
        files.sort(key=sort_key)

        # 4.3) Dibuja miniaturas en cuadrícula
        thumb_w, thumb_h = 120, 90
        x0, x, y_img = 40, 40, y - thumb_h - 2*lh
        c.setFont("Helvetica-Bold", 10)

        for fn in files:
            tag = fn[4:-4]
            img_path = os.path.join(out_dir, fn)

            # salto de página si no cabe la siguiente ficha
            if y_img < bottom:
                c.showPage()
                draw_header()
                y_img = H - 130 - thumb_h - lh
                x = x0
                c.setFont("Helvetica-Bold", 10)

            # nueva fila si excede ancho
            if x + thumb_w > W - x0:
                x = x0
                y_img -= thumb_h + 2*lh

            # título
            c.drawString(x, y_img + thumb_h + lh, f"Label: {tag}")

            # imagen
            try:
                img = ImageReader(img_path)
                c.drawImage(img, x, y_img, width=thumb_w, height=thumb_h, preserveAspectRatio=True)
            except:
                c.setFont("Helvetica", 8)
                c.drawString(x, y_img + thumb_h/2, "[imagen no dispo]")
                c.setFont("Helvetica-Bold", 10)

            x += thumb_w + 20

        c.save()