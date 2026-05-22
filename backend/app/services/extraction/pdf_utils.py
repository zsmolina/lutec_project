import base64
from io import BytesIO

import fitz


def pixmap_to_base64(pix: fitz.Pixmap) -> str:
    buffer = BytesIO(pix.tobytes("jpeg"))
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def hd_matrix(zoom: float = 4.5) -> fitz.Matrix:
    return fitz.Matrix(zoom, zoom)
