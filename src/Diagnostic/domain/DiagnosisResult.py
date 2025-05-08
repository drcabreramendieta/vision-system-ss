from dataclasses import dataclass, field
from datetime import datetime
from Diagnostic.domain import InferenceLabel
import numpy as np

@dataclass
class DiagnosisResult:
    """
    Resultado de inferencia con su sesión asociada.
    """
    session_id: str               # <-- Nuevo campo
    label: InferenceLabel
    frame: np.ndarray             # El frame original (puede usarse para logging o replay)
    timestamp: datetime = field(default_factory=datetime.now)

#Atributos mínimos:

#label: Resultado o etiqueta obtenida de la inferencia (por ejemplo, "fisura", "corrosión", "ok").
#frame: Referencia o identificación del frame evaluado (puede ser la ruta de la imagen, un identificador o incluso el objeto imagen).
#timestamp: Marca temporal que indica cuándo se generó el resultado.

