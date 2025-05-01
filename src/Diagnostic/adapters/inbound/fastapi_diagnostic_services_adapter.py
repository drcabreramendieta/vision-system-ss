# src/Diagnostic/adapters/inbound/fastapi_diagnostic_services_adapter.py
from fastapi import APIRouter, HTTPException, UploadFile
from dependency_injector.wiring import inject, Provide
from Diagnostic.ports.inbound.diagnosis_services_port import DiagnosisServicesPort
from Diagnostic import DiagnosticContainer
import numpy as np
from PIL import Image

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])

@router.get("/models")
@inject
def list_models(
    svc: DiagnosisServicesPort = Provide[DiagnosticContainer.diagnosis_services]
):
    return [{"id": m.id, "name": m.name, "description": m.description}
            for m in svc.get_models()]

@router.post("/models/{model_id}")
@inject
def select_model(
    model_id: str,
    svc: DiagnosisServicesPort = Provide[DiagnosticContainer.diagnosis_services]
):
    ok = svc.set_model(model_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Model not found or failed to load")
    return {"status": "model set", "model_id": model_id}

@router.post("/run")
@inject
def run_diagnosis(
    file: UploadFile,
    svc: DiagnosisServicesPort = Provide[DiagnosticContainer.diagnosis_services]
):
    """
    Recibe una imagen con el frame; devuelve el DiagnosisResult.
    """
    img = Image.open(file.file).convert("RGB")
    arr = np.array(img)
    result = svc.run_inference(arr)
    return {
        "label": result.label.name,
        "timestamp": result.timestamp.isoformat()
    }
