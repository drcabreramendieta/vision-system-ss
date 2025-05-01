
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class Model:
    """
    Representa la información esencial de un modelo de inferencia.
    """
    id: str
    name: str
    description: str
    uri: Optional[str] = None             # Ruta al modelo (p.ej. en MLflow)
    implementation: Optional[Any] = None  # Objeto de inferencia cargado (p.ej. pyfunc) 