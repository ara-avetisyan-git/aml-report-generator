"""Reporting period handling."""
from __future__ import annotations

import re

import pandas as pd


def parse_period(label: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    """'2026-Q3' -> (2026-07-01, 2026-09-30); '2026' -> full year; '2026-09' -> month."""
    label = label.strip().upper()
    if m := re.fullmatch(r"(\d{4})-Q([1-4])", label):
        year, q = int(m.group(1)), int(m.group(2))
        start = pd.Timestamp(year, 3 * (q - 1) + 1, 1)
        return start, start + pd.offsets.QuarterEnd(0)
    if m := re.fullmatch(r"(\d{4})-(\d{2})", label):
        start = pd.Timestamp(int(m.group(1)), int(m.group(2)), 1)
        return start, start + pd.offsets.MonthEnd(0)
    if m := re.fullmatch(r"(\d{4})", label):
        year = int(m.group(1))
        return pd.Timestamp(year, 1, 1), pd.Timestamp(year, 12, 31)
    raise ValueError(f"Cannot parse period '{label}'. Use e.g. 2026-Q3, 2026-09 or 2026.")
