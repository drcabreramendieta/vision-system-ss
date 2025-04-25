"""
TODO: Armar un contenedor de contenedores. Aquí se inyecta las dependencias desde otros contenedores. Ver ejemplo en https://python-dependency-injector.ets-labs.org/examples/decoupled-packages.html
"""
from dependency_injector import containers, providers
from Video import VideoContainer
from unittest.mock import MagicMock
from Diagnostic.ports.inbound import DiagnosisServicesPort
from Diagnostic.diagnostic_container import DiagnosticContainer
from Report.report_container import ReportContainer

class ApplicationContainer(containers.DeclarativeContainer):
    
    # Puesto por Diego para poder testear el contenedor de video?
    mock_diagnosis = MagicMock(DiagnosisServicesPort)
    #video_container = providers.Container(
    #    VideoContainer,
    #    diagnosis_services=mock_diagnosis
    #    )

    """
    Contenedor raíz de la aplicación:
      - Carga configuración general (config.yaml)
      - Anida los contenedores de Video, Diagnostic y Report
      - Centraliza el wiring de adaptadores inbound (FastAPI routers)
    """
    wiring_config = containers.WiringConfiguration(  #Esto me dió el GPT, pero no sé si es correcto. Ya que internamente ya se hace un wiring
        modules=[
            "Video.adapters.inbound.fastapi_video_services_adapter",
            "Diagnostic.adapters.inbound.fastapi_diagnostic_services_adapter",
            "Report.adapters.inbound.fastapi_report_services_adapter",
        ]
    )

    # Configuración general con secciones por módulo
    config = providers.Configuration(yaml_files=["config.yaml"]) #Se puede hacer esto con un solo archivo de configuración o se puede hacer uno por módulo. Preguntar a Diego si es necesario tener un config.yaml por módulo o uno general?

    # Subcontenedores
    diagnostic = providers.Container(
        DiagnosticContainer,
        config=config.diagnostic,
    )

    report = providers.Container(
        ReportContainer,
        config=config.report,
    )

    video = providers.Container(
        VideoContainer,
        config=config.video,
        diagnosis_services=mock_diagnosis,
    )