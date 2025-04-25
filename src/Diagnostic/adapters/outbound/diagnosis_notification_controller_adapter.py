from Diagnostic.ports.outbound.notification_controller_port import NotificationControllerPort
from Report.ports.inbound.report_services_port import ReportServicesPort
from Diagnostic.domain.DiagnosisResult import DiagnosisResult

class DiagnosisNotificationControllerAdapter(NotificationControllerPort):
    """
    Envía cada DiagnosisResult al módulo de Report,
    usando el puerto inbound ReportServicesPort.
    """
    def __init__(self, report_services: ReportServicesPort):
        self._report_services = report_services

    def notify_result(self, result: DiagnosisResult) -> bool:
        # Desempaquetamos el resultado y lo pasamos al ReportServices:
        self._report_services.add_result(
            session_id=result.session_id,
            frame=result.frame,
            label=result.label.value,
            timestamp=result.timestamp
        )
        return True