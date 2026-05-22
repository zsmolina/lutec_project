from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.archive_validation import load_pdf_entries
from app.domain.enums import InvoiceFormat
from app.pipelines.batch_processor import BatchProcessor


def main() -> int:
    parser = argparse.ArgumentParser(description="Procesar lote ZIP de facturas Lutec")
    parser.add_argument(
        "--format",
        required=True,
        choices=[item.value for item in InvoiceFormat],
    )
    parser.add_argument("--zip", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if not args.zip.is_file():
        print(f"ZIP no encontrado: {args.zip}", file=sys.stderr)
        return 1

    zip_bytes = args.zip.read_bytes()
    processor = BatchProcessor(InvoiceFormat(args.format))
    pdf_entries = load_pdf_entries(zip_bytes, processor.settings)
    result = processor.process_zip_bytes(zip_bytes, args.output, pdf_entries)

    print(f"\nFormato: {result.format.label}")
    print(f"Total: {result.total} | Exitosos: {result.succeeded} | Fallidos: {result.failed}")
    print(f"Excel: {result.excel_path}")

    for outcome in result.outcomes:
        if not outcome.success:
            print(f"  - {outcome.filename}: {outcome.error}")

    return 0 if result.failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
