import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)


def cleanup_stale_files(directory: Path, max_age_hours: int) -> int:
    if not directory.exists():
        return 0

    cutoff = time.time() - (max_age_hours * 3600)
    removed = 0

    for path in directory.iterdir():
        if path.name == ".gitkeep":
            continue
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if mtime >= cutoff:
            continue
        if path.is_file():
            path.unlink(missing_ok=True)
            removed += 1
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file():
                    child.unlink(missing_ok=True)
            path.rmdir()
            removed += 1

    if removed:
        logger.info("Limpieza en %s: %d archivo(s) eliminado(s)", directory, removed)
    return removed
