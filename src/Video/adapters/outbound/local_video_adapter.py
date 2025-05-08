# src/Video/adapters/outbound/local_video_adapter.py
import cv2, numpy as np, threading
from datetime import datetime
from typing import Callable
from uuid import UUID
from Video.domain.Frame import Frame
from Video.ports.outbound.streaming_controller_port import StreamingControllerPort

class LocalVideoAdapter(StreamingControllerPort):
    """
    Adapter basado en OpenCV que corre la lectura de frames en
    un hilo separado y reinicia al finalizar el video.
    """
    def __init__(self, video_path: str): # AQUI CREAR UN DICCIONARIO DE HILOS DE LA SESION. actualmente solo se crea un hilo. Asociando una N cantidad de hilos a una sesion. Debería poder crear varios hilos 
        self.video_path = video_path
        self.cap: cv2.VideoCapture | None = None
        self._thread: threading.Thread | None = None
        self._stop_evt = threading.Event()

    def open_stream(self, session_id: UUID, observer: Callable[[Frame], None]) -> bool: #Hace falta un id del hilo. ESTE ADAPTADOR DE SALIDA QUE HAGA UN MAPEO DE LOS ID DE SESION A LOS HILOS QUE TIENE CORRIENDO
        if self._thread and self._thread.is_alive():
            # Ya hay un stream corriendo
            return False
        self._stop_evt.clear()
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise RuntimeError(f"No se pudo abrir video {self.video_path}")
        def _reader():
            while not self._stop_evt.is_set():
                ret, frame_data = self.cap.read()
                if not ret:
                    # fin del video: reiniciar
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                #frame_id = f"{session_id}_{int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))}"
                #frame = Frame(frame_id, np.array(frame_data), datetime.now()) # Antes estaba así

                frame_no = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                frame = Frame(
                session_id=session_id,      # viene del open_stream(...)
                frame_id=frame_no,
                data=np.array(frame_data),
                timestamp=datetime.now()
                )
                # notificar al observador
                observer(frame)
            # al salir libera recursos
            self.cap.release()
        self._thread = threading.Thread(target=_reader, daemon=True)
        self._thread.start()
        return True

    def close_stream(self, session_id: UUID) -> bool:
        """
        Señala al hilo que debe detenerse y espera a que termine.
        """
        if self._thread and self._thread.is_alive():
            self._stop_evt.set()
            self._thread.join(timeout=2.0)
            # debemos poner más lógica para asegurarnos de que el hilo se detuvo
            if self._thread.is_alive():
                raise RuntimeError(f"El hilo de video no se detuvo en el tiempo esperado")
        return True # Este true asume que si se cumplió todo
