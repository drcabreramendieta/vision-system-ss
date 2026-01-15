# src/Report/adapters/outbound/websocket_notification_adapter.py

from __future__ import annotations

import asyncio
from typing import Dict, Any

from Report.adapters.ws_connection_manager import WsConnectionManager
from Report.domain import ReportEntry
from Report.ports.outbound import ReportNotificationPort


class WebSocketNotificationAdapter(ReportNotificationPort):
    """Adapter outbound: emite notificaciones vía WebSocket.

    - Envía SOLO a clientes suscritos al `session_id` correspondiente.
    - El filtrado de "solo cambios de estado" se hace en la capa de aplicación
      (ReportServices), por eso aquí simplemente emitimos cada entry que llega.
    """

    def __init__(self, ws_manager: WsConnectionManager) -> None:
        self._ws = ws_manager
        self._lock = asyncio.Lock()
        self._event_index: Dict[str, int] = {}

    async def _next_event_index(self, session_id: str) -> int:
        async with self._lock:
            self._event_index[session_id] = self._event_index.get(session_id, 0) + 1
            return self._event_index[session_id]

    async def notify_entry(self, entry: ReportEntry) -> None:
        sid = str(entry.session_id)
        payload: Dict[str, Any] = {
            "type": "state_change",
            "session_id": sid,
            "event_index": await self._next_event_index(sid),
            "frame_path": entry.frame_path,
            "label": entry.label,
            "timestamp": entry.timestamp.isoformat(),
        }
        await self._ws.broadcast_json(topic=sid, payload=payload)

    async def notify_summary(self, summary, metadata) -> None:
        sid = str(summary.session_id)
        payload: Dict[str, Any] = {
            "type": "summary",
            "session_id": sid,
            "start_time": summary.start_time.isoformat(),
            "end_time": summary.end_time.isoformat(),
            "duration_seconds": summary.duration_seconds,
            "total_frames": summary.total_frames,
            "fps": summary.fps,
            "counts_by_label": summary.counts_by_label,
            "total_events": summary.total_events,
            "longest_normal_run": getattr(summary, "longest_normal_run", None)
            or getattr(summary, "longest_normal_run_seconds", None),
            "first_anomaly_time": summary.first_anomaly_time.isoformat() if summary.first_anomaly_time else None,
            "last_anomaly_time": summary.last_anomaly_time.isoformat() if summary.last_anomaly_time else None,
            "metadata": metadata,
        }
        await self._ws.broadcast_json(topic=sid, payload=payload)
