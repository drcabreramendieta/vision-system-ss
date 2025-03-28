
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class VideoSession:
    """
    Representa el ciclo de vida de una sesión de diagnóstico (start, stop, pause, resume).
    """
    session_id: str
    status: str  # "IN_PROGRESS", "PAUSED", "STOPPED", etc.
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
