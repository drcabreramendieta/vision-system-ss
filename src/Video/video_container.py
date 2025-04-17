from dependency_injector import containers, providers
from Video.adapters.outbound import LocalVideoAdapter, DiagnosticNotificationControllerAdapter
from Video.domain import Sessions
from Video.application import VideoLifecycleServices

class VideoContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    diagnosis_services = providers.Dependency()

    sessions_container = providers.Factory(Sessions)
    stream_controller = providers.Factory(
        LocalVideoAdapter,
        video_path=config.video_path
        )
    notification_controller = providers.Factory(
        DiagnosticNotificationControllerAdapter,
        diagnosis_services=diagnosis_services
        )
    video_lifecycle_services = providers.Factory(
        VideoLifecycleServices,
        stream_controller=stream_controller,
        notification_controller=notification_controller,
        sessions_container = sessions_container
        )