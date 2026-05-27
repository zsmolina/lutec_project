from fastapi import APIRouter

from app.api.v1.extractions import router as extractions_router
from app.api.v1.formap import router as formap_router
from app.config import get_settings
from app.domain.enums import EnergyRetailer
from app.services.extraction.registry import list_supported_formats, list_supported_retailers
from app.services.job_manager import get_job_manager

api_router = APIRouter(prefix="/v1")
api_router.include_router(extractions_router)
api_router.include_router(formap_router)


@api_router.get("/health")
def health_check():
    settings = get_settings()
    return {
        "status": "ok",
        "openai_configured": settings.openai_configured,
        "limits": {
            "max_zip_size_mb": settings.max_zip_size_mb,
            "max_pdf_count": settings.max_pdf_count,
            "max_pdf_size_mb": settings.max_pdf_size_mb,
            "max_formap_excel_mb": settings.max_formap_excel_mb,
        },
    }


@api_router.get("/retailers")
def supported_retailers():
    return {"retailers": list_supported_retailers()}


@api_router.get("/formats")
def supported_formats(retailer: str | None = None):
    if retailer is None:
        return {"formats": list_supported_formats()}
    try:
        r = EnergyRetailer(retailer)
    except ValueError:
        return {"formats": []}
    return {"formats": list_supported_formats(r)}
