"""
TODO: Armar un contenedor siguiendo los lineamientos del de video
"""

from dependency_injector import containers, providers
from Report.adapters.outbound.diagnosis_registry_adapter import DiagnosisRegistryAdapter
from Report.adapters.outbound.notification_controller_adapter import NotificationControllerAdapter
from Report.application.report_services import ReportServices

class ReportContainer(containers.DeclarativeContainer):
    """
    Contenedor para el módulo Report:
      - Carga configuración de base de datos
      - Define adaptadores outbound para almacenamiento y notificaciones
      - Expone un singleton de ReportServices
    """
    wiring_config = containers.WiringConfiguration(
        modules=[
            "Report.adapters.inbound.fastapi_report_services_adapter", # Preguntar a Diego si sería algo así
        ]
    )

    # Sección de configuración (config.yaml)
    config = providers.Configuration() #También tiene que cargar algún archivo de configuración .yaml? Con la uri del servidor de la base de datos POR EJEMPLO?

    # Adaptador para persistir ReportEntry en Diagnosis Registry
    diagnosis_registry = providers.Factory(
        DiagnosisRegistryAdapter,
        db_url=config.db.url,
    )

    # Adaptador para notificaciones (e.g., webhook, email)
    notification_controller = providers.Factory(
        NotificationControllerAdapter,
    )

    # Servicio de aplicación que gestiona la creación de reportes
    report_services = providers.Singleton(
        ReportServices,
        storage_port=diagnosis_registry,
        notification_port=notification_controller,
    )

