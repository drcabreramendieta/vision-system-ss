from abc import ABC, abstractmethod
from datetime import datetime

class ReportServicesPort(ABC):
    """
    Expone los servicios para gestionar reportes:
      - add_result: Almacena un frame (ReportEntry) asociado a un cambio de estado.
      - generate_summary: Retorna un resumen de la sesión en formato string.
    """

    @abstractmethod
    def add_result(self, session_id: str, frame, label: str, timestamp: datetime) -> None: #Esto se debe conectar con la clase DiagnosisResults del modulo de Diagnostico?
        """
        Almacena un nuevo 'ReportEntry' asociado a la sesión, normalmente
        cuando se detecta un cambio de estado y se quiere guardar el frame.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_summary(self, session_id: str) -> str:
        """
        Devuelve un resumen (texto) de la sesión dada.
        """
        raise NotImplementedError

