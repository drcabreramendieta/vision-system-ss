from dependency_injector import containers, providers

from Report.adapters.outbound import SqliteReportStorageAdapter, WebSocketNotificationAdapter
from Report.adapters.ws_connection_manager import WsConnectionManager
from Report.application import ReportServices


class ReportContainer(containers.DeclarativeContainer):
    """Contenedor de DI para módulo Report."""

    config = providers.Configuration(yaml_files=["config.yaml"])

    # Infraestructura compartida (WebSockets)
    ws_manager = providers.Singleton(WsConnectionManager)

    # Persistencia
    storage = providers.Singleton(
        SqliteReportStorageAdapter,
        db_url=config.report.db_url,
    )

    # Notificador (outbound)
    notifier = providers.Singleton(
        WebSocketNotificationAdapter,
        ws_manager=ws_manager,
    )

    # Servicio de aplicación
    report_services = providers.Singleton(
        ReportServices,
        storage=storage,
        notifier=notifier,
        frames_dir=config.report.frames_dir,
    )
