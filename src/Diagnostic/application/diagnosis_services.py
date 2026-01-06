# diagnostic/application/diagnosis_services.py

import numpy as np
from Diagnostic.domain import DiagnosisResult
from Diagnostic.ports.inbound import DiagnosisServicesPort
from Diagnostic.ports.outbound import ModelRepositoryPort
from Diagnostic.ports.outbound import NotificationControllerPort

class DiagnosisServicesImpl(DiagnosisServicesPort):
    """
    Implementación del puerto de entrada 'diagnosis_services_port' para la ejecución
    de inferencia/diagnóstico.

    Esta clase inyecta las dependencias de:
      - ModelRepositoryPort: para ejecutar la inferencia usando el modelo cargado.
      - NotificationPort: para notificar el resultado de la inferencia.
    """
    def __init__(self,
                 model_repository: ModelRepositoryPort,
                 notification_controller: NotificationControllerPort):
        """
        :param model_repository: para inferir con el modelo activo.
        :param notification_controller: para notificar resultados.
        """
        self.repo = model_repository
        self.notify = notification_controller

    def run_inference(self, frame: np.ndarray, session_id: str) -> DiagnosisResult: # Modificamos para que al run_inference se le pase el session_id. El paquete DiagnosisResult no tiene el session_id y no queremos integrarlo ahí para mantener más limpio la clase y los servicios de diagnóstico
        # 1) ejecutar inferencia
        result = self.repo.run_inference(frame, session_id)
        # 2) notificar el resultado (ya contiene session_id)
        self.notify.notify_result(session_id, result) # Ahora result contiene el session_id
        
        return result
    





    
