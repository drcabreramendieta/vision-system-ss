# File: diagnostic/adapters/outbound/model_repository_adapter.py

from typing import List, Any
import datetime
import random

from Diagnostic.domain.Model import Model
from Diagnostic.domain.DiagnosisResult import DiagnosisResult
from Diagnostic.ports.outbound.model_repository_port import ModelRepositoryPort

class ModelRepositoryAdapter(ModelRepositoryPort):
    """
    Implementa el puerto de salida para interactuar con el Model Registry.
    Simula la carga de modelos y la ejecución de inferencia.
    """

    def __init__(self):
        # Simulamos un registro de modelos en memoria.
        self._models = {
            "model1": Model(
                id="model1",
                name="ResNet50",
                description="Modelo ResNet50 entrenado para detectar defectos."
            ),
            "model2": Model(
                id="model2",
                name="VGG16",
                description="Modelo VGG16 para clasificación de imágenes en inspección."
            )
        }
        # Diccionario para almacenar modelos "cargados"
        self._loaded_models = {}

    def get_models(self) -> List[Model]:
        """
        Retorna la lista de todos los modelos disponibles.
        """
        return list(self._models.values())

    def load_model(self, model_id: str) -> Model:
        """
        Carga el modelo indicado por su ID.
        Si el modelo existe, lo marca como cargado y lo retorna.
        """
        if model_id in self._models:
            model = self._models[model_id]
            # Simulación de "carga" del modelo (e.g., cargar pesos en memoria)
            self._loaded_models[model_id] = model
            return model
        else:
            raise ValueError(f"Model with id '{model_id}' not found.")

    def run_inference(self, model: Model, frame: Any) -> DiagnosisResult:
        """
        Ejecuta la inferencia utilizando el modelo especificado sobre el frame recibido.
        Esta implementación simula la inferencia seleccionando aleatoriamente una etiqueta.
        """
        # Simulación de inferencia: seleccionar una etiqueta al azar
        possible_labels = ["ok", "defect", "anomaly"]
        selected_label = random.choice(possible_labels)
        
        # Crear y retornar el resultado de diagnóstico
        result = DiagnosisResult(
            label=selected_label,
            frame=frame,  # Se podría procesar el frame si fuera necesario
            timestamp=datetime.datetime.now()
        )
        return result

# Ejemplo de uso (para pruebas)
if __name__ == "__main__":
    adapter = ModelRepositoryAdapter()
    
    # Obtener lista de modelos
    models = adapter.get_models()
    print("Available Models:")
    for m in models:
        print(m)
    
    # Cargar un modelo
    try:
        model = adapter.load_model("model1")
        print(f"\nLoaded Model: {model}")
    except ValueError as e:
        print(e)
    
    # Ejecutar inferencia (simulación) sobre un frame (por ejemplo, una cadena que representa la imagen)
    dummy_frame = "frame_001.jpg"
    diagnosis_result = adapter.run_inference(model, dummy_frame)
    print("\nDiagnosis Result:")
    print(diagnosis_result)
