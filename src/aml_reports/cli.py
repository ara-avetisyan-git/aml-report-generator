"""Command-line interface: build the periodic report from CSV extracts."""
from __future__ import annotations

import argparse
from pathlib import Path

from . import quality
from .excel_report import build_summary, build_workbook
from .kpis import build_kpis
from .loaders import read_table
from .period import parse_period


def _cmd_build(args) -> int:
    start, end = parse_period(args.period)
    tables = {k: read_table(k, v) for k, v in
              (("alerts", args.alerts), ("customers", args.customers),
               ("screening", args.screening), ("training", args.training)) if v}
    if not tables:
        raise ValueError("Provide at least one input file (--alerts, --customers, --screening, --training)")

    issues: list[dict] = []
    if "alerts" in tables:
        issues += quality.check_alerts(tables["alerts"])
    if "customers" in tables:
        issues += quality.check_customers(tables["customers"])
    if "screening" in tables:
        issues += quality.check_screening(tables["screening"])
    issues += quality.check_cross(tables.get("alerts"), tables.get("customers"))

    kpis = build_kpis(start, end, **tables)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"aml_report_{args.period.replace(' ', '')}"
    xlsx, summary = out / f"{stem}.xlsx", out / f"{stem}.md"
    build_workbook(kpis, issues, args.period, args.entity, str(xlsx))
    summary.write_text(build_summary(kpis, issues, args.period, args.entity), encoding="utf-8")
    print(f"Report written: {xlsx}\nSummary written: {summary}\nData-quality findings: {len(issues)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aml-report", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("build", help="Build the Excel report and summary")
    p.add_argument("--period", required=True, help="e.g. 2026-Q3, 2026-09 or 2026")
    p.add_argument("--entity", default="Company")
    p.add_argument("--alerts")
    p.add_argument("--customers")
    p.add_argument("--screening")
    p.add_argument("--training")
    p.add_argument("--output-dir", default="outputs")
    p.set_defaults(func=_cmd_build)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}")
        return 2
