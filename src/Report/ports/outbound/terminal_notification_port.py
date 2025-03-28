
from abc import ABC, abstractmethod
#PREGUNTAR A DIEGO LOS ATRIBUTOS DE DONDE SALDRÍAN
class TerminalNotificationPort(ABC):
    """
    Notifica directamente al Terminal System cuando un reporte está listo.
    """

    @abstractmethod
    def notify_report_ready(self, session_id: str) -> None:
        """
        Notifica que el reporte de la sesión está listo.
        """
        raise NotImplementedError

    @abstractmethod
    def notify_summary(self, session_id: str, summary: str) -> None:
        """
        Notifica un resumen (ej. texto) de la sesión al Terminal System.
        """
        raise NotImplementedError
