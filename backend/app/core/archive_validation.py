"""Validación de archivos ZIP y PDF para lotes de facturas."""

import zipfile
from io import BytesIO
from pathlib import PurePosixPath

from app.config import Settings
from app.core.exceptions import EmptyArchiveError, InvalidArchiveError

MACOSX_PREFIX = "__MACOSX/"


def _is_safe_zip_member(name: str) -> bool:
    if not name or name.startswith(MACOSX_PREFIX):
        return False
    path = PurePosixPath(name)
    return not path.is_absolute() and ".." not in path.parts


def _is_pdf_entry(name: str) -> bool:
    return name.lower().endswith(".pdf")


def _list_pdf_entries(zip_file: zipfile.ZipFile) -> list[str]:
    entries = [
        name
        for name in zip_file.namelist()
        if _is_safe_zip_member(name) and _is_pdf_entry(name)
    ]
    if not entries:
        raise EmptyArchiveError("El ZIP no contiene archivos PDF válidos.")
    return entries


def load_pdf_entries(zip_bytes: bytes, settings: Settings) -> list[str]:
    if len(zip_bytes) > settings.max_zip_size_bytes:
        raise InvalidArchiveError(
            f"El ZIP supera el tamaño máximo permitido ({settings.max_zip_size_mb} MB)."
        )

    try:
        with zipfile.ZipFile(BytesIO(zip_bytes)) as archive:
            if archive.testzip() is not None:
                raise InvalidArchiveError("El archivo ZIP está corrupto.")

            entries = _list_pdf_entries(archive)
            if len(entries) > settings.max_pdf_count:
                raise InvalidArchiveError(
                    f"El ZIP contiene demasiados PDFs (máximo {settings.max_pdf_count})."
                )

            for entry in entries:
                info = archive.getinfo(entry)
                if info.file_size > settings.max_pdf_size_bytes:
                    raise InvalidArchiveError(
                        f"El PDF '{entry}' supera el tamaño máximo "
                        f"({settings.max_pdf_size_mb} MB)."
                    )
            return entries
    except zipfile.BadZipFile as exc:
        raise InvalidArchiveError("El archivo no es un ZIP válido.") from exc


def validate_pdf_payload(pdf_bytes: bytes, settings: Settings, filename: str) -> None:
    if len(pdf_bytes) > settings.max_pdf_size_bytes:
        raise InvalidArchiveError(
            f"El PDF '{filename}' supera el tamaño máximo ({settings.max_pdf_size_mb} MB)."
        )
    if not pdf_bytes.startswith(b"%PDF"):
        raise InvalidArchiveError(f"El archivo '{filename}' no parece ser un PDF válido.")
