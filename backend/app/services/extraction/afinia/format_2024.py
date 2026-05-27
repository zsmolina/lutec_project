"""Extractor Afinia — plantilla hoja única 2024 (alineado con extractor_afinia_test_2024.py)."""

import fitz

from app.domain.enums import InvoiceFormat
from app.domain.models.invoice_afinia import FacturaAfinia2024Data
from app.services.excel_exporter import ColumnConfig
from app.services.extraction.excel_columns import INVOICE_EXCEL_COLUMNS
from app.services.extraction.afinia.base import AfiniaInvoiceExtractor
from app.services.extraction.pdf_utils import hd_matrix, pixmap_to_base64

_SYSTEM_PROMPT = (
    "Actúas como un perito auditor senior de facturación eléctrica experto en el formato "
    "AFINIA de Hoja Única.\n"
    "Tu tarea única es transcribir textualmente los valores de las imágenes provistas, "
    "aplicando reglas estrictas.\n\n"
    "REGLAS INVIOLABLES DE EXTRACCIÓN DIRECTA:\n"
    "- ESTRATO / CLASIFICACIÓN: Ubícate en el bloque de DATOS DEL CLIENTE. Localiza de "
    "forma exacta la etiqueta o palabra clave 'CLASIFICACIÓN'. Debes extraer textualmente "
    "el contenido de la línea que está escrita justo abajo de ella. En esta estructura de "
    "Afinia, el valor literal impreso es 'Com (Sencilla Niv, 1) Carib' (o la clasificación "
    "técnica correspondiente). Queda estrictamente prohibido ignorar este campo, inventar, "
    "devolver solo un dígito suelto (ej: '4') o confundirlo con otro número del documento. "
    "Debe ser la cadena completa de clasificación técnica bajo 'CLASIFICACIÓN'.\n"
    "- ENERGÍA MES VALOR (REGLA DE NEGOCIO ESTRICTA): Busca el valor del consumo de energía "
    "líquida del mes. Este valor se encuentra más arriba en la sección o desglose detallado "
    "de consumos (por concepto de cantidad facturada de energía activa). Queda "
    "TERMINANTEMENTE PROHIBIDO tomar el valor de la celda que dice 'SUBTOTAL ENERGIA:'. "
    "Tu objetivo es el valor puro del consumo del mes, libre de otros subtotales.\n"
    "- TOTAL A PAGAR: Busca la etiqueta exacta 'TOTAL A PAGAR MES:' al final de la "
    "liquidación derecha y extrae ese número limpio.\n"
    "- NIC: Extrae los 7 dígitos bajo 'USE ESTE NUMERO PARA CONSULTAS NIC'.\n"
    "- DOCUMENTO EQUIVALENTE: Toma el número consecutivo de la franja 'DATOS DE FACTURA No.'.\n"
    "- PROPIEDAD DEL ACTIVO: Devuelve siempre cadena vacía: \"\".\n"
    "- TIPO DE CONSUMO CALCULADO: Toma el valor de la derecha de 'CÁLCULO DEL CONSUMO:' "
    "(ej: 'MEDICION').\n\n"
    "REGLAS DE FORMATEO NUMÉRICO:\n"
    "1. Quita signos de $, espacios y puntos de miles en campos monetarios "
    "(ej: '23.269.610,00' -> 23269610.00).\n"
    "2. Convierte las comas decimales de tarifas o promedios en puntos (ej: '31,50' -> 31.50).\n\n"
    "Escribe la salida respetando rigurosamente el formato JSON solicitado."
)


class AfiniaExtractor2024(AfiniaInvoiceExtractor):
    format = InvoiceFormat.FORMAT_2024
    _response_model = FacturaAfinia2024Data

    @property
    def excel_column_config(self) -> list[ColumnConfig]:
        return INVOICE_EXCEL_COLUMNS

    def system_prompt(self) -> str:
        return _SYSTEM_PROMPT

    def crop_pdf_regions(self, pdf_bytes: bytes) -> list[str]:
        """Recortes idénticos al script original (6 regiones, orden fijo)."""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        images: list[str] = []
        matrix = hd_matrix()

        p1 = doc[0]
        w_p1, h_p1 = p1.rect.width, p1.rect.height

        regions = [
            fitz.Rect(w_p1 * 0.50, 0, w_p1, h_p1 * 0.20),
            fitz.Rect(0, h_p1 * 0.11, w_p1 * 0.65, h_p1 * 0.60),
            fitz.Rect(w_p1 * 0.50, h_p1 * 0.12, w_p1, h_p1 * 0.35),
            fitz.Rect(w_p1 * 0.45, h_p1 * 0.35, w_p1, h_p1 * 0.85),
            fitz.Rect(0, h_p1 * 0.55, w_p1 * 0.50, h_p1 * 0.78),
            fitz.Rect(0, h_p1 * 0.72, w_p1 * 0.55, h_p1 * 0.98),
        ]
        for box in regions:
            pix = p1.get_pixmap(matrix=matrix, clip=box, alpha=False)
            images.append(pixmap_to_base64(pix))

        doc.close()
        return images
