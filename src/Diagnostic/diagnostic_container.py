# src/Diagnostic/diagnostic_container.py
from dependency_injector import containers, providers
from Diagnostic.application.config_services import ConfigServicesImpl
from Diagnostic.adapters.outbound.mlflow_model_repository_adapter import MlflowModelRepositoryAdapter
from Diagnostic.adapters.outbound.diagnosis_notification_controller_adapter import DiagnosisNotificationControllerAdapter
from Diagnostic.application.diagnosis_services import DiagnosisServicesImpl
from Report.ports.inbound.report_services_port import ReportServicesPort

class DiagnosticContainer(containers.DeclarativeContainer):
    """Contenedor de DI para módulo Diagnostic."""


#   0) Configuración de inyección de dependencias
    # Se especifica el módulo donde se encuentran los adaptadores FastAPI
    wiring_config = containers.WiringConfiguration(
        modules=[
            "Diagnostic.adapters.inbound.fastapi_diagnostic_services_adapter"
        ]
    )

#   1) Carga desde config.yml
    config = providers.Configuration(yaml_files=['config.yaml'])

#   2) Repositorio MLflow, recibe la URI y el nombre de modelo desde config
    model_repository = providers.Singleton(
        MlflowModelRepositoryAdapter,
        tracking_uri=config.Diagnostic.mlflowuri,
    )

    # 3) Servicio de configuración (puerto inbound), que delega en el repo
    config_services = providers.Singleton(
        ConfigServicesImpl,
        model_repository=model_repository,
    )

    # 4) Adaptador para enviar resultados al módulo Report
    report_services = providers.Dependency(instance_of=ReportServicesPort)

    notification_controller = providers.Singleton(
        DiagnosisNotificationControllerAdapter,
        report_services=report_services,
    )

    # 5) Servicio principal de diagnóstico
    diagnosis_services = providers.Singleton(
        DiagnosisServicesImpl,
        model_repository=model_repository,
        notification_controller=notification_controller,
        config_services=config_services,
    )
