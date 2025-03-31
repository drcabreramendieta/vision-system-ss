
import uuid
import datetime
from enum import Enum
from datetime import datetime
from typing import Optional
from Video.ports.outbound import StreamingControllerPort
from Video.ports.outbound import NotificationControllerPort
from Video.domain.Frame import Frame

# Definición del enumerado para los estados de la sesión
class VideoSessionStatus(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    STOPPED = "STOPPED"

#Sessions seria una colección de VideoSession
class VideoSession: #APARTE OTRA CLASE QUE SE LLAME SESSIONS Y QUE TENGA EL GENERADOR DE UUID (UN OBJETO DE TIPO SESSIONS, CON DICCIONARIO DE SESIONES)
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
        self.session_id = str(uuid.uuid4())  # Genera automáticamente un identificador único para la sesión. 
        self.status = VideoSessionStatus.IN_PROGRESS # Estado inicial de la sesión.
        self.start_time = start_time
        self.end_time = None
        self.streaming_controller = streaming_controller
        self.notification_controller = notification_controller
        
        
    def start_session(self):
        """
        Inicia el stream de video utilizando el puerto de salida para streaming.
        Se pasa un callback interno para procesar cada frame recibido.
        """
        if self.streaming_controller is not None:
            # Se abre el stream, pasando el session_id y la función callback _on_frame_received.
            # Nos registramos el observador del stream de esta sesion
            self.streaming_controller.open_stream(self.session_id,self._frame_observer) #Nos registramos como observadores del stream
    
    def _frame_observer(self, frame: Frame) -> None: #XQ NO hacemos que la misma session sea el observador? La clase session debería implementar el método observer . Cuando creamos una sessión, tambien abrimos el streaming.
        """
        Callback interno que se invoca cada vez que se recibe un frame.
        Llama al puerto de salida para notificar el frame al módulo de diagnóstico.

        :param frame: Objeto que representa el frame recibido.
        """
        # Aquí se puede agregar lógica adicional para procesar el frame antes de enviarlo.
        if self.notification_controller is not None:
            self.notification_controller.notify(session_id=self.session_id, frame=frame) #Se envía el frame al módulo de diagnóstico   
    
    def stop_session(self) -> None:
        """
        Cierra el stream de video utilizando el puerto de salida para streaming.
        """
        if self.streaming_controller is not None:
            self.streaming_controller.close_stream(self.session_id) #Se cierra el stream asociado a la sesión
            self.status = VideoSessionStatus.STOPPED #Se cambia el estado de la sesión a STOPPED
            self.end_time = datetime.now() #Se registra el tiempo de finalización


    def update_status(self, new_status: VideoSessionStatus) -> None:
        """
        Actualiza el estado de la sesión. Si se detiene, se registra el end_time.
        """
        self.status = new_status
        if new_status == VideoSessionStatus.STOPPED:
            self.end_time = datetime.now()    
    
