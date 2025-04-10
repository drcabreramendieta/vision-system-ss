# file: test/video/test_video_lifecycle_services.py

import unittest
import datetime
from Video.application.video_lifecycle_services import VideoLifecycleServices
from Video.domain.VideoSession import VideoSessionStatus
from .dummy_streaming_controller import DummyStreamingController
from .dummy_notification_controller import DummyNotificationController

class TestVideoLifecycleServices(unittest.TestCase):
    def setUp(self):
        # Instanciar los dummies para los puertos de salida.
        self.streaming_controller = DummyStreamingController()
        self.notification_controller = DummyNotificationController()
        # Crear la instancia del servicio, inyectando los dummies.
        self.video_service = VideoLifecycleServices(
            self.streaming_controller,
            self.notification_controller
        )

    def test_start_diagnostic(self):
        """
        Prueba individual para start_diagnostic().
        Se verifica que se cree y almacene una sesión con estado IN_PROGRESS.
        """
        session_id = self.video_service.start_diagnostic()
        self.assertIsInstance(session_id, str, "El session_id debe ser una cadena de texto")
        session = self.video_service.sessions_container.get_session(session_id)
        self.assertIsNotNone(session, "La sesión debe existir en el contenedor")
        self.assertEqual(session.status.value, VideoSessionStatus.IN_PROGRESS.value,
                         "El estado inicial debe ser IN_PROGRESS")
        # Verificar que el observer se haya invocado (es decir, que se haya notificado al menos un frame)
        self.assertGreater(len(self.notification_controller.notified_frames), 0,
                            "Debe haberse notificado al menos un frame al iniciar el stream")

    def test_stop_diagnostic(self):
        """
        Prueba individual para stop_diagnostic(session_id).
        Verifica que el estado se actualice a STOPPED y que se asigne end_time.
        """
        session_id = self.video_service.start_diagnostic()
        self.video_service.stop_diagnostic(session_id)
        session = self.video_service.sessions_container.get_session(session_id)
        self.assertEqual(session.status.value, VideoSessionStatus.STOPPED.value,
                         "El estado debe ser STOPPED tras detener la sesión")
        self.assertIsNotNone(session.end_time, "El end_time debe asignarse al detener la sesión")

    def test_get_session_status(self):
        """
        Prueba individual para get_session_status(session_id).
        Primero se verifica el estado tras iniciar la sesión y luego después de detenerla.
        """
        session_id = self.video_service.start_diagnostic()
        status_initial = self.video_service.get_session_status(session_id)
        self.assertEqual(status_initial, VideoSessionStatus.IN_PROGRESS.value,
                         "El estado inicial debe ser IN_PROGRESS")
        self.video_service.stop_diagnostic(session_id)
        status_final = self.video_service.get_session_status(session_id)
        self.assertEqual(status_final, VideoSessionStatus.STOPPED.value,
                         "El estado final debe ser STOPPED después de detener la sesión")

if __name__ == '__main__':
    unittest.main()
