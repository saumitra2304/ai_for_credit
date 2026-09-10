from types import SimpleNamespace

from observability import (
    EXCEPTIONS,
    env_int,
    metrics_allowed,
    normalize_path,
    record_exception,
)


def test_env_int_clamps_and_falls_back():
    assert env_int("KUBER_MISSING_CONCURRENCY", 8, maximum=32) == 8
    monkey = "not-a-number"
    import os

    os.environ["KUBER_TEST_CONCURRENCY"] = monkey
    try:
        assert env_int("KUBER_TEST_CONCURRENCY", 8) == 8
        os.environ["KUBER_TEST_CONCURRENCY"] = "64"
        assert env_int("KUBER_TEST_CONCURRENCY", 8, maximum=32) == 32
        os.environ["KUBER_TEST_CONCURRENCY"] = "0"
        assert env_int("KUBER_TEST_CONCURRENCY", 8, minimum=1) == 1
    finally:
        os.environ.pop("KUBER_TEST_CONCURRENCY", None)


def test_normalize_path_groups_chat_and_memo():
    assert normalize_path("/chat") == "/chat"
    assert normalize_path("/chat/abc") == "/chat/{id}"
    assert normalize_path("/chat/abc/memo") == "/chat/{id}/memo"
    assert normalize_path("/admin/logs") == "/admin"


def test_record_exception_increments_counter():
    before = EXCEPTIONS.labels(type="RuntimeError", path="/chat")._value.get()
    record_exception("RuntimeError", "/chat")
    after = EXCEPTIONS.labels(type="RuntimeError", path="/chat")._value.get()
    assert after == before + 1


def test_metrics_allowed_loopback_and_token(monkeypatch):
    loopback = SimpleNamespace(
        client=SimpleNamespace(host="127.0.0.1"),
        headers={},
    )
    assert metrics_allowed(loopback) is True

    monkeypatch.setenv("INTERNAL_TOKEN", "secret-token")
    docker = SimpleNamespace(
        client=SimpleNamespace(host="10.0.0.4"),
        headers={"x-internal-token": "secret-token"},
    )
    assert metrics_allowed(docker) is True

    public = SimpleNamespace(
        client=SimpleNamespace(host="203.0.113.10"),
        headers={},
    )
    assert metrics_allowed(public) is False
