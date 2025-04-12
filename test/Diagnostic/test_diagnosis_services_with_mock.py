# file: test/diagnostic/test_diagnosis_services_with_mock.py

import unittest
import datetime
import numpy as np
from unittest.mock import MagicMock
from Diagnostic.application.diagnosis_services import DiagnosisServicesImpl
from Diagnostic.domain.DiagnosisResult import DiagnosisResult
from Diagnostic.domain.InferenceLabel import InferenceLabel
from Diagnostic.ports.outbound.model_repository_port import ModelRepositoryPort
from Diagnostic.ports.outbound.notification_controller_port import NotificationControllerPort  

class TestDiagnosisServicesWithMock(unittest.TestCase):
    def setUp(self):
        # Creamos mocks para los puertos de salida:
        # model_repository_port se utilizará para ejecutar la inferencia.
        self.mock_model_repository = MagicMock(spec=ModelRepositoryPort)
        # notification_controller_port se usaría para notificar, si es que se requiere.
        self.mock_notification_controller = MagicMock(spec=NotificationControllerPort)
        self.mock_notification_controller.notify_result.return_value = True

        # Creamos un dummy modelo; en la implementación se almacenaría en active_model.
        dummy_model = MagicMock()
        dummy_model.id = "model_1"
        dummy_model.name = "TestModel"
        dummy_model.description = "A dummy model"

        # Configuramos el mock para load_model si fuera necesario.
        self.mock_model_repository.load_model.return_value = dummy_model

        # Configuramos run_inference() para que retorne un DiagnosisResult simulado.
        dummy_result = DiagnosisResult(
            label=InferenceLabel.NORMAL, 
            frame=np.random.rand(224, 224, 3) * 255, 
            timestamp=datetime.datetime.now()
        )
        self.mock_model_repository.run_inference.return_value = dummy_result

        # Instanciamos el servicio de inferencia; se asume que requiere un modelo activo.
        self.diagnosis_service = DiagnosisServicesImpl(
            model_repository=self.mock_model_repository,
            notification=self.mock_notification_controller,
            active_model=dummy_model
        )
    
    def test_run_inference(self):
        """
        Verifica que run_inference llama al método run_inference del repositorio con el modelo activo y el frame proporcionado,
        y retorna un DiagnosisResult con el label esperado.
        """
        dummy_frame = np.random.rand(224, 224, 3) * 255  # Puede ser un objeto o una representación de frame.
        result = self.diagnosis_service.run_inference(dummy_frame)
        # Verificar que se llame a run_inference del repositorio con el modelo activo y el frame.
        self.mock_model_repository.run_inference.assert_called_once_with(self.diagnosis_service.active_model, dummy_frame)
        self.assertIsInstance(result, DiagnosisResult)
        self.assertEqual(result.label, InferenceLabel.NORMAL)

if __name__ == '__main__':
    unittest.main()
