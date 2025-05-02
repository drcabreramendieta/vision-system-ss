from fastapi import FastAPI
from Video.adapters.inbound.fastapi_video_services_adapter import router
from Diagnostic.adapters.inbound.fastapi_diagnostic_services_adapter import router as diag_router
import application_container

def create_app() -> FastAPI:
    container = application_container.ApplicationContainer()
    app = FastAPI()
    app.container = container
    app.include_router(router)
    app.include_router(diag_router)
    return app

app = create_app()