import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

from app.config import Settings, get_settings
from app.core.exceptions import FormatDetectionError, JobCancelledError
from app.core.archive_validation import load_pdf_entries
from app.domain.enums import EnergyRetailer, InvoiceFormat, display_format_label
from app.services.excel_exporter import ExcelExporter
from app.services.extraction.excel_columns import INVOICE_EXCEL_COLUMNS
from app.services.extraction.registry import get_extractor
from app.services.format_classifier import classify_invoice_format
from app.services.openai_client import create_openai_client
from app.services.zip_archive import ZipPdfEntry, iter_pdfs_from_zip, iter_pdfs_from_zip_path

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int, str | None, int, int], None]
CancelCheck = Callable[[], bool]


@dataclass
class InvoiceProcessOutcome:
    filename: str
    success: bool
    nic: str | None = None
    error: str | None = None
    format_detected: str | None = None
    format_label: str | None = None


@dataclass
class BatchProcessResult:
    total: int
    succeeded: int
    failed: int
    excel_path: Path
    outcomes: list[InvoiceProcessOutcome] = field(default_factory=list)


class BatchProcessor:
    def __init__(
        self,
        retailer: EnergyRetailer,
        settings: Settings | None = None,
    ):
        self.retailer = retailer
        self.settings = settings or get_settings()
        self._client = create_openai_client(self.settings)

    def process_zip_path(
        self,
        zip_path: Path,
        excel_output: Path,
        pdf_entry_names: list[str],
        on_progress: ProgressCallback | None = None,
        should_cancel: CancelCheck | None = None,
    ) -> BatchProcessResult:
        return self._process_entries(
            iter_pdfs_from_zip_path(zip_path, self.settings, pdf_entry_names),
            len(pdf_entry_names),
            excel_output,
            on_progress,
            should_cancel,
        )

    def process_zip_bytes(
        self,
        zip_bytes: bytes,
        excel_output: Path,
        pdf_entry_names: list[str],
        on_progress: ProgressCallback | None = None,
        should_cancel: CancelCheck | None = None,
    ) -> BatchProcessResult:
        return self._process_entries(
            iter_pdfs_from_zip(zip_bytes, self.settings, pdf_entry_names),
            len(pdf_entry_names),
            excel_output,
            on_progress,
            should_cancel,
        )

    def process_zip_file(
        self,
        zip_path: Path,
        excel_output: Path,
        pdf_entry_names: list[str] | None = None,
    ) -> BatchProcessResult:
        zip_bytes = zip_path.read_bytes()
        entries = pdf_entry_names or load_pdf_entries(zip_bytes, self.settings)
        return self.process_zip_bytes(zip_bytes, excel_output, entries)

    def _process_entries(
        self,
        entries: Iterator[ZipPdfEntry],
        total: int,
        excel_output: Path,
        on_progress: ProgressCallback | None,
        should_cancel: CancelCheck | None,
    ) -> BatchProcessResult:
        exporter = ExcelExporter(excel_output, INVOICE_EXCEL_COLUMNS)
        outcomes: list[InvoiceProcessOutcome] = []
        succeeded = 0
        failed = 0

        logger.info(
            "Iniciando lote %s con detección automática — %d PDF(s)",
            self.retailer.label,
            total,
        )

        for index, entry in enumerate(entries, start=1):
            if should_cancel and should_cancel():
                raise JobCancelledError("Procesamiento cancelado por el usuario.")

            if on_progress:
                on_progress(index - 1, total, f"Clasificando: {entry.name}", succeeded, failed)

            outcome = self._process_single_pdf(entry, index, total, exporter)
            outcomes.append(outcome)

            if outcome.success:
                succeeded += 1
            else:
                failed += 1

            if on_progress:
                on_progress(index, total, entry.name, succeeded, failed)

        exporter.finalize()

        logger.info(
            "Lote finalizado (auto): %d/%d exitosos → %s",
            succeeded,
            total,
            excel_output,
        )
        return BatchProcessResult(
            total=total,
            succeeded=succeeded,
            failed=failed,
            excel_path=excel_output,
            outcomes=outcomes,
        )

    def _process_single_pdf(
        self,
        entry: ZipPdfEntry,
        index: int,
        total: int,
        exporter: ExcelExporter,
    ) -> InvoiceProcessOutcome:
        logger.info("[%d/%d] Procesando: %s", index, total, entry.name)
        invoice_format: InvoiceFormat | None = None
        try:
            invoice_format = classify_invoice_format(
                entry.data, self._client, self.retailer, self.settings
            )
            extractor = get_extractor(self.retailer, invoice_format)
            logger.info(
                "[%d/%d] Formato detectado: %s (%s)",
                index,
                total,
                invoice_format.value,
                entry.name,
            )
            data = extractor.extract(entry.data, self._client, self.settings)
            exporter.append_invoice(data)
            logger.info("Registrado NIC=%s", data.nic)
            return InvoiceProcessOutcome(
                filename=entry.name,
                success=True,
                nic=data.nic,
                format_detected=invoice_format.value,
                format_label=display_format_label(self.retailer, invoice_format),
            )
        except FormatDetectionError as exc:
            logger.warning("Formato no detectado en %s: %s", entry.name, exc)
            return InvoiceProcessOutcome(
                filename=entry.name,
                success=False,
                error=str(exc),
            )
        except Exception as exc:
            logger.exception("Falló %s", entry.name)
            return InvoiceProcessOutcome(
                filename=entry.name,
                success=False,
                error=str(exc),
                format_detected=invoice_format.value if invoice_format else None,
                format_label=(
                    display_format_label(self.retailer, invoice_format)
                    if invoice_format
                    else None
                ),
            )
