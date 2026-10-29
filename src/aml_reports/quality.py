"""Data-quality checks run before any figure is reported."""
from __future__ import annotations

import pandas as pd


def _issue(dataset: str, check: str, count: int, detail: str) -> dict:
    return {"dataset": dataset, "check": check, "records": count, "detail": detail}


def check_alerts(alerts: pd.DataFrame) -> list[dict]:
    issues = []
    dup = int(alerts["alert_id"].duplicated().sum())
    if dup:
        issues.append(_issue("alerts", "duplicate alert_id", dup, "Each alert must be unique"))
    no_open = int(alerts["opened_date"].isna().sum())
    if no_open:
        issues.append(_issue("alerts", "missing or invalid opened_date", no_open, "Excluded from period counts"))
    if "closed_date" in alerts:
        closed = alerts["status"].eq("closed")
        no_close = int((closed & alerts["closed_date"].isna()).sum())
        if no_close:
            issues.append(_issue("alerts", "closed alert without closed_date", no_close, "Excluded from timing metrics"))
        backwards = int((alerts["closed_date"] < alerts["opened_date"]).sum())
        if backwards:
            issues.append(_issue("alerts", "closed_date before opened_date", backwards, "Excluded from timing metrics"))
        stray = int((~closed & alerts["closed_date"].notna()).sum())
        if stray:
            issues.append(_issue("alerts", "closed_date on a non-closed alert", stray, "Check status field"))
    return issues


def check_customers(customers: pd.DataFrame) -> list[dict]:
    issues = []
    dup = int(customers["customer_id"].duplicated().sum())
    if dup:
        issues.append(_issue("customers", "duplicate customer_id", dup, "Latest record is not identifiable"))
    bad = int((~customers["final_level"].isin(["low", "medium", "high"])).sum())
    if bad:
        issues.append(_issue("customers", "unknown risk level", bad, "Expected low / medium / high"))
    if "next_review_date" in customers:
        missing = int(customers["next_review_date"].isna().sum())
        if missing:
            issues.append(_issue("customers", "missing next_review_date", missing, "Cannot test review timeliness"))
    return issues


def check_screening(screening: pd.DataFrame) -> list[dict]:
    issues = []
    unknown = int((~screening["status"].isin(["clear", "review", "potential match"])).sum())
    if unknown:
        issues.append(_issue("screening", "unknown status value", unknown, "Expected clear / review / potential match"))
    return issues


def check_cross(alerts: pd.DataFrame | None, customers: pd.DataFrame | None) -> list[dict]:
    if alerts is None or customers is None:
        return []
    orphans = int((~alerts["customer_id"].isin(customers["customer_id"])).sum())
    if orphans:
        return [_issue("alerts", "alert for unknown customer", orphans, "customer_id not found in customer file")]
    return []
