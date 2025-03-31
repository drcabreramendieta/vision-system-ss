from dataclasses import dataclass
from datetime import datetime
import numpy as np

@dataclass
class Frame:
    """
    Representa un frame obtenido desde el DVR o fuente de video.
    El atributo 'data' es un np.ndarray que representa la imagen.
    """
    frame_id: str
    data: np.ndarray
    timestamp: datetime
