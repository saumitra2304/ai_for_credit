"""
Deterministic flattening of probe24 company_details into a compact,
years-as-columns table.

Replaces the map/reduce LLM passes entirely. The extraction step was asking an
8B model to transcribe ~730 labelled numbers at ~7 tokens/sec; this does the
same job in microseconds and cannot hallucinate a digit.
"""

RATIOS = [
    "revenue_growth", "gross_profit_margin", "net_margin", "ebitda_margin",
    "return_on_equity", "return_on_capital_employed", "debt_ratio",
    "debt_by_equity", "interest_coverage_ratio", "current_ratio", "quick_ratio",
    "inventory_by_sales_days", "debtors_by_sales_days", "payables_by_sales_days",
    "cash_conversion_cycle", "sales_by_net_fixed_assets",
]

PNL = [
    "net_revenue", "total_cost_of_materials_consumed",
    "total_employee_benefit_expense", "total_other_expenses",
    "operating_profit", "other_income", "depreciation",
    "profit_before_interest_and_tax", "interest", "profit_before_tax",
    "income_tax", "profit_after_tax",
]

BS_ASSETS = [
    "tangible_assets", "noncurrent_investments", "inventories",
    "trade_receivables", "cash_and_bank_balances",
    "short_term_loans_and_advances", "other_current_assets",
]

BS_LIABILITIES = [
    "share_capital", "reserves_and_surplus", "long_term_borrowings",
    "short_term_borrowings", "trade_payables", "other_current_liabilities",
    "short_term_provisions", "long_term_provisions",
]

BS_SUBTOTALS = [
    "total_equity", "total_debt", "net_fixed_assets", "total_current_assets",
    "total_current_liabilities", "total_non_current_liabilities",
]

CASH_FLOW = [
    "cash_flows_from_used_in_operating_activities",
    "cash_flows_from_used_in_investing_activities",
    "cash_flows_from_used_in_financing_activities",
    "cash_flow_statement_at_end_of_period",
]

# Caps keep probe extras inside the LLM char budget (see open_ai.CHAR_BUDGET).
MAX_MSME_TREND_PERIODS = 4
MAX_MSME_SUPPLIERS = 15
MAX_LEGAL_CASES = 12
MAX_LEGAL_FIELD_CHARS = 50
MAX_DIRECTORS = 25
MAX_BOARD_EVENTS = 20
MAX_ALLOTMENTS = 8


def _fmt(v):
    """Blank for missing, plain integers where possible."""
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def _clip(text, max_len=MAX_LEGAL_FIELD_CHARS):
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def _legal_priority(case):
    score = 0
    if case.get("case_status") == "Pending":
        score += 1000
    severity = (case.get("severity") or "").lower()
    if severity == "high":
        score += 100
    elif severity == "medium":
        score += 50
    return (score, case.get("date") or "0000-01-01")


def flatten_msme_delays(data, max_trend=MAX_MSME_TREND_PERIODS,
                        max_suppliers=MAX_MSME_SUPPLIERS):
    """Compact MSME trend + latest-period supplier delays (bounded)."""
    msme = data.get("msme_supplier_payment_delays") or {}
    lines = []

    trend = msme.get("trend") or []
    if trend:
        lines.append("-- MSME PAYMENT DELAYS (trend) --")
        for period in trend[-max_trend:]:
            lines.append(
                f"{period.get('period')} | total due {_fmt(period.get('amount'))}"
            )

    delays_for_period = msme.get("delays_for_period") or {}
    supplier_delays = delays_for_period.get("delays") or []
    if delays_for_period or supplier_delays:
        lines.append("-- MSME SUPPLIER DELAYS (latest period) --")
        lines.append(
            f"Period {delays_for_period.get('latest_period')} | "
            f"total due {_fmt(delays_for_period.get('total_amount_due_for_period'))}"
        )
        ranked = sorted(
            supplier_delays,
            key=lambda row: row.get("amount_due") or 0,
            reverse=True,
        )
        for row in ranked[:max_suppliers]:
            lines.append(
                f"{_clip(row.get('supplier_name'), 60)} | "
                f"due {_fmt(row.get('amount_due'))} | "
                f"from {row.get('amount_due_from_date') or 'n/a'}"
            )
        omitted = len(supplier_delays) - max_suppliers
        if omitted > 0:
            lines.append(f"... {omitted} more suppliers not shown")

    return lines


def flatten_governance(data):
    """MCA board roster, role changes, allotments, and statutory filing dates.

    These live on company_details but were dropped from the financial table, so
    follow-ups about directors / governance / annual filings had nothing to cite.
    """
    lines = []
    signatories = [
        row for row in (data.get("authorized_signatories") or [])
        if isinstance(row, dict)
    ]
    if signatories:
        current = [s for s in signatories if not s.get("date_of_cessation")]
        ceased = [s for s in signatories if s.get("date_of_cessation")]
        lines.append(
            f"-- BOARD / SIGNATORIES -- current {len(current)} | ceased {len(ceased)}"
        )
        for person in current[:MAX_DIRECTORS]:
            lines.append(
                f"{person.get('name')} | {person.get('designation')} | "
                f"DIN {person.get('din') or 'n/a'} | "
                f"appointed {person.get('date_of_appointment') or 'n/a'} | "
                f"current role since "
                f"{person.get('date_of_appointment_for_current_designation') or 'n/a'}"
            )
        omitted = len(current) - MAX_DIRECTORS
        if omitted > 0:
            lines.append(f"... {omitted} more current directors not shown")
        for person in ceased[:8]:
            lines.append(
                f"{person.get('name')} | {person.get('designation')} | "
                f"ceased {person.get('date_of_cessation')} | "
                f"appointed {person.get('date_of_appointment') or 'n/a'}"
            )

        events = []
        for person in signatories:
            for ev in person.get("association_history") or []:
                if not isinstance(ev, dict):
                    continue
                date = ev.get("event_date") or ""
                if not date:
                    continue
                events.append((
                    date,
                    person.get("name"),
                    ev.get("designation_after_event") or person.get("designation"),
                    ev.get("event"),
                ))
        events.sort(key=lambda row: row[0], reverse=True)
        if events:
            lines.append("-- BOARD ROLE CHANGES (MCA association history) --")
            seen = set()
            kept = 0
            for date, name, desig, event in events:
                key = (date, name, desig)
                if key in seen:
                    continue
                seen.add(key)
                extra = f" | {event}" if event else ""
                lines.append(f"{date} | {name} | {desig}{extra}")
                kept += 1
                if kept >= MAX_BOARD_EVENTS:
                    break

    allotments = [
        row for row in (data.get("securities_allotment") or [])
        if isinstance(row, dict)
    ]
    if allotments:
        lines.append(f"-- SECURITIES ALLOTMENT -- {len(allotments)} records")
        for row in allotments[:MAX_ALLOTMENTS]:
            bits = [
                row.get("date") or row.get("allotment_date") or row.get("year"),
                row.get("instrument") or row.get("security_type"),
                row.get("particulars") or row.get("description"),
                row.get("number_of_shares") or row.get("shares"),
            ]
            line = " | ".join(str(bit) for bit in bits if bit)
            if line:
                lines.append(line)

    filing = data.get("filing_dates") or {}
    if isinstance(filing, dict) and filing:
        aoc = filing.get("aoc_4") or {}
        mgt = filing.get("mgt_7") or {}
        if aoc or mgt:
            lines.append(
                "-- STATUTORY FILING DATES -- "
                "(MCA AOC-4 / MGT-7, not the listed-company annual-report PDF)"
            )
            if isinstance(aoc, dict) and (aoc.get("financial_year") or aoc.get("filing_date")):
                lines.append(
                    f"AOC-4 financial statements | FY {aoc.get('financial_year')} | "
                    f"filed {aoc.get('filing_date')}"
                )
            if isinstance(mgt, dict) and (mgt.get("financial_year") or mgt.get("filing_date")):
                lines.append(
                    f"MGT-7 annual return | FY {mgt.get('financial_year')} | "
                    f"filed {mgt.get('filing_date')}"
                )
    return lines


def flatten_legal_history(data, max_cases=MAX_LEGAL_CASES):
    """Compact probe legal_history rows, prioritising pending/high-severity cases."""
    legal = data.get("legal_history") or []
    if not legal:
        return []

    pending = sum(1 for case in legal if case.get("case_status") == "Pending")
    severe = sum(
        1 for case in legal
        if (case.get("severity") or "").lower() in ("high", "medium")
    )
    lines = [
        "-- LITIGATION (Probe legal_history) -- "
        f"total {len(legal)} | pending {pending} | medium-or-high severity {severe}"
    ]

    ranked = sorted(legal, key=_legal_priority, reverse=True)
    for case in ranked[:max_cases]:
        lines.append(
            f"{case.get('date') or 'n/a'} | {case.get('case_status')} | "
            f"{case.get('severity')} | {_clip(case.get('court'), 40)} | "
            f"{case.get('case_number')} | {case.get('case_category')} | "
            f"{_clip(case.get('petitioner'))} v {_clip(case.get('respondent'))}"
        )

    omitted = len(legal) - max_cases
    if omitted > 0:
        lines.append(
            f"... {omitted} more cases not shown "
            "(pending / high-severity cases shown first)"
        )
    return lines


def _rows(label_prefix, keys, per_year, getter):
    """One row per key, one column per year."""
    lines = []
    for key in keys:
        cells = [_fmt(getter(per_year[y], key)) for y in per_year]
        if any(cells):  # drop rows that are empty across every year
            lines.append(f"{label_prefix}{key} | " + " | ".join(cells))
    return lines


def flatten_company(entry, nature="STANDALONE", years=("2025", "2024", "2023")):
    """
    Flatten one company into a compact pipe-delimited block.

    nature: keep only STANDALONE or only CONSOLIDATED. Keeping both doubles the
    payload for almost identical numbers -- in this dataset 2025 revenue is
    50,425,569,000 under both.
    """
    data = entry.get("data", {}) if isinstance(entry, dict) else {}
    company = data.get("company", {}) or {}
    financials = data.get("financials", []) or []

    # index the wanted years, newest first
    per_year = {}
    for y in years:
        for f in financials:
            if not isinstance(f, dict):
                continue
            if f.get("nature") != nature:
                continue
            if str(f.get("year", "")).startswith(y):
                per_year[y] = f
                break
    header = [
        f"COMPANY: {company.get('legal_name')} | CIN {company.get('cin')}",
        (
            f"Status {company.get('efiling_status')} | Incorporated "
            f"{company.get('incorporation_date')} | {company.get('classification')}"
        ),
        (
            f"Paid-up capital {_fmt(company.get('paid_up_capital'))} | "
            f"Authorized {_fmt(company.get('authorized_capital'))} | "
            f"Charges {_fmt(company.get('sum_of_charges'))}"
        ),
    ]
    governance = flatten_governance(data)
    if not per_year:
        return "\n".join(header + ([""] + governance if governance else []))

    out = list(header)
    out.append(f"Basis: {nature}. All figures INR absolute unless a ratio/percentage.")
    out.append("")
    out.append("METRIC | " + " | ".join(per_year.keys()))

    out.append("-- RATIOS --")
    out += _rows("", RATIOS, per_year, lambda f, k: (f.get("ratios") or {}).get(k))

    out.append("-- PROFIT AND LOSS --")
    out += _rows("", PNL, per_year,
                 lambda f, k: ((f.get("pnl") or {}).get("lineItems") or {}).get(k))

    out.append("-- BALANCE SHEET: ASSETS --")
    out += _rows("", BS_ASSETS, per_year,
                 lambda f, k: ((f.get("bs") or {}).get("assets") or {}).get(k))

    out.append("-- BALANCE SHEET: LIABILITIES --")
    out += _rows("", BS_LIABILITIES, per_year,
                 lambda f, k: ((f.get("bs") or {}).get("liabilities") or {}).get(k))

    out.append("-- BALANCE SHEET: SUBTOTALS --")
    out += _rows("", BS_SUBTOTALS, per_year,
                 lambda f, k: ((f.get("bs") or {}).get("subTotals") or {}).get(k))

    out.append("-- CASH FLOW --")
    out += _rows("", CASH_FLOW, per_year,
                 lambda f, k: (f.get("cash_flow") or {}).get(k))

    # Signals a credit analyst wants that live outside `financials`
    score = data.get("probe_financial_score") or {}
    if score:
        out.append("-- PROBE SCORES (1-5) --")
        out.append(" | ".join(f"{k}={v}" for k, v in score.items()))

    out.extend(flatten_msme_delays(data))
    out.extend(flatten_legal_history(data))

    ratings = data.get("credit_ratings") or []
    out.append(f"-- CREDIT RATINGS -- {'none on record' if not ratings else len(ratings)}")
    out.extend(governance)

    return "\n".join(out)


def flatten_all(filtered_results, nature="STANDALONE"):
    blocks = [flatten_company(e, nature=nature) for e in filtered_results]
    return "\n\n".join(b for b in blocks if b)