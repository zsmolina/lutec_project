from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.api.schemas.extractions import (
    BatchJobCreatedResponse,
    BatchJobStatusResponse,
    InvoiceOutcomeResponse,
)
from app.domain.enums import InvoiceFormat
from app.services.job_manager import ExtractionJob, JobStatus, get_job_manager
from app.services.output_filenames import invoice_consolidated_filename

router = APIRouter(prefix="/extractions", tags=["extractions"])


def _parse_format(format_value: str) -> InvoiceFormat:
    try:
        return InvoiceFormat(format_value)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Formato inválido. Use: {', '.join(f.value for f in InvoiceFormat)}",
        ) from exc


def _job_to_status(job: ExtractionJob) -> BatchJobStatusResponse:
    download_ready = (
        job.status == JobStatus.COMPLETED
        and job.excel_path is not None
        and job.excel_path.is_file()
        and job.succeeded > 0
    )
    return BatchJobStatusResponse(
        job_id=job.job_id,
        status=job.status.value,
        format=job.invoice_format.value,
        format_label=job.invoice_format.label,
        total=job.total,
        processed=job.processed,
        succeeded=job.succeeded,
        failed=job.failed,
        current_file=job.current_file,
        error=job.error,
        outcomes=[InvoiceOutcomeResponse(**item) for item in job.outcomes],
        download_ready=download_ready,
    )


@router.post("/batch", response_model=BatchJobCreatedResponse, status_code=202)
async def create_batch_extraction(
    format: str = Form(...),
    file: UploadFile = File(...),
):
    invoice_format = _parse_format(format)

    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=422, detail="Se requiere un archivo .zip")

    zip_bytes = await file.read()
    if not zip_bytes:
        raise HTTPException(status_code=422, detail="El archivo ZIP está vacío")

    job = get_job_manager().create_job(invoice_format, zip_bytes)
    return BatchJobCreatedResponse(
        job_id=job.job_id,
        status=job.status.value,
        format=job.invoice_format.value,
        format_label=job.invoice_format.label,
        total=job.total,
    )


@router.get("/jobs/{job_id}", response_model=BatchJobStatusResponse)
def get_batch_job_status(job_id: str):
    job = get_job_manager().get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo de extracción no encontrado")
    return _job_to_status(job)


@router.delete("/jobs/{job_id}", response_model=BatchJobStatusResponse)
def cancel_batch_job(job_id: str):
    manager = get_job_manager()
    try:
        job = manager.cancel_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Trabajo de extracción no encontrado") from exc
    return _job_to_status(job)


@router.get("/jobs/{job_id}/download")
def download_batch_excel(job_id: str):
    job = get_job_manager().get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo de extracción no encontrado")

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=409, detail="El procesamiento aún no ha finalizado")

    if not job.excel_path or not job.excel_path.is_file():
        raise HTTPException(status_code=404, detail="No hay archivo Excel disponible")

    if job.succeeded == 0:
        raise HTTPException(
            status_code=409,
            detail="No se generó Excel porque ninguna factura se procesó correctamente",
        )

    download_name = invoice_consolidated_filename(job.invoice_format.value)
    return FileResponse(
        path=job.excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=download_name,
    )
