from typing import Callable
from abc import ABC, abstractmethod
from Video.domain.Frame import Frame

class StreamingControllerPort(ABC):
    """
    Interactúa con el servicio de streaming que provee frames.
    """

    @abstractmethod
    def open_stream(self,session_id: str, observer: Callable[[Frame],None]) -> None:
        """
        Abre la conexión/stream para la sesión dada y, por cada frame recibido,
        invoca la función 'observer'.
        """
        raise NotImplementedError


    @abstractmethod
    def close_stream(self, session_id: str) -> None:
        """
        Cierra el stream asociado a la sesión.
        """
        raise NotImplementedError
