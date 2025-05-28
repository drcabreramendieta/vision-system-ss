# src/Video/adapters/outbound/diagnostic_notification_controller_adapter.py
from PIL import Image
import numpy as np
from Video.ports.outbound.notification_controller_port import NotificationControllerPort
from Diagnostic.ports.inbound.diagnosis_services_port import DiagnosisServicesPort

# tamaño de entrada del modelo (lectura estática o config)
TARGET_SHAPE = (352, 288)  # (ancho, alto)

class DiagnosticNotificationControllerAdapter(NotificationControllerPort):
    def __init__(self, diagnosis_services: DiagnosisServicesPort):
        self.diagnosis_services = diagnosis_services

    def notify(self, session_id, frame):
        # ahora el frame tiene su propio session_id,
        # pero seguimos recibiéndolo por el puerto
        # Se debe pre‐procesar exactamente igual que en el endpoint HTTP
        # 1) Convertir el array BGR de OpenCV a RGB PIL.Image
        img = Image.fromarray(frame.data[..., ::-1])  # cv2 usa BGR

        # 2) Resize
        img = img.resize(TARGET_SHAPE, Image.BILINEAR)

        # 3) Pasar a np.array y reordenar ejes
        # arr = np.array(img).transpose(2, 0, 1).astype(np.float32) Así estaba antes, pero no es correcto
        arr = np.array(img).astype(np.float32)            # (H, W, C) = (288, 352, 3). PIL → numpy siempre da (alto, ancho, canales)
        arr = arr.transpose(2, 1, 0) 
        arr = arr / 255.0 # Normalizar a [0, 1] si es necesario. Esto debido a que en el entrenamiento se usaba ToTensor(). Debe tener (C, H, W)
        
        # 4) Ejecutar  inferencia y capturar resultado. le pasamos ambos al servicio de diagnóstico
        result = self.diagnosis_services.run_inference(arr, str(session_id)) # Hacemos str(session_id) porque el servicio de diagnóstico espera un string
        
        # 5) print con frame.frame_id (Para verificar el stream de frames y el resultado de inferencia)
        print(f"[Frame {frame.frame_id} → Inf] session={session_id} label={result.label.name}")
        return True
