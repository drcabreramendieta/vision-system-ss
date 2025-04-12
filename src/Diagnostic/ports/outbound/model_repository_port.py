from abc import ABC, abstractmethod
from typing import List, Any
import numpy as np
from Diagnostic.domain.Model import Model
from Diagnostic.domain.DiagnosisResult import DiagnosisResult
from Diagnostic.domain import InferenceLabel

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
    def run_inference(self, model: Model, frame: np.ndarray) -> DiagnosisResult: # Para ser más coherentes con la arquitectura hexagonal, es mejor devolver un DiagnosisResult (que contiene la etiqueta, timestamp y el frame) en lugar de solo la etiqueta. Esto hace que exista coherencia y al momento de notificar, no tengamos que pasarle el frame nuevamente al puerto de salida de notificación, sino que ya va todo empaquetado en el DiagnosisResult. Hablar con Diego
        """
        Ejecuta la inferencia con el 'model' especificado
        y el frame suministrado, retornando un DiagnosisResult.
        """
        raise NotImplementedError

    