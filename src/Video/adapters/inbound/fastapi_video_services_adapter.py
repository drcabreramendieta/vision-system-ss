from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from Video import VideoContainer 
from Video.ports.inbound import VideoLifecyclePort
#Inyectamos estos dos para proteger de errores si se intenta iniciar un diagnóstico sin haber configurado el modelo
from Diagnostic.ports.inbound.diagnosis_services_port import DiagnosisServicesPort
#from Diagnostic.diagnostic_container import DiagnosticContainer
#from Video.video_container import VideoContainer
from application_container import ApplicationContainer

router = APIRouter(prefix="/video", tags=["video"])

@router.post("/start", response_model=UUID)
@inject
async def start_diagnostic(
        video_svc: Annotated[
        VideoLifecyclePort,
        Depends(Provide[ApplicationContainer.video.video_lifecycle_services]), # Antes estaba así: Depends(Provide[VideoContainer.video_lifecycle_services])
        ],
        diag_svc: Annotated[
        DiagnosisServicesPort,
        Depends(Provide[ApplicationContainer.diagnostic.diagnosis_services]), # Antes estaba así: Depends(Provide[DiagnosticContainer.diagnosis_services])
        ],
) -> UUID:
    """
    Inicia una nueva sesión de diagnóstico de video y retorna su UUID.
    """
    print(">> inyectado cls:", type(diag_svc), diag_svc)

    if not diag_svc.has_model():
        raise HTTPException(
            status_code=400,
            detail="No hay modelo cargado. Selecciona primero uno con POST /diagnosis/models/{model_id}"
        )
    try:
        print("🔵 Arrancando vídeo con instancia:", id(diag_svc), "has_model():", diag_svc.has_model())
        return video_svc.start_diagnostic()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop/{session_id}", response_model=str)
@inject
async def stop_diagnostic(
    session_id: UUID,
    video_lifecycle_services: Annotated[VideoLifecyclePort, Depends(Provide[ApplicationContainer.video.video_lifecycle_services])]
) -> str:
    """
    Detiene la sesión de diagnóstico especificada y retorna un mensaje de confirmación.
    """
    try:
        return video_lifecycle_services.stop_diagnostic(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{session_id}", response_model=str)
@inject
async def get_session_status(
    session_id: UUID,
    video_lifecycle_services: Annotated[VideoLifecyclePort, Depends(Provide[ApplicationContainer.video.video_lifecycle_services])]
) -> str:
    """
    Retorna el estado actual de la sesión de diagnóstico.
    """
    try:
        return video_lifecycle_services.get_session_status(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

