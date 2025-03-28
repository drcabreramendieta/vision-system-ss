
from Video.ports.inbound.video_ingest_port import VideoIngestPort
from Video.ports.outbound.dvr_source_port import DvrSourcePort
from Video.ports.outbound.diagnostic_module_port import DiagnosticModulePort

class VideoIngestServices(VideoIngestPort):
    """
    Implementa la ingesta de frames y su envío al Módulo de Diagnóstico.
    """

    def __init__(self, dvr_source: DvrSourcePort, diagnostic_module: DiagnosticModulePort):
        """
        Inyecta los puertos de salida:
          - dvr_source (para obtener frames)
          - diagnostic_module (para enviar frames a diagnóstico)
        """
        self.dvr_source = dvr_source
        self.diagnostic_module = diagnostic_module
        self._is_ingesting = {}

    def start_ingest(self, session_id: str) -> None:
        """
        Abre el stream y comienza a obtener frames, enviándolos al Módulo de Diagnóstico.
        En un escenario real, podría correrse en un hilo separado o un bucle asíncrono.
        """
        self.dvr_source.open_stream(session_id)
        self._is_ingesting[session_id] = True

        # Ejemplo simplificado: un bucle "controlado"
        # En la práctica, se usaría un hilo o async
        while self._is_ingesting[session_id]:
            frame = self.dvr_source.get_next_frame(session_id)
            if not frame:
                # No hay más frames o hubo un error
                break
            # Enviar frame al Módulo de Diagnóstico
            self.diagnostic_module.send_frame_to_diagnosis(
                session_id=session_id,
                frame_id=frame.frame_id,
                data=frame.data,
                timestamp=frame.timestamp
            )

        # Al salir del bucle, cerramos el stream
        self.dvr_source.close_stream(session_id)

    def stop_ingest(self, session_id: str) -> None:
        """
        Detiene la ingesta de frames, provocando la salida del bucle.
        """
        if session_id in self._is_ingesting:
            self._is_ingesting[session_id] = False
