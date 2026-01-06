
from dependency_injector import containers, providers
from Report.adapters.outbound import SqliteReportStorageAdapter
from Report.adapters.outbound import WebSocketNotificationAdapter
from Report.application import ReportServices

class ReportContainer(containers.DeclarativeContainer):
    """Contenedor de DI para módulo Report."""


    # Configuración de inyección de dependencias
    config = providers.Configuration(yaml_files=["config.yaml"])
    # storage
    storage = providers.Singleton(
        SqliteReportStorageAdapter,
        db_url = config.report.db_url
    )
    # notifier (WebSocket)
    notifier = providers.Singleton(WebSocketNotificationAdapter)

    # servicio de aplicación
    report_services = providers.Singleton(
        ReportServices,
        storage = storage,
        notifier = notifier,
        frames_dir = config.report.frames_dir
    )

