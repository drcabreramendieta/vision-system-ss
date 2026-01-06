from .fastapi_diagnostic_services_adapter import router as diagnosis_router
from .fastapi_config_services_adapter import router as config_router

__all__ = ["diagnosis_router", "config_router"]
