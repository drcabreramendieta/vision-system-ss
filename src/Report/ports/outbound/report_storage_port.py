# src/Report/ports/outbound/report_storage_port.py
from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from Report.domain import ReportEntry

class ReportStoragePort(ABC):
    @abstractmethod
    def save_entry(self, entry: ReportEntry) -> None:
        """Persistir un ReportEntry (DB + filesystem si aplica)."""
        raise NotImplementedError

    @abstractmethod
    def fetch_entries(self, session_id: UUID) -> List[ReportEntry]:
        """Leer desde BD todas las entradas de la sesión."""
        raise NotImplementedError

    @abstractmethod
    def list_sessions(self) -> List[UUID]:
        """Listar session_id (tabla sessions)."""
        raise NotImplementedError

