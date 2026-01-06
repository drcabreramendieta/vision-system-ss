# src/Report/ports/outbound/report_notification_port.py
from abc import ABC, abstractmethod
from Report.domain import ReportEntry
from Report.domain import SessionSummary

class ReportNotificationPort(ABC):
    @abstractmethod
    def notify_entry(self, entry: ReportEntry) -> None:
        """Emite por WebSocket la nueva entrada."""
        raise NotImplementedError


    @abstractmethod
    def notify_summary(self, summary: SessionSummary, metadata: dict) -> None:
        """Emite un evento de cierre con el resumen."""
        raise NotImplementedError

