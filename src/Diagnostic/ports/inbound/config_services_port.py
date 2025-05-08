from abc import ABC, abstractmethod
from typing import List
from Diagnostic.domain.Model import Model

class ConfigServicesPort(ABC):
    """
    Define los servicios de configuración que expone el Módulo de Diagnóstico.
    """

    @abstractmethod
    def get_models(self) -> List[Model]:
        """Retorna la lista de modelos disponibles."""
        raise NotImplementedError

    @abstractmethod
    def has_model(self) -> bool:
        """Devuelve True si ya se cargó/un modelo está activo."""
        raise NotImplementedError

    @abstractmethod
    def set_model(self, model_id: str) -> bool:
        """
        Recibe el identificador del modelo a establecer como activo.
        Devuelve True si el modelo se cargó correctamente, False en caso contrario.
        """
        raise NotImplementedError

