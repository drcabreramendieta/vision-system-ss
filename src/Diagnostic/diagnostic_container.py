"""
TODO: Armar un contenedor siguiendo los lineamientos del de video
"""

from dependency_injector import containers, providers
from Diagnostic.application.config_services import ConfigServicesImpl
from Diagnostic.adapters.outbound.mlflow_model_repository_adapter import MlflowModelRepositoryAdapter
from Diagnostic.adapters.outbound.diagnosis_notification_controller_adapter import DiagnosisNotificationControllerAdapter
from Diagnostic.application.diagnosis_services import DiagnosisServicesImpl

class DiagnosticContainer(containers.DeclarativeContainer):
    """
    Contenedor para el módulo Diagnostic:
      - Carga configuración de MLflow
      - Define adaptadores outbound para repositorio de modelos y notificaciones
      - Expone un singleton de DiagnosisServicesImpl
    """
    wiring_config = containers.WiringConfiguration(
        modules=[
            "Diagnostic.adapters.inbound.fastapi_diagnostic_services_adapter",   # Preguntar a Diego si sería algo así
        ]
    )

    # Sección de configuración (config.yaml)
    config = providers.Configuration() #También tiene que cargar algún archivo de configuración .yaml? Con la uri del servidor de MLflow POR EJEMPLO?

    # Servicio para seleccionar/configurar el modelo activo
    config_services = providers.Singleton(
        ConfigServicesImpl,
        mlflow_config=config.mlflow,  
    )

    # Adaptador para cargar y manejar modelos de MLflow
    model_repository = providers.Factory(
        MlflowModelRepositoryAdapter,
        config_services=config_services,
    )

    # Adaptador para notificar resultados de diagnóstico al Report Module
    notification_controller = providers.Factory(
        DiagnosisNotificationControllerAdapter,
    )

    # Servicio de aplicación que orquesta la inferencia
    diagnosis_services = providers.Singleton(
        DiagnosisServicesImpl,
        model_repository_port=model_repository,
        notification_controller_port=notification_controller,
    )