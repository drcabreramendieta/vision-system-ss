from datetime import datetime
from typing import List
from Report.domain.ReportEntry import ReportEntry


class Report:
    """
    Representa el reporte completo de una sesión específica.
    Contiene múltiples 'ReportEntry'.
    """

    def __init__(self, session_id):
        """
        :param session_id: Identificador de la sesión a la que pertenece este reporte.
        """
        self.session_id = session_id
        self.entries = List[ReportEntry]  # Lista de ReportEntry
        self.generated_time = datetime.now() 

    def add_entry(self, entry):
        """
        Agrega un ReportEntry al reporte.
        """
        self.entries.append(entry)

    def generate_summary(self):
        """
        Crea un resumen en formato string, por ejemplo, contando cuántos labels hay.
        """
        label_count = {}
        for entry in self.entries:
            label_count[entry.label] = label_count.get(entry.label, 0) + 1

        summary = [f"Resumen de la sesión {self.session_id}:"]
        for label, count in label_count.items():
            summary.append(f"  {label}: {count}")
        return "\n".join(summary)

    def __repr__(self):
        return (f"Report(session_id={self.session_id}, "
                f"entries={len(self.entries)})")
