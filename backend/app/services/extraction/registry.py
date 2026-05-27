from app.core.exceptions import UnsupportedFormatError
from app.domain.enums import EnergyRetailer, InvoiceFormat, formats_for_retailer
from app.services.extraction.afinia.format_2024 import AfiniaExtractor2024
from app.services.extraction.afinia.format_2025_2026 import AfiniaExtractor2025_2026
from app.services.extraction.base import InvoiceExtractor
from app.services.extraction.format_2023 import Extractor2023
from app.services.extraction.format_2024 import Extractor2024
from app.services.extraction.format_2025_2026 import Extractor2025_2026

_ExtractorKey = tuple[EnergyRetailer, InvoiceFormat]

_EXTRACTORS: dict[_ExtractorKey, InvoiceExtractor] = {
    (EnergyRetailer.AIRE, InvoiceFormat.FORMAT_2023): Extractor2023(),
    (EnergyRetailer.AIRE, InvoiceFormat.FORMAT_2024): Extractor2024(),
    (EnergyRetailer.AIRE, InvoiceFormat.FORMAT_2025_2026): Extractor2025_2026(),
    (EnergyRetailer.AFINIA, InvoiceFormat.FORMAT_2024): AfiniaExtractor2024(),
    (EnergyRetailer.AFINIA, InvoiceFormat.FORMAT_2025_2026): AfiniaExtractor2025_2026(),
}


def get_extractor(retailer: EnergyRetailer, invoice_format: InvoiceFormat) -> InvoiceExtractor:
    if invoice_format is InvoiceFormat.AUTO:
        raise UnsupportedFormatError("El formato AUTO no tiene extractor asociado.")
    extractor = _EXTRACTORS.get((retailer, invoice_format))
    if extractor is None:
        raise UnsupportedFormatError(
            f"Formato {invoice_format.value} no soportado para {retailer.label}."
        )
    return extractor


def list_supported_formats(retailer: EnergyRetailer | None = None) -> list[dict[str, str]]:
    retailers = [retailer] if retailer is not None else list(EnergyRetailer)
    result: list[dict[str, str]] = []
    for r in retailers:
        for fmt in formats_for_retailer(r):
            result.append(
                {
                    "retailer": r.value,
                    "retailer_label": r.label,
                    "id": fmt.value,
                    "label": fmt.label,
                }
            )
    return result


def list_supported_retailers() -> list[dict[str, object]]:
    return [
        {
            "id": retailer.value,
            "label": retailer.label,
            "formats": [
                {"id": fmt.value, "label": fmt.label}
                for fmt in formats_for_retailer(retailer)
            ],
        }
        for retailer in EnergyRetailer
    ]
