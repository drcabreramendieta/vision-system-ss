# src/Video/domain/Sessions.py
from typing import Dict
from uuid import UUID
from Video.domain.VideoSession import VideoSession

class Sessions:
    """
    Contenedor para gestionar múltiples VideoSession.
    """
    def __init__(self):
        self._sessions: Dict[UUID, VideoSession] = {}

    def add_session(self, session: VideoSession) -> None:
        """
        Agrega una nueva sesión.
        Lanza ValueError si session_id ya existe.
        """
        if session.session_id in self._sessions:
            raise ValueError(f"Sesión {session.session_id} ya existe")
        self._sessions[session.session_id] = session

    def get_session(self, session_id: UUID) -> VideoSession | None:
        return self._sessions.get(session_id)

    def remove_session(self, session_id: UUID) -> None:
        self._sessions.pop(session_id, None)

    def list_sessions(self) -> list[VideoSession]:
        return list(self._sessions.values())
