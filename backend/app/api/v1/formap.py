from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.config import get_settings
from app.core.exceptions import FormapConsolidationError
from app.services.formap_consolidator import consolidate_formap_workbook
from app.services.output_filenames import FORMAP_OUTPUT_FILENAME

router = APIRouter(prefix="/formap", tags=["formap"])

ALLOWED_EXTENSIONS = (".xlsx", ".xlsm")


@router.post("/consolidate")
async def consolidate_formap(file: UploadFile = File(...)):
    """Recibe un Excel Formap y devuelve el reporte unificado estilizado."""
    filename = (file.filename or "").lower()
    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=422,
            detail="Se requiere un archivo Excel (.xlsx o .xlsm).",
        )

    source_bytes = await file.read()
    settings = get_settings()

    if len(source_bytes) > settings.max_formap_excel_bytes:
        raise HTTPException(
            status_code=422,
            detail=f"El archivo supera el tamaño máximo ({settings.max_formap_excel_mb} MB).",
        )

    if not source_bytes:
        raise HTTPException(status_code=422, detail="El archivo Excel está vacío.")

    try:
        output_bytes = consolidate_formap_workbook(source_bytes)
    except FormapConsolidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return Response(
        content=output_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{FORMAP_OUTPUT_FILENAME}"'},
    )
