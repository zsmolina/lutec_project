import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.config import get_settings
from app.core.exceptions import JobCancelledError, LutecError
from app.services.job_manager import get_job_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    settings.resolve_temp_dir()
    removed = get_job_manager().cleanup_storage()
    logging.getLogger(__name__).info(
        "Lutec API iniciada (archivos temporales eliminados: %d)", removed
    )
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(LutecError)
    async def lutec_error_handler(_: Request, exc: LutecError):
        status = 409 if isinstance(exc, JobCancelledError) else 400
        return JSONResponse(status_code=status, content={"detail": str(exc)})

    app.include_router(api_router, prefix="/api")
    return app


app = create_app()
