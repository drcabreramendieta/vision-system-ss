
from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class ReportEntry:
    """
    Representa un “registro” en el reporte, correspondiente a un frame evaluado.
    """
    session_id: str
    frame_id: str
    data: Any  # puede ser la imagen, la ruta, etc.
    label: str
    timestamp: datetime
