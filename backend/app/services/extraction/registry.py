from app.core.exceptions import UnsupportedFormatError
from app.domain.enums import InvoiceFormat
from app.services.extraction.base import InvoiceExtractor
from app.services.extraction.format_2023 import Extractor2023
from app.services.extraction.format_2024 import Extractor2024
from app.services.extraction.format_2025_2026 import Extractor2025_2026

_EXTRACTORS: dict[InvoiceFormat, InvoiceExtractor] = {
    InvoiceFormat.FORMAT_2023: Extractor2023(),
    InvoiceFormat.FORMAT_2024: Extractor2024(),
    InvoiceFormat.FORMAT_2025_2026: Extractor2025_2026(),
}


def get_extractor(invoice_format: InvoiceFormat) -> InvoiceExtractor:
    extractor = _EXTRACTORS.get(invoice_format)
    if extractor is None:
        raise UnsupportedFormatError(f"Formato no soportado: {invoice_format}")
    return extractor


def list_supported_formats() -> list[dict[str, str]]:
    return [
        {"id": fmt.value, "label": fmt.label}
        for fmt in InvoiceFormat
    ]
