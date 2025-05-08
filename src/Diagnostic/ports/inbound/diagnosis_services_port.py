from abc import ABC, abstractmethod
from Diagnostic.domain.DiagnosisResult import DiagnosisResult
import numpy as np

class DiagnosisServicesPort(ABC):
    """
    Define el servicio de inferencia/diagnóstico que ofrece el Módulo de Diagnóstico.
    """

    @abstractmethod
    def has_model(self) -> bool:
        """
        Verifica si hay un modelo cargado para realizar inferencias.
        """
        raise NotImplementedError

    @abstractmethod
    def run_inference(self, frame: np.ndarray, session_id: str ) -> DiagnosisResult: # Se devuelve un objeto de tipo DiagnosisResult (que incluye session_id)
        """
        Ejecuta el proceso de inferencia sobre el 'frame' dado,
        retornando un objeto DiagnosisResult. Ahora se le pasa el session_id
        para que el servicio de diagnóstico lo pase al NotificationController.
        Con esto se asocia el resultado de la inferencia a la sesión correspondiente.
        """
        raise NotImplementedError
