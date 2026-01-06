# src/Diagnostic/adapters/inbound/fastapi_diagnostic_services_adapter.py
from fastapi import APIRouter, HTTPException, UploadFile, Depends, Query
from dependency_injector.wiring import inject, Provide
from Diagnostic.ports.inbound import DiagnosisServicesPort
from Diagnostic.domain import DiagnosisResult
import numpy as np
from PIL import Image

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])

@router.post("/run")
@inject
def run_diagnosis(
    file: UploadFile,
    session_id: str = Query(..., description="UUID de la sesión de vídeo"),
    svc: DiagnosisServicesPort = Depends(Provide["diagnostic.diagnosis_services"])
):
        
    """
    Recibe una imagen con el frame; devuelve el DiagnosisResult (que incluye el session_id).
    """
    # 1) Abrir y forzar RGB
    img = Image.open(file.file).convert("RGB")

    # 2) Redimensionar al tamaño que vio tu modelo (ancho, alto)
    #    (tu modelo se entrenó con H=352, W=288)
    img = img.resize((352,288), resample=Image.BILINEAR)

    # 3) Pasar a array NumPy y reordenar ejes a CxHxW
    arr = np.array(img)                   # shape (352, 288, 3)
    arr = arr.transpose(2, 1, 0)          # shape (3, 352, 288)
    arr = arr / 255.0
    # 4) Asegurar tipo float32 (firma de MLflow)
    arr = arr.astype(np.float32)

    # 5) Llamar al servicio
    result = svc.run_inference(arr, session_id)

    return {
        "session_id": result.session_id,
        "label": result.label.name,
        "timestamp": result.timestamp.isoformat()
    }
