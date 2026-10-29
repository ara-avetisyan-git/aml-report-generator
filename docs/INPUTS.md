# Input files (CSV, UTF-8)

| File | Required columns | Optional columns |
|---|---|---|
| alerts | alert_id, rule_id, severity, customer_id, opened_date, status (open / closed / escalated) | closed_date, outcome (false_positive / no_action / str_filed), analyst |
| customers | customer_id, final_level (low / medium / high) | due_diligence, next_review_date |
| screening | customer_id, status (CLEAR / REVIEW / POTENTIAL MATCH) | disposition (false_positive / pending / ...), un_reference |
| training | employee_id, department, completed (yes / no) | course, score |

Dates use ISO format (YYYY-MM-DD). The columns line up with the output of the other tools in this portfolio
(`transaction-monitoring-rules`, `kyc-risk-scoring`, `sanctions-toolkit`).
