import fitz

from app.domain.enums import InvoiceFormat
from app.services.excel_exporter import ColumnConfig
from app.services.extraction.excel_columns import INVOICE_EXCEL_COLUMNS
from app.services.extraction.base import InvoiceExtractor
from app.services.extraction.pdf_utils import hd_matrix, pixmap_to_base64
from app.services.extraction.prompt_shared import AUDITOR_ROLE, NUMERIC_RULES

_ANCHOR_RULES_2024 = (
    "REGLAS DE ANCLAJE GENERAL:\n"
    "1. ESTRATO: Ubica 'Estrato/Clasificación:' y extrae toda la cadena a la derecha.\n"
    "2. PROPIEDAD DEL ACTIVO: Label 'Propiedad Activo:' en la tabla técnica de la primera página.\n"
    "3. ENERGÍA MES VALOR: Recuadro superior izquierdo, etiqueta 'Energía' (no Total Mes).\n"
    "4. FACTOR MULTIPLICADOR: Columna 'Mult.' en tabla de lectura del medidor.\n"
    "5. TIPO DE CONSUMO: 'REAL' o 'ESTIMADO' en mayúsculas.\n"
    "6. CONSUMO ACTUAL: Valor de la última barra derecha del histograma.\n"
    "7. TARIFA (CU): Página 2, tabla 'Componentes del Costo Unitario'."
)

_SYSTEM_PROMPT = AUDITOR_ROLE + NUMERIC_RULES + _ANCHOR_RULES_2024

class Extractor2024(InvoiceExtractor):
    format = InvoiceFormat.FORMAT_2024

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
            box_tarifa = fitz.Rect(0, h_p2 * 0.40, w_p2, h_p2)
            pix = p2.get_pixmap(matrix=matrix, clip=box_tarifa, alpha=False)
            images.append(pixmap_to_base64(pix))

        doc.close()
        return images
