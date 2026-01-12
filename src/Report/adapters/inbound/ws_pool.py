# src/Report/adapters/inbound/ws_pool.py
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Set
from uuid import UUID, uuid4

from fastapi import WebSocket


@dataclass(frozen=True)
class TerminalRegistration:
    id: UUID
    session_id: str
    terminal_id: Optional[str]
    created_at: datetime


class WsPool:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()

        # Compatibilidad: el viejo "connected" (broadcast de todo)
        self.broadcast: Set[WebSocket] = set()

        # Nuevos: conexiones filtradas por sesión
        self.by_session: Dict[str, Set[WebSocket]] = {}

        # Registro Terminal: registration_id -> info
        self.registrations: Dict[UUID, TerminalRegistration] = {}

        # Para saber qué sockets pertenecen a un registration_id (poder limpiar)
        self.by_registration: Dict[UUID, Set[WebSocket]] = {}

        # Índice incremental por sesión (para UI)
        self.event_index_by_session: Dict[str, int] = {}

    async def register(self, session_id: str, terminal_id: Optional[str]) -> TerminalRegistration:
        reg = TerminalRegistration(id=uuid4(), session_id=session_id, terminal_id=terminal_id, created_at=datetime.utcnow())
        async with self._lock:
            self.registrations[reg.id] = reg
            self.by_registration[reg.id] = set()
            self.by_session.setdefault(session_id, set())
            self.event_index_by_session.setdefault(session_id, 0)
        return reg

    async def unregister(self, registration_id: UUID) -> bool:
        async with self._lock:
            reg = self.registrations.pop(registration_id, None)
            socks = self.by_registration.pop(registration_id, set())
        # cerrar sockets fuera del lock
        for ws in list(socks):
            try:
                await ws.close(code=1000)
            except Exception:
                pass
        return reg is not None

    async def connect_broadcast(self, ws: WebSocket) -> None:
        async with self._lock:
            self.broadcast.add(ws)

    async def connect_session(self, ws: WebSocket, session_id: str) -> None:
        async with self._lock:
            self.by_session.setdefault(session_id, set()).add(ws)

    async def connect_registration(self, ws: WebSocket, registration_id: UUID) -> Optional[TerminalRegistration]:
        async with self._lock:
            reg = self.registrations.get(registration_id)
            if not reg:
                return None
            self.by_registration.setdefault(registration_id, set()).add(ws)
            self.by_session.setdefault(reg.session_id, set()).add(ws)
            self.event_index_by_session.setdefault(reg.session_id, 0)
            return reg

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self.broadcast.discard(ws)
            for sset in self.by_session.values():
                sset.discard(ws)
            for rset in self.by_registration.values():
                rset.discard(ws)

    async def next_event_index(self, session_id: str) -> int:
        async with self._lock:
            self.event_index_by_session[session_id] = self.event_index_by_session.get(session_id, 0) + 1
            return self.event_index_by_session[session_id]

    async def send_json(self, session_id: str, payload: str) -> None:
        # Envía a:
        # - broadcast
        # - suscritos por session_id
        async with self._lock:
            targets = list(self.broadcast) + list(self.by_session.get(session_id, set()))
        for ws in targets:
            try:
                await ws.send_text(payload)
            except Exception:
                await self.disconnect(ws)

    async def stats(self) -> dict:
        async with self._lock:
            return {
                "broadcast_clients": len(self.broadcast),
                "sessions_with_clients": {sid: len(wss) for sid, wss in self.by_session.items() if wss},
                "registrations": len(self.registrations),
            }


ws_pool = WsPool()

# Compatibilidad si algún archivo importaba "connected"
connected = ws_pool.broadcast
