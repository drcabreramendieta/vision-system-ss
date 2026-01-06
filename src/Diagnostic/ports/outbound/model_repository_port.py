from abc import ABC, abstractmethod
from typing import List
import numpy as np
from Diagnostic.domain import DiagnosisResult
from Diagnostic.domain import Model

class ModelRepositoryPort(ABC):
    """
    Define la interfaz para interactuar con el repositorio de modelos
    (por ejemplo, un Model Registry o un almacenamiento local).
    """

    @abstractmethod
    def get_models(self) -> List[Model]:
        """Devuelve la lista de todos los modelos disponibles."""
        raise NotImplementedError

    @abstractmethod
    def load_model(self, model_id: str) -> bool:
        """
        Carga (activa) el modelo identificado por 'model_id' para futuras inferencias.
        Retorna True si la carga fue exitosa.
        """
        raise NotImplementedError

    @abstractmethod
    def has_model(self) -> bool:
        """
        Retorna True si hay un modelo activo en el repositorio.
        """
        raise NotImplementedError

    @abstractmethod
    def run_inference(self, frame: np.ndarray, session_id: str) -> DiagnosisResult:
        """
        Ejecuta inferencia y devuelve un DiagnosisResult
        con session_id incluido.
        """
        raise NotImplementedError

    
