from dependency_injector import containers, providers
from Video.adapters.outbound import LocalVideoAdapter, DiagnosticNotificationControllerAdapter
from Video.domain import Sessions
from Video.application import VideoLifecycleServices
from Diagnostic.ports.inbound.diagnosis_services_port import DiagnosisServicesPort

class VideoContainer(containers.DeclarativeContainer):
    # Esto comentamos para Centralizar el contenedor raíz. De este modo, no se estará usando dos instancias distintas del servicio de diagnóstico:

    #Una instancia de DiagnosisServicesImpl para atender los endpoints de /diagnosis.
    #Otra distinta de DiagnosisServicesImpl para atender /video/start.

    #wiring_config = containers.WiringConfiguration(modules=["Video.adapters.inbound.fastapi_video_services_adapter",
    #                                                        "Diagnostic.adapters.inbound.fastapi_diagnostic_services_adapter",])
    
    config = providers.Configuration(yaml_files=["config.yaml"])
    diagnosis_services = providers.Dependency(instance_of=DiagnosisServicesPort)

    sessions_container = providers.Factory(Sessions)

    stream_controller = providers.Factory(
        LocalVideoAdapter,
        video_path=config.video.video_path   #Así se usan las variables de configuración
        )
    notification_controller = providers.Factory(
        DiagnosticNotificationControllerAdapter,
        diagnosis_services=diagnosis_services
        )
    video_lifecycle_services = providers.Singleton(
        VideoLifecycleServices,
        streaming_controller=stream_controller,
        notification_controller=notification_controller,
        sessions_container = sessions_container
        )