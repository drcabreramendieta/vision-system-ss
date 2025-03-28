
from abc import ABC, abstractmethod

class VideoIngestPort(ABC):
    """
    Maneja la ingesta de frames y su posterior envío al Módulo de Diagnóstico.
    """

    @abstractmethod
    def start_ingest(self, session_id: str) -> None:
        """
        Abre el stream con el DVR y comienza a obtener frames para la sesión dada.
        """
        raise NotImplementedError

    @abstractmethod
    def stop_ingest(self, session_id: str) -> None:
        """
        Cierra el stream y deja de obtener frames.
        """
        raise NotImplementedError
