import zipfile
from collections.abc import Iterator
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from app.config import Settings
from app.core.archive_validation import load_pdf_entries, validate_pdf_payload


@dataclass(frozen=True)
class ZipPdfEntry:
    name: str
    data: bytes


def iter_pdfs_from_zip(
    zip_bytes: bytes,
    settings: Settings,
    pdf_entry_names: list[str] | None = None,
) -> Iterator[ZipPdfEntry]:
    entry_names = pdf_entry_names or load_pdf_entries(zip_bytes, settings)
    with zipfile.ZipFile(BytesIO(zip_bytes)) as archive:
        yield from _iter_pdf_entries(archive, entry_names, settings)


def iter_pdfs_from_zip_path(
    zip_path: Path,
    settings: Settings,
    pdf_entry_names: list[str],
) -> Iterator[ZipPdfEntry]:
    with zipfile.ZipFile(zip_path) as archive:
        yield from _iter_pdf_entries(archive, pdf_entry_names, settings)


def _iter_pdf_entries(
    archive: zipfile.ZipFile,
    entry_names: list[str],
    settings: Settings,
) -> Iterator[ZipPdfEntry]:
    for name in entry_names:
        data = archive.read(name)
        validate_pdf_payload(data, settings, name)
        yield ZipPdfEntry(name=name, data=data)
