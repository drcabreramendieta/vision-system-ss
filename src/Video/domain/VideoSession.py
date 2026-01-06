from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


# Definición del enumerado para los estados de la sesión
class VideoSessionStatus(Enum):
    CREATED = "Created"
    IN_PROGRESS = "In_progress"
    STOPPED = "Stopped"


@dataclass
class VideoSession:
    """
    Representa el ciclo de vida de una sesión de video.
    Se genera automáticamente un session_id y se establece el estado inicial.
    """
    session_id: UUID = field(default_factory=uuid4)
    status: VideoSessionStatus = VideoSessionStatus.CREATED
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

