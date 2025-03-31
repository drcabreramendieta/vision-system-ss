# Descripción: Puerto de entrada que expone métodos para controlar la sesión de video y, por ende, el ciclo de vida del diagnóstico.
from abc import ABC, abstractmethod

class VideoLifecyclePort(ABC):
    """
    Expone métodos para controlar la sesión de video y, por ende, el ciclo de vida del diagnóstico.
    """
    # Se debe cambiar el tipo de dato de session_id
    @abstractmethod
    def start_diagnostic(self, session_id: str) -> None:
        """
        Inicia la sesión de diagnóstico, creando o actualizando una VideoSession.
        """
        raise NotImplementedError

    @abstractmethod
    def stop_diagnostic(self, session_id: str) -> None:
        """
        Detiene la sesión, marcándola como STOPPED.
        """
        raise NotImplementedError

    @abstractmethod
    def get_session_status(self, session_id: str) -> str:
        """
        Retorna el estado actual de la sesión (IN_PROGRESS, STOPPED, etc.).
        """
        raise NotImplementedError
