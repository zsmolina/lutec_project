import logging
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from app.config import Settings, get_settings
from app.core.exceptions import JobCancelledError
from app.core.archive_validation import load_pdf_entries
from app.domain.enums import EnergyRetailer, InvoiceFormat
from app.pipelines.batch_processor import BatchProcessor
from app.services.storage_cleanup import cleanup_stale_files

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExtractionJob:
    job_id: str
    retailer: EnergyRetailer
    invoice_format: InvoiceFormat
    zip_path: Path
    pdf_entry_names: list[str]
    status: JobStatus = JobStatus.QUEUED
    total: int = 0
    processed: int = 0
    succeeded: int = 0
    failed: int = 0
    current_file: str | None = None
    error: str | None = None
    excel_path: Path | None = None
    outcomes: list[dict] = field(default_factory=list)
    _cancel_event: threading.Event = field(default_factory=threading.Event, repr=False)


class JobManager:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._jobs: dict[str, ExtractionJob] = {}
        self._lock = threading.Lock()

    def create_job(self, retailer: EnergyRetailer, zip_bytes: bytes) -> ExtractionJob:
        """Responde al instante; la validación del ZIP ocurre en el hilo de fondo."""
        job_id = str(uuid.uuid4())
        jobs_dir = self.settings.resolve_jobs_dir()
        zip_path = jobs_dir / f"{job_id}.zip"
        zip_path.write_bytes(zip_bytes)

        job = ExtractionJob(
            job_id=job_id,
            retailer=retailer,
            invoice_format=InvoiceFormat.AUTO,
            zip_path=zip_path,
            pdf_entry_names=[],
            total=0,
            current_file="Validando archivos del ZIP…",
        )
        with self._lock:
            self._jobs[job_id] = job

        thread = threading.Thread(
            target=self._run_job,
            args=(job_id,),
            name=f"extraction-{job_id[:8]}",
            daemon=True,
        )
        thread.start()
        return job

    def get_job(self, job_id: str) -> ExtractionJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def cancel_job(self, job_id: str) -> ExtractionJob:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                raise KeyError(job_id)
            if job.status in {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}:
                return job
            job._cancel_event.set()
            job.status = JobStatus.CANCELLED
            job.current_file = None
            job.error = "Procesamiento cancelado por el usuario."
            return job

    def cleanup_storage(self) -> int:
        jobs_dir = self.settings.resolve_jobs_dir()
        return cleanup_stale_files(jobs_dir, self.settings.job_ttl_hours)

    def _run_job(self, job_id: str) -> None:
        job = self.get_job(job_id)
        if not job:
            return

        excel_path = self.settings.resolve_jobs_dir() / f"{job_id}.xlsx"

        try:
            with self._lock:
                if job._cancel_event.is_set():
                    job.status = JobStatus.CANCELLED
                    job.error = "Procesamiento cancelado por el usuario."
                    return
                job.current_file = "Validando archivos del ZIP…"

            pdf_entry_names = load_pdf_entries(job.zip_path.read_bytes(), self.settings)

            with self._lock:
                locked_job = self._jobs.get(job_id)
                if not locked_job or locked_job._cancel_event.is_set():
                    if locked_job:
                        locked_job.status = JobStatus.CANCELLED
                        locked_job.error = "Procesamiento cancelado por el usuario."
                    return
                locked_job.pdf_entry_names = pdf_entry_names
                locked_job.total = len(pdf_entry_names)
                locked_job.status = JobStatus.PROCESSING
                locked_job.excel_path = excel_path
                locked_job.current_file = None

            processor = BatchProcessor(job.retailer, self.settings)

            def on_progress(
                processed: int,
                total: int,
                current_file: str | None,
                succeeded: int,
                failed: int,
            ) -> None:
                with self._lock:
                    locked_job = self._jobs.get(job_id)
                    if not locked_job:
                        return
                    locked_job.total = total
                    locked_job.processed = processed
                    locked_job.current_file = current_file
                    locked_job.succeeded = succeeded
                    locked_job.failed = failed

            result = processor.process_zip_path(
                job.zip_path,
                excel_path,
                job.pdf_entry_names,
                on_progress=on_progress,
                should_cancel=job._cancel_event.is_set,
            )

            with self._lock:
                locked_job = self._jobs[job_id]
                if locked_job._cancel_event.is_set():
                    locked_job.status = JobStatus.CANCELLED
                    locked_job.error = "Procesamiento cancelado por el usuario."
                    locked_job.current_file = None
                    return
                locked_job.status = JobStatus.COMPLETED
                locked_job.total = result.total
                locked_job.processed = result.total
                locked_job.succeeded = result.succeeded
                locked_job.failed = result.failed
                locked_job.current_file = None
                locked_job.outcomes = [
                    {
                        "filename": outcome.filename,
                        "success": outcome.success,
                        "nic": outcome.nic,
                        "error": outcome.error,
                        "format_detected": outcome.format_detected,
                        "format_label": outcome.format_label,
                    }
                    for outcome in result.outcomes
                ]
                locked_job.excel_path = result.excel_path

        except JobCancelledError:
            with self._lock:
                locked_job = self._jobs.get(job_id)
                if locked_job:
                    locked_job.status = JobStatus.CANCELLED
                    locked_job.error = "Procesamiento cancelado por el usuario."
                    locked_job.current_file = None
        except Exception as exc:
            logger.exception("Job %s falló", job_id)
            with self._lock:
                locked_job = self._jobs.get(job_id)
                if locked_job and locked_job.status != JobStatus.CANCELLED:
                    locked_job.status = JobStatus.FAILED
                    locked_job.error = str(exc)
                    locked_job.current_file = None


_job_manager: JobManager | None = None


def get_job_manager() -> JobManager:
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager()
    return _job_manager
