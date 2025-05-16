from datetime import datetime
from typing import Any
from dataclasses import dataclass
from uuid import UUID

@dataclass
class ReportEntry:
    session_id: UUID
    frame_path: str         # Ruta al archivo en disco
    label: str
    timestamp: datetime
