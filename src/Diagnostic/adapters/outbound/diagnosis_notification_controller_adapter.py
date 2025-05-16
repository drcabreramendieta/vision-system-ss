from Diagnostic.ports.outbound.notification_controller_port import NotificationControllerPort
from Report.ports.inbound.report_services_port import ReportServicesPort
from Diagnostic.domain.DiagnosisResult import DiagnosisResult

class DiagnosisNotificationControllerAdapter(NotificationControllerPort):
    """
    Envía cada DiagnosisResult al módulo de Report,
    creando un ReportEntry que se persiste y notifica.
    """
    def __init__(self, report_services: ReportServicesPort):
        self._report_services = report_services

    def notify_result(self, session_id: str, result: DiagnosisResult) -> bool: # Modificamos para que al notify_result se le pase el session_id. El paquete DiagnosisResult no tiene el session_id y no queremos integrarlo ahí para mantener más limpio la clase y los servicios de diagnóstico
        # Llamamos al ReportService con la sesión explícita:
        self._report_services.add_result(
            session_id=session_id,
            frame=result.frame,
            label=result.label.value,
            timestamp=result.timestamp,
        )
        return True