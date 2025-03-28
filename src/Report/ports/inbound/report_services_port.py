from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from Report.domain.Report import Report

class ReportServicesPort(ABC):
    """
    Recibe y almacena resultados, y permite consultar/generar reportes.
    """

    @abstractmethod
    def add_result(self, session_id: str, frame: Any, label: str, timestamp: datetime) -> None:
        """
        Almacena un nuevo registro de reporte (ReportEntry) asociado a la sesión.
        """
        raise NotImplementedError

    @abstractmethod
    def get_report(self, session_id: str) -> Report:
        """
        Retorna un reporte completo (un objeto Report) con todas las entradas asociadas a la sesión.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_summary(self, session_id: str) -> str:
        """
        Crea un resumen (por ejemplo, en formato texto) con estadísticas de la sesión.
        """
        raise NotImplementedError
