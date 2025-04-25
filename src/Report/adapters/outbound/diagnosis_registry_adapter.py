# Adaptador de ejemplo para persistir Report, ReportEntry y Event en SQLite
# Aún hay que definir el esquema de la base de datos y las tablas
# Creado para propositos de prueba y demostración

import sqlite3
from Report.ports.outbound.diagnosis_registry_port import DiagnosisRegistryPort
from Report.domain.Report import Report
from Report.domain.ReportEntry import ReportEntry
from Report.domain.Event import Event

class DiagnosisRegistryAdapter(DiagnosisRegistryPort):
    """
    Adapter que persiste Report, ReportEntry y Event en SQLite.
    """
    def __init__(self, db_url: str):
        # db_url: ruta al archivo SQLite, ex: 'reports.db'
        self.db_url = db_url
        self.conn = sqlite3.connect(self.db_url, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                session_id TEXT PRIMARY KEY,
                created_at TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS report_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                frame_id TEXT,
                label TEXT,
                timestamp TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                type TEXT,
                timestamp TEXT
            )
        ''')
        self.conn.commit()

    def save_report(self, report: Report) -> None:
        c = self.conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO reports(session_id, created_at) VALUES (?, ?)",
            (report.session_id, report.created_at.isoformat())
        )
        self.conn.commit()

    def save_report_entry(self, entry: ReportEntry) -> None:
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO report_entries(session_id, frame_id, label, timestamp) VALUES (?, ?, ?, ?)",
            (entry.session_id, entry.frame.frame_id, entry.frame.label, entry.timestamp.isoformat())
        )
        self.conn.commit()

    def save_event(self, event: Event) -> None:
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO events(session_id, type, timestamp) VALUES (?, ?, ?)",
            (event.session_id, event.type, event.timestamp.isoformat())
        )
        self.conn.commit()

    def get_report(self, session_id: str) -> Report:
        c = self.conn.cursor()
        c.execute("SELECT created_at FROM reports WHERE session_id = ?", (session_id,))
        row = c.fetchone()
        if not row:
            return None
        report = Report(session_id=session_id, created_at=row[0])
        # Cargar entries
        c.execute(
            "SELECT frame_id, label, timestamp FROM report_entries WHERE session_id = ? ORDER BY id",
            (session_id,)
        )
        for frame_id, label, ts in c.fetchall():
            report.add_entry(ReportEntry(session_id=session_id, frame_id=frame_id, label=label, timestamp=ts))
        # Cargar events
        c.execute(
            "SELECT type, timestamp FROM events WHERE session_id = ? ORDER BY id",
            (session_id,)
        )
        for type_, ts in c.fetchall():
            report.add_event(Event(session_id=session_id, type=type_, timestamp=ts))
        return report
