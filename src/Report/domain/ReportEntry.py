from datetime import datetime
from typing import Any

class ReportEntry:
    """
    Representa la información de un frame (o evento) asociado a una sesión.
    Se utiliza para guardar datos puntuales en el reporte.
    """

    def __init__(self, session_id, frame, label, timestamp): #Ponemos algo en el timestamp?
        """
        :param session_id: Identificador de la sesión a la que pertenece este registro.
        :param frame: Frame (imagen o representación) asociado al cambio de estado.
        :param label: Etiqueta de diagnóstico (p.ej. "DEFECT", "OK") u otro identificador.
        :param timestamp: Momento en que se generó este registro.
        """
        self.session_id = session_id
        self.frame = frame
        self.label = label
        self.timestamp = timestamp

    def __repr__(self):
        return (f"ReportEntry(session_id={self.session_id}, "
                f"label={self.label}, timestamp={self.timestamp})")
