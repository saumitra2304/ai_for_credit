import io
import re

CRORE = 10_000_000
LAKH = 100_000

_BLUE = "#2563eb"
_TEAL = "#0d9488"
_AMBER = "#d97706"
_SLATE = "#334155"
_MUTED = "#64748b"
_GRID = "#e2e8f0"
_FACE = "#f8fafc"
_INK = "#0f172a"


def _year_label(value):
    if not value:
        return ""
    match = re.match(r"^(\d{4})", str(value))
    return match.group(1) if match else str(value)


def _num(value):
    if value is None or value == "":
        return None
    try:
        n = float(value)
    except (TypeError, ValueError):
        return None
    return n if n == n else None


def crore(value):
    n = _num(value)
    if n is None:
        return None
    return round(n / CRORE, 2)


def _group_en_in(value, max_frac=2):
    rounded = round(float(value), max_frac)
    if rounded == int(rounded):
        whole = str(int(abs(rounded)))
        frac = ""
    else:
        text = f"{abs(rounded):.{max_frac}f}".rstrip("0").rstrip(".")
        if "." in text:
            whole, frac_part = text.split(".", 1)
            frac = "." + frac_part
        else:
            whole, frac = text, ""
    sign = "-" if rounded < 0 else ""
    if len(whole) <= 3:
        return sign + whole + frac
    last3 = whole[-3:]
    rest = whole[:-3]
    chunks = []
    while rest:
        chunks.append(rest[-2:])
        rest = rest[:-2]
    grouped = list(reversed(chunks)) + [last3]
    return sign + ",".join(grouped) + frac


def format_inr_compact(value):
    n = _num(value)
    if n is None:
        return "—"
    abs_n = abs(n)
    sign = "-" if n < 0 else ""
    if abs_n >= CRORE:
        return f"{sign}Rs {_group_en_in(abs_n / CRORE)} crore"
    if abs_n >= LAKH:
        return f"{sign}Rs {_group_en_in(abs_n / LAKH)} lakh"
    return f"{sign}Rs {_group_en_in(abs_n)}"


def _standalone_years(financials):
    rows = [
        row
        for row in (financials or [])
        if isinstance(row, dict) and (row.get("nature") or "STANDALONE") == "STANDALONE"
    ]
    rows.sort(key=lambda row: str(row.get("year") or ""))
    return rows


def standalone_year_labels(payload) -> tuple[str, ...]:
    data = (payload or {}).get("data") or payload or {}
    labels = []
    for row in _standalone_years(data.get("financials")):
        year = _year_label(row.get("year"))
        if year and year not in labels:
            labels.append(year)
    labels.sort(reverse=True)
    return tuple(labels[:6]) or ("2025", "2024", "2023")


def _peer_name(peer):
    raw = peer.get("legalName") or peer.get("legal_name") or "Peer"
    return re.sub(r" PRIVATE LIMITED| LIMITED", "", raw, flags=re.I).strip() or raw


def extract_memo_charts(payload):
    data = (payload or {}).get("data") or payload or {}
    company = data.get("company") or {}
    financials = _standalone_years(data.get("financials"))

    pnl = []
    balance_sheet = []
    cash_flow = []
    margins = []
    for row in financials:
        items = ((row.get("pnl") or {}).get("lineItems") or {})
        sub = ((row.get("bs") or {}).get("subTotals") or {})
        ratios = row.get("ratios") or {}
        cf = row.get("cash_flow") or {}
        year = _year_label(row.get("year"))
        pnl.append(
            {
                "year": year,
                "revenue": crore(items.get("net_revenue")),
                "pat": crore(items.get("profit_after_tax")),
            }
        )
        balance_sheet.append(
            {
                "year": year,
                "equity": crore(sub.get("total_equity")),
                "debt": crore(sub.get("total_debt")),
            }
        )
        cash_flow.append(
            {
                "year": year,
                "operating": crore(cf.get("cash_flows_from_used_in_operating_activities")),
                "investing": crore(cf.get("cash_flows_from_used_in_investing_activities")),
                "financing": crore(cf.get("cash_flows_from_used_in_financing_activities")),
            }
        )
        margins.append(
            {
                "year": year,
                "ebitda": _num(ratios.get("ebitda_margin")),
                "net": _num(ratios.get("net_margin")),
            }
        )

    peer_block = (data.get("peer_comparison") or [{}])[0] or {}
    peers = []
    for peer in peer_block.get("peers") or []:
        revenue = crore(peer.get("revenue"))
        if revenue is None:
            continue
        peers.append(
            {
                "name": _peer_name(peer),
                "legal_name": peer.get("legalName") or peer.get("legal_name") or _peer_name(peer),
                "cin": str(peer.get("cin") or "").strip().upper(),
                "revenue": revenue,
            }
        )
    peers.sort(key=lambda row: row["revenue"], reverse=True)
    peers = peers[:8]

    bench = (peer_block.get("benchMarks") or peer_block.get("benchmarks") or [{}])[0] or {}
    peer_bench = [
        {
            "metric": "Net margin",
            "company": _num(bench.get("net_margin")),
            "median": _num(bench.get("median_net_margin")),
        },
        {
            "metric": "EBITDA",
            "company": _num(bench.get("ebitda_margin")),
            "median": _num(bench.get("median_ebitda_margin")),
        },
        {
            "metric": "ROE",
            "company": _num(bench.get("return_on_equity")),
            "median": _num(bench.get("median_return_on_equity")),
        },
    ]
    peer_bench = [row for row in peer_bench if row["company"] is not None or row["median"] is not None]

    return {
        "company_name": company.get("legal_name") or "Company",
        "cin": company.get("cin") or "",
        "pnl": pnl,
        "balance_sheet": balance_sheet,
        "cash_flow": cash_flow,
        "margins": margins,
        "peers": peers,
        "peer_bench": peer_bench,
    }


def select_peer_cins_from_charts(chart_sets, exclude=(), limit=3):
    """Top Probe peer-revenue CINs, same ranking as the Show charts peer bars."""
    from memo_attachments import parse_extra_cins

    blocked = {str(cin).strip().upper() for cin in exclude if cin}
    ranked = []
    for charts in chart_sets or []:
        for peer in charts.get("peers") or []:
            parsed = parse_extra_cins(peer.get("cin") or "")
            if not parsed:
                continue
            cin = parsed[0]
            if cin in blocked:
                continue
            ranked.append((peer.get("revenue") or 0, cin))
    ranked.sort(key=lambda row: row[0], reverse=True)
    out = []
    seen = set()
    for _, cin in ranked:
        if cin in seen:
            continue
        seen.add(cin)
        out.append(cin)
        if len(out) >= max(0, int(limit)):
            break
    return out


def select_peer_cins(payload, exclude=(), limit=3):
    return select_peer_cins_from_charts(
        [extract_memo_charts(payload)], exclude=exclude, limit=limit
    )


def flatten_memo_extras(payload) -> str:
    data = (payload or {}).get("data") or payload or {}
    lines = []

    peer_block = (data.get("peer_comparison") or [{}])[0] or {}
    peers = peer_block.get("peers") or []
    if peers:
        lines.append("-- PEER COMPARISON (Probe) --")
        ranked = []
        for peer in peers:
            if not isinstance(peer, dict):
                continue
            ranked.append(
                (
                    _peer_name(peer),
                    peer.get("revenue"),
                    str(peer.get("cin") or "").strip().upper(),
                )
            )
        ranked.sort(key=lambda row: row[1] or 0, reverse=True)
        for name, revenue, cin in ranked[:10]:
            suffix = f" | CIN {cin}" if cin else ""
            lines.append(f"{name} | revenue {revenue}{suffix}")
        bench = (peer_block.get("benchMarks") or peer_block.get("benchmarks") or [{}])[0] or {}
        if isinstance(bench, dict) and bench:
            lines.append("-- VS INDUSTRY MEDIAN --")
            for key, median_key, label in (
                ("net_margin", "median_net_margin", "net margin"),
                ("ebitda_margin", "median_ebitda_margin", "EBITDA margin"),
                ("return_on_equity", "median_return_on_equity", "ROE"),
                ("return_on_capital_employed", "median_return_on_capital_employed", "ROCE"),
                ("current_ratio", "median_current_ratio", "current ratio"),
            ):
                company = bench.get(key)
                median = bench.get(median_key)
                if company is None and median is None:
                    continue
                lines.append(f"{label} | company {company} | industry median {median}")

    related = data.get("related_party_transactions") or []
    if related:
        latest = sorted(related, key=lambda row: str(row.get("financial_year") or ""), reverse=True)[0]
        parties = latest.get("company") or []
        if parties:
            lines.append(
                f"-- RELATED PARTIES -- FY {latest.get('financial_year')} "
                f"({len(parties)} counterparties)"
            )
            ranked = sorted(
                [p for p in parties if isinstance(p, dict)],
                key=lambda row: row.get("amount") or 0,
                reverse=True,
            )
            for party in ranked[:10]:
                lines.append(
                    f"{party.get('legal_name') or party.get('name')} | "
                    f"{party.get('type_of_transaction')} | amount {party.get('amount')}"
                )

    holders = data.get("shareholdings_more_than_five_percent") or []
    if holders:
        latest = sorted(holders, key=lambda row: str(row.get("financial_year") or ""), reverse=True)[0]
        lines.append(f"-- SHAREHOLDING >5% -- FY {latest.get('financial_year')}")
        for bucket in ("company", "llp", "individual", "others"):
            for row in latest.get(bucket) or []:
                if not isinstance(row, dict):
                    continue
                lines.append(
                    f"{row.get('name')} | {row.get('shareholding_percentage')}% | {bucket}"
                )

    return "\n".join(lines)


def _apply_style(ax, title, ylabel):
    ax.set_title("")
    ax.set_ylabel(ylabel, fontsize=9, color=_MUTED)
    ax.tick_params(colors=_MUTED, labelsize=8, length=0)
    ax.grid(axis="y", linestyle="-", linewidth=0.7, color=_GRID)
    ax.set_axisbelow(True)
    ax.set_facecolor(_FACE)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(_GRID)
    ax.spines["bottom"].set_color(_GRID)


def _value_formatter(ax, axis="y"):
    from matplotlib.ticker import FuncFormatter

    fmt = FuncFormatter(lambda v, _p: _group_en_in(v, 1) if isinstance(v, (int, float)) else str(v))
    if axis == "x":
        ax.xaxis.set_major_formatter(fmt)
    else:
        ax.yaxis.set_major_formatter(fmt)


def _png_from_axes(draw_fn):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans", "sans-serif"],
            "axes.edgecolor": "#e2e8f0",
            "axes.linewidth": 0.8,
        }
    )
    fig, ax = plt.subplots(figsize=(8.0, 3.7), dpi=180, facecolor="#ffffff")
    draw_fn(ax)
    fig.tight_layout(pad=0.7)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor="#ffffff", bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def _grouped_bars(ax, years, series, ylabel, title):
    import numpy as np

    idx = np.arange(len(years))
    n = max(len(series), 1)
    width = min(0.72 / n, 0.26)
    offset = (n - 1) * width / 2
    palette = [_BLUE, _TEAL, _AMBER]
    for i, (label, values) in enumerate(series):
        ax.bar(
            idx - offset + i * width,
            [v or 0 for v in values],
            width,
            label=label,
            color=palette[i % len(palette)],
            linewidth=0,
            zorder=3,
        )
    ax.set_xticks(list(idx), years)
    ax.legend(frameon=False, fontsize=8, loc="upper left", ncol=min(3, n))
    _apply_style(ax, title, ylabel)
    _value_formatter(ax, "y")


def chart_pngs(charts: dict) -> list[tuple[str, bytes]]:
    images = []
    pnl = [row for row in (charts.get("pnl") or []) if row.get("year")]
    if pnl:
        years = [row["year"] for row in pnl]
        revenue = [row.get("revenue") or 0 for row in pnl]
        pat = [row.get("pat") or 0 for row in pnl]

        def draw(ax):
            xs = list(range(len(years)))
            ax.plot(xs, revenue, color=_BLUE, marker="o", markersize=4.5, linewidth=2.4, label="Revenue")
            ax.fill_between(xs, revenue, color=_BLUE, alpha=0.08)
            ax.plot(xs, pat, color=_TEAL, marker="o", markersize=4.5, linewidth=2.4, label="PAT")
            ax.set_xticks(xs, years)
            ax.legend(frameon=False, fontsize=8, loc="upper left")
            _apply_style(ax, "Revenue and PAT", "Rs crore")
            _value_formatter(ax, "y")

        images.append(("Revenue and PAT (Rs crore)", _png_from_axes(draw)))

    sheet = [row for row in (charts.get("balance_sheet") or []) if row.get("year")]
    if sheet:
        years = [row["year"] for row in sheet]

        def draw(ax):
            _grouped_bars(
                ax,
                years,
                [
                    ("Equity", [row.get("equity") or 0 for row in sheet]),
                    ("Debt", [row.get("debt") or 0 for row in sheet]),
                ],
                "Rs crore",
                "Equity vs debt",
            )

        images.append(("Equity vs debt (Rs crore)", _png_from_axes(draw)))

    flows = [row for row in (charts.get("cash_flow") or []) if row.get("year")]
    if any((row.get("operating") or row.get("investing") or row.get("financing")) for row in flows):
        years = [row["year"] for row in flows]

        def draw(ax):
            _grouped_bars(
                ax,
                years,
                [
                    ("Operating", [row.get("operating") or 0 for row in flows]),
                    ("Investing", [row.get("investing") or 0 for row in flows]),
                    ("Financing", [row.get("financing") or 0 for row in flows]),
                ],
                "Rs crore",
                "Cash flow",
            )

        images.append(("Cash flow (Rs crore)", _png_from_axes(draw)))

    margins = [row for row in (charts.get("margins") or []) if row.get("year")]
    if any(row.get("ebitda") is not None or row.get("net") is not None for row in margins):
        years = [row["year"] for row in margins]

        def draw(ax):
            xs = list(range(len(years)))
            ax.plot(
                xs,
                [row.get("ebitda") or 0 for row in margins],
                color=_AMBER,
                marker="o",
                markersize=4.5,
                linewidth=2.4,
                label="EBITDA margin",
            )
            ax.plot(
                xs,
                [row.get("net") or 0 for row in margins],
                color=_BLUE,
                marker="o",
                markersize=4.5,
                linewidth=2.4,
                label="Net margin",
            )
            ax.set_xticks(xs, years)
            ax.legend(frameon=False, fontsize=8, loc="best")
            _apply_style(ax, "Margins", "%")

        images.append(("Margins (%)", _png_from_axes(draw)))

    peers = charts.get("peers") or []
    if peers:
        names = [row["name"][:24] for row in peers]
        values = [row.get("revenue") or 0 for row in peers]

        def draw(ax):
            ax.barh(names[::-1], values[::-1], color=_BLUE, height=0.55, linewidth=0, zorder=3)
            _apply_style(ax, "Peer revenue", "Revenue (Rs crore)")
            ax.grid(axis="x", linestyle="-", linewidth=0.7, color=_GRID)
            ax.grid(axis="y", visible=False)
            _value_formatter(ax, "x")

        images.append(("Peer revenue (Rs crore)", _png_from_axes(draw)))

    bench = charts.get("peer_bench") or []
    if bench:
        metrics = [row["metric"] for row in bench]
        company_vals = [row.get("company") or 0 for row in bench]
        median_vals = [row.get("median") or 0 for row in bench]

        def draw(ax):
            _grouped_bars(
                ax,
                metrics,
                [("Company", company_vals), ("Industry median", median_vals)],
                "Value",
                "Vs industry median",
            )

        images.append(("Vs industry median", _png_from_axes(draw)))

    return images
