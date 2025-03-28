from datetime import datetime
from typing import Dict

from Video.ports.inbound.video_lifecycle_port import VideoLifecyclePort
from Video.domain.VideoSession import VideoSession

class VideoLifecycleServices(VideoLifecyclePort):
    """
    Implementa la gestión del ciclo de vida de la sesión de video.
    """

    def __init__(self):
        # Aquí se podría usar un repositorio o un diccionario en memoria
        self.sessions: Dict[str, VideoSession] = {}

    def start_diagnostic(self, session_id: str) -> None:
        """
        Crea o actualiza la VideoSession para marcarla como IN_PROGRESS.
        """
        session = self.sessions.get(session_id)
        if session is None:
            session = VideoSession(session_id=session_id, status="IN_PROGRESS")
            self.sessions[session_id] = session
        else:
            session.status = "IN_PROGRESS"
            session.start_time = datetime.now()
            session.end_time = None

    def stop_diagnostic(self, session_id: str) -> None:
        """
        Marca la sesión como STOPPED y registra end_time.
        """
        session = self.sessions.get(session_id)
        if session:
            session.status = "STOPPED"
            session.end_time = datetime.now()

    def pause_diagnostic(self, session_id: str) -> None:
        """
        Marca la sesión como PAUSED.
        """
        session = self.sessions.get(session_id)
        if session and session.status == "IN_PROGRESS":
            session.status = "PAUSED"

    def resume_diagnostic(self, session_id: str) -> None:
        """
        Reanuda la sesión si está en PAUSED.
        """
        session = self.sessions.get(session_id)
        if session and session.status == "PAUSED":
            session.status = "IN_PROGRESS"

    def get_session_status(self, session_id: str) -> str:
        """
        Retorna el estado actual de la sesión.
        """
        session = self.sessions.get(session_id)
        return session.status if session else "NOT_FOUND"
