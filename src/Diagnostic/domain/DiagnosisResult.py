from dataclasses import dataclass, field
import datetime
from Diagnostic.domain import InferenceLabel
import numpy as np

@dataclass
class DiagnosisResult:
    """
    Almacena el resultado de la inferencia para un frame.
    El atributo 'label' es de tipo InferenceLabel, encapsulando el valor entero.
    """
    label: InferenceLabel
    frame: np.ndarray
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

#Atributos mínimos:

#label: Resultado o etiqueta obtenida de la inferencia (por ejemplo, "fisura", "corrosión", "ok").
#frame: Referencia o identificación del frame evaluado (puede ser la ruta de la imagen, un identificador o incluso el objeto imagen).
#timestamp: Marca temporal que indica cuándo se generó el resultado.

# Se usa el decorador @dataclass para simplificar la definición de las clases y generar automáticamente métodos como __init__ y __repr__.
# Campo 'frame': Se define con tipo Any para permitir flexibilidad; en una implementación real se podría especificar un tipo concreto (por ejemplo, np.ndarray si se usa OpenCV).
# Default Factory en timestamp: Se utiliza field(default_factory=datetime.datetime.now) para que el valor de timestamp se asigne en el momento de instanciar la clase, evitando problemas al usar un valor estático.