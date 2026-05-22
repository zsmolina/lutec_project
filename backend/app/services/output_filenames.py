"""Nombres de archivo de salida para descargas y exportaciones."""


def invoice_consolidated_filename(format_value: str) -> str:
    """Ej. formato 2023 → «Facturas Consolidadas 2023.xlsx»."""
    year_label = (format_value or "facturas").replace("_", "-")
    return f"Facturas Consolidadas {year_label}.xlsx"


FORMAP_OUTPUT_FILENAME = "Informe Formap.xlsx"
