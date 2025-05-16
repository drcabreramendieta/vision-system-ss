# src/Report/adapters/outbound/sqlite_report_storage_adapter.py
import sqlite3
from uuid import UUID
import os
from datetime import datetime
from typing import List
from Report.domain.ReportEntry import ReportEntry
from Report.ports.outbound.report_storage_port import ReportStoragePort

class SqliteReportStorageAdapter(ReportStoragePort):
    def __init__(self, db_url: str):
        """
        db_url puede ser:
          - "sqlite:///./report.db"   (relativo)
          - "sqlite:////home/user/report.db"  (absoluto)
          - "./report.db"  (directo path)
        """
        # 1) Extraer ruta de fichero de la URI
        if db_url.startswith("sqlite:///"):
            path = db_url[len("sqlite:///"):]
        else:
            path = db_url

        # 2) Asegurar carpeta padre existe
        db_dir = os.path.dirname(path) or "."
        os.makedirs(db_dir, exist_ok=True)

        # 3) Conectarse al fichero SQLite
        #self.conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)

        # Abrimos con check_same_thread=False para poder usar en varios hilos
        self.conn = sqlite3.connect(
            path,
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False
        )
        # Lock para serializar commits y evitar condiciones de carrera
        import threading
        self._lock = threading.Lock()

        # 4) Crear esquemas si no existen
        self._migrate()

    def _migrate(self):
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS sessions (
                       session_id TEXT PRIMARY KEY,
                       start_time TIMESTAMP,
                       end_time TIMESTAMP
                     )""")
        c.execute("""CREATE TABLE IF NOT EXISTS report_entries (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       session_id TEXT,
                       frame_path TEXT,
                       label TEXT,
                       timestamp TIMESTAMP
                     )""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_entries_session ON report_entries(session_id)")
        self.conn.commit()

    def save_entry(self, entry: ReportEntry) -> None:
        with self._lock:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT OR IGNORE INTO sessions(session_id, start_time) VALUES(?,?)",
                (str(entry.session_id), entry.timestamp)
            )
            cur.execute(
                "INSERT INTO report_entries(session_id, frame_path, label, timestamp) VALUES(?,?,?,?)",
                (str(entry.session_id), entry.frame_path, entry.label, entry.timestamp)
            )
            self.conn.commit()





    def fetch_entries(self, session_id: UUID) -> List[ReportEntry]:
        cur = self.conn.cursor()
        cur.execute("""SELECT frame_path,label,timestamp
                       FROM report_entries
                       WHERE session_id=?
                       ORDER BY timestamp""",
                    (str(session_id),))
        rows = cur.fetchall()
        return [
            ReportEntry(session_id, fp, lab, ts)
            for fp, lab, ts in rows
        ]

    def list_sessions(self) -> List[UUID]:
        cur = self.conn.cursor()
        cur.execute("SELECT session_id FROM sessions")
        return [UUID(sid) for (sid,) in cur.fetchall()]
