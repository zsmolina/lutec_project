"""Nombres de archivo de salida para descargas y exportaciones."""


def invoice_consolidated_filename(retailer_value: str, format_value: str) -> str:
    """Ej. Air-e auto → «Facturas Air-e Consolidadas.xlsx»."""
    retailer_label = {"aire": "Air-e", "afinia": "Afinia"}.get(
        retailer_value, retailer_value.capitalize()
    )
    if format_value in ("auto", ""):
        return f"Facturas {retailer_label} Consolidadas.xlsx"
    year_label = format_value.replace("_", "-")
    return f"Facturas {retailer_label} Consolidadas {year_label}.xlsx"


FORMAP_OUTPUT_FILENAME = "Informe Formap.xlsx"
