from __future__ import annotations  # Para que las anotaciones se conviertan en cadenas
from typing import TYPE_CHECKING
import uuid 
from uuid import UUID
import datetime
from enum import Enum, auto
from datetime import datetime
from typing import Optional


if TYPE_CHECKING: # Para evitar importaciones circulares
    from Video.ports.outbound.streaming_controller_port import StreamingControllerPort
    from Video.ports.outbound.notification_controller_port import NotificationControllerPort
    from Video.domain.Frame import Frame


# Definición del enumerado para los estados de la sesión
class VideoSessionStatus(Enum):
    CREATED = "Created"
    IN_PROGRESS = "In_progress"
    STOPPED = "Stopped"


class VideoSession: #
    """
    Representa el ciclo de vida de una sesión de video.
    Se genera automáticamente un session_id y se establece el estado inicial.
    Se inyectan las dependencias para interactuar con el servicio de streaming
    y para notificar al módulo de diagnóstico.
    """
    def __init__(self,streaming_controller: StreamingControllerPort,notification_controller: NotificationControllerPort, start_time: datetime = datetime.now()):
        """
        Inicializa una nueva sesión de video.

        :param streaming_controller: Instancia del puerto de salida para el control del streaming.
        :param notification_controller: Instancia del puerto de salida para notificar al módulo de diagnóstico.
        """
        self.session_id = uuid.uuid4()  # Genera automáticamente un identificador único para la sesión. 
        self.status = VideoSessionStatus.CREATED # Estado inicial de la sesión.
        self.start_time = start_time
        self.end_time = None
        self.streaming_controller = streaming_controller
        self.notification_controller = notification_controller
        
        
    def start_session(self):
        """
        Inicia el stream de video utilizando el puerto de salida para streaming.
        Se pasa un callback interno para procesar cada frame recibido.
        """
        # Se abre el stream, pasando el session_id y la función callback _on_frame_received.
        # Nos registramos el observador del stream de esta sesion
        # DEBERIAMOS RETORNAR UN IDENTIFICADOR DEL HILO STREAMING
        # HAY QUE RESTRINGIR QUE SEA 1 STREAM POR SESION
        if self.streaming_controller.open_stream(self.session_id,self._frame_observer): #Nos registramos como observadores del stream
            self.status = VideoSessionStatus.IN_PROGRESS # Se actualiza el estado de la sesión a IN_PROGRESS.
        else:
            raise Exception("El canal no se pudo abrir") # Si no se puede abrir el stream, se lanza una excepción.
    
    def _frame_observer(self, frame: Frame) -> None: #XQ NO hacemos que la misma session sea el observador? La clase session debería implementar el método observer . Cuando creamos una sessión, tambien abrimos el streaming.
        """
        Callback interno que se invoca cada vez que se recibe un frame.
        Llama al puerto de salida para notificar el frame al módulo de diagnóstico.

        :param frame: Objeto que representa el frame recibido y contiene la session id.
        """
        # Aquí se puede agregar lógica adicional para procesar el frame antes de enviarlo.
        try:
            self.notification_controller.notify(session_id=self.session_id, frame=frame) #Se envía el frame al módulo de diagnóstico
        except Exception as e:
            # loguea, pero no rompas el hilo
            print(f"[VideoSession {self.session_id}] error en notify: {e}")
    
    def stop_session(self) -> None:
        """
        Cierra el stream de video utilizando el puerto de salida para streaming.
        """
        if self.status == VideoSessionStatus.IN_PROGRESS:
            self.streaming_controller.close_stream(self.session_id) #Se cierra el stream asociado a la sesión
            self.status = VideoSessionStatus.STOPPED #Se cambia el estado de la sesión a STOPPED
            self.end_time = datetime.now() #Se registra el tiempo de finalización
        else:
            raise Exception("La sesión no está en progreso")


