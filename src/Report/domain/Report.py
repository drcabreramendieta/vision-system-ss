from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from Report.domain.ReportEntry import ReportEntry

@dataclass
class Report:
    """
    Representa un reporte completo asociado a una sesión.
    """
    session_id: str
    entries: List[ReportEntry] = field(default_factory=list)
    generated_time: datetime = field(default_factory=datetime.now)
