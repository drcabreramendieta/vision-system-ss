# file: test/video/test_video_lifecycle_services_with_mock.py

import unittest
import datetime
from unittest.mock import MagicMock, ANY
from uuid import UUID
from Video.application.video_lifecycle_services import VideoLifecycleServices
from Video.domain.VideoSession import VideoSessionStatus
from Video.ports.outbound.streaming_controller_port import StreamingControllerPort
from Video.ports.outbound.notification_controller_port import NotificationControllerPort

class TestVideoLifecycleServicesWithMock(unittest.TestCase):

    def setUp(self):
        # Crear mocks para los puertos de salida.
        self.mock_streaming_controller = MagicMock(spec=StreamingControllerPort)
        self.mock_notification_controller = MagicMock(spec=NotificationControllerPort)
        
        # Configuramos el mock para open_stream para que retorne True y ejecute el observer.
        def open_stream_side_effect(session_id, observer):
            # Simula la llamada al observer con un frame dummy.
            dummy_frame = type("DummyFrame", (), {
                "frame_id": "dummy_frame_1",
                "data": [0, 1, 2],
                "timestamp": datetime.datetime.now()
            })()
            observer(dummy_frame)
            return True  # Indica que el canal se abrió exitosamente.

        self.mock_streaming_controller.open_stream.side_effect = open_stream_side_effect
        # Configuramos close_stream para que retorne True.
        self.mock_streaming_controller.close_stream.return_value = True
        # Configuramos notify para que retorne True (según el nuevo contrato).
        self.mock_notification_controller.notify.return_value = True

        # Instanciamos el servicio inyectando los mocks.
        self.video_service = VideoLifecycleServices(
            streaming_controller=self.mock_streaming_controller,
            notification_controller=self.mock_notification_controller
        )

    def test_start_diagnostic(self):
        """
        Verifica que start_diagnostic cree una sesión correcta, llame a open_stream
        y notifique un frame.
        """
        session_id = self.video_service.start_diagnostic()
        # Verificamos que el session_id es del tipo UUID.
        self.assertIsInstance(session_id, UUID, "El session_id debe ser un UUID.")
        session = self.video_service.sessions_container.get_session(session_id)
        self.assertIsNotNone(session, "La sesión debe estar almacenada en el contenedor.")
        self.assertEqual(session.status.value, VideoSessionStatus.IN_PROGRESS.value,
                         "El estado inicial debe ser IN_PROGRESS.")
        # Verificamos que open_stream fue llamado con el session_id y algún observer.
        self.mock_streaming_controller.open_stream.assert_called_with(session_id, ANY)
        # Verificamos que notify fue llamado.
        self.assertTrue(self.mock_notification_controller.notify.called,
                        "El método notify debe ser llamado al recibir un frame.")
        # Dado que notify se llama con argumentos con palabra clave, se revisa en kwargs.
        args, kwargs = self.mock_notification_controller.notify.call_args
        # En este caso esperamos que no se hayan pasado parámetros posicionales.
        self.assertEqual(len(args), 0, "No se esperaban argumentos posicionales en notify.")
        # Verificamos que en kwargs se pasen 'session_id' y 'frame'.
        self.assertIn('session_id', kwargs, "Falta el parámetro 'session_id' en notify.")
        self.assertIn('frame', kwargs, "Falta el parámetro 'frame' en notify.")

    def test_stop_diagnostic(self):
        """
        Verifica que stop_diagnostic actualice el estado a STOPPED y llame a close_stream.
        """
        session_id = self.video_service.start_diagnostic()
        self.video_service.stop_diagnostic(session_id)
        session = self.video_service.sessions_container.get_session(session_id)
        self.assertEqual(session.status.value, VideoSessionStatus.STOPPED.value,
                         "El estado debe ser STOPPED tras detener la sesión.")
        self.mock_streaming_controller.close_stream.assert_called_with(session_id)

    def test_get_session_status(self):
        """
        Verifica que get_session_status retorne el estado correcto antes y después de detener la sesión.
        """
        session_id = self.video_service.start_diagnostic()
        status_initial = self.video_service.get_session_status(session_id)
        self.assertEqual(status_initial, VideoSessionStatus.IN_PROGRESS.value,
                         "El estado inicial debe ser IN_PROGRESS.")
        self.video_service.stop_diagnostic(session_id)
        status_final = self.video_service.get_session_status(session_id)
        self.assertEqual(status_final, VideoSessionStatus.STOPPED.value,
                         "El estado tras detener debe ser STOPPED.")

    def test_start_diagnostic_failure(self):
        """
        Simula que open_stream retorna False, lo cual debe provocar que start_diagnostic lance una excepción.
        """
        # Configuramos open_stream para simular fallo.
        self.mock_streaming_controller.open_stream.side_effect = lambda session_id, observer: False
        with self.assertRaises(Exception) as context:
            self.video_service.start_diagnostic()
        self.assertIn("El canal no se pudo abrir", str(context.exception),
                      "Debe lanzar excepción si open_stream retorna False.")

    def test_dummy_frame_content(self):
        """
        Verifica que el dummy frame enviado por el observer tenga el contenido esperado.
        """
        # Configuramos un side_effect personalizado para open_stream.
        def custom_open_stream(session_id, observer):
            dummy_frame = type("DummyFrame", (), {
                "frame_id": "test_frame_123",
                "data": [10, 20, 30],
                "timestamp": datetime.datetime(2023, 1, 1, 12, 0, 0)
            })()
            observer(dummy_frame)
            return True

        self.mock_streaming_controller.open_stream.side_effect = custom_open_stream
        session_id = self.video_service.start_diagnostic()
        
        # Verificamos que notify fue llamado.
        self.assertTrue(self.mock_notification_controller.notify.called,
                        "El método notify debió ser llamado al recibir un frame.")
        # Capturamos los argumentos de la última llamada a notify.
        args, kwargs = self.mock_notification_controller.notify.call_args
        # Dado que notify se invoca con argumentos con nombre, no debemos esperar argumentos posicionales.
        self.assertEqual(len(args), 0, "No se esperaban argumentos posicionales en notify.")
        # Extraemos los valores de kwargs.
        self.assertIn('session_id', kwargs, "Falta el parámetro 'session_id' en notify.")
        self.assertIn('frame', kwargs, "Falta el parámetro 'frame' en notify.")
        notified_session_id = kwargs['session_id']
        notified_frame = kwargs['frame']
        self.assertEqual(notified_session_id, session_id,
                         "El session_id notificado debe coincidir con el de la sesión.")
        self.assertEqual(notified_frame.frame_id, "test_frame_123", "El frame_id debe ser 'test_frame_123'.")
        self.assertEqual(notified_frame.data, [10, 20, 30], "Los datos del frame deben ser [10, 20, 30].")
        self.assertEqual(notified_frame.timestamp, datetime.datetime(2023, 1, 1, 12, 0, 0),
                         "El timestamp debe ser el esperado.")

if __name__ == '__main__':
    unittest.main()
