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

    def set_model(self, model: Model) -> None:
        """
        Configura el modelo a utilizar mediante su carga desde el Model Repository.
        Recibe una instancia de Model y usa su 'id' para cargarlo.
        
        :param model: Instancia de Model con la información a configurar.
        """
        # Llama al método 'load_model' del repositorio para "cargar" el modelo.
        loaded_model = self.model_repository.load_model(model.id)
        # Se almacena el modelo cargado para uso posterior.
        self.active_model = loaded_model



