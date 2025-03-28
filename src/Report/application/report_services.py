# file: report/application/report_services.py

from datetime import datetime
from typing import Any

from Report.ports.inbound.report_services_port import ReportServicesPort
from Report.ports.outbound.diagnosis_registry_port import DiagnosisRegistryPort
from Report.ports.outbound.terminal_notification_port import TerminalNotificationPort

from Report.domain.ReportEntry import ReportEntry
from Report.domain.Report import Report

class ReportServices(ReportServicesPort):
    """
    Implementa el puerto de entrada para manejar la recepción de resultados y la generación de reportes.
    """

    def __init__(self, 
                 registry_port: DiagnosisRegistryPort, 
                 notification_port: TerminalNotificationPort):
        """
        Inyecta los puertos de salida necesarios.
        """
        self.registry_port = registry_port
        self.notification_port = notification_port

    def add_result(self, session_id: str, frame: Any, label: str, timestamp: datetime) -> None:
        """
        Crea un ReportEntry y lo guarda a través del DiagnosisRegistryPort.
        """
        entry = ReportEntry(
            session_id=session_id,
            frame_id=str(getattr(frame, "frame_id", "unknown_frame")),
            data=getattr(frame, "data", frame),  # fallback si 'frame' es un simple dict
            label=label,
            timestamp=timestamp
        )
        self.registry_port.save_entry(entry)

    def get_report(self, session_id: str) -> Report:
        """
        Recupera todas las entradas de la sesión y construye un objeto Report.
        """
        entries = self.registry_port.get_entries_by_session(session_id)
        # Se podría retornar un Report guardado, pero aquí lo construimos en el momento
        report = Report(session_id=session_id, entries=entries)
        return report

    def generate_summary(self, session_id: str) -> str:
        """
        Crea un resumen de la sesión (por ejemplo, conteo de defectos vs OK).
        Luego notifica al Terminal si se desea.
        """
        entries = self.registry_port.get_entries_by_session(session_id)
        
        # Ejemplo: contar cuántas veces aparece cada label
        label_count = {}
        for e in entries:
            label_count[e.label] = label_count.get(e.label, 0) + 1
        
        summary_str = f"Summary for session {session_id}:\n"
        for label, count in label_count.items():
            summary_str += f"  {label}: {count}\n"

        # Notificar al Terminal System
        self.notification_port.notify_summary(session_id, summary_str)
        return summary_str
