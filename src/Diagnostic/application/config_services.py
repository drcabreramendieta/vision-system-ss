# diagnostic/application/config_services.py

from typing import List
from Diagnostic.domain.Model import Model
from Diagnostic.ports.inbound.config_services_port import ConfigServicesPort
from Diagnostic.ports.outbound.model_repository_port import ModelRepositoryPort

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
        # Variable para almacenar el modelo activo (si es necesario)
        self.active_model = None

    def get_models(self) -> List[Model]:
        """
        Retorna la lista de modelos disponibles consultando el Model Repository.
        
        :return: Lista de objetos Model.
        """
        return self.model_repository.get_models()

    def set_model(self, model_id: str) -> bool: #Esto no debería recibir un modelo, sino un id o la referencia a un objeto. Debe devolver un true o false
        """
        Configura el modelo a utilizar mediante su carga desde el Model Repository.

        :param model: Instancia de Model con la información a configurar.
        """
        # Llama al método 'load_model' del repositorio para "cargar" el modelo. Cargar el modelo (ya con el uso de adaptadores) podría significar que se lo guarda en memoria y se lo deja disponible para la inferencia. Ya con el adaptador de MLflow, se encargaría de cargar el modelo en memoria (o algo por el estilo).
        loaded_model = self.model_repository.load_model(model_id)
        # Se almacena el modelo cargado para uso posterior.
        self.active_model = loaded_model
        # load_model busca dentro de la lista de modelos y le dice al repositorio que cargue o active el modelo
        # Cuando se implemente el adaptador del repositorio de modelos, allí hay instrucciones para cargar el modelo con MLflow
        # Implementar los adaptadores de salida 
        return loaded_model # Esto estaba faltando, ahora devuelve el modelo cargado 02/05/2025
