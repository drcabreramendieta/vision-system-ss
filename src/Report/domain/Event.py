
class Event:
    """
    Representa un cambio de estado o suceso relevante dentro de la sesión.
    Puede usarse para notificar y almacenar en la base de datos de reportes.
    """

    def __init__(self, session_id, old_state, new_state, timestamp, frame=None):
        """
        :param session_id: Identificador de la sesión donde ocurre el evento.
        :param old_state: Estado anterior.
        :param new_state: Estado nuevo.
        :param timestamp: Momento en que se produce el cambio.
        :param frame: (Opcional) Frame asociado al evento de cambio.
        """
        self.session_id = session_id
        self.old_state = old_state
        self.new_state = new_state
        self.timestamp = timestamp
        self.frame = frame

    def __repr__(self):
        return (f"Event(session_id={self.session_id}, "
                f"old_state={self.old_state}, new_state={self.new_state}, "
                f"timestamp={self.timestamp})")
