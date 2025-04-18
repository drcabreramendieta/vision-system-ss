"""
TODO: Armar un contenedor de contenedores. Aquí se inyecta las dependencias desde otros contenedores. Ver ejemplo en https://python-dependency-injector.ets-labs.org/examples/decoupled-packages.html
"""
from dependency_injector import containers, providers
from Video import VideoContainer
from unittest.mock import MagicMock
from Diagnostic.ports.inbound import DiagnosisServicesPort

class ApplicationContainer(containers.DeclarativeContainer):
    mock_diagnosis = MagicMock(DiagnosisServicesPort)
    video_container = providers.Container(
        VideoContainer,
        diagnosis_services=mock_diagnosis
        )