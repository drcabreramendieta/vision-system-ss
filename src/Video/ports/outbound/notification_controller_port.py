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
        Envía cada Frame al módulo de Diagnóstico,
        incluyendo la session_id.
        """
        raise NotImplementedError
