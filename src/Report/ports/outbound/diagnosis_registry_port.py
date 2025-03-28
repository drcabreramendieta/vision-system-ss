
from abc import ABC, abstractmethod
from typing import List
from Report.domain.ReportEntry import ReportEntry
from Report.domain.Report import Report

class DiagnosisRegistryPort(ABC):
    """
    Permite persistir o recuperar entradas de reporte.
    """

    @abstractmethod
    def save_entry(self, entry: ReportEntry) -> None:
        """
        Guarda un ReportEntry en la base de datos o almacenamiento correspondiente.
        """
        raise NotImplementedError

    @abstractmethod
    def get_entries_by_session(self, session_id: str) -> List[ReportEntry]:
        """
        Retorna todas las entradas asociadas a la sesión.
        """
        raise NotImplementedError

    @abstractmethod
    def save_report(self, report: Report) -> None:
        """
        Guarda un Report completo, si fuera necesario.
        """
        raise NotImplementedError

    @abstractmethod
    def get_report(self, session_id: str) -> Report:
        """
        Retorna un Report completo a partir de la información persistida.
        """
        raise NotImplementedError
