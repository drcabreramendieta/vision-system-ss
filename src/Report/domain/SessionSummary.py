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

    # Basado en cambios de estado
    total_frames: int              # número de transiciones + 1
    fps: float                     # total_frames / duration_seconds
    counts_by_label: Dict[str,int] # cuántas veces entra cada estado
    total_events: int              # total_frames - 1

    longest_normal_run_seconds: float
    first_anomaly_time: Optional[datetime]
    last_anomaly_time: Optional[datetime]
    first_occurrence_by_label: Dict[str,datetime]
    last_occurrence_by_label:  Dict[str,datetime]

    # Nuevas métricas temporales
    time_per_label: Dict[str,float]                  # segundos totales en cada estado
    pct_anomaly: float                               # % del tiempo en anomalía
    mean_interval_between_anomalies: float           # segundos promedio entre anomalías
    anomalies_per_minute: float                      # número de anomalías / minuto
