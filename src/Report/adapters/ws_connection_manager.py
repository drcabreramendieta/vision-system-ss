# src/Report/adapters/ws_connection_manager.py
from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, DefaultDict, Dict, Set

from fastapi import WebSocket


class WsConnectionManager:
    """Gestiona conexiones WebSocket por *topic*.

    - Un *topic* es un string: aquí lo usaremos como `session_id`.
    - El endpoint WebSocket (adaptador de entrada) registra conexiones con `connect()`.
    - El adapter de notificación (outbound) emite eventos con `broadcast_json()`.

    Nota: esta clase es *infraestructura compartida*; no es dominio ni aplicación.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._topics: DefaultDict[str, Set[WebSocket]] = defaultdict(set)

    async def connect(self, ws: WebSocket, topic: str) -> None:
        """Acepta y registra un WebSocket en un topic."""
        await ws.accept()
        async with self._lock:
            self._topics[topic].add(ws)

    async def disconnect(self, ws: WebSocket, topic: str | None = None) -> None:
        """Elimina el WebSocket del topic indicado o de todos si topic=None."""
        async with self._lock:
            if topic is not None:
                if topic in self._topics:
                    self._topics[topic].discard(ws)
                    if not self._topics[topic]:
                        del self._topics[topic]
                return

            # remove from all topics
            empty = []
            for t, conns in self._topics.items():
                conns.discard(ws)
                if not conns:
                    empty.append(t)
            for t in empty:
                del self._topics[t]

    async def broadcast_json(self, topic: str, payload: Dict[str, Any]) -> None:
        """Envía un JSON a todos los WebSockets registrados en el topic."""
        async with self._lock:
            conns = list(self._topics.get(topic, set()))

        dead: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)

        # limpiar desconectados
        for ws in dead:
            await self.disconnect(ws)

    async def stats(self) -> Dict[str, Any]:
        async with self._lock:
            return {
                "topics": {t: len(s) for t, s in self._topics.items()},
                "total_clients": sum(len(s) for s in self._topics.values()),
            }
