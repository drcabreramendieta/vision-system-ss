# src/Report/adapters/inbound/fastapi_report_services_adapter.py
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Set
from uuid import UUID
from dependency_injector.wiring import inject, Provide
from Report.ports.inbound import ReportServicesPort
#from Report import ReportContainer
from Report.domain import ReportEntry
from Report.domain import SessionSummary
from Report.adapters.inbound import connected

router = APIRouter(prefix="/report", tags=["report"])

@router.post("/entry")
@inject
async def add_entry(
    entry: ReportEntry,
    svc: ReportServicesPort = Depends(Provide["report.report_services"])
):
    svc.add_result(entry)
    return {"status":"ok"}

@router.get("/sessions", response_model=List[UUID])
@inject
async def list_sessions(
    svc: ReportServicesPort = Depends(Provide["report.report_services"])
):
    return svc.list_sessions()

@router.get("/entries/{session_id}", response_model=List[ReportEntry])
@inject
async def get_entries(
    session_id: UUID,
    svc: ReportServicesPort = Depends(Provide["report.report_services"])
):
    return svc.get_entries(session_id)

@router.get("/summary/{session_id}", response_model=SessionSummary)
@inject
async def get_summary(
    session_id: UUID,
    operator: str,
    location: str,
    job_order: str = None,
    svc: ReportServicesPort = Depends(Provide["report.report_services"])
):
    return svc.get_summary(session_id, operator, location, job_order)

#@router.websocket("/ws/{session_id}")
#@inject
#async def websocket_endpoint(
#    websocket: WebSocket,
#    session_id: str,
#    notifier: WebSocketNotificationAdapter = Depends(Provide[ApplicationContainer.report.notifier])
#):
#    await notifier.connect(session_id, websocket)
#    try:
#        while True:
#            await websocket.receive_text()  # Mantiene vivo el socket
#    except WebSocketDisconnect:
#        notifier.disconnect(session_id, websocket)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Socket para streaming en vivo de ReportEntry.
    Cualquiera se conecta aquí y recibe todos los eventos en tiempo real.
    """
    await websocket.accept()
    connected.add(websocket)
    try:
        # Nos quedamos a la escucha (no necesitamos recibir nada)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected.remove(websocket)
