# src/Report/adapters/outbound/websocket_notification_adapter.py
import json
from Report.domain import ReportEntry, SessionSummary
from Report.ports.outbound import ReportNotificationPort
from Report.adapters.inbound.ws_pool import ws_pool


class WebSocketNotificationAdapter(ReportNotificationPort):
    """
    Envía eventos por WS.
    - broadcast: todos (compatibilidad)
    - session subscribers: solo los que están suscritos a esa session_id
    """

    async def notify_entry(self, entry: ReportEntry) -> None:
        sid = str(entry.session_id)
        event_index = await ws_pool.next_event_index(sid)

        payload = {
            "type": "state_change",
            "session_id": sid,
            "event_index": event_index,   # índice de cambios (útil para UI)
            "timestamp": entry.timestamp.isoformat(),
            "label": entry.label,
            # opcional: por si el Terminal quiere mostrar miniatura o debug
            "frame_path": entry.frame_path,
        }
        await ws_pool.send_json(session_id=sid, payload=json.dumps(payload))

    async def notify_summary(self, summary: SessionSummary, metadata: dict) -> None:
        sid = str(summary.session_id)
        payload = {
            "type": "summary",
            "session_id": sid,
            "start_time": summary.start_time.isoformat(),
            "end_time": summary.end_time.isoformat(),
            "duration_seconds": summary.duration_seconds,
            "total_frames": summary.total_frames,
            "fps": summary.fps,
            "counts_by_label": summary.counts_by_label,
            "total_events": summary.total_events,
            # FIX: nombre correcto
            "longest_normal_run_seconds": summary.longest_normal_run_seconds,
            # compat por si algún cliente viejo esperaba "longest_normal_run"
            "longest_normal_run": summary.longest_normal_run_seconds,
            "first_anomaly_time": summary.first_anomaly_time.isoformat() if summary.first_anomaly_time else None,
            "last_anomaly_time": summary.last_anomaly_time.isoformat() if summary.last_anomaly_time else None,
            "metadata": metadata,
        }
        await ws_pool.send_json(session_id=sid, payload=json.dumps(payload))
