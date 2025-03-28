from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class Frame:
    """
    Representa un frame (o imagen) obtenido desde el DVR o la fuente de video.
    """
    frame_id: str
    data: Any  # Puede ser la ruta de la imagen, un objeto OpenCV, etc.
    timestamp: datetime
