from fastapi import FastAPI
from Video.adapters.inbound.fastapi_video_services_adapter import router
import application_container

def create_app() -> FastAPI:
    container = application_container.ApplicationContainer()
    app = FastAPI()
    app.container = container
    app.include_router(router)
    return app

app = create_app()