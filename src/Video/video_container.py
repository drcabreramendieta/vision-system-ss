from dependency_injector import containers, providers
from Video.adapters.outbound import (
    DiagnosticNotificationControllerAdapter,
    InMemoryVideoSessionRepository,
    LocalVideoAdapter,
    RtspVideoAdapter,   # Añadido para soporte RTSP
)
from Video.application import VideoLifecycleServices
from Diagnostic.ports.inbound import DiagnosisServicesPort

class VideoContainer(containers.DeclarativeContainer):
    # Esto comentamos para Centralizar el contenedor raíz. De este modo, no se estará usando dos instancias distintas del servicio de diagnóstico:

    #Una instancia de DiagnosisServicesImpl para atender los endpoints de /diagnosis.
    #Otra distinta de DiagnosisServicesImpl para atender /video/start.

    #wiring_config = containers.WiringConfiguration(modules=["Video.adapters.inbound.fastapi_video_services_adapter",
    #                                                        "Diagnostic.adapters.inbound.fastapi_diagnostic_services_adapter",])
    
    config = providers.Configuration(yaml_files=["config.yaml"])
    diagnosis_services = providers.Dependency(instance_of=DiagnosisServicesPort)

    session_repository = providers.Singleton(InMemoryVideoSessionRepository)


    # Antes así, solo con LocalVideoAdapter para probar flujo con video local
#    stream_controller = providers.Factory(
#        LocalVideoAdapter,
#        video_path=config.video.video_path   #Así se usan las variables de configuración
#        )
    
# Ahora colocamos un selector de adaptador según config.yaml 
    stream_controller = providers.Selector(
        config.video.adapter,
        local=providers.Factory(
            LocalVideoAdapter,
            video_path=config.video.video_path,
        ),
        rtsp=providers.Factory(
            RtspVideoAdapter,
            rtsp_url=config.video.rtsp_url,
            transport=config.video.rtsp_transport,
            low_latency=config.video.low_latency,
            stimeout_us=config.video.stimeout_us,
            reconnect=config.video.reconnect,
            reconnect_delay_s=config.video.reconnect_delay_s,
            buffer_size=config.video.buffer_size,
        ),
    )

    notification_controller = providers.Factory(
        DiagnosticNotificationControllerAdapter,
        diagnosis_services=diagnosis_services
        )
    video_lifecycle_services = providers.Singleton(
        VideoLifecycleServices,
        streaming_controller=stream_controller,
        notification_controller=notification_controller,
        session_repository=session_repository,
        )
