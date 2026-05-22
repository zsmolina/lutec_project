import fitz

from app.domain.enums import InvoiceFormat
from app.services.excel_exporter import ColumnConfig
from app.services.extraction.excel_columns import INVOICE_EXCEL_COLUMNS
from app.services.extraction.base import InvoiceExtractor
from app.services.extraction.pdf_utils import hd_matrix, pixmap_to_base64

_SYSTEM_PROMPT = (
    "Actúas como un perito auditor senior de facturación eléctrica. Tu objetivo es transcribir "
    "con precisión matemática absoluta los datos de las imágenes provistas.\n\n"
    "REGLAS DE TRADUCCIÓN NUMÉRICA DIFERENCIADAS (ESTRICTO):\n"
    "1. PARA VALORES DE MONEDA (Total a Pagar y Energía Mes):\n"
    "   - Son valores en MILLONES de pesos. Remueve todos los puntos para formar el entero de millones.\n"
    "   - EJEMPLO: '33.613.960' → 33613960.00.\n\n"
    "2. PARA CONSUMO DIARIO, CONSUMO ACTUAL Y FACTOR MULTIPLICADOR:\n"
    "   - EJEMPLO consumo actual '92.400' o '92400' → 92400.0. Prohibido truncar a 92.4.\n"
    "   - EJEMPLO consumo diario '2.457,93' → 2457.93.\n\n"
    "REGLAS DE ANCLAJE GENERAL:\n"
    "1. ESTRATO: Celda 'Estrato/Clasificación:'.\n"
    "2. PROPIEDAD DEL ACTIVO: Label 'Propiedad del Activo:'.\n"
    "3. ENERGÍA MES: Etiqueta 'Energía' en recuadro superior izquierdo.\n"
    "4. FACTOR MULTIPLICADOR: Columna 'Mult.'.\n"
    "5. TIPO DE CONSUMO: 'REAL' o 'ESTIMADO'.\n"
    "6. CONSUMO ACTUAL: Cifra entera de la última barra del histograma.\n"
    "7. TARIFA (CU): Página 2, tabla 'TARIFA DE ENERGÍA'."
)

class Extractor2025_2026(InvoiceExtractor):
    format = InvoiceFormat.FORMAT_2025_2026

    @property
    def excel_column_config(self) -> list[ColumnConfig]:
        return INVOICE_EXCEL_COLUMNS

    def system_prompt(self) -> str:
        return _SYSTEM_PROMPT

    def crop_pdf_regions(self, pdf_bytes: bytes) -> list[str]:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        images: list[str] = []
        matrix = hd_matrix()

        p1 = doc[0]
        w_p1, h_p1 = p1.rect.width, p1.rect.height

        regions_p1 = [
            fitz.Rect(w_p1 * 0.50, 0, w_p1, h_p1 * 0.25),
            fitz.Rect(0, h_p1 * 0.20, w_p1, h_p1 * 0.60),
            fitz.Rect(0, h_p1 * 0.55, w_p1, h_p1),
        ]
        for box in regions_p1:
            pix = p1.get_pixmap(matrix=matrix, clip=box, alpha=False)
            images.append(pixmap_to_base64(pix))

        if len(doc) > 1:
            p2 = doc[1]
            w_p2, h_p2 = p2.rect.width, p2.rect.height
            box_tarifa = fitz.Rect(w_p2 * 0.35, h_p2 * 0.60, w_p2, h_p2)
            pix = p2.get_pixmap(matrix=matrix, clip=box_tarifa, alpha=False)
            images.append(pixmap_to_base64(pix))

        doc.close()
        return images
