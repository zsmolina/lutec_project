from enum import Enum


class EnergyRetailer(str, Enum):
    AIRE = "aire"
    AFINIA = "afinia"

    @property
    def label(self) -> str:
        labels = {
            EnergyRetailer.AIRE: "Air-e",
            EnergyRetailer.AFINIA: "Afinia",
        }
        return labels[self]


class InvoiceFormat(str, Enum):
    AUTO = "auto"
    FORMAT_2023 = "2023"
    FORMAT_2024 = "2024"
    FORMAT_2025_2026 = "2025_2026"

    @property
    def label(self) -> str:
        labels = {
            InvoiceFormat.AUTO: "Detección automática",
            InvoiceFormat.FORMAT_2023: "Factura 2023",
            InvoiceFormat.FORMAT_2024: "Factura 2024",
            InvoiceFormat.FORMAT_2025_2026: "Factura 2025/2026",
        }
        return labels[self]

    @property
    def short_year_label(self) -> str:
        """Etiqueta corta de año para resúmenes (2023, 2024, 2025/2026)."""
        if self is InvoiceFormat.FORMAT_2025_2026:
            return "2025/2026"
        if self is InvoiceFormat.AUTO:
            return "auto"
        return self.value


def display_format_label(retailer: EnergyRetailer, invoice_format: InvoiceFormat) -> str:
    """Etiqueta legible combinando comercializador y formato detectado."""
    return f"{retailer.label} · {invoice_format.label}"


def formats_for_retailer(retailer: EnergyRetailer) -> tuple[InvoiceFormat, ...]:
    """Formatos de factura soportados por comercializador (sin AUTO)."""
    if retailer is EnergyRetailer.AFINIA:
        return (InvoiceFormat.FORMAT_2024, InvoiceFormat.FORMAT_2025_2026)
    return (
        InvoiceFormat.FORMAT_2023,
        InvoiceFormat.FORMAT_2024,
        InvoiceFormat.FORMAT_2025_2026,
    )
