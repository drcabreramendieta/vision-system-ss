from abc import ABC, abstractmethod
from Diagnostic.domain.DiagnosisResult import DiagnosisResult

class NotificationControllerPort(ABC):
    """
    Define la interfaz para notificar o reportar resultados
    de la inferencia a otro subsistema (ej. Módulo de Reporte).
    """

    @abstractmethod
    def notify_result(self, session_id: str, result: DiagnosisResult) -> bool:
        """
        Envía el resultado (label, frame, timestamp) al componente
        que corresponda (por ejemplo, un Módulo de Reporte).
        """
        raise NotImplementedError
