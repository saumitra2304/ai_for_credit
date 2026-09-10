from memo_charts import (
    chart_pngs,
    crore,
    extract_memo_charts,
    flatten_memo_extras,
    format_inr_compact,
    select_peer_cins,
    select_peer_cins_from_charts,
)
from memo_charts import _group_en_in
from memo_document import memo_filename, render_docx, render_pdf


def test_crore_and_compact_format():
    assert crore(1_234_567_890) == 123.46
    assert format_inr_compact(1_234_567_890) == "Rs 123.46 crore"
    assert format_inr_compact(5_000_000) == "Rs 50 lakh"
    assert format_inr_compact(50_000) == "Rs 50,000"
    assert _group_en_in(12345) == "12,345"
    assert _group_en_in(1234567) == "12,34,567"


def test_extract_memo_charts_from_standalone_filings():
    payload = {
        "data": {
            "company": {"legal_name": "Acme Private Limited", "cin": "U123"},
            "financials": [
                {
                    "year": "2023-03-31",
                    "nature": "STANDALONE",
                    "pnl": {"lineItems": {"net_revenue": 100_000_000, "profit_after_tax": 10_000_000}},
                    "bs": {"subTotals": {"total_equity": 50_000_000, "total_debt": 20_000_000}},
                    "cash_flow": {"cash_flows_from_used_in_operating_activities": 5_000_000},
                    "ratios": {"ebitda_margin": 12.5, "net_margin": 10.0},
                },
                {
                    "year": "2024-03-31",
                    "nature": "STANDALONE",
                    "pnl": {"lineItems": {"net_revenue": 120_000_000, "profit_after_tax": 12_000_000}},
                    "bs": {"subTotals": {"total_equity": 55_000_000, "total_debt": 22_000_000}},
                },
            ],
            "peer_comparison": [
                {
                    "peers": [
                        {
                            "legalName": "Peer A LIMITED",
                            "cin": "L99999MH1990PLC000001",
                            "revenue": 200_000_000,
                        },
                        {"legalName": "Peer B", "cin": "U12345MH2010PTC000001", "revenue": 80_000_000},
                    ]
                }
            ],
        }
    }
    charts = extract_memo_charts(payload)
    assert charts["company_name"] == "Acme Private Limited"
    assert [row["year"] for row in charts["pnl"]] == ["2023", "2024"]
    assert charts["pnl"][1]["revenue"] == 12.0
    assert charts["peers"][0]["name"] == "Peer A"
    assert charts["peers"][0]["cin"] == "L99999MH1990PLC000001"
    assert charts["peers"][0]["revenue"] == 20.0
    assert charts["cash_flow"][0]["operating"] == 0.5
    extras = flatten_memo_extras(payload)
    assert "Peer A" in extras
    pngs = chart_pngs(charts)
    assert len(pngs) >= 4
    assert all(img.startswith(b"\x89PNG") for _, img in pngs)


def test_select_peer_cins_ranks_probe_revenue_and_skips_self():
    borrower = "L16005WB1910PLC001985"
    payload = {
        "data": {
            "company": {"cin": borrower},
            "peer_comparison": [
                {
                    "peers": [
                        {
                            "legalName": "Indian Potash Limited",
                            "revenue": 500_000_000_000,
                        },
                        {
                            "legalName": "Godfrey Phillips India Limited",
                            "cin": "L16004MH1936PLC008587",
                            "revenue": 40_000_000_000,
                        },
                        {
                            "legalName": "Borrower itself",
                            "cin": borrower,
                            "revenue": 90_000_000_000,
                        },
                        {
                            "legalName": "VST Industries Limited",
                            "cin": "L29150TG1930PLC000576",
                            "revenue": 15_000_000_000,
                        },
                        {
                            "legalName": "Tiny Co",
                            "cin": "U11111MH2010PTC000111",
                            "revenue": 1_000_000,
                        },
                    ]
                }
            ],
        }
    }
    cins = select_peer_cins(payload, exclude=[borrower], limit=3)
    assert cins == [
        "L16004MH1936PLC008587",
        "L29150TG1930PLC000576",
        "U11111MH2010PTC000111",
    ]
    charts = extract_memo_charts(payload)
    assert select_peer_cins_from_charts([charts], exclude=[borrower], limit=2) == [
        "L16004MH1936PLC008587",
        "L29150TG1930PLC000576",
    ]


def test_pdf_and_docx_are_real_files():
    markdown = "# Acme\n\n## Risk conclusion\n\nLeverage is moderate.\n"
    charts = {
        "company_name": "Acme",
        "cin": "U123",
        "pnl": [{"year": "2023", "revenue": 10, "pat": 1}, {"year": "2024", "revenue": 12, "pat": 1.2}],
        "balance_sheet": [{"year": "2023", "equity": 5, "debt": 2}, {"year": "2024", "equity": 5.5, "debt": 2.2}],
        "peers": [{"name": "Peer A", "revenue": 20}],
    }
    pdf = render_pdf(markdown, [charts], "Acme Private Limited")
    docx = render_docx(markdown, [charts], "Acme Private Limited")
    assert pdf.startswith(b"%PDF")
    assert docx.startswith(b"PK")
    assert memo_filename("Acme Private Limited", "pdf") == "Acme-Private-Limited-credit-memo.pdf"


def test_pdf_survives_wide_tables_page_breaks_and_markdown_links():
    header = "| " + " | ".join(f"FY{year}" for year in range(2018, 2026)) + " |"
    divider = "| " + " | ".join("---" for _ in range(8)) + " |"
    row = "| " + " | ".join("Rs 12,345.67 crore" for _ in range(8)) + " |"
    table = "\n".join([header, divider] + [row] * 28)
    markdown = (
        "# Godrej Properties Limited (CIN L74120MH1985PLC035308)\n\n"
        "## Financial position\n\n"
        f"{table}\n\n"
        "## Recommendation and conditions\n\n"
        "1. Track cash conversion ([icra.in](https://www.icra.in/Rating/RatingDetails"
        "?CompanyId=21792&CompanyName=Godrej+Properties+Limited&utm_source=openai))\n"
        "2. Prepare a litigation heat-map for high-severity DRT/NCLT matters.\n"
        "3. Obtain MSME settlement plan for dues of Rs 2.63 crore.\n"
    )
    pdf = render_pdf(markdown, [], "Godrej Properties Limited (CIN L74120MH1985PLC035308)")
    assert pdf.startswith(b"%PDF")


def test_pdf_colors_strengths_risks_and_negative_figures():
    markdown = (
        "## Strengths\n\n"
        "- Near-zero leverage.\n\n"
        "## Red flags / watch items\n\n"
        "- Short-term borrowings jumped.\n\n"
        "| Metric | FY26 |\n| --- | --- |\n| Cash flow from investing | -1,538.38 |\n"
    )
    pdf = render_pdf(markdown, [], "ITC LIMITED")
    assert pdf.startswith(b"%PDF")
