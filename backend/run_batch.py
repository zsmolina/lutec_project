from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.archive_validation import load_pdf_entries
from app.domain.enums import EnergyRetailer
from app.pipelines.batch_processor import BatchProcessor


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Procesar lote ZIP de facturas Lutec (detección automática de formato)"
    )
    parser.add_argument(
        "--retailer",
        default=EnergyRetailer.AIRE.value,
        choices=[item.value for item in EnergyRetailer],
        help="Comercializador (aire o afinia)",
    )
    parser.add_argument("--zip", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if not args.zip.is_file():
        print(f"ZIP no encontrado: {args.zip}", file=sys.stderr)
        return 1

    retailer = EnergyRetailer(args.retailer)
    zip_bytes = args.zip.read_bytes()
    processor = BatchProcessor(retailer)
    pdf_entries = load_pdf_entries(zip_bytes, processor.settings)
    result = processor.process_zip_bytes(zip_bytes, args.output, pdf_entries)

    print(f"\nComercializador: {retailer.label}")
    print(f"Total: {result.total} | Exitosos: {result.succeeded} | Fallidos: {result.failed}")
    print(f"Excel: {result.excel_path}")

    for outcome in result.outcomes:
        if outcome.success:
            print(f"  + {outcome.filename}: {outcome.format_label} (NIC {outcome.nic})")
        else:
            print(f"  - {outcome.filename}: {outcome.error}")

    return 0 if result.failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
