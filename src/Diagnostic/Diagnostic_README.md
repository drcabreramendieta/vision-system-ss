# Módulo de Diagnóstico (Vision System)

Este submódulo se encarga de:

1. Listar y seleccionar la versión de modelo de MLflow.  
2. Ejecutar inferencia sobre frames recibidos.  
3. Notificar resultados al Módulo de Reporte.

# Estructura Hexagonal

Diagnostic/
├─ adapters/
│  ├─ inbound/   ← FastAPI, CLI…
│  └─ outbound/  ← MLflow, Report…
├─ application/  ← Casos de uso (ConfigServices, DiagnosisServices)
├─ domain/       ← Model, InferenceLabel, DiagnosisResult
└─ ports/        ← Interfaces inbound/outbound


# Endpoints HTTP (FastAPI)
| Método       | Ruta              | Descripción                              |
|--------------|-------------------|------------------------------------------|
| GET  /models | Listado de modelos| Devuelve id, name, description           |
| POST /models/{id} | Selección modelo | Activa un modelo para inferencia       |
| POST /run    | Ejecutar inferencia| Recibe imagen y devuelve etiqueta/timestamp |

# Flujo de Datos

1. El Terminal solicita un diagnóstico a /diagnosis/run.
2. El FastAPI Adapter convierte la imagen en np.ndarray.
3. DiagnosisServicesImpl.run_inference() orquesta:
    3.1 ModelRepository.load_model() (previamente via /models/{id}).
    3.2 ModelRepository.run_inference(frame).
    3.3 NotificationController.notify_result().
4. Report Module persiste en la base de Diagnosis Registry y notifica al Terminal vía WebSocket/HTTP.