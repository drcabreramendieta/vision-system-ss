
import numpy as np
from typing import List, Any
import mlflow
import mlflow.pyfunc
from datetime import datetime
from Diagnostic.ports.outbound.model_repository_port import ModelRepositoryPort
from Diagnostic.domain.Model import Model
from Diagnostic.domain.DiagnosisResult import DiagnosisResult
from Diagnostic.domain.InferenceLabel import InferenceLabel


class MlflowModelRepositoryAdapter(ModelRepositoryPort):
    """
    Adapter para interactuar con MLflow Model Registry:
      - Obtiene registros de modelos
      - Carga un modelo específico
      - Ejecuta inferencia usando el modelo cargado
    """
    def __init__(self, config_services):
        # ConfigServicesImpl expone la URI y nombre de experimento
        mlflow_config = config_services.get_mlflow_config()  # Preguntar a Diego si sería algo así o dónde se define lo del servidor MLflow
        mlflow.set_tracking_uri(mlflow_config.tracking_uri)
        self.model_name = mlflow_config.model_name
        self.client = mlflow.tracking.MlflowClient()

    def get_models(self) -> List[Model]:
        """Lista modelos registrados bajo el nombre configurado"""
        registered = self.client.get_registered_model(self.model_name)
        versions = registered.latest_versions or []
        return [Model(id=ver.version, uri=ver.source) for ver in versions]

    def load_model(self, model_id: str) -> Model:
        """Carga un modelo específico en memoria"""
        model_uri = f"models:/{self.model_name}/{model_id}"
        pyfunc_model = mlflow.pyfunc.load_model(model_uri)
        return Model(id=model_id, implementation=pyfunc_model)

    def run_inference(self, model: Model, frame: 'np.ndarray') -> DiagnosisResult:
        """Ejecuta la inferencia y empaqueta el resultado en un DiagnosisResult"""
        # Preprocesamiento si aplica
        input_df = frame.data[None, ...]
        pred = model.implementation.predict(input_df)
        # Asumimos que pred es etiqueta o arreglo
        label = InferenceLabel(pred)
        result = DiagnosisResult(
            session_id=None,
            frame=frame,
            label=label,
            timestamp=datetime.now()
        )
        return result


