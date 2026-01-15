# src/Report/adapters/inbound/fastapi_report_services_adapter.py

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict

from Report.adapters.ws_connection_manager import WsConnectionManager
from Report.domain import ReportEntry, SessionSummary
from Report.ports.inbound import ReportServicesPort

router = APIRouter(prefix="/report", tags=["report"])


# =========================
# DTOs (Pydantic) - Inbound/Outbound API
# =========================

class ReportEntryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: UUID
    frame_path: str
    label: str
    timestamp: datetime


class SessionSummaryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: UUID
    start_time: datetime
    end_time: datetime
    duration_seconds: float

    total_frames: int
    fps: float
    counts_by_label: Dict[str, int]
    total_events: int

    longest_normal_run_seconds: float
    first_anomaly_time: Optional[datetime]
    last_anomaly_time: Optional[datetime]
    first_occurrence_by_label: Dict[str, datetime]
    last_occurrence_by_label: Dict[str, datetime]

    time_per_label: Dict[str, float]
    pct_anomaly: float
    mean_interval_between_anomalies: float
    anomalies_per_minute: float


# =========================
# REST endpoints
# =========================

@router.post("/entry")
@inject
async def add_entry(
    payload: ReportEntryDTO,
    svc: ReportServicesPort = Depends(Provide["report.report_services"]),
):
    # DTO -> Dominio
    entry = ReportEntry(**payload.model_dump())
    svc.add_result(entry)
    return {"status": "ok"}


@router.get("/sessions", response_model=List[UUID])
@inject
async def list_sessions(
    svc: ReportServicesPort = Depends(Provide["report.report_services"]),
):
    return svc.list_sessions()


@router.get("/entries/{session_id}", response_model=List[ReportEntryDTO])
@inject
async def get_entries(
    session_id: UUID,
    svc: ReportServicesPort = Depends(Provide["report.report_services"]),
):
    entries = svc.get_entries(session_id)
    return [ReportEntryDTO.model_validate(e) for e in entries]


@router.get("/summary/{session_id}", response_model=SessionSummaryDTO)
@inject
async def get_summary(
    session_id: UUID,
    operator: str,
    location: str,
    job_order: str | None = None,
    svc: ReportServicesPort = Depends(Provide["report.report_services"]),
):
    try:
        summary = svc.get_summary(session_id, operator, location, job_order)
        return SessionSummaryDTO.model_validate(summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ws/stats")
@inject
async def ws_stats(
    ws_manager: WsConnectionManager = Depends(Provide["report.ws_manager"]),
):
    return await ws_manager.stats()


# =========================
# WebSocket endpoint (directo por session_id)
# =========================

@router.websocket("/ws/{session_id}")
@inject
async def websocket_session_endpoint(
    websocket: WebSocket,
    session_id: str,
    ws_manager: WsConnectionManager = Depends(Provide["report.ws_manager"]),
):
    # Validación: session_id debe ser UUID
    try:
        UUID(session_id)
    except Exception:
        await websocket.close(code=1008)
        return

    await ws_manager.connect(websocket, topic=session_id)

    try:
        # Mantener viva la conexión (no necesitamos mensajes entrantes)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.disconnect(websocket, topic=session_id)
