# src/Report/adapters/inbound/fastapi_report_services_adapter.py

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel

from Report.ports.inbound import ReportServicesPort
from Report.domain import ReportEntry, SessionSummary
from Report.adapters.inbound.ws_pool import ws_pool

router = APIRouter(prefix="/report", tags=["report"])


# ----------------------------
# Endpoints HTTP (existentes)
# ----------------------------

@router.get("/sessions", response_model=List[UUID])
@inject
async def list_sessions(
    svc: ReportServicesPort = Depends(Provide["report.report_services"]),
):
    try:
        return svc.list_sessions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entries/{session_id}", response_model=List[ReportEntry])
@inject
async def get_entries(
    session_id: UUID,
    svc: ReportServicesPort = Depends(Provide["report.report_services"]),
):
    try:
        return svc.get_entries(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/{session_id}", response_model=SessionSummary)
@inject
async def get_summary(
    session_id: UUID,
    operator: str,
    location: str,
    job_order: Optional[str] = None,
    svc: ReportServicesPort = Depends(Provide["report.report_services"]),
):
    try:
        return svc.get_summary(session_id, operator, location, job_order)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------
# Registro opcional (WS por registration_id)
# -----------------------------------------

class TerminalRegisterReq(BaseModel):
    session_id: UUID
    terminal_id: Optional[str] = None
    server_host: Optional[str] = None
    server_port: Optional[int] = None


class TerminalRegisterResp(BaseModel):
    registration_id: UUID
    session_id: UUID
    ws_url: str


@router.post("/terminal/register", response_model=TerminalRegisterResp)
async def terminal_register(req: TerminalRegisterReq, request: Request):
    reg = await ws_pool.register(session_id=str(req.session_id), terminal_id=req.terminal_id)

    scheme = "wss" if request.url.scheme == "https" else "ws"
    host = req.server_host or (request.url.hostname or "127.0.0.1")
    port = req.server_port or request.url.port
    if port is None:
        port = 443 if scheme == "wss" else 80

    ws_url = f"{scheme}://{host}:{port}/report/terminal/ws/{reg.id}"
    return TerminalRegisterResp(registration_id=reg.id, session_id=req.session_id, ws_url=ws_url)


@router.get("/terminal/registrations")
async def terminal_registrations():
    regs = list(ws_pool.registrations.values())
    return [
        {
            "registration_id": str(r.id),
            "session_id": r.session_id,
            "terminal_id": r.terminal_id,
            "created_at": r.created_at.isoformat(),
        }
        for r in regs
    ]


@router.delete("/terminal/registrations/{registration_id}")
async def terminal_unregister(registration_id: UUID):
    ok = await ws_pool.unregister(registration_id)
    if not ok:
        raise HTTPException(status_code=404, detail="registration_id not found")
    return {"status": "ok"}


@router.get("/ws/stats")
async def ws_stats():
    return await ws_pool.stats()


# ----------------------------
# WebSockets
# ----------------------------

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WS principal:
    - /report/ws?session_id=<UUID>  -> filtra por sesión
    - /report/ws                   -> broadcast (debug)
    """
    await websocket.accept()

    session_id = websocket.query_params.get("session_id")
    if session_id:
        await ws_pool.connect_session(websocket, session_id=session_id)
    else:
        await ws_pool.connect_broadcast(websocket)

    try:
        while True:
            await websocket.receive_text()  # keepalive (cliente manda "ping")
    except WebSocketDisconnect:
        await ws_pool.disconnect(websocket)
    except Exception:
        await ws_pool.disconnect(websocket)


@router.websocket("/terminal/ws/{registration_id}")
async def terminal_ws(websocket: WebSocket, registration_id: UUID):
    """
    Aceptamos primero para evitar HTTP 403.
    Si registration_id no existe, cerramos con 1008.
    """
    await websocket.accept()

    reg = await ws_pool.connect_registration(websocket, registration_id=registration_id)
    if reg is None:
        await websocket.close(code=1008)
        return

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_pool.disconnect(websocket)
    except Exception:
        await ws_pool.disconnect(websocket)
