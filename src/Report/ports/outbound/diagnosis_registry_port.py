
from abc import ABC, abstractmethod
from Report.domain.ReportEntry import ReportEntry
from Report.domain import Report
from Report.domain import Event

class DiagnosisRegistryPort(ABC):
    """
    Permite persistir y recuperar información de reportes (Report, ReportEntry, Event).
    """

    @abstractmethod
    def save_report(self, report: Report) -> None:
        """
        Guarda o actualiza un Report en la base de datos.
        """
        raise NotImplementedError

    @abstractmethod
    def save_report_entry(self, entry: ReportEntry) -> None:
        """
        Guarda un ReportEntry (frame asociado a cambio de estado).
        """
        raise NotImplementedError

    @abstractmethod
    def save_event(self, event: Event) -> None:
        """
        Guarda un evento que representa un cambio de estado.
        """
        raise NotImplementedError

    @abstractmethod
    def get_report(self, session_id: str) -> Report:
        """
        Recupera el Report de una sesión específica.
        """
        raise NotImplementedError
