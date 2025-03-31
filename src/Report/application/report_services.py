# file: report/application/report_services.py

from datetime import datetime
from Report.ports.inbound import ReportServicesPort
from Report.ports.outbound import DiagnosisRegistryPort
from Report.ports.outbound import NotificationControllerPort
from Report.domain import ReportEntry
from Report.domain import Report
from Report.domain import Event

class ReportServices(ReportServicesPort):
    """
    Implementa los métodos para gestionar la creación de ReportEntry y la generación de resúmenes.
    """

    def __init__(self, 
                 storage_port: DiagnosisRegistryPort, 
                 notification_port: NotificationControllerPort):
        """
        Inyecta los puertos de salida:
         - diagnosis_registry_port (almacenamiento de reportes)
         - notification_controller_port (notificaciones)
        """
        self.storage_port = storage_port
        self.notification_port = notification_port

    def add_result(self, session_id: str, frame, label: str, timestamp: datetime) -> None:
        """
        Almacena un nuevo 'ReportEntry' en el reporte de la sesión, típicamente
        cuando se detecta un cambio de estado y se desea guardar ese frame.
        """
        entry = ReportEntry(session_id, frame, label, timestamp)
        # Guardamos el entry en el storage
        self.storage_port.save_report_entry(entry)
        # Opcional: Podríamos guardar un 'Event' si queremos
        #event = Event(session_id, old_state, new_state, timestamp, frame=frame) # Esto se debe pensar bien, PREGUNTAR DIEGO
        #self.storage_port.save_event(event)
        #self.notification_port.notify_event(event)

    def generate_summary(self, session_id: str) -> str:
        """
        Construye un resumen de la sesión, lo notifica y lo retorna.
        """
        # Recuperar el Report actual
        report = self.storage_port.get_report(session_id)
        if not report:
            return f"No existe reporte para la sesión {session_id}"

        summary = report.generate_summary()
        # Notificar que el reporte está listo
        self.notification_port.notify_report_ready(session_id, summary)
        return summary
