# src/Diagnostic/diagnostic_container.py
from dependency_injector import containers, providers
from Diagnostic.application.config_services import ConfigServicesImpl
from Diagnostic.adapters.outbound.mlflow_model_repository_adapter import MlflowModelRepositoryAdapter
from Diagnostic.adapters.outbound.diagnosis_notification_controller_adapter import DiagnosisNotificationControllerAdapter
from Diagnostic.application.diagnosis_services import DiagnosisServicesImpl
from Report.ports.inbound.report_services_port import ReportServicesPort

class DiagnosticContainer(containers.DeclarativeContainer):
    """Contenedor de DI para módulo Diagnostic."""


    # 0) Configuración de inyección de dependencias
    # Se especifica el módulo donde se encuentran los adaptadores FastAPI
    wiring_config = containers.WiringConfiguration(
        modules=[
            "Diagnostic.adapters.inbound.fastapi_diagnostic_services_adapter"
        ]
    )

    # 1) Carga desde config.yml
    config = providers.Configuration(yaml_files=['config.yml'])

    # 2) Adaptador para Report Module (se inyecta al crear instancia)
    report_services = providers.Dependency(instance_of=ReportServicesPort)

    # 3) Configuración de servicios (ModelRegistry)
    config_services = providers.Singleton(
        ConfigServicesImpl,
        model_repository=providers.Dependency()    # Esto tiene que ir así? lo inyecta automáticamente más adelante? o borramos la línea?
    )

    # 4) Repositorio de modelos MLflow
    model_repository = providers.Singleton(   #Está bien que sea singleton? Antes pusimos factory
        # No es necesario que sea singleton, pero se recomienda para evitar múltiples conexiones a la misma base de datos
        MlflowModelRepositoryAdapter,
        config_services=config_services  
        # Aquí debería ir algo como config.Diagnostic.model_registry.uri? algo así? o es el config_services?
    )

    # 5) Notificador de resultados al Report Module
    notification_controller = providers.Singleton( # Está bien que sea singleton? Antes pusimos factory
        DiagnosisNotificationControllerAdapter,
        report_services=report_services
    )

    # 6) Servicio principal
    diagnosis_services = providers.Singleton(
        DiagnosisServicesImpl,
        model_repository=model_repository,
        notification_controller=notification_controller,
        config_services=config_services
    )
