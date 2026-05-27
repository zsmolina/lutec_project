"""Clasificación automática de formato Air-e por año de emisión."""

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


class _FormatoAnioDetectado(str, Enum):
    ANIO_2023 = "2023"
    ANIO_2024 = "2024"
    ANIO_2025_2026 = "2025-2026"
    DESCONOCIDO = "DESCONOCIDO"


class _ClasificacionOutput(BaseModel):
    formato_detectado: _FormatoAnioDetectado = Field(
        description=(
            "Formato según el año de la Fecha de Emisión (2023, 2024, o 2025-2026)."
        )
    )


_FORMATO_TO_INVOICE: dict[_FormatoAnioDetectado, InvoiceFormat] = {
    _FormatoAnioDetectado.ANIO_2023: InvoiceFormat.FORMAT_2023,
    _FormatoAnioDetectado.ANIO_2024: InvoiceFormat.FORMAT_2024,
    _FormatoAnioDetectado.ANIO_2025_2026: InvoiceFormat.FORMAT_2025_2026,
}

_CLASSIFIER_PROMPT = (
    "Actúas como un perito auditor senior de documentos fiscales con precisión absoluta.\n"
    "Analiza la imagen provista del recuadro fiscal de una factura de Air-e.\n\n"
    "REGLA DE EXTRACCIÓN FLEXIBLE (OCR ENFOQUE):\n"
    "1. Busca en toda la imagen cualquier texto con formato de fecha (DD/MM/AAAA o similar).\n"
    "2. Identifica la fecha de emisión del documento (ignora resoluciones o textos legales).\n"
    "3. Extrae el año numérico de 4 dígitos de esa fecha de emisión.\n\n"
    "REGLAS DE CLASIFICACIÓN EXCLUSIVAS:\n"
    "- Año 2023 -> '2023'\n"
    "- Año 2024 -> '2024'\n"
    "- Año 2025 o 2026 -> '2025-2026'\n"
    "- Si no puedes determinar el año -> 'DESCONOCIDO'\n\n"
    "Tu única prioridad es el año numérico de la fecha."
)


def _crop_fiscal_header_b64(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        p1 = doc[0]
        w_p1, h_p1 = p1.rect.width, p1.rect.height
        box = fitz.Rect(w_p1 * 0.30, h_p1 * 0.02, w_p1, h_p1 * 0.36)
        pix = p1.get_pixmap(matrix=_FISCAL_CLIP_MATRIX, clip=box, alpha=False)
        return pixmap_to_base64(pix)
    finally:
        doc.close()


def classify_aire_format(
    pdf_bytes: bytes,
    client: OpenAI,
    settings: Settings | None = None,
) -> InvoiceFormat:
    cfg = settings or get_settings()

    try:
        img_b64 = _crop_fiscal_header_b64(pdf_bytes)
    except Exception as exc:
        logger.exception("Error al recortar cabecera fiscal Air-e")
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
            response_format=_ClasificacionOutput,
            temperature=cfg.openai_temperature,
        )
        detected = completion.choices[0].message.parsed.formato_detectado
    except Exception as exc:
        logger.exception("Error en clasificación Air-e")
        raise FormatDetectionError(
            "No se pudo clasificar el formato de la factura (error de IA)."
        ) from exc

    invoice_format = _FORMATO_TO_INVOICE.get(detected)
    if invoice_format is None:
        raise FormatDetectionError(
            "No se detectó el año de emisión en la factura. "
            "Verifique que el PDF sea una factura Air-e legible."
        )

    return invoice_format
