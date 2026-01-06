from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from Video.ports.inbound import VideoLifecyclePort

router = APIRouter(prefix="/video", tags=["video"])

@router.post("/start", response_model=UUID)
@inject
async def start_video_session(
    video_svc: Annotated[
        VideoLifecyclePort,
        Depends(Provide["video.video_lifecycle_services"]),
    ],
) -> UUID:
    """
    Inicia una nueva sesión de video y retorna su UUID.
    """
    try:
        return video_svc.start_video_session()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop/{session_id}", response_model=str)
@inject
async def stop_video_session(
    session_id: UUID,
    video_lifecycle_services: Annotated[VideoLifecyclePort, Depends(Provide["video.video_lifecycle_services"])]
) -> str:
    """
    Detiene la sesión de video especificada y retorna el estado final.
    """
    try:
        return video_lifecycle_services.stop_video_session(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{session_id}", response_model=str)
@inject
async def get_session_status(
    session_id: UUID,
    video_lifecycle_services: Annotated[VideoLifecyclePort, Depends(Provide["video.video_lifecycle_services"])]
) -> str:
    """
    Retorna el estado actual de la sesión de video.
    """
    try:
        return video_lifecycle_services.get_session_status(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
