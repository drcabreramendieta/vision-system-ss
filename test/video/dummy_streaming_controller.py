# file: test/video/dummy_streaming_controller.py

import datetime
from typing import Callable
from uuid import UUID
from Video.ports.outbound import StreamingControllerPort
from Video.domain import Frame

class DummyStreamingController(StreamingControllerPort):
    """
    Dummy para simular la apertura y cierre del stream.
    Se asegura de devolver True en open_stream para indicar que el canal se abrió correctamente.
    """
    def open_stream(self, session_id: UUID, observer: Callable[[Frame], None]) -> bool:
        # Creamos un frame dummy.
        class DummyFrame:
            frame_id = "dummy_frame_1"
            data = [0, 1, 2]  # Simulación de datos; en producción se usará un np.ndarray.
            timestamp = datetime.datetime.now()
        dummy_frame = DummyFrame()
        # Invocamos el observer para simular la recepción de un frame.
        observer(dummy_frame)
        # Retornamos True para indicar que la apertura fue exitosa.
        return True

    def get_next_frame(self, session_id: UUID):
        raise NotImplementedError("No se usa en el modo observer-based.")

    def close_stream(self, session_id: UUID) -> bool:
        # Simula cerrar el stream sin errores y retorna True.
        return True
