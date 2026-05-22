"""Columnas del Excel consolidado de facturas (todos los formatos)."""

from app.services.excel_exporter import ColumnConfig

INVOICE_EXCEL_COLUMNS: list[ColumnConfig] = [
    ("NIC", "texto"),
    ("Documento Equivalente", "texto"),
    ("Fecha Emisión", "texto"),
    ("Titular del Pago", "texto"),
    ("Estrato", "texto"),
    ("Propiedad del Activo", "texto"),
    ("Total a Pagar", "moneda"),
    ("Energía Mes ($)", "moneda"),
    ("Factor Multiplicador", "decimal_dinamico"),
    ("Consumo Actual (kWh)", "entero_miles"),
    ("Tipo de Consumo Calculado", "texto"),
    ("Fecha Lectura Anterior", "texto"),
    ("Fecha Lectura Actual", "texto"),
    ("Mes", "texto"),
    ("Año", "texto"),
    ("Días Consumo", "entero"),
    ("Consumo Diario (kWh)", "decimal_fijo"),
    ("G (Generación)", "tarifa"),
    ("T (Transmisión)", "tarifa"),
    ("P (Pérdidas)", "tarifa"),
    ("R (Restricciones)", "tarifa"),
    ("D (Distribución)", "tarifa"),
    ("C (Comercialización)", "tarifa"),
    ("CU Aplicado", "tarifa"),
]
