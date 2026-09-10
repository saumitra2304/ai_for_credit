from typing import Dict
import time

from aiohttp import ClientSession

from observability import PROBE_IN_FLIGHT, PROBE_LATENCY, record_probe_error
from probe_errors import ensure_probe_ok
from sme_api.base import sme_headers, sme_url
from request_ctx import span, log_event


async def company_details(client: ClientSession, cin: str, semaphore) -> Dict:
    async with semaphore:
        PROBE_IN_FLIGHT.inc()
        started = time.perf_counter()
        try:
            async with span("probe.company_details", cin=cin):
                async with client.get(
                    sme_url("/company_details"),
                    params={"cin": cin},
                    headers=sme_headers(),
                ) as resp:
                    status = resp.status
                    try:
                        payload = await resp.json()
                    except Exception:
                        payload = await resp.text()
                    if status >= 400:
                        record_probe_error()
                        await log_event(
                            "error",
                            "probe",
                            f"company_details {cin} HTTP {status}",
                        )
                    return ensure_probe_ok(status, cin, payload)
        except Exception:
            record_probe_error()
            raise
        finally:
            PROBE_LATENCY.labels(route="company_details").observe(time.perf_counter() - started)
            PROBE_IN_FLIGHT.dec()
