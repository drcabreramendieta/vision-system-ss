# src/Video/adapters/outbound/rtsp_video_adapter.py

import os
import time
import cv2
import numpy as np
import threading
from datetime import datetime
from typing import Callable, Optional
from uuid import UUID

from Video.domain import Frame
from Video.ports.outbound import StreamingControllerPort


class RtspVideoAdapter(StreamingControllerPort):
    """
    Adapter OUTBOUND para capturar frames desde RTSP (DVR/cámara).
    Diseñado para comportarse como LocalVideoAdapter:
      - SOLO 1 stream activo a la vez (un hilo).
      - open_stream -> True si abrió y arrancó el hilo.
      - open_stream -> False si ya hay un hilo activo.
      - si no abre el RTSP, lanza RuntimeError con detalle.
    """

    def __init__(
        self,
        rtsp_url: str,
        transport: str = "tcp",
        low_latency: bool = True,
        stimeout_us: int = 5_000_000,
        reconnect: bool = True,
        reconnect_delay_s: float = 1.0,
        buffer_size: Optional[int] = 1,
    ):
        self.rtsp_url = rtsp_url
        self.transport = transport
        self.low_latency = low_latency
        self.stimeout_us = stimeout_us
        self.reconnect = reconnect
        self.reconnect_delay_s = reconnect_delay_s
        self.buffer_size = buffer_size

        self.cap: cv2.VideoCapture | None = None
        self._thread: threading.Thread | None = None
        self._stop_evt = threading.Event()
        self._active_session_id: UUID | None = None
        self._frame_counter: int = 0

    def _set_ffmpeg_options(self) -> None:
        # Importante: esto emula tu ffplay:
        # -rtsp_transport tcp -fflags nobuffer -flags low_delay
        opts = [f"rtsp_transport;{self.transport}"]

        if self.stimeout_us:
            opts.append(f"stimeout;{int(self.stimeout_us)}")

        if self.low_latency:
            opts.append("fflags;nobuffer")
            opts.append("flags;low_delay")
            opts.append("max_delay;0")

        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "|".join(opts)

    def _open_capture(self) -> cv2.VideoCapture:
        self._set_ffmpeg_options()

        cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
        if not cap.isOpened():
            # Fallback genérico (a veces CAP_FFMPEG no engancha)
            cap = cv2.VideoCapture(self.rtsp_url)

        if not cap.isOpened():
            raise RuntimeError(
                "[RTSP] No se pudo abrir el stream.\n"
                f"  url={self.rtsp_url}\n"
                f"  OPENCV_FFMPEG_CAPTURE_OPTIONS={os.environ.get('OPENCV_FFMPEG_CAPTURE_OPTIONS')}\n"
                "  Nota: si esto abre en tu script, revisa si el server está haciendo 2 procesos por --reload."
            )

        # Hint de buffersize (no siempre lo respeta RTSP, pero intentamos)
        if self.buffer_size is not None:
            try:
                cap.set(cv2.CAP_PROP_BUFFERSIZE, int(self.buffer_size))
            except Exception:
                pass

        return cap

    def open_stream(self, session_id: UUID, observer: Callable[[Frame], None]) -> bool:
        # 1) Si ya hay hilo activo, no abrimos otro (igual que LocalVideoAdapter)
        if self._thread and self._thread.is_alive():
            return False

        self._stop_evt.clear()
        self._active_session_id = session_id
        self._frame_counter = 0

        # 2) Abrir RTSP (si falla, lanza RuntimeError con detalle)
        self.cap = self._open_capture()

        def _reader():
            assert self.cap is not None
            cap = self.cap

            while not self._stop_evt.is_set():
                ret, frame_data = cap.read()

                if (not ret) or frame_data is None:
                    if not self.reconnect:
                        break

                    # Intento de reconexión
                    try:
                        cap.release()
                    except Exception:
                        pass

                    time.sleep(self.reconnect_delay_s)
                    if self._stop_evt.is_set():
                        break

                    try:
                        cap = self._open_capture()
                        self.cap = cap
                        continue
                    except Exception:
                        # reintenta luego
                        time.sleep(self.reconnect_delay_s)
                        continue

                self._frame_counter += 1
                frame = Frame(
                    session_id=session_id,
                    frame_id=self._frame_counter,  # contador lógico (RTSP no da POS_FRAMES confiable)
                    data=np.array(frame_data),
                    timestamp=datetime.now(),
                )
                observer(frame)

            try:
                cap.release()
            except Exception:
                pass

        self._thread = threading.Thread(target=_reader, daemon=True)
        self._thread.start()
        return True

    def close_stream(self, session_id: UUID) -> bool:
        # Permitimos cerrar aunque el session_id no coincida exactamente,
        # pero si quieres estrictitud, lo validamos.
        if self._thread and self._thread.is_alive():
            self._stop_evt.set()
            self._thread.join(timeout=2.0)
            if self._thread.is_alive():
                raise RuntimeError("El hilo RTSP no se detuvo en el tiempo esperado")

        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass

        self.cap = None
        self._active_session_id = None
        return True
