from memo_generate import MEMO_CACHE_VERSION, _cached_markdown, company_slots, render_memo_bytes


def test_company_slots_skips_internal_memo_cache():
    cache = {
        "U123": {"label": "Acme", "flat": "METRIC | 2024"},
        "__memo__": {"markdown": "# cached"},
        "_skip": {"label": "nope"},
    }
    slots = company_slots(cache)
    assert [cin for cin, _ in slots] == ["U123"]


def test_render_memo_bytes_rejects_unknown_format():
    try:
        render_memo_bytes("# Hi", [], "xlsx", "Acme")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "pdf or docx" in str(exc)


def test_stale_memo_cache_is_ignored():
    assert _cached_markdown({"__memo__": "# old string cache"}) == ""
    assert _cached_markdown({"__memo__": {"markdown": "# v1", "version": 1}}) == ""
    assert (
        _cached_markdown(
            {"__memo__": {"markdown": "# v4", "version": MEMO_CACHE_VERSION, "fingerprint": ""}}
        )
        == "# v4"
    )
