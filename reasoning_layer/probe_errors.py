class ProbeError(Exception):
    def __init__(self, cin: str, status: int, detail: str = ""):
        self.cin = cin
        self.status = status
        self.detail = (detail or "")[:240]
        extra = f" ({self.detail})" if self.detail else ""
        super().__init__(f"Could not load filings for {cin}: HTTP {status}{extra}")


def ensure_probe_ok(status: int, cin: str, payload) -> dict:
    if status >= 400:
        detail = ""
        if isinstance(payload, dict):
            detail = str(payload.get("message") or payload.get("detail") or payload.get("error") or "")
        elif isinstance(payload, str):
            detail = payload
        raise ProbeError(cin, status, detail)
    if not isinstance(payload, dict) or not payload.get("data"):
        raise ProbeError(cin, status or 502, "response missing company data")
    return payload
