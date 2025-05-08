from dataclasses import dataclass
from datetime import datetime
import numpy as np
from uuid import UUID

@dataclass
class Frame:
    """
    Representa un frame obtenido desde el DVR o fuente de video.
    El atributo 'data' es un np.ndarray que representa la imagen.
    """
    session_id: UUID       # <— nuevo. Frame también tiene un session_id
    frame_id: int
    data: np.ndarray
    timestamp: datetime
