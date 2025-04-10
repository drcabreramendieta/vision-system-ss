# file: test/video/dummy_streaming_controller.py
import datetime
from Video.ports.outbound.streaming_controller_port import StreamingControllerPort
from Video.domain.Frame import Frame
from typing import Callable

class DummyStreamingController(StreamingControllerPort):
    def open_stream(self, session_id: str, observer: Callable[[Frame], None]) -> bool:
        """
        Simula la apertura del stream. Llama al observer con un frame dummy y devuelve True.
        """
        # Creamos un dummy frame
        class DummyFrame:
            frame_id = "dummy_frame_1"
            data = [0, 1, 2]  # Idealmente, en producción usarías un np.ndarray
            timestamp = datetime.datetime.now()
        
        dummy_frame = DummyFrame()
        observer(dummy_frame)
        # Devuelve True para simular que el canal se abrió correctamente
        return True


    def close_stream(self, session_id: str) -> bool:
        # Simula el cierre correcto del stream y retorna True
        return True
