from fastapi import APIRouter, HTTPException, Depends
from dependency_injector.wiring import inject, Provide
from Diagnostic.ports.inbound import ConfigServicesPort

router = APIRouter(prefix="/diagnosis", tags=["diagnosis-config"])


@router.get("/models")
@inject
def list_models(
    svc: ConfigServicesPort = Depends(Provide["diagnostic.config_services"]),
):
    return [{"id": m.id, "name": m.name, "description": m.description}
            for m in svc.get_models()]


@router.post("/models/{model_id}")
@inject
def select_model(
    model_id: str,
    svc: ConfigServicesPort = Depends(Provide["diagnostic.config_services"]),
):
    ok = svc.set_model(model_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Model not found or failed to load")
    return {"status": "model set", "model_id": model_id}


@router.get("/models/active")
@inject
def has_active_model(
    svc: ConfigServicesPort = Depends(Provide["diagnostic.config_services"]),
):
    return {"has_model": svc.has_model()}
