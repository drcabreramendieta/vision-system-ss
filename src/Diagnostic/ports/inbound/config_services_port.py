from abc import ABC, abstractmethod
from typing import List
from Diagnostic.domain.Model import Model

class ConfigServicesPort(ABC):
    """
    Define los servicios de configuración que expone el Módulo de Diagnóstico.
    """

    @abstractmethod
    def get_models(self) -> List[Model]:
        """
        Retorna la lista de modelos disponibles.
        """
        raise NotImplementedError

    @abstractmethod
    def set_model(self, model: Model) -> None:
        """
        Recibe una instancia de 'Model' y la establece
        como modelo a usar (vía carga en el repositorio).
        """
        raise NotImplementedError

