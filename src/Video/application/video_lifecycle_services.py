from datetime import datetime
from typing import Callable
from uuid import UUID
from Video.ports.inbound import VideoLifecyclePort
from Video.ports.outbound import (
    NotificationControllerPort,
    StreamingControllerPort,
    VideoSessionRepositoryPort,
)
from Video.domain import VideoSession, VideoSessionStatus
from Video.domain import Frame

class VideoLifecycleServices(VideoLifecyclePort):
    """
    Implementa los servicios de ciclo de vida:
      - start_video_session
      - stop_video_session
      - get_session_status
    Inyecta los puertos de salida 'streaming_controller' y 'notification_controller'.
    """

    def __init__(
        self,
        streaming_controller: StreamingControllerPort,
        notification_controller: NotificationControllerPort,
        session_repository: VideoSessionRepositoryPort,
    ):
        """
        Inyecta el puerto de salida para obtener frames.
        """
        self.streaming_controller = streaming_controller
        self.notification_controller = notification_controller
        self.session_repository = session_repository


    def _build_frame_observer(self, session_id: UUID) -> Callable[[Frame], None]:
        def _observer(frame: Frame) -> None:
            try:
                self.notification_controller.notify(session_id=session_id, frame=frame)
            except Exception as exc:
                print(f"[VideoLifecycleServices {session_id}] error en notify: {exc}")
        return _observer

    def start_video_session(self) -> UUID:
        """
        Crea una nueva VideoSession, inyectando los puertos outbound.
        Inicia el stream y retorna el session_id generado.
        """
        session = VideoSession()
        self.session_repository.add_session(session)
        observer = self._build_frame_observer(session.session_id)
        if self.streaming_controller.open_stream(session.session_id, observer):
            session.status = VideoSessionStatus.IN_PROGRESS
            self.session_repository.update_session(session)
        else:
            self.session_repository.remove_session(session.session_id)
            raise RuntimeError("El canal no se pudo abrir")
        return session.session_id
        

    def stop_video_session(self, session_id: UUID) -> str: #USAR EL MISMO NOMBRE DE LA CLASE. DEVOLVER UN ENUM DE VideoSessionStatus
        """
        Detiene la sesión, cerrando el stream y actualizando el estado.
        """
        session = self.session_repository.get_session(session_id)
        if not session:
            raise KeyError(f"Sesión {session_id} no encontrada")
        if session.status != VideoSessionStatus.IN_PROGRESS:
            raise RuntimeError("La sesión no está en progreso")
        self.streaming_controller.close_stream(session_id)
        session.status = VideoSessionStatus.STOPPED
        session.end_time = datetime.now()
        self.session_repository.update_session(session)
        return session.status.value


    def get_session_status(self, session_id: UUID) -> str:  #Devolver un elemento class VideoSessionStatus defubudi en VideoSession.py
        """
        Retorna el estado actual de la sesión como cadena.
        """
        session = self.session_repository.get_session(session_id)
        return session.status.value if session else "NOT_FOUND"   #Ver bien que pasa si no existe la session
        # Lanzar raise exception "no existe session"
