"""Extractor Afinia — plantilla 2025/2026 (2 hojas PDF; alineado con extractor_afinia_test_2025-2026.py)."""

import logging

import fitz

from app.domain.enums import InvoiceFormat
from app.domain.models.invoice_afinia import FacturaAfinia2025_2026Data
from app.services.excel_exporter import ColumnConfig
from app.services.extraction.excel_columns import INVOICE_EXCEL_COLUMNS
from app.services.extraction.afinia.base import AfiniaInvoiceExtractor
from app.services.extraction.pdf_utils import hd_matrix, pixmap_to_base64

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Actúas como un perito auditor senior de facturación eléctrica experto en AFINIA (Grupo EPM).\n"
    "Transcribe con precisión matemática los datos de las imágenes segmentadas provistas.\n\n"
    "REGLAS DE FORMATEO NUMÉRICO INTERNACIONAL:\n"
    "1. Valores Moneda: Remueve signos de pesos, espacios y puntos de miles por completo "
    "(ej: '$ 11.353.190' -> 11353190.00).\n"
    "2. Valores Técnicos y Tarifas: El documento usa comas decimales. DEBES reemplazar la coma "
    "por punto decimal internacional (ej: '334,44' -> 334.44).\n\n"
    "REGLAS DE UBICACIÓN Y ANCLAJE VISUAL ESTRICTO:\n"
    "- NIC: Extrae los 7 dígitos de la etiqueta 'NIC.:' en la zona superior derecha de la Hoja 1. "
    "Ignora el NIU.\n"
    "- DOCUMENTO EQUIVALENTE: Toma el número consecutivo de 'Factura de Venta No.' o "
    "'Documento Equivalente No.' de la Hoja 1.\n"
    "- IDENTIDAD DEL TITULAR LEGAL: En la sección izquierda de la Hoja 1, localiza la etiqueta "
    "literal 'Titular de Pago'. El valor real está escrito INMEDIATAMENTE abajo o al lado de "
    "este rótulo en letras MAYÚSCULAS (ej: 'MUNICIPIO DE TOLUVIE').\n"
    "- ESTRATO / CLASIFICACIÓN (HOJA 1): Texto exacto del campo 'Estrato/Clasificación' en "
    "Datos del Usuario. Prohibido vacío.\n"
    "- PROPIEDAD DEL ACTIVO (HOJA 2): Extrae estrictamente la palabra limpia que define la "
    "propiedad de la grilla (ej. 'Particular', 'Cliente', 'Empresa'). Queda TERMINANTEMENTE "
    "PROHIBIDO incluir la palabra adyacente 'Medición' en este campo.\n"
    "- TIPO DE CONSUMO CALCULADO (LECTURA DINÁMICA - HOJA 2): Localiza el bloque de datos "
    "técnicos en la Hoja 2. Busca el texto escrito horizontalmente enfrente o al lado derecho "
    "de la celda de Propiedad del Activo (por ejemplo, si dice 'Empresa', mira enfrente y "
    "transcribe el valor exacto como 'MEDICIÓN' u otra tipificación que aparezca). No dejes "
    "este campo vacío ni quemado.\n"
    "- TOTAL A PAGAR (CORRECCIÓN DE NEGOCIO): Ubícate en el recuadro destacado superior derecho "
    "de la Hoja 1. Ignora la cifra del rótulo grande 'Total a Pagar:'. Debes extraer "
    "EXCLUSIVAMENTE el valor numérico asociado a la etiqueta 'Total mes' que se encuentra "
    "inmediatamente abajo (el cual refleja el cobro limpio del periodo sin saldos acumulados).\n"
    "- ENERGÍA MES VALOR (VALOR NETO ENERGÍA - REGLA INVIOLABLE):\n"
    "  Debes ir ÚNICAMENTE a la Hoja 1, localizar el recuadro titulado 'Resumen facturación mes' "
    "y extraer el valor numérico que está al lado derecho de la palabra literal 'Energía' "
    "(ej: de '$ 11.353.190' devuelves 11353190.00).\n"
    "  Queda PROHIBIDO extraer este campo del desglose o conceptos de la segunda hoja. Tu único "
    "anclaje es la palabra 'Energía' dentro de 'Resumen facturación mes' de la primera página.\n"
    "- LECTURAS (HOJA 2): Localiza el bloque 'Datos de lectura'. Extrae en la misma línea "
    "horizontal la Fecha de Lectura Anterior, Lectura Actual y Días Facturados. Extrae también "
    "el 'Factor' multiplicador.\n"
    "- GRÁFICA DE CONSUMO (HOJA 1 LADO IZQUIERDO): Localiza el histograma 'Consumo de los "
    "últimos 6 meses kWh'. Identifica la ULTIMA BARRA de la derecha y extrae el valor de "
    "consumo de este mes impreso justo debajo de ella. Justo abajo del gráfico localiza el "
    "promedio diario de consumo kWh ('Promedio día').\n"
    "- TARIFA COMPONENTES CU (HOJA 2 SECCIÓN REGULATORIA):\n"
    "  Localiza la tabla vertical titulada 'Costo unitario $/kWh'. Haz un mapeo por fila "
    "horizontal celda a celda:\n"
    "  * Sigla G o G: es generacion\n"
    "  * Sigla T o T: es transmision\n"
    "  * Sigla PR o PR: representa pérdidas (asígnase al campo perdidas)\n"
    "  * Sigla R o R: es restricciones\n"
    "  * Sigla D, D: o D es distribucion\n"
    "  * Sigla C o C: es comercializacion\n"
    "  * Sigla CU o CU: es el Costo Unitario Aplicado final cobrado ('cu_aplicado').\n\n"
    "Estructura la salida alineada rigurosamente al JSON solicitado."
)


class AfiniaExtractor2025_2026(AfiniaInvoiceExtractor):
    format = InvoiceFormat.FORMAT_2025_2026
    _response_model = FacturaAfinia2025_2026Data

    @property
    def excel_column_config(self) -> list[ColumnConfig]:
        return INVOICE_EXCEL_COLUMNS

    def system_prompt(self) -> str:
        return _SYSTEM_PROMPT

    def crop_pdf_regions(self, pdf_bytes: bytes) -> list[str]:
        """Recortes A–F idénticos al script original (Hoja 1 + Hoja 2 del PDF)."""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        images: list[str] = []
        matrix = hd_matrix()

        p1 = doc[0]
        w_p1, h_p1 = p1.rect.width, p1.rect.height

        regions_p1 = [
            fitz.Rect(w_p1 * 0.40, 0, w_p1, h_p1 * 0.30),
            fitz.Rect(0, h_p1 * 0.12, w_p1 * 0.35, h_p1 * 0.32),
            fitz.Rect(0, h_p1 * 0.25, w_p1, h_p1 * 0.55),
            fitz.Rect(0, h_p1 * 0.40, w_p1 * 0.65, h_p1 * 0.85),
        ]
        for box in regions_p1:
            pix = p1.get_pixmap(matrix=matrix, clip=box, alpha=False)
            images.append(pixmap_to_base64(pix))

        if len(doc) > 1:
            p2 = doc[1]
            w_p2, h_p2 = p2.rect.width, p2.rect.height
            regions_p2 = [
                fitz.Rect(0, p2.rect.height * 0.05, w_p2, p2.rect.height * 0.45),
                fitz.Rect(w_p2 * 0.30, p2.rect.height * 0.10, w_p2, p2.rect.height * 0.85),
            ]
            for box in regions_p2:
                pix = p2.get_pixmap(matrix=matrix, clip=box, alpha=False)
                images.append(pixmap_to_base64(pix))
        else:
            logger.warning(
                "PDF Afinia 2025/2026 con una sola página: faltan recortes de Hoja 2 "
                "(lecturas y costo unitario)."
            )

        doc.close()
        return images
