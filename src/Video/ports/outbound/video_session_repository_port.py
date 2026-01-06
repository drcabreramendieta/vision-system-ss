from abc import ABC, abstractmethod
from uuid import UUID
from Video.domain import VideoSession


class VideoSessionRepositoryPort(ABC):
    """
    Puerto de salida para persistir sesiones de video.
    """

    @abstractmethod
    def add_session(self, session: VideoSession) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_session(self, session_id: UUID) -> VideoSession | None:
        raise NotImplementedError

    @abstractmethod
    def update_session(self, session: VideoSession) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_session(self, session_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_sessions(self) -> list[VideoSession]:
        raise NotImplementedError
