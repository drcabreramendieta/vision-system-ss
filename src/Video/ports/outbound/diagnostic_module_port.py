
from abc import ABC, abstractmethod
from datetime import datetime

class DiagnosticModulePort(ABC):
    """
    Permite enviar frames al Módulo de Diagnóstico.
    """

    @abstractmethod
    def send_frame_to_diagnosis(self, session_id: str, frame_id: str, data, timestamp: datetime) -> None:
        """
        Envía el frame (con su ID, datos y timestamp) al Módulo de Diagnóstico para su inferencia.
        """
        raise NotImplementedError
