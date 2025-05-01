# src/Diagnostic/adapters/outbound/mlflow_model_repository_adapter.py
import mlflow, mlflow.pyfunc
from Diagnostic.ports.outbound.model_repository_port import ModelRepositoryPort
from Diagnostic.domain.Model import Model
from Diagnostic.domain.DiagnosisResult import DiagnosisResult
from Diagnostic.domain.InferenceLabel import InferenceLabel
from datetime import datetime
import numpy as np

class MlflowModelRepositoryAdapter(ModelRepositoryPort):
    def __init__(self, config_services):
        mlflow_config = config_services.get_mlflow_config()
        mlflow.set_tracking_uri(mlflow_config.tracking_uri)
        self.model_name = mlflow_config.model_name
        self.client = mlflow.tracking.MlflowClient()
        self._active_pyfunc = None

    def get_models(self):
        registered = self.client.get_registered_model(self.model_name)
        versions = registered.latest_versions or []
        return [
            Model(
                id=ver.version,
                name=self.model_name,
                description=f"v{ver.version}",
                uri=ver.source
            )
            for ver in versions
        ]

    def load_model(self, model_id: str) -> bool:
        uri = f"models:/{self.model_name}/{model_id}"
        try:
            self._active_pyfunc = mlflow.pyfunc.load_model(uri)
            return True
        except Exception:
            return False

    def run_inference(self, frame: np.ndarray) -> DiagnosisResult:
        # Preprocesado mínimo: adaptamos el numpy
        input_df = frame[np.newaxis, ...]
        pred = self._active_pyfunc.predict(input_df)
        label = InferenceLabel(int(pred))  
        return DiagnosisResult(frame=frame,
                               label=label,
                               timestamp=datetime.now(),
                               session_id=None)
