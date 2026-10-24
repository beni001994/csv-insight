"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from typing import Optional, Sequence

from . import __version__
from .stats import ColumnSummary, summarise_csv


def format_text(summaries: list[ColumnSummary]) -> str:
    blocks = []
    for s in summaries:
        lines = [f"{s.name} ({s.kind})", f"  values: {s.count}  missing: {s.missing}  unique: {s.unique}"]
        if s.kind == "numeric":
            lines.append(f"  min: {s.minimum:g}  max: {s.maximum:g}  mean: {s.mean:.2f}  median: {s.median:g}")
        elif s.top_values:
            top = ", ".join(f"{value} ({n})" for value, n in s.top_values)
            lines.append(f"  most common: {top}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csv-insight", description="Summarise the columns of a CSV file.")
    parser.add_argument("file", help="path to a CSV file, or - to read from standard input")
    parser.add_argument("-d", "--delimiter", default=",", help="field delimiter (default: ,)")
    parser.add_argument("--top", type=int, default=3, help="number of common values to show for text columns")
    parser.add_argument("--json", action="store_true", help="print the summary as JSON")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.file == "-":
            summaries = summarise_csv(sys.stdin, args.delimiter, args.top)
        else:
            with open(args.file, newline="", encoding="utf-8-sig") as handle:
                summaries = summarise_csv(handle, args.delimiter, args.top)
    except (OSError, ValueError) as err:
        print(f"csv-insight: error: {err}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps([asdict(s) for s in summaries], indent=2))
    else:
        print(format_text(summaries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
