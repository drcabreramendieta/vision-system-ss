
from abc import ABC, abstractmethod
from datetime import datetime
from Video.domain.Frame import Frame

class NotificationControllerPort(ABC):
    """
    Permite enviar frames al Módulo de Diagnóstico.
    """

    @abstractmethod
    def notify(self, session_id: str, frame:Frame) -> None: # BUSCAR COMO PONER EL TIPO DE DATO DEL SESSION_ID QUE VIENE DE LA CLASE SESSIONS
        """
        Envía el frame (con su ID, datos y timestamp) al Módulo de Diagnóstico para su inferencia.
        """
        raise NotImplementedError
