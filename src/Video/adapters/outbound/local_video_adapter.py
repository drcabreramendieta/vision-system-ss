# file: video/adapters/outbound/local_video_adapter.py

import cv2
import numpy as np
from datetime import datetime
from typing import Callable
from Video.domain.Frame import Frame
from Video.ports.outbound.streaming_controller_port import StreamingControllerPort

class LocalVideoAdapter(StreamingControllerPort):
    """
    Adaptador que simula la adquisición de video leyendo un archivo local.
    Utiliza OpenCV para leer el video y, por cada frame, invoca el callback (observer).
    """

    def __init__(self, video_path: str):
        self.video_path = video_path
        self.cap = None

    def open_stream(self, session_id: str, observer: Callable[[Frame], None]) -> None:
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise RuntimeError(f"No se pudo abrir el video: {self.video_path}")
        while self.cap.isOpened():
            ret, frame_data = self.cap.read()
            if not ret:
                break
            # Crear un frame usando la información leída
            frame_id = "frame_" + str(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
            frame = Frame(
                frame_id=frame_id,
                data=frame_data,  # np.ndarray con la imagen
                timestamp=datetime.now()
            )
            observer(frame)
        self.close_stream(session_id)

    def get_next_frame(self, session_id: str) -> Frame:
        raise NotImplementedError("Este adaptador usa observer-based, no pull-based.")

    def close_stream(self, session_id: str) -> None:
        if self.cap:
            self.cap.release()
            self.cap = None
