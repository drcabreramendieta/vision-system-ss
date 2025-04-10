from uuid import UUID
from abc import ABC, abstractmethod
from datetime import datetime
from Video.domain.Frame import Frame

class NotificationControllerPort(ABC):
    """
    Permite enviar frames al Módulo de Diagnóstico.
    """

    @abstractmethod
    def notify(self, session_id: UUID, frame:Frame) -> bool: # BUSCAR COMO PONER EL TIPO DE DATO DEL SESSION_ID QUE VIENE DE LA CLASE SESSIONS
        """
        Envía el frame (con su ID, datos y timestamp) al Módulo de Diagnóstico para su inferencia.
        
        :param session_id: Identificador de la sesión.
        :param frame: Objeto Frame que contiene la información del frame.
        :return: True si la notificación fue enviada correctamente, False en caso contrario.
        """
        raise NotImplementedError
