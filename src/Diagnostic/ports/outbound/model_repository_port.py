from abc import ABC, abstractmethod
from typing import List, Any
from Diagnostic.domain.Model import Model
from Diagnostic.domain.DiagnosisResult import DiagnosisResult

class ModelRepositoryPort(ABC):
    """
    Define la interfaz para interactuar con el repositorio de modelos
    (por ejemplo, un Model Registry o un almacenamiento local).
    """

    @abstractmethod
    def get_models(self) -> List[Model]:
        """
        Devuelve la lista de todos los modelos disponibles.
        """
        raise NotImplementedError

    @abstractmethod
    def load_model(self, model_id: str) -> Model:
        """
        Carga la información (pesos, configuración) del modelo
        identificado por 'model_id'.
        """
        raise NotImplementedError

    @abstractmethod
    def run_inference(self, model: Model, frame: Any) -> DiagnosisResult:
        """
        Ejecuta la inferencia con el 'model' especificado
        y el frame suministrado, retornando un DiagnosisResult.
        """
        raise NotImplementedError

    