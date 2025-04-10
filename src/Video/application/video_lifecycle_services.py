from datetime import datetime
from typing import Dict
from uuid import UUID
from Video.ports.inbound import VideoLifecyclePort
from Video.ports.outbound import StreamingControllerPort
from Video.ports.outbound import NotificationControllerPort
from Video.domain import VideoSession, VideoSessionStatus
from Video.domain import Sessions

class VideoLifecycleServices(VideoLifecyclePort):
    """
    Implementa los servicios de ciclo de vida:
      - start_diagnostic
      - stop_diagnostic
      - get_session_status
    Inyecta los puertos de salida 'streaming_controller' y 'notification_controller'.
    """

    def __init__(self, streaming_controller: StreamingControllerPort, notification_controller: NotificationControllerPort):
        """
        Inyecta el puerto de salida para obtener frames.
        """
        # Aquí se podría usar un repositorio o un diccionario en memoria
        self.sessions: Dict[str, VideoSession] = {} # Esta asignación la vamos a dejar asÍ? Ya tenemos la clase Sessions
        self.streaming_controller = streaming_controller
        self.notification_controller = notification_controller
        self.sessions_container = Sessions()


    def start_diagnostic(self) -> UUID: 
        """
        Crea una nueva VideoSession, inyectando los puertos outbound.
        Inicia el stream y retorna el session_id generado.
        """
        session = VideoSession(
            streaming_controller=self.streaming_controller,
            notification_controller=self.notification_controller
        )
        self.sessions_container.add_session(session)
        session.start_session() #Inicia el stream

        # self.sessions[session.session_id] = session #Así estaba antes
        return session.session_id
        

    def stop_diagnostic(self, session_id: UUID) -> None:
        """
        Detiene la sesión, cerrando el stream y actualizando el estado.
        """
        # session = self.sessions.get(session_id) #Así estaba antes        
        session = self.sessions_container.get_session(session_id)
        session.stop_session()


    def get_session_status(self, session_id: str) -> str:
        """
        Retorna el estado actual de la sesión como cadena.
        """
        session = self.sessions_container.get_session(session_id)
        return session.status.value if session else "NOT_FOUND"
