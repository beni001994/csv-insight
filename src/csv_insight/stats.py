"""Column statistics for CSV data."""

from __future__ import annotations

import csv
import statistics
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, Optional


@dataclass
class ColumnSummary:
    name: str
    kind: str  # "numeric" or "text"
    count: int  # non-empty values
    missing: int
    unique: int
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    mean: Optional[float] = None
    median: Optional[float] = None
    top_values: list[tuple[str, int]] = field(default_factory=list)


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except ValueError:
        return None


def summarise_column(name: str, values: Iterable[str], top: int = 3) -> ColumnSummary:
    """Summarise one column. Empty strings count as missing values.

    A column is numeric when every non-empty value parses as a number.
    """
    raw = [v.strip() for v in values]
    present = [v for v in raw if v != ""]
    missing = len(raw) - len(present)
    numbers = [_to_float(v) for v in present]
    is_numeric = bool(present) and all(n is not None for n in numbers)

    summary = ColumnSummary(
        name=name,
        kind="numeric" if is_numeric else "text",
        count=len(present),
        missing=missing,
        unique=len(set(present)),
    )
    if is_numeric:
        nums = [n for n in numbers if n is not None]
        summary.minimum = min(nums)
        summary.maximum = max(nums)
        summary.mean = statistics.fmean(nums)
        summary.median = statistics.median(nums)
    else:
        summary.top_values = Counter(present).most_common(top)
    return summary


def summarise_csv(lines: Iterable[str], delimiter: str = ",", top: int = 3) -> list[ColumnSummary]:
    """Summarise every column of CSV text. The first row must be a header."""
    reader = csv.reader(lines, delimiter=delimiter)
    try:
        header = next(reader)
    except StopIteration:
        raise ValueError("CSV input is empty") from None

    columns: list[list[str]] = [[] for _ in header]
    for row in reader:
        for i in range(len(header)):
            columns[i].append(row[i] if i < len(row) else "")
    return [summarise_column(name, col, top) for name, col in zip(header, columns)]
