# Descripción: Puerto de entrada que expone métodos para controlar la sesión de video.
from abc import ABC, abstractmethod
from uuid import UUID

class VideoLifecyclePort(ABC):
    """
    Expone métodos para controlar la sesión de video.
    """
    # Se debe cambiar el tipo de dato de session_id
    @abstractmethod
    def start_video_session(self) -> UUID:
        """
        Inicia la sesión de video, creando o actualizando una VideoSession.
        """
        raise NotImplementedError

    @abstractmethod
    def stop_video_session(self, session_id: UUID) -> str:
        """
        Detiene la sesión, marcándola como STOPPED.
        """
        raise NotImplementedError

    @abstractmethod
    def get_session_status(self, session_id: UUID) -> str:
        """
        Retorna el estado actual de la sesión (IN_PROGRESS, STOPPED, etc.).
        """
        raise NotImplementedError
