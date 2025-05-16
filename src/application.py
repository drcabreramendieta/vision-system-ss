from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager
from Video.adapters.inbound.fastapi_video_services_adapter import router as video_router
from Diagnostic.adapters.inbound.fastapi_diagnostic_services_adapter import router as diag_router
from Report.adapters.inbound.fastapi_report_services_adapter import router as report_router
from Report.application.report_services import ReportServices
import application_container

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Este bloque se ejecuta *antes* de arrancar los servidores,
    y después de que se detenga el servidor (en shutdown).
    """
    # Startup: capturamos el loop principal para notificaciones desde hilos
    ReportServices.MAIN_LOOP = asyncio.get_event_loop()
    yield
    # Aquí podrías poner lógica de limpieza si la necesitas
    

def create_app() -> FastAPI:
    # 1) Instancio el contenedor raíz
    container = application_container.ApplicationContainer()
    # 2) Wireo los módulos de FastAPI donde usas @inject + Provide[...]
    container.wire(modules=[
        "Video.adapters.inbound.fastapi_video_services_adapter",
        "Diagnostic.adapters.inbound.fastapi_diagnostic_services_adapter",
        "Report.adapters.inbound.fastapi_report_services_adapter",
    ])

    # 3) Asigno el contenedor a la app. Creamos la app inyectando el lifespan
    app = FastAPI(lifespan=lifespan)
    # 4) Asignamos el container
    app.container = container
    # 5) Montado de routers
    app.include_router(video_router)
    app.include_router(diag_router)
    app.include_router(report_router)

    return app

app = create_app()