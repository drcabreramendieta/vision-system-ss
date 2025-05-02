# diagnostic/application/diagnosis_services.py

import numpy as np
from Diagnostic.domain.DiagnosisResult import DiagnosisResult
from Diagnostic.ports.inbound.diagnosis_services_port import DiagnosisServicesPort
from Diagnostic.ports.outbound.model_repository_port import ModelRepositoryPort
from Diagnostic.ports.outbound.notification_controller_port import NotificationControllerPort
from Diagnostic.application.config_services import ConfigServicesImpl

class DiagnosisServicesImpl(DiagnosisServicesPort):
    """
    Implementación del puerto de entrada 'diagnosis_services_port' para la ejecución
    de inferencia/diagnóstico.

    Esta clase inyecta las dependencias de:
      - ModelRepositoryPort: para ejecutar la inferencia usando el modelo cargado.
      - NotificationPort: para notificar el resultado de la inferencia.
      
    Se asume que el modelo activo ya fue configurado (por ejemplo, mediante ConfigServicesImpl).
    """
    def __init__(self,
                 model_repository: ModelRepositoryPort,
                 notification_controller: NotificationControllerPort,
                 config_services: ConfigServicesImpl):
        """
        :param model_repository: para inferir con el modelo activo.
        :param notification_controller: para notificar resultados.
        :param config_services: para listar y cambiar el modelo activo.
        """
        self.repo = model_repository
        self.notify = notification_controller
        self.config = config_services

    def get_models(self):
        return self.config.get_models() # Listar modelos disponibles. Inyectado desde ConfigServicesImpl.

    def set_model(self, model_id: str) -> bool:
        return self.config.set_model(model_id) # Seteo el modelo. Inyectado desde ConfigServicesImpl.

    def run_inference(self, frame: np.ndarray, session_id: str) -> DiagnosisResult: # Modificamos para que al run_inference se le pase el session_id. El paquete DiagnosisResult no tiene el session_id y no queremos integrarlo ahí para mantener más limpio la clase y los servicios de diagnóstico
        result = self.repo.run_inference(frame)
        self.notify.notify_result(session_id, result)
        return result



    