import io
from types import SimpleNamespace

from docx import Document

from memo_attachments import (
    attachment_blocks,
    extract_attachment,
    parse_extra_cins,
    parse_search_lines,
    required_search_suffix,
)
from memo_generate import (
    MEMO_CACHE_VERSION,
    brief_fingerprint,
    memo_brief,
    _cached_markdown,
    flatten_chat_trail,
    merge_auto_peer_cins,
)


def test_parse_extra_cins_dedupes_and_uppercases():
    assert parse_extra_cins("L16005WB1910PLC001985, u12345mh2010ptc000001\nL16005WB1910PLC001985") == [
        "L16005WB1910PLC001985",
        "U12345MH2010PTC000001",
    ]


def test_parse_search_lines_keeps_order_and_caps_count():
    raw = "ITC cigarette tax\n\nFMCG volume India\n" + "\n".join(f"q{i}" for i in range(20))
    lines = parse_search_lines(raw)
    assert lines[0] == "ITC cigarette tax"
    assert lines[1] == "FMCG volume India"
    assert len(lines) <= 8


def test_extract_csv_and_docx_attachments():
    csv_text = extract_attachment("cma.csv", b"Metric,FY26\nRevenue,100\n")
    assert "Revenue" in csv_text
    assert "100" in csv_text

    buf = io.BytesIO()
    doc = Document()
    doc.add_paragraph("Sanction note: WC limit Rs 500 crore.")
    doc.save(buf)
    docx_text = extract_attachment("note.docx", buf.getvalue())
    assert "WC limit" in docx_text


def test_extract_rejects_unknown_type():
    try:
        extract_attachment("photo.png", b"\x89PNG")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "png" in str(exc).lower() or "type" in str(exc).lower()


def test_memo_brief_fingerprint_changes_with_notes_and_files():
    a = memo_brief(notes="Add HUL as peer")
    b = memo_brief(notes="Add Nestle as peer")
    c = memo_brief(notes="Add HUL as peer", attachments=[("a.csv", "Revenue,1")])
    assert brief_fingerprint(a) != brief_fingerprint(b)
    assert brief_fingerprint(a) != brief_fingerprint(c)
    assert brief_fingerprint(a) == brief_fingerprint(memo_brief(notes="Add HUL as peer"))


def test_cached_markdown_requires_matching_fingerprint():
    cache = {
        "__memo__": {
            "markdown": "# cached",
            "version": MEMO_CACHE_VERSION,
            "fingerprint": "abc",
        }
    }
    assert _cached_markdown(cache, "abc") == "# cached"
    assert _cached_markdown(cache, "other") == ""
    assert _cached_markdown({"__memo__": {"markdown": "# v3", "version": 3}}, "") == ""


def test_merge_auto_peer_cins_fills_from_charts_when_user_omits_them():
    charts = [
        {
            "cin": "L16005WB1910PLC001985",
            "peers": [
                {"name": "Godfrey", "cin": "L16004MH1936PLC008587", "revenue": 40},
                {"name": "VST", "cin": "L29150TG1930PLC000576", "revenue": 15},
            ],
        }
    ]
    filled = merge_auto_peer_cins(
        [],
        charts,
        exclude=["L16005WB1910PLC001985"],
        auto=True,
        limit=3,
    )
    assert filled == ["L16004MH1936PLC008587", "L29150TG1930PLC000576"]
    manual = merge_auto_peer_cins(
        ["U12345MH2010PTC000001"],
        charts,
        exclude=["L16005WB1910PLC001985"],
        auto=True,
        limit=3,
    )
    assert manual == ["U12345MH2010PTC000001"]
    assert merge_auto_peer_cins([], charts, exclude=["L16005WB1910PLC001985"], auto=False) == []


def test_attachment_blocks_and_required_searches():
    text = attachment_blocks([("cma.csv", "Revenue | 100")])
    assert "cma.csv" in text
    assert "Revenue | 100" in text
    suffix = required_search_suffix(["ITC cigarette tax", "FMCG volume"])
    assert "ITC cigarette tax" in suffix
    assert "web_search" in suffix
    assert required_search_suffix([]) == ""


def test_flatten_chat_trail_includes_officer_and_assistant():
    chat = SimpleNamespace(
        message_trail=[
            {"query": "Complete credit analysis", "response": "Advance with monitoring."},
            {"query": "What is the cash conversion cycle?", "response": "About 70 days."},
        ]
    )
    text = flatten_chat_trail(chat)
    assert "Complete credit analysis" in text
    assert "70 days" in text
