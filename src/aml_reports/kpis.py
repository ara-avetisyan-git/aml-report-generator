"""KPI calculation for the reporting period."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class Kpis:
    period_start: pd.Timestamp
    period_end: pd.Timestamp
    headline: dict = field(default_factory=dict)
    alerts_by_rule: pd.DataFrame | None = None
    alerts_by_severity: pd.DataFrame | None = None
    alerts_by_outcome: pd.DataFrame | None = None
    customer_risk: pd.DataFrame | None = None
    screening: pd.DataFrame | None = None
    training: pd.DataFrame | None = None


def _count_table(series: pd.Series, name: str, order: list[str] | None = None) -> pd.DataFrame:
    counts = series.value_counts()
    if order:
        counts = counts.reindex(order, fill_value=0)
    table = counts.rename("count").rename_axis(name).reset_index()
    total = table["count"].sum()
    table["share"] = table["count"] / total if total else 0.0
    return table


def alert_kpis(alerts: pd.DataFrame, start, end, stale_days: int = 30) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    opened = alerts[(alerts["opened_date"] >= start) & (alerts["opened_date"] <= end)]
    closed = opened[opened["status"] == "closed"]
    timed = closed.dropna(subset=["closed_date"]) if "closed_date" in closed else closed.iloc[0:0]
    timed = timed[timed["closed_date"] >= timed["opened_date"]]
    days = (timed["closed_date"] - timed["opened_date"]).dt.days if len(timed) else pd.Series(dtype=float)

    still_open = opened[opened["status"].isin(["open", "escalated"])]
    stale = still_open[(end - still_open["opened_date"]).dt.days > stale_days]

    outcome = closed["outcome"] if "outcome" in closed else pd.Series(dtype=str)
    false_pos = int((outcome == "false_positive").sum())
    str_filed = int((outcome == "str_filed").sum())

    headline = {
        "Alerts opened in period": len(opened),
        "Alerts closed": len(closed),
        "Closure rate": len(closed) / len(opened) if len(opened) else 0.0,
        "Average days to close": float(days.mean()) if len(days) else None,
        "Median days to close": float(days.median()) if len(days) else None,
        f"Open alerts older than {stale_days} days": len(stale),
        "False-positive rate (closed)": false_pos / len(closed) if len(closed) else 0.0,
        "STRs filed": str_filed,
    }
    by_rule = _count_table(opened["rule_id"], "rule_id")
    by_sev = _count_table(opened["severity"], "severity", ["high", "medium", "low"])
    by_outcome = _count_table(outcome.replace("", "pending"), "outcome") if len(outcome) else pd.DataFrame(columns=["outcome", "count", "share"])
    return headline, by_rule, by_sev, by_outcome


def customer_kpis(customers: pd.DataFrame, end) -> tuple[dict, pd.DataFrame]:
    table = _count_table(customers["final_level"], "risk_level", ["low", "medium", "high"])
    overdue = 0
    if "next_review_date" in customers:
        overdue = int((customers["next_review_date"] < end).sum())
    high = int((customers["final_level"] == "high").sum())
    return {
        "Customers": len(customers),
        "High-risk customers": high,
        "High-risk share": high / len(customers) if len(customers) else 0.0,
        "Overdue periodic reviews": overdue,
    }, table


def screening_kpis(screening: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    per_customer = screening.assign(
        rank=screening["status"].map({"clear": 0, "review": 1, "potential match": 2})
    ).sort_values("rank").drop_duplicates("customer_id", keep="last")
    table = _count_table(per_customer["status"], "status", ["potential match", "review", "clear"])
    pending = 0
    if "disposition" in per_customer:
        hits = per_customer[per_customer["status"].isin(["review", "potential match"])]
        pending = int((hits["disposition"].isin(["", "pending"])).sum())
    return {
        "Customers screened": len(per_customer),
        "Potential matches": int((per_customer["status"] == "potential match").sum()),
        "Hits awaiting disposition": pending,
    }, table


def training_kpis(training: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    done = training["completed"].isin(["yes", "y", "true", "1"])
    by_dept = training.assign(done=done).groupby("department").agg(
        employees=("employee_id", "nunique"), completed=("done", "sum"),
        average_score=("score", "mean") if "score" in training else ("done", "mean"),
    ).reset_index()
    by_dept["completion_rate"] = by_dept["completed"] / by_dept["employees"]
    return {
        "Employees in scope": int(training["employee_id"].nunique()),
        "Training completion rate": float(done.mean()) if len(training) else 0.0,
    }, by_dept


def build_kpis(start, end, alerts=None, customers=None, screening=None, training=None) -> Kpis:
    k = Kpis(period_start=start, period_end=end)
    if alerts is not None:
        h, k.alerts_by_rule, k.alerts_by_severity, k.alerts_by_outcome = alert_kpis(alerts, start, end)
        k.headline.update(h)
    if customers is not None:
        h, k.customer_risk = customer_kpis(customers, end)
        k.headline.update(h)
    if screening is not None:
        h, k.screening = screening_kpis(screening)
        k.headline.update(h)
    if training is not None:
        h, k.training = training_kpis(training)
        k.headline.update(h)
    return k
