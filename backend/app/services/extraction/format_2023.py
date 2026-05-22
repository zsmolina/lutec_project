import fitz

from app.domain.enums import InvoiceFormat
from app.services.excel_exporter import ColumnConfig
from app.services.extraction.excel_columns import INVOICE_EXCEL_COLUMNS
from app.services.extraction.base import InvoiceExtractor
from app.services.extraction.pdf_utils import hd_matrix, pixmap_to_base64
from app.services.extraction.prompt_shared import AUDITOR_ROLE, NUMERIC_RULES

_ANCHOR_RULES_2023 = (
    "REGLAS DE ANCLAJE GENERAL 2023:\n"
    "1. IDENTIFICADORES FISCALES: Ubica las etiquetas 'Documento Equivalente:' y 'Fecha de Emisión:' en el recorte superior izquierdo y transcríbelas.\n"
    "2. NIC: Ubica la etiqueta 'NIC O CUENTA:' en el recorte superior derecho y extrae el número limpio.\n"
    "3. ENERGÍA MES Y TOTAL A PAGAR: Busca el gran recuadro de cobros. Jala el valor a la derecha de 'Energía' para Energía Mes y el valor a la derecha de 'Total Mes' para Total a Pagar.\n"
    "4. DATOS DE IDENTIDAD (ANÁLISIS MATRICIAL DE LA GRILLA DEL CLIENTE - RECORTE D):\n"
    "   - Para 'Titular de Pago': Ubica el rótulo literal 'Nombre:' y extrae el texto completo en MAYÚSCULAS.\n"
    "   - Para 'Estrato': Localiza 'Estrato/Clasificación:' y transcribe el valor dinámico real completo.\n"
    "   - Para 'Propiedad del Activo': Localiza 'Propiedad del Activo:' y extrae su casilla.\n"
    "5. INFORMACIÓN DE LECTURA: Extrae fechas, días facturados y factor múltiplo.\n"
    "6. INDICADORES DE CONSUMO: 'Consumo Calculado' como 'REAL' o 'ESTIMADO'. 'Promedio Día' para consumo diario.\n"
    "7. TARIFA (CU): En página 2 abajo a la izquierda, transcribe G, T, P, R, D, C y 'CU Aplicado:'."
)

_SYSTEM_PROMPT = AUDITOR_ROLE + NUMERIC_RULES + _ANCHOR_RULES_2023

class Extractor2023(InvoiceExtractor):
    format = InvoiceFormat.FORMAT_2023

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
            fitz.Rect(0, 0, w_p1 * 0.50, h_p1 * 0.25),
            fitz.Rect(w_p1 * 0.50, 0, w_p1, h_p1 * 0.25),
            fitz.Rect(w_p1 * 0.45, h_p1 * 0.15, w_p1, h_p1 * 0.45),
            fitz.Rect(0, h_p1 * 0.12, w_p1, h_p1 * 0.48),
            fitz.Rect(w_p1 * 0.40, h_p1 * 0.35, w_p1, h_p1 * 0.55),
            fitz.Rect(0, h_p1 * 0.50, w_p1, h_p1 * 0.85),
        ]
        for box in regions_p1:
            pix = p1.get_pixmap(matrix=matrix, clip=box, alpha=False)
            images.append(pixmap_to_base64(pix))

        if len(doc) > 1:
            p2 = doc[1]
            w_p2, h_p2 = p2.rect.width, p2.rect.height
            box_tarifa = fitz.Rect(0, h_p2 * 0.65, w_p2 * 0.45, h_p2)
            pix = p2.get_pixmap(matrix=matrix, clip=box_tarifa, alpha=False)
            images.append(pixmap_to_base64(pix))

        doc.close()
        return images
