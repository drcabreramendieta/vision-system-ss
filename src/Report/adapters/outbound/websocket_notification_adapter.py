# src/Report/adapters/outbound/websocket_notification_adapter.py
import asyncio
from fastapi import WebSocket
from collections import defaultdict
from Report.domain import ReportEntry
from Report.domain import SessionSummary
from Report.ports.outbound import ReportNotificationPort
from Report.adapters.inbound import connected
import json

class WebSocketNotificationAdapter(ReportNotificationPort):
    """
    Adapter que hace broadcast de cada ReportEntry a todos los sockets conectados.
    """

    async def notify_entry(self, entry: ReportEntry) -> None:
        payload = {
            "session_id": str(entry.session_id),
            "frame_path": entry.frame_path,
            "label": entry.label,
            "timestamp": entry.timestamp.isoformat()
        }
        msg = json.dumps(payload)
        # enviar a todos los sockets vigentes
        for ws in list(connected):
            try:
                await ws.send_text(msg)
            except Exception:
                # si se cayó uno, lo quitamos
                connected.remove(ws)

    async def notify_summary(self, summary, metadata) -> None: 
    #  Emite un mensaje de tipo "summary" cuando se invoque
        payload = {
            "type": "summary",
            "session_id": str(summary.session_id),
            "start_time": summary.start_time.isoformat(),
            "end_time": summary.end_time.isoformat(),
            "duration_seconds": summary.duration_seconds,
            "total_frames": summary.total_frames,
            "fps": summary.fps,
            "counts_by_label": summary.counts_by_label,
            "total_events": summary.total_events,
            "longest_normal_run": summary.longest_normal_run,
            "first_anomaly_time": summary.first_anomaly_time.isoformat() if summary.first_anomaly_time else None,
            "last_anomaly_time": summary.last_anomaly_time.isoformat() if summary.last_anomaly_time else None,
            "metadata": metadata
        }
        msg = json.dumps(payload)
        for ws in list(connected):
            try:
                await ws.send_text(msg)
            except Exception:
                connected.remove(ws)
