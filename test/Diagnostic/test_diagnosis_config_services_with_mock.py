# file: test/diagnostic/test_diagnosis_config_services_with_mock.py

import unittest
from unittest.mock import MagicMock
from Diagnostic.application import ConfigServicesImpl
from Diagnostic.domain import Model

class TestDiagnosisConfigServicesWithMock(unittest.TestCase):
    def setUp(self):
        # Creamos un mock para el puerto de salida: model_repository_port.
        self.mock_model_repository = MagicMock()
        # Configuramos el mock para que get_models() retorne una lista de modelos.
        self.mock_model_repository.get_models.return_value = [
            Model(id="model_1", name="TestModel", description="A test model")
        ]
        # Configuramos el mock para load_model() para simular la carga exitosa.
        self.mock_model_repository.load_model.return_value = True
        # Instanciamos el servicio de configuración inyectando el puerto mock.
        self.config_service = ConfigServicesImpl(
            model_repository=self.mock_model_repository
        )
    
    def test_get_models(self):
        """
        Verifica que get_models() retorne la lista de modelos proveniente del repositorio.
        """
        models = self.config_service.get_models()
        self.mock_model_repository.get_models.assert_called_once()
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0].id, "model_1")
    
    def test_set_model(self):
        """
        Verifica que set_model() invoque load_model() con el ID adecuado y almacene el modelo activo.
        """
        model_to_set = Model(id="model_1", name="TestModel", description="A test model")
        ok = self.config_service.set_model(model_to_set.id)
        self.mock_model_repository.load_model.assert_called_once_with("model_1")
        self.assertTrue(ok)

if __name__ == '__main__':
    unittest.main()
