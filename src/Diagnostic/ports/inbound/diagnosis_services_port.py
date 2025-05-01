from abc import ABC, abstractmethod
from Diagnostic.domain.DiagnosisResult import DiagnosisResult
import numpy as np

class DiagnosisServicesPort(ABC):
    """
    Define el servicio de inferencia/diagnóstico que ofrece el Módulo de Diagnóstico.
    """

    @abstractmethod
    def run_inference(self, frame: np.ndarray) -> bool: # Se devuelve un objeto de tipo InferenceLabel
        """
        Ejecuta el proceso de inferencia sobre el 'frame' dado,
        retornando un objeto DiagnosisResult.
        """
        raise NotImplementedError
