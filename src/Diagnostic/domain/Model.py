from dataclasses import dataclass

@dataclass
class Model:
    """
    Representa la información esencial de un modelo de inferencia.
    """
    id: str
    name: str
    description: str

# Atributos mínimos:
#id: Identificador único del modelo.
#name: Nombre descriptivo del modelo.
#description: Breve descripción del modelo (por ejemplo, la arquitectura, entrenamiento, etc.).
# Se usa el decorador @dataclass para simplificar la definición de las clases y generar automáticamente métodos como __init__ y __repr__.   