
from abc import ABC, abstractmethod
from Video.domain.Frame import Frame

class DvrSourcePort(ABC):
    """
    Interactúa con el DVR System para abrir/cerrar stream y obtener frames.
    """

    @abstractmethod
    def open_stream(self, session_id: str) -> None:
        """
        Abre la conexión o stream para la sesión dada.
        """
        raise NotImplementedError

    @abstractmethod
    def get_next_frame(self, session_id: str) -> Frame:
        """
        Obtiene el siguiente frame del DVR.
        """
        raise NotImplementedError

    @abstractmethod
    def close_stream(self, session_id: str) -> None:
        """
        Cierra el stream asociado a la sesión.
        """
        raise NotImplementedError
