from typing import Callable
from uuid import UUID
from Video.domain import Frame
from Video.application import VideoLifecycleServices
from Video.ports.outbound import StreamingControllerPort
from Video.ports.outbound import NotificationControllerPort
from Video.adapters.outbound import InMemoryVideoSessionRepository

#mock del adaptador de PE
class MockStreamingController(StreamingControllerPort):
    """
    Mock del adaptador de PE.
    """
    def open_stream(self, session_id: UUID, observer: Callable[[Frame], None]) -> bool:
        """
        Mock para abrir el stream.
        """
        return True

    def close_stream(self, session_id: UUID) -> bool:
        """
        Mock para cerrar el stream.
        """
        return True

class MockNotificationController(NotificationControllerPort):
    """
    Mock del adaptador de notificaciones.
    """
    def notify(self, session_id: UUID, frame: Frame) -> None:
        """
        Mock para enviar notificaciones.
        """
        print(f"Notificación enviada para la sesión {session_id}: {frame.frame_id}")    

def main():
    """
    Función principal para ejecutar el test.
    """
    # Crear instancias de los mocks
    streaming_controller = MockStreamingController()
    notification_controller = MockNotificationController()
    session_repository = InMemoryVideoSessionRepository()
    # Crear instancia del servicio de ciclo de vida
    video_lifecycle_service = VideoLifecycleServices(
        streaming_controller,
        notification_controller,
        session_repository,
    )
    # Iniciar la sesion de video
    session_id = video_lifecycle_service.start_video_session()
    # Detener la sesion de video
    video_lifecycle_service.stop_video_session(session_id)
    # Obtener el estado de la sesión
    status = video_lifecycle_service.get_session_status(session_id)
    print(f"Estado de la sesión: {status}")

if __name__ == "__main__":
    main()

#HACER TEST UNITARIOS DE CADA UNO DE LOS MÉTODOS DE CADA MODULO
# LEER LA DOCUMENTACIÓN DE UNITTEST PARA HACER TEST UNITARIOS
# crear carpetas de test por modulo


# El adaptador de salida implementa los puertos de salida
# y usa los servicios de la aplicación (mediante el puerto de entrada) para interactuar con el dominio.
# No se usa directamente la aplicación, sino el adaptador de entrada.
# En el adaptador si está la tecnología concreta (por ejemplo, Flask o FastAPI).
# eL DE VIDEO DEBE USAR LOS FRAMES DE UN VIDEO EN LOCAL. DEBEN ESTAR IMPLEMENTADOS LOS MÉTODOS COMO ESTAN DEFINIDOS EN EL PUERTO DE SALIDA (DEBE SER VALIDO)

# el adaptador de diagnostico vamos a usar con tecnología MLFLOW
