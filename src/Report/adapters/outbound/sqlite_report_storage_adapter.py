# src/Report/adapters/outbound/sqlite_report_storage_adapter.py

import sqlite3
from uuid import UUID
import os
import threading
from datetime import datetime
from typing import List, Union

from Report.domain import ReportEntry
from Report.ports.outbound import ReportStoragePort

class SqliteReportStorageAdapter(ReportStoragePort):
    def __init__(self, db_url: str):
        """
        db_url puede ser:
          - "sqlite:///./report.db"   (relativo)
          - "sqlite:////home/user/report.db"  (absoluto)
          - "./report.db"  (directo path)
        """
        # --- Extraer ruta de fichero
        if db_url.startswith("sqlite:///"):
            path = db_url[len("sqlite:///"):]
        else:
            path = db_url

        # --- Asegurar carpeta existe
        db_dir = os.path.dirname(path) or "."
        os.makedirs(db_dir, exist_ok=True)

        # --- Conectar
        self.conn = sqlite3.connect(
            path,
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False
        )
        self._lock = threading.Lock()
        self._migrate()

    def _migrate(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
              session_id TEXT PRIMARY KEY,
              start_time TIMESTAMP,
              end_time   TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS report_entries (
              id          INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id  TEXT,
              frame_path  TEXT,
              label       TEXT,
              timestamp   TIMESTAMP
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_entries_session ON report_entries(session_id)")
        self.conn.commit()

    def save_entry(self, entry: ReportEntry) -> None:
        """
        Inserta:
          - En 'sessions' solo la primera vez (INSERT OR IGNORE)
          - En 'report_entries' cada cambio de estado
        """
        # Aseguramos un único formateo string del UUID
        session_id_str = str(entry.session_id)

        with self._lock:
            cur = self.conn.cursor()
            # Si no existe la sesión, la creamos con start_time
            cur.execute(
                "INSERT OR IGNORE INTO sessions(session_id, start_time) VALUES(?,?)",
                (session_id_str, entry.timestamp)
            )
            # Luego insertamos la entrada de reporte
            cur.execute(
                "INSERT INTO report_entries(session_id, frame_path, label, timestamp) VALUES(?,?,?,?)",
                (session_id_str, entry.frame_path, entry.label, entry.timestamp)
            )
            self.conn.commit()

    def fetch_entries(self, session_id: UUID) -> List[ReportEntry]:
        """
        Recupera todas las entradas para una sesión, ordenadas por timestamp.
        """
        session_id_str = str(session_id)
        cur = self.conn.cursor()
        cur.execute("""
            SELECT frame_path, label, timestamp
              FROM report_entries
             WHERE session_id=?
             ORDER BY timestamp
        """, (session_id_str,))
        rows = cur.fetchall()
        return [
            ReportEntry(session_id, fp, lab, ts)
            for fp, lab, ts in rows
        ]

    def list_sessions(self) -> List[UUID]:
        """
        Devuelve solo los session_id que puedan parsearse a UUID válidos.
        Omite silenciosamente cualquier otro valor.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT session_id FROM sessions")
        sessions: List[UUID] = []

        for (raw_sid,) in cur.fetchall():
            # Puede venir como bytes o str
            sid = raw_sid.decode('utf-8') if isinstance(raw_sid, (bytes, bytearray)) else raw_sid
            try:
                sessions.append(UUID(sid))
            except (ValueError, TypeError):
                # Omitimos entradas mal formadas
                continue

        return sessions
