# ESTO HAY QUE CAMBIAR COMPLETAMENTE

import mlflow
import numpy as np
import datetime
from Diagnostic.adapters.outbound import MlflowModelRepositoryAdapter
from Diagnostic.domain.Model import Model
from Diagnostic.domain.DiagnosisResult import DiagnosisResult
from Diagnostic.domain.InferenceLabel import InferenceLabel

def main():
    # Configura el tracking URI para MLflow. Este valor varía según tu entorno.
    # Por ejemplo, si tienes MLflow corriendo localmente en el puerto 5000:
    tracking_uri = "http://127.0.0.1:5000"
    # O bien, para utilizar un backend local (por ejemplo, usando un directorio):
    # tracking_uri = "file:///home/tu_usuario/mlflow_tracking"

    # Configura MLflow para utilizar este tracking URI
    mlflow.set_tracking_uri(tracking_uri)
    
    # Instanciar el adaptador para el Model Registry usando MLflow.
    adapter = MlflowModelRepositoryAdapter(tracking_uri=tracking_uri)
    
    # Listar los modelos disponibles en el registro
    models = adapter.get_models()
    print("Modelos disponibles en el registro:")
    for model in models:
        print(f"- ID: {model.id}, Nombre: {model.name}, Descripción: {model.description}")

    # Supongamos que queremos cargar el primer modelo de la lista.
    if not models:
        print("No se encontraron modelos en el registro.")
        return

    model_id = models[0].id
    try:
        loaded_model = adapter.load_model(model_id)
        print("\nModelo cargado:")
        print(f"ID: {loaded_model.id}, Nombre: {loaded_model.name}, Descripción: {loaded_model.description}")
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        return

    # Simular la adquisición de un frame:
    # Creamos un dummy frame usando NumPy, por ejemplo, una imagen de 224x224 con 3 canales (RGB).
    dummy_frame_data = np.random.rand(224, 224, 3) * 255  # Valores entre 0 y 255
    dummy_frame_data = dummy_frame_data.astype(np.uint8)   # Convertir a enteros (formato común de imagen)
    
    # Ejecutar la inferencia usando el adaptador.
    try:
        diagnosis_result = adapter.run_inference(loaded_model, dummy_frame_data)
        print("\nResultado de la inferencia:")
        print(f"Etiqueta: {diagnosis_result.label}")
        print(f"Timestamp: {diagnosis_result.timestamp}")
        # Si deseas, podrías mostrar información adicional del DiagnosisResult.
    except Exception as e:
        print(f"Error durante la inferencia: {e}")

if __name__ == "__main__":
    main()
