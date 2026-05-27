class LutecError(Exception):
    """Error base de la aplicación Lutec."""


class InvalidArchiveError(LutecError):
    """ZIP inválido, corrupto o que no cumple políticas de seguridad."""


class EmptyArchiveError(LutecError):
    """El archivo ZIP no contiene PDFs procesables."""


class UnsupportedFormatError(LutecError):
    """Formato de factura no registrado en el motor de extracción."""


class JobCancelledError(LutecError):
    """El trabajo de extracción fue cancelado por el usuario."""


class FormapConsolidationError(LutecError):
    """Error al consolidar un libro Excel Formap."""


class FormatDetectionError(LutecError):
    """No se pudo determinar el formato/año de la factura."""
