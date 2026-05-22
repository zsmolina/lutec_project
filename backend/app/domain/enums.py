from enum import Enum


class InvoiceFormat(str, Enum):
    FORMAT_2023 = "2023"
    FORMAT_2024 = "2024"
    FORMAT_2025_2026 = "2025_2026"

    @property
    def label(self) -> str:
        labels = {
            InvoiceFormat.FORMAT_2023: "Factura 2023",
            InvoiceFormat.FORMAT_2024: "Factura 2024",
            InvoiceFormat.FORMAT_2025_2026: "Factura 2025/2026",
        }
        return labels[self]
