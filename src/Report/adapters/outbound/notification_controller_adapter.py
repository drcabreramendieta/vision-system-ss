# Adaptador creado para propósitos de prueba y demostración


from Report.ports.outbound.notification_controller_port import NotificationControllerPort
from Report.domain.Event import Event

class NotificationControllerAdapter(NotificationControllerPort):
    """
    Adapter que notifica al sistema externo (p.ej., consola o webhook) eventos y reportes listos.
    """
    def __init__(self):
        # Inicializar clientes externos si los hubiera
        pass

    def notify_report_ready(self, session_id: str, summary: str) -> None:
        # Ejemplo simple: imprimir en consola
        print(f"[NOTIFICATION] Report ready for session {session_id}: {summary}")
        return True

    def notify_event(self, event: Event) -> None:
        # Ejemplo simple: imprimir evento
        print(f"[EVENT] Session {event.session_id}: {event.type} at {event.timestamp}")
        return True
