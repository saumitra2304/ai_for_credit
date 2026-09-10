import pytest

from probe_errors import ProbeError, ensure_probe_ok


def test_ensure_probe_ok_rejects_http_errors():
    with pytest.raises(ProbeError) as exc:
        ensure_probe_ok(403, "U123", {"message": "forbidden"})
    assert exc.value.status == 403
    assert "U123" in str(exc.value)


def test_ensure_probe_ok_rejects_payload_without_data():
    with pytest.raises(ProbeError):
        ensure_probe_ok(200, "U123", {"status": "error"})


def test_ensure_probe_ok_returns_valid_payload():
    payload = {"data": {"company": {"cin": "U123"}}}
    assert ensure_probe_ok(200, "U123", payload) is payload
