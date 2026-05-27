"""Clasificación automática de formato Afinia por año de emisión."""

from __future__ import annotations

import logging
from enum import Enum

import fitz
from openai import OpenAI
from pydantic import BaseModel, Field

from app.config import Settings, get_settings
from app.core.exceptions import FormatDetectionError
from app.domain.enums import InvoiceFormat
from app.services.extraction.pdf_utils import pixmap_to_base64

logger = logging.getLogger(__name__)

_FISCAL_CLIP_MATRIX = fitz.Matrix(2.0, 2.0)


class _FormatoAnioAfinia(str, Enum):
    ANIO_2024 = "2024"
    ANIO_2025_2026 = "2025-2026"
    DESCONOCIDO = "DESCONOCIDO"


class _ClasificacionAfiniaOutput(BaseModel):
    formato_detectado: _FormatoAnioAfinia = Field(
        description="Formato Afinia según año de Fecha de Emisión (2024 o 2025-2026)."
    )


_FORMATO_TO_INVOICE: dict[_FormatoAnioAfinia, InvoiceFormat] = {
    _FormatoAnioAfinia.ANIO_2024: InvoiceFormat.FORMAT_2024,
    _FormatoAnioAfinia.ANIO_2025_2026: InvoiceFormat.FORMAT_2025_2026,
}

_CLASSIFIER_PROMPT = (
    "Actúas como un perito auditor senior de documentos fiscales con precisión absoluta.\n"
    "Analiza la imagen provista del bloque fiscal de una factura de Afinia (Grupo EPM).\n\n"
    "REGLA DE EXTRACCIÓN FLEXIBLE (OCR ENFOQUE):\n"
    "1. Busca fechas en formato DD/MM/AAAA (emisión, factura o datos de factura).\n"
    "2. Identifica la fecha de emisión del documento.\n"
    "3. Extrae el año numérico de 4 dígitos.\n\n"
    "REGLAS DE CLASIFICACIÓN EXCLUSIVAS (AFINIA):\n"
    "- Año 2024 -> '2024'\n"
    "- Año 2025 o 2026 -> '2025-2026'\n"
    "- Cualquier otro año o indeterminado -> 'DESCONOCIDO'\n\n"
    "Afinia en este sistema solo admite plantillas 2024 y 2025/2026."
)


def _crop_fiscal_header_b64(pdf_bytes: bytes) -> str:
    """Recorte holgado de cabecera derecha/superior (emisión y datos de factura)."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        p1 = doc[0]
        w_p1, h_p1 = p1.rect.width, p1.rect.height
        box = fitz.Rect(w_p1 * 0.40, h_p1 * 0.02, w_p1, h_p1 * 0.38)
        pix = p1.get_pixmap(matrix=_FISCAL_CLIP_MATRIX, clip=box, alpha=False)
        return pixmap_to_base64(pix)
    finally:
        doc.close()


def classify_afinia_format(
    pdf_bytes: bytes,
    client: OpenAI,
    settings: Settings | None = None,
) -> InvoiceFormat:
    cfg = settings or get_settings()

    try:
        img_b64 = _crop_fiscal_header_b64(pdf_bytes)
    except Exception as exc:
        logger.exception("Error al recortar cabecera fiscal Afinia")
        raise FormatDetectionError(
            "No se pudo leer la cabecera del PDF para detectar el formato."
        ) from exc

    try:
        completion = client.beta.chat.completions.parse(
            model=cfg.openai_classifier_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": _CLASSIFIER_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"},
                        },
                    ],
                }
            ],
            response_format=_ClasificacionAfiniaOutput,
            temperature=cfg.openai_temperature,
        )
        detected = completion.choices[0].message.parsed.formato_detectado
    except Exception as exc:
        logger.exception("Error en clasificación Afinia")
        raise FormatDetectionError(
            "No se pudo clasificar el formato de la factura Afinia (error de IA)."
        ) from exc

    invoice_format = _FORMATO_TO_INVOICE.get(detected)
    if invoice_format is None:
        raise FormatDetectionError(
            "No se detectó un año de emisión compatible con Afinia (2024 o 2025/2026). "
            "Verifique que el PDF sea una factura Afinia legible."
        )

    return invoice_format
