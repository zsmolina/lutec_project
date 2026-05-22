"""CLI: consolidar Excel Formap desde backend."""

import argparse
import sys
from pathlib import Path

from app.services.formap_consolidator import consolidate_formap_workbook


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", required=True, help="Excel Formap de entrada")
    parser.add_argument("--output", "-o", required=True, help="Excel unificado de salida")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: no existe {input_path}", file=sys.stderr)
        return 1

    output_path = Path(args.output)
    output_path.write_bytes(consolidate_formap_workbook(input_path.read_bytes()))
    print(f"Guardado: {output_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
