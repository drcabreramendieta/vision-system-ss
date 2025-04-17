from Video.ports.outbound import NotificationControllerPort
from Diagnostic.ports.inbound import DiagnosisServicesPort

class DiagnosticNotificationControllerAdapter(NotificationControllerPort):
    def __init__(self, diagnosis_services:DiagnosisServicesPort):
        self.diagnosis_services = diagnosis_services

    def notify(self, session_id, frame):
        self.diagnosis_services.run_inference(frame=frame)
        return True