from abc import ABC, abstractmethod
from Report.domain import Event

class NotificationControllerPort(ABC):
    """
    Notifica cambios o reportes al Terminal System (u otro sistema externo).
    """

    @abstractmethod
    def notify_report_ready(self, session_id: str, summary: str) -> None:
        """
        Notifica que el reporte de la sesión está listo, enviando un resumen.
        """
        raise NotImplementedError

    @abstractmethod
    def notify_event(self, event: Event) -> None:
        """
        Notifica un evento (cambio de estado) al sistema externo.
        """
        raise NotImplementedError
