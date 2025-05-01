"""
TODO: Armar un contenedor de contenedores. Aquí se inyecta las dependencias desde otros contenedores. Ver ejemplo en https://python-dependency-injector.ets-labs.org/examples/decoupled-packages.html
"""
from dependency_injector import containers, providers
from Video import VideoContainer
from unittest.mock import MagicMock
from Diagnostic.ports.inbound import DiagnosisServicesPort
#from Diagnostic.diagnostic_container import DiagnosticContainer
from Report.ports.inbound import ReportServicesPort
from Report.report_container import ReportContainer

class ApplicationContainer(containers.DeclarativeContainer):
    
    # Puesto por Diego para poder testear el contenedor de video?
    mock_diagnosis = MagicMock(DiagnosisServicesPort)
    mock_report = MagicMock(ReportServicesPort)
    #video_container = providers.Container(
    #    VideoContainer,
    #    diagnosis_services=mock_diagnosis
    #    )

    # Subcontenedores
    #report = providers.Container(    # Este no tiene dependencias
    #    ReportContainer,
    #)

    #diagnostic = providers.Container(
    #    DiagnosticContainer,
    #    report_services= mock_report # report.report_services,  # Inyectar el servicio de Report
    #)

    video = providers.Container(
        VideoContainer,
        diagnosis_services= mock_diagnosis #diagnostic.diagnosis_services,  # Inyectar el servicio de diagnóstico
    )

# Las APIs de cada módulo sería parecido como los de video 