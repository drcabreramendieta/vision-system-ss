# src/Report/domain/SessionSummary.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

@dataclass
class SessionSummary:
    session_id: UUID
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    total_frames: int
    fps: float
    counts_by_label: Dict[str, int]
    total_events: int
    longest_normal_run: int
    first_anomaly_time: Optional[datetime]
    last_anomaly_time: Optional[datetime]
