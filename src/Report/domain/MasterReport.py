
class MasterReport:
    """
    Contiene los reportes de todas las sesiones, sirviendo como
    plantilla para la persistencia en la base de datos (Report Storage o Diagnosis Registry?).
    """

    def __init__(self):
        # Diccionario: {session_id: Report}
        self.reports = {}

    def add_report(self, report):
        """
        Agrega o reemplaza un reporte completo para una sesión.
        """
        self.reports[report.session_id] = report

    def get_report(self, session_id):
        """
        Retorna el Report asociado a la sesión.
        """
        return self.reports.get(session_id)

    def list_reports(self):
        """
        Retorna una lista de todos los Report almacenados.
        """
        return list(self.reports.values())
