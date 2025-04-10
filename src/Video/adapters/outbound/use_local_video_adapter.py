from Video.adapters.outbound.local_video_adapter import LocalVideoAdapter
from Video.domain.Frame import Frame

# Instanciar el adaptador con la ruta del video
adapter = LocalVideoAdapter("/mnt/c/Users/UPS/Desktop/Proyecto Sewer-Seer/Desarrollo del Proyecto/Procesamiento de Imágenes/Videos_testbed/F0_C1_D1/_video_F0_C1_D_0.mp4")

def process_frame(frame: Frame):
    # Procesa el frame recibido (por ejemplo, imprimir el ID y el tamaño de la imagen)
    print(f"Frame recibido: {frame.frame_id} con data de forma {frame.data.shape}")

# Iniciar el stream de video (se espera que procese todos los frames y luego cierre el stream)
try:
    success = adapter.open_stream("session_dummy", process_frame)
    if success:
        print("Stream procesado correctamente.")
except Exception as e:
    print(f"Error al procesar el stream: {e}")
