# file: test/video/dummy_notification_controller.py

from Video.ports.outbound.notification_controller_port import NotificationControllerPort

class DummyNotificationController(NotificationControllerPort):
    """
    Dummy para simular la notificación al módulo de diagnóstico.
    Guarda internamente los frames notificados para luego poder verificar en el test.
    """
    def __init__(self):
        self.notified_frames = []  # Lista para almacenar (session_id, frame)

    def notify(self, session_id: str, frame) -> None:
        self.notified_frames.append((session_id, frame))
