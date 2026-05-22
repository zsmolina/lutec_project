"""Cálculo de mes y año de facturación a partir de fechas de lectura."""

from __future__ import annotations

import re

_DATE_PARTS = re.compile(r"^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})$")

MONTH_LABELS_ES: tuple[str, ...] = (
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
)


def _normalize_year(year: int) -> int:
    if year < 100:
        return 2000 + year if year < 50 else 1900 + year
    return year


def _parse_month_year_parts(fecha_lectura_actual: str | None) -> tuple[int | None, int | None]:
    if fecha_lectura_actual is None:
        return None, None

    raw = str(fecha_lectura_actual).strip()
    if not raw:
        return None, None

    match = _DATE_PARTS.match(raw)
    if not match:
        return None, None

    try:
        month = int(match.group(2))
        year = _normalize_year(int(match.group(3)))
    except ValueError:
        return None, None

    if not 1 <= month <= 12:
        return None, None

    return month, year


def billing_period_from_reading_date(
    fecha_lectura_actual: str | None,
) -> tuple[str | None, str | None]:
    """
    Devuelve mes (nombre en español) y año (texto, ej. «2026») desde Fecha Lectura Actual.

    No consulta el PDF: solo interpreta el valor ya extraído (DD/MM/AAAA).
    """
    month, year = _parse_month_year_parts(fecha_lectura_actual)
    if month is None or year is None:
        return None, None
    return MONTH_LABELS_ES[month - 1], str(year)
