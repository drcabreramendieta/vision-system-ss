# file: Diagnostic/adapters/outbound/mlflow_model_repository_adapter.py

import mlflow.pyfunc
import datetime
import numpy as np
from typing import List, Any

# Importamos el puerto de salida que debemos implementar.
from Diagnostic.ports.outbound.model_repository_port import ModelRepositoryPort

# Importamos las entidades de dominio.
from Diagnostic.domain.Model import Model
from Diagnostic.domain.DiagnosisResult import DiagnosisResult
from Diagnostic.domain.InferenceLabel import InferenceLabel

class MLflowModelRepositoryAdapter(ModelRepositoryPort):
    """
    Adaptador para el repositorio de modelos que utiliza MLflow.
    
    Este adaptador implementa la interfaz ModelRepositoryPort y se encarga de:
      - Listar modelos disponibles.
      - Cargar un modelo a partir de un identificador (que en este caso, se usará como URI).
      - Ejecutar la inferencia a través del modelo cargado y devolver un DiagnosisResult.
    
    Se espera que la configuración de MLflow (tracking URI) se realice antes de instanciar este adaptador.
    """
    def __init__(self, tracking_uri: str):
        """
        Inicializa el adaptador con el tracking URI.
        
        :param tracking_uri: La URI del servidor de MLflow Tracking/Registry.
        """
        import mlflow
        mlflow.set_tracking_uri(tracking_uri)
        self.tracking_uri = tracking_uri

    def get_models(self) -> List[Model]:
        """
        Retorna la lista de modelos disponibles en el Model Registry.
        
        Nota: Para simplificar, en esta implementación se retorna una lista estática.
        En una implementación real, se podría utilizar MLflowClient para buscar modelos publicados.
        
        :return: Lista de objetos Model.
        """
        # Ejemplo: Retornamos una lista de modelos ficticios.
        return [
            Model(id="model_1", name="ResNet50", description="Modelo ResNet50 entrenado para detección de defectos"),
            Model(id="model_2", name="VGG16", description="Modelo VGG16 para clasificación de imágenes")
        ]
    
    def load_model(self, model_id: str) -> Model:
        """
        Carga el modelo registrado en MLflow utilizando el model_id (que en este caso se espera sea un URI).
        
        Utiliza mlflow.pyfunc.load_model para cargar el modelo real.
        
        :param model_id: Identificador o URI del modelo.
        :return: Un objeto Model con información básica y, en un adaptador real, el modelo cargado.
        :raises RuntimeError: Si no se puede cargar el modelo.
        """
        try:
            # Carga el modelo a través de MLflow
            loaded_model = mlflow.pyfunc.load_model(model_id)
            # Aquí podrías almacenar el objeto loaded_model en el Model,
            # pero para efectos de la abstracción, retornamos un objeto Model con los metadatos.
            return Model(id=model_id, name="LoadedModel", description="Modelo cargado desde MLflow")
        except Exception as e:
            raise RuntimeError(f"Error al cargar el modelo con id {model_id}: {e}")
    
    def run_inference(self, model: Model, frame: Any) -> DiagnosisResult:
        """
        Ejecuta la inferencia utilizando el modelo cargado y el frame proporcionado.
        
        En una implementación real, se utilizaría el objeto cargado de MLflow (por ejemplo, un objeto PyFuncModel)
        para realizar la predicción. Aquí, simulamos una predicción.
        
        :param model: Objeto Model que representa el modelo activo.
        :param frame: Datos del frame sobre el que se ejecuta la inferencia (por ejemplo, un np.ndarray).
        :return: Un objeto DiagnosisResult con el resultado de la inferencia.
        """
        try:
            # Simular la ejecución de la inferencia:
            # En una implementación real, cargarías el modelo MLflow y llamarías a predict.
            # Por ejemplo: prediction = loaded_model.predict(np.array([frame]))
            # Aquí simulamos que se ha predicho un label NORMAL.
            prediction = InferenceLabel.NORMAL
            
            # Crear y retornar un DiagnosisResult completo.
            result = DiagnosisResult(
                label=prediction,
                frame=frame,  # Se espera que frame sea un np.ndarray o similar.
                timestamp=datetime.datetime.now()
            )
            return result
        except Exception as e:
            raise RuntimeError(f"Error durante la inferencia: {e}")
