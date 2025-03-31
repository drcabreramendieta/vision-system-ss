
class Sessions:
    """
    Contenedor para gestionar múltiples VideoSession.
    Permite agregar, recuperar, eliminar y listar sesiones.
    """
    def __init__(self):
        # Diccionario interno para almacenar sesiones: {session_id: VideoSession}
        self._sessions = {}

    def add_session(self, session): # REVISAR BIEN SI ASI DEBERÍA SER
        """
        Agrega una nueva sesión al contenedor.

        :param session: Instancia de VideoSession a agregar.
        """
        self._sessions[session.session_id] = session

    def get_session(self, session_id):
        """
        Recupera una sesión a partir de su session_id.

        :param session_id: Identificador de la sesión.
        :return: La instancia de VideoSession o None si no existe.
        """
        return self._sessions.get(session_id)

    def remove_session(self, session_id):
        """
        Elimina una sesión del contenedor.

        :param session_id: Identificador de la sesión a eliminar.
        """
        if session_id in self._sessions:
            del self._sessions[session_id]

    def list_sessions(self):
        """
        Retorna una lista de todas las sesiones almacenadas.

        :return: Lista de instancias de VideoSession.
        """
        return list(self._sessions.values())
