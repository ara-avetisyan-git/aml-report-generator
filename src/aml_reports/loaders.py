"""Input files and their expected columns."""
from __future__ import annotations

import pandas as pd

SCHEMAS = {
    "alerts": {
        "required": ["alert_id", "rule_id", "severity", "customer_id", "opened_date", "status"],
        "optional": ["closed_date", "outcome", "analyst"],
        "dates": ["opened_date", "closed_date"],
    },
    "customers": {
        "required": ["customer_id", "final_level"],
        "optional": ["due_diligence", "next_review_date"],
        "dates": ["next_review_date"],
    },
    "screening": {
        "required": ["customer_id", "status"],
        "optional": ["disposition", "un_reference"],
        "dates": [],
    },
    "training": {
        "required": ["employee_id", "department", "completed"],
        "optional": ["course", "score"],
        "dates": [],
    },
}


def read_table(kind: str, path: str) -> pd.DataFrame:
    schema = SCHEMAS[kind]
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = [c for c in schema["required"] if c not in df.columns]
    if missing:
        raise ValueError(f"{kind}: missing required columns {missing} in {path}")
    for col in schema["dates"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col].replace("", pd.NA), errors="coerce")
    for col in ("status", "severity", "final_level", "outcome", "disposition", "completed"):
        if col in df.columns:
            df[col] = df[col].str.strip().str.lower()
    if "score" in df.columns:
        df["score"] = pd.to_numeric(df["score"].replace("", pd.NA), errors="coerce")
    return df
