"""Fachada de clasificación automática de formato por comercializador."""

from openai import OpenAI

from app.config import Settings
from app.domain.enums import EnergyRetailer, InvoiceFormat
from app.services.extraction.afinia.classifier import classify_afinia_format
from app.services.extraction.aire.classifier import classify_aire_format


def classify_invoice_format(
    pdf_bytes: bytes,
    client: OpenAI,
    retailer: EnergyRetailer,
    settings: Settings | None = None,
) -> InvoiceFormat:
    """Detecta el formato de extracción según comercializador y fecha de emisión."""
    if retailer is EnergyRetailer.AFINIA:
        return classify_afinia_format(pdf_bytes, client, settings)
    return classify_aire_format(pdf_bytes, client, settings)
