"""Full credit + distress section dump for the credit agent."""

import json

from financial_flatten import _fmt

CREDIT_FIELDS = (
    "credit_ratings",
    "credit_rating_rationale",
    "unaccepted_rating",
    "defaulter_list",
    "bifr_history",
    "cdr_history",
    "struckoff248_details",
    "key_indicators",
    "legal_cases_of_financial_disputes",
)


def _latest_debt(data):
    financials = data.get("financials") or []
    latest = None
    for f in financials:
        if not isinstance(f, dict) or f.get("nature") != "STANDALONE":
            continue
        if latest is None or str(f.get("year", "")) > str(latest.get("year", "")):
            latest = f
    if not latest:
        return None
    bs = latest.get("bs") or {}
    return {
        "year": latest.get("year"),
        "total_debt": ((bs.get("subTotals") or {}).get("total_debt")),
        "long_term_borrowings": ((bs.get("liabilities") or {}).get("long_term_borrowings")),
        "short_term_borrowings": ((bs.get("liabilities") or {}).get("short_term_borrowings")),
    }


def flatten_credit(entry):
    data = entry.get("data", {}) if isinstance(entry, dict) else {}
    company = data.get("company") or {}

    block = {
        "company": {
            "legal_name": company.get("legal_name"),
            "cin": company.get("cin"),
            "efiling_status": company.get("efiling_status"),
            "sum_of_charges": company.get("sum_of_charges"),
        },
        "latest_standalone_debt": _latest_debt(data),
    }
    for field in CREDIT_FIELDS:
        block[field] = data.get(field)

    return json.dumps(block, indent=2, default=str)
