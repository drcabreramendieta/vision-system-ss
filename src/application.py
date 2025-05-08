from fastapi import FastAPI
from Video.adapters.inbound.fastapi_video_services_adapter import router as video_router
from Diagnostic.adapters.inbound.fastapi_diagnostic_services_adapter import router as diag_router
import application_container

def create_app() -> FastAPI:
    # 1) Instancio el contenedor raíz
    container = application_container.ApplicationContainer()
    # 2) Wireo los módulos de FastAPI donde usas @inject + Provide[...]
    container.wire(modules=[
        "Video.adapters.inbound.fastapi_video_services_adapter",
        "Diagnostic.adapters.inbound.fastapi_diagnostic_services_adapter",
    ])
    # 3) Asigno el contenedor a la app
    app = FastAPI()
    app.container = container
    # 4) Montado de routers
    app.include_router(video_router)
    app.include_router(diag_router)
    return app

app = create_app()