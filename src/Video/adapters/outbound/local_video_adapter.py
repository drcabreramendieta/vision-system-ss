# file: video/adapters/outbound/local_video_adapter.py

import cv2
import numpy as np
from datetime import datetime
from typing import Callable
from Video.domain.Frame import Frame
from Video.ports.outbound.streaming_controller_port import StreamingControllerPort

class LocalVideoAdapter(StreamingControllerPort):
    """
    LocalVideoAdapter implementa la interfaz StreamingControllerPort para adquirir frames de un video local.
    
    Utiliza OpenCV para abrir y leer el archivo de video. Por cada frame leído, invoca un
    callback (observer) suministrado, pasando un objeto Frame que contiene:
      - frame_id: Identificador generado (por ejemplo, basado en el número de frame).
      - data: El contenido del frame en forma de np.ndarray.
      - timestamp: La marca de tiempo en el momento de la lectura.

    Al finalizar la lectura (o si se produce un error), se cierran los recursos asociados (VideoCapture).
    
    Ejemplo de uso:
        adapter = LocalVideoAdapter("ruta/al/video.mp4")
        def process_frame(frame: Frame):
            print("Frame recibido:", frame.frame_id)
        adapter.open_stream("session_id_123", process_frame)
    """

    def __init__(self, video_path: str):
        """
        Inicializa el adaptador de video con la ruta del archivo.

        :param video_path: Ruta al archivo de video local.
        """
        self.video_path = video_path
        print("path video:", self.video_path)
        self.cap = None  # Se usará para almacenar el objeto VideoCapture

    def open_stream(self, session_id: str, observer: Callable[[Frame], None]) -> bool:
        """
        Abre el video local y, por cada frame leído, ejecuta el callback (observer) con un objeto Frame.
        
        Procedimiento:
         1. Se intenta abrir el video con OpenCV.
         2. Si no se puede abrir, se lanza un RuntimeError.
         3. Mientras el video esté abierto, se leen los frames uno a uno.
         4. Por cada frame leído, se genera un identificador, se crea un objeto Frame y se invoca al observer.
         5. Cuando no se puedan leer más frames, se cierra el stream y se retorna True.

        :param session_id: Identificador de la sesión (no se usa para la lectura, pero se requiere por contrato).
        :param observer: Función callback que se invoca por cada frame leído. Debe aceptar un objeto Frame.
        :return: True si el stream se abre, procesa y cierra correctamente.
        :raises RuntimeError: Si no se puede abrir el video.
        """
        # Abrir el archivo de video usando OpenCV
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise RuntimeError(f"No se pudo abrir el video: {self.video_path}")

        # Leer frames mientras el video esté abierto
        while self.cap.isOpened():
            ret, frame_data = self.cap.read()
            if not ret:
                # Fin del video o error en la lectura
                break

            # Generar un frame_id basado en el número de frame actual
            frame_number = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            frame_id = f"frame_{frame_number}"

            # Garantizar que frame_data sea un np.ndarray
            if not isinstance(frame_data, np.ndarray):
                frame_data = np.array(frame_data)

            # Crear el objeto Frame
            frame = Frame(
                frame_id=frame_id,
                data=frame_data,
                timestamp=datetime.now()
            )

            # Llamar al callback observer con el frame
            observer(frame)

        # Una vez terminado el bucle (fin de video o error), cerrar el stream.
        self.close_stream(session_id)
        return True

    def get_next_frame(self, session_id: str) -> Frame:
        """
        Este adaptador opera en modo observer, es decir, no se implementa la funcionalidad pull para obtener el siguiente frame.
        
        :param session_id: Identificador de la sesión.
        :raises NotImplementedError: Siempre, porque este método no es aplicable en el modo observer.
        """
        raise NotImplementedError("Este adaptador usa observer-based, no pull-based.")

    def close_stream(self, session_id: str) -> bool:
        """
        Cierra el stream de video y libera los recursos asociados.
        
        :param session_id: Identificador de la sesión.
        :return: True si se liberaron correctamente los recursos.
        """
        if self.cap:
            self.cap.release()
            self.cap = None
        return True
