# diagnostic/application/diagnosis_services.py

import numpy as np
from Diagnostic.domain.DiagnosisResult import DiagnosisResult
from Diagnostic.domain import InferenceLabel
from Diagnostic.domain.Model import Model
from Diagnostic.ports.inbound.diagnosis_services_port import DiagnosisServicesPort
from Diagnostic.ports.outbound.model_repository_port import ModelRepositoryPort
from Diagnostic.ports.outbound.notification_controller_port import NotificationControllerPort

class DiagnosisServicesImpl(DiagnosisServicesPort):
    """
    Implementación del puerto de entrada 'diagnosis_services_port' para la ejecución
    de inferencia/diagnóstico.

    Esta clase inyecta las dependencias de:
      - ModelRepositoryPort: para ejecutar la inferencia usando el modelo cargado.
      - NotificationPort: para notificar el resultado de la inferencia.
      
    Se asume que el modelo activo ya fue configurado (por ejemplo, mediante ConfigServicesImpl).
    """
    def __init__(self, model_repository: ModelRepositoryPort, notification: NotificationControllerPort, active_model: Model): # Inyectamos las dependencias
        """
        Constructor que recibe las dependencias necesarias para ejecutar la inferencia.
        
        :param model_repository: Instancia que implementa ModelRepositoryPort.
        :param notification: Instancia que implementa NotificationPort.
        :param active_model: Modelo cargado que se usará para la inferencia.
        """
        self.model_repository = model_repository
        self.notification = notification
        self.active_model = active_model

    # Un core de paso no sirve de nada (hay que evitar eso)
    def run_inference(self, frame: np.ndarray) -> DiagnosisResult: #InferenceLabel tiene el label en un formato enum. Pero por coherencia, nos conviene devolver el DiagnosisResult completo, ya que contiene la etiqueta, el frame y el timestamp.
        """
        Ejecuta la inferencia sobre el frame dado utilizando el modelo activo.
      
        :param frame: Datos del frame (por ejemplo, imagen o representación) a evaluar.
        :return: Objeto DiagnosisResult con el resultado completo que contiene la etiqueta de la inferencia.
        """
        # Ejecuta la inferencia usando el modelo activo
        result = self.model_repository.run_inference(self.active_model, frame) #ESTO ESTA BIEN XQ SIRVE COMO FILTRO DE INFORMACIÓN
        
        # Notifica el resultado obtenido
        self.notification.notify_result(result)
        
        # Retorna el resultado de la inferencia
        return result # Devuelve el DiagnosisResult completo
