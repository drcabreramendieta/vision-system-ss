# src/Diagnostic/adapters/outbound/mlflow_model_repository_adapter.py

import mlflow
import mlflow.pyfunc
from typing import List
import numpy as np
import pandas as pd
from datetime import datetime

from Diagnostic.ports.outbound.model_repository_port import ModelRepositoryPort
from Diagnostic.domain.Model import Model
from Diagnostic.domain.DiagnosisResult import DiagnosisResult
from Diagnostic.domain.InferenceLabel import InferenceLabel

class MlflowModelRepositoryAdapter(ModelRepositoryPort):
    def __init__(self, tracking_uri: str):
        print(f"[MLFLOW ADAPTER] __init__ recibe tracking_uri = {tracking_uri!r}")
        mlflow.set_tracking_uri(tracking_uri)
        print(f"[MLFLOW ADAPTER] mlflow.get_tracking_uri() → {mlflow.get_tracking_uri()!r}")
        self.client = mlflow.tracking.MlflowClient()
        self._active_pyfunc = None
        self._active_model_name = None
        self._active_model_version = None

    def get_models(self) -> List[Model]:
        """
        Lista TODOS los modelos registrados en MLflow (no filtra versiones).
        """
        registered_models = self.client.search_registered_models()
        return [
            Model(
                id=rm.name,
                name=rm.name,
                description=rm.description or "",
                uri=None,
                implementation=None
            )
            for rm in registered_models
        ]

    def load_model(self, model_id: str) -> bool:
        """
        Activa (carga) la última versión del modelo cuyo nombre es `model_id`.
        En esta variante imprimimos el traceback si algo falla.
        """
        try:
            rm = self.client.get_registered_model(model_id)
            versions = rm.latest_versions or []
            if not versions:
                print(f"[MLFLOW ADAPTER] No hay versiones para el modelo '{model_id}'")
                return False

            # Elegimos la de mayor número
            latest = sorted(versions, key=lambda v: int(v.version), reverse=True)[0]
            uri = f"models:/{latest.name}/{latest.version}"
            print(f"[MLFLOW ADAPTER] Cargando modelo desde URI: {uri}")

            # Aquí puede saltar la excepción
            self._active_pyfunc = mlflow.pyfunc.load_model(uri)
            print(f"[MLFLOW ADAPTER] Modelo cargado correctamente: {latest.name} v{latest.version}")
            return True

        except Exception as e:
            import traceback; traceback.print_exc()
            # Para que FastAPI muestre 500 con el detalle:
            raise RuntimeError(f"Falló al cargar modelo '{model_id}' desde MLflow: {e}")

    def run_inference(self, frame: np.ndarray, session_id: str) -> DiagnosisResult:
        """
        Ejecuta inferencia con el modelo cargado.
        """
        if self._active_pyfunc is None:
            raise RuntimeError("No hay modelo cargado. Llama antes a load_model().")


        #print(f"[MLFLOW ADAPTER] run_inference recibe frame.shape={frame.shape} session_id={session_id}")
        #print(f"[MLFLOW ADAPTER] frame={frame}")

        # el batch axis se lo añade aquí
        batch = frame[np.newaxis, ...]  # shape (1, C, H, W) Agregamos un batch axis
        #print(f"[MLFLOW ADAPTER] batch.shape={batch.shape} batch={batch}")


        raw_pred = self._active_pyfunc.predict(batch)
        #print(f"[MLFLOW ADAPTER] raw_pred={raw_pred}")
        #print(f"[MLFLOW ADAPTER] type(raw_pred)={type(raw_pred)}")
        # 1) Extrae array de raw_pred
        if isinstance(raw_pred, dict):
            # p.ej. {'output': array([[0.1, 0.7, 0.2, …]])}
            arr = list(raw_pred.values())[0]
        elif isinstance(raw_pred, pd.DataFrame):
            arr = raw_pred.values
        else:
            arr = raw_pred
        
        # 2) Nos aseguramos un NumPy array
        arr = np.asarray(arr)  #  shape (1, num_classes)

        # 3) Toma la primera fila y haz argmax
        scores = arr[0]               # shape (n_classes,)
        label_idx = int(np.argmax(scores))
        #print(f"[MLFLOW ADAPTER] scores={scores} label_idx={label_idx}")
        # 4) Ahora sí es un índice válido entre 0 y 9
        label = InferenceLabel(label_idx)

        return DiagnosisResult(
            session_id=session_id,      # <-- aquí incluimos el session_id
            label=label,
            frame=frame,
            timestamp=datetime.now()
        )