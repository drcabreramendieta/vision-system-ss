from abc import ABC, abstractmethod
from typing import Any
from Diagnostic.domain.DiagnosisResult import DiagnosisResult

class DiagnosisServicesPort(ABC):
    """
    Define el servicio de inferencia/diagnóstico que ofrece el Módulo de Diagnóstico.
    """

    @abstractmethod
    def run_inference(self, frame: Any) -> DiagnosisResult:
        """
        Ejecuta el proceso de inferencia sobre el 'frame' dado,
        retornando un objeto DiagnosisResult.
        """
        raise NotImplementedError
