from typing import Dict
from uuid import UUID
from Video.domain import VideoSession
from Video.ports.outbound import VideoSessionRepositoryPort


class InMemoryVideoSessionRepository(VideoSessionRepositoryPort):
    """
    Repositorio en memoria para sesiones de video.
    """

    def __init__(self) -> None:
        self._sessions: Dict[UUID, VideoSession] = {}

    def add_session(self, session: VideoSession) -> None:
        if session.session_id in self._sessions:
            raise ValueError(f"Sesion {session.session_id} ya existe")
        self._sessions[session.session_id] = session

    def get_session(self, session_id: UUID) -> VideoSession | None:
        return self._sessions.get(session_id)

    def update_session(self, session: VideoSession) -> None:
        if session.session_id not in self._sessions:
            raise KeyError(f"Sesion {session.session_id} no encontrada")
        self._sessions[session.session_id] = session

    def remove_session(self, session_id: UUID) -> None:
        self._sessions.pop(session_id, None)

    def list_sessions(self) -> list[VideoSession]:
        return list(self._sessions.values())
