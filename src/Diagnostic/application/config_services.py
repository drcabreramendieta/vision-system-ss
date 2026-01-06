# diagnostic/application/config_services.py

from typing import List
from Diagnostic.domain import Model
from Diagnostic.ports.inbound import ConfigServicesPort
from Diagnostic.ports.outbound import ModelRepositoryPort

class ConfigServicesImpl(ConfigServicesPort):
    """
    Implementación del puerto de entrada 'config_services_port' para la configuración
    de modelos en el Módulo de Diagnóstico.

    Esta clase inyecta la dependencia del puerto de salida 'ModelRepositoryPort'
    para obtener la lista de modelos y cargar un modelo específico.
    """
    def __init__(self, model_repository: ModelRepositoryPort): # Inyectamos la dependencia
        """
        Constructor que recibe el adaptador de salida para el repositorio de modelos.
        
        :param model_repository: Instancia que implementa ModelRepositoryPort.
        """
        self.model_repository = model_repository

    def get_models(self) -> List[Model]:
        """
        Retorna la lista de modelos disponibles consultando el Model Repository.
        
        :return: Lista de objetos Model.
        """
        return self.model_repository.get_models()

    def set_model(self, model_id: str) -> bool:
        """
        Configura el modelo a utilizar mediante su carga desde el Model Repository.

        :param model_id: Identificador del modelo a configurar.
        """
        # Llama al método 'load_model' del repositorio para "cargar" el modelo. Cargar el modelo (ya con el uso de adaptadores) podría significar que se lo guarda en memoria y se lo deja disponible para la inferencia. Ya con el adaptador de MLflow, se encargaría de cargar el modelo en memoria (o algo por el estilo).
        # load_model busca dentro de la lista de modelos y le dice al repositorio que cargue o active el modelo
        # Cuando se implemente el adaptador del repositorio de modelos, allí hay instrucciones para cargar el modelo con MLflow
        # Implementar los adaptadores de salida 
        return self.model_repository.load_model(model_id)
    
    def has_model(self) -> bool:
        # Devuelve True si el repositorio tiene un modelo activo
        return self.model_repository.has_model()
