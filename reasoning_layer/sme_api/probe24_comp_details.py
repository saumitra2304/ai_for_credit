from typing import Dict

from aiohttp import ClientSession

from sme_api.base import sme_headers, sme_url
from request_ctx import span, log_event


async def company_details(client: ClientSession, cin: str, semaphore) -> Dict:
    async with semaphore:
        async with span("probe.company_details", cin=cin):
            async with client.get(
                sme_url("/company_details"),
                params={"cin": cin},
                headers=sme_headers(),
            ) as resp:
                if resp.status >= 400:
                    await log_event(
                        "error",
                        "probe",
                        f"company_details {cin} HTTP {resp.status}",
                    )
                return await resp.json()
