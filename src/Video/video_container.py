from dependency_injector import containers, providers
from Video.adapters.outbound import LocalVideoAdapter, DiagnosticNotificationControllerAdapter
from Video.domain import Sessions
from Video.application import VideoLifecycleServices

class VideoContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["Video.adapters.inbound.fastapi_video_services_adapter"])
    config = providers.Configuration(yaml_files=["config.yaml"])
    diagnosis_services = providers.Dependency()

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