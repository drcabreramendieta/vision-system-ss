# src/Report/ports/inbound/report_services_port.py
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from Report.domain import ReportEntry
from Report.domain import SessionSummary
from datetime import datetime
import numpy as np

class ReportServicesPort(ABC):
    
    @abstractmethod
    def add_result(self,
                   session_id: str,
                   frame: np.ndarray,
                   label: str,
                   timestamp: datetime) -> None:
        """
        Procesa un resultado de inferencia:
          - Guarda el frame en disco
          - Persiste metadatos en BD
          - Notifica por WebSocket
        """
        raise NotImplementedError

    @abstractmethod
    def list_sessions(self) -> List[UUID]:
        """Devuelve todos los session_id registrados."""
        raise NotImplementedError

    @abstractmethod
    def get_entries(self, session_id: UUID) -> List[ReportEntry]:
        """Devuelve lista de entradas de una sesión."""
        raise NotImplementedError

    @abstractmethod
    def get_summary(self, session_id: UUID,
                    operator: str, location: str,
                    job_order: Optional[str]=None
                   ) -> SessionSummary:
        """
        Genera estadísticas y produce SessionSummary.
        Metadatos: operador, ubicación, orden de trabajo.
        """
        raise NotImplementedError


