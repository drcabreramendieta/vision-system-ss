from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from Video import VideoContainer
from Video.ports.inbound import VideoLifecyclePort

router = APIRouter(prefix="/video", tags=["video"])

@router.post("/start", response_model=UUID)
@inject
async def start_diagnostic(
    video_lifecycle_services: Annotated[VideoLifecyclePort, Depends(Provide[VideoContainer.video_lifecycle_services])]
) -> UUID:
    """
    Inicia una nueva sesión de diagnóstico de video y retorna su UUID.
    """
    try:
        
        return video_lifecycle_services.start_diagnostic()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop/{session_id}", response_model=str)
@inject
async def stop_diagnostic(
    session_id: UUID,
    video_lifecycle_services: Annotated[VideoLifecyclePort, Depends(Provide[VideoContainer.video_lifecycle_services])]
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
    video_lifecycle_services: Annotated[VideoLifecyclePort, Depends(Provide[VideoContainer.video_lifecycle_services])]
) -> str:
    """
    Retorna el estado actual de la sesión de diagnóstico.
    """
    try:
        return video_lifecycle_services.get_session_status(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

