# aml-report-generator

[![CI](https://github.com/ara-avetisyan-git/aml-report-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/ara-avetisyan-git/aml-report-generator/actions)

Automates the **periodic AML/CFT management report**: it reads CSV extracts (alerts, customer risk, screening results,
training), checks the data, calculates the KPIs for a chosen period and writes a formatted **Excel workbook with charts**
and a short **Markdown summary**.

## What it reports

- **Alerts:** opened / closed, closure rate, average and median days to close, open alerts older than 30 days,
  false-positive rate, STRs filed; breakdowns by rule, severity and outcome.
- **Customers:** risk-level distribution, high-risk share, overdue periodic reviews.
- **Screening:** customers screened, potential matches, hits awaiting disposition.
- **Training:** completion rate and average score by department.
- **Data quality:** duplicates, closed alerts without a closing date, dates in the wrong order, alerts for unknown
  customers, unknown status values. Findings are listed in the report, so figures are never presented without caveats.

## Install and run

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q

aml-report build --period 2026-Q3 --entity "Demo Company" \
  --alerts examples/alerts.csv --customers examples/customers.csv \
  --screening examples/screening.csv --training examples/training.csv \
  --output-dir outputs
```

Periods: `2026-Q3`, `2026-09` or `2026`. Every input is optional; the report contains what you provide.
Input columns are described in [docs/INPUTS.md](docs/INPUTS.md). The example files are synthetic and contain
a few deliberate data errors so the quality checks have something to find.

## Design choices

Figures are calculated from a clearly defined population (alerts *opened* in the period), invalid records are excluded
from timing metrics rather than silently corrected, and everything is reproducible from the input files.

## License

MIT. Author: Ara Avetisyan, AML/CFT compliance - [LinkedIn](https://www.linkedin.com/in/ara-avetisyan-1795802a)
