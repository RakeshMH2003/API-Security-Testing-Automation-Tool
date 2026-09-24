import httpx
import asyncio
from typing import List, Dict

COMMON_API_PATHS = [
    "/api/v1/health", "/health", "/status", "/ping",
    "/api/v1/users", "/api/v1/auth/login", "/api/v1/auth/register",
    "/openapi.json", "/swagger.json", "/v1/swagger.json", "/v2/swagger.json",
    "/api-docs", "/docs", "/graphql", "/api/v1/orders", "/api/v1/payments"
]

async def spider_crawl_target(target_url: str, depth: int = 2) -> List[Dict]:
    """Probes the target URL for common API routes and spec declarations."""
    base_url = target_url.rstrip('/')
    discovered_endpoints = []

    async with httpx.AsyncClient(timeout=5.0, verify=False) as client:
        tasks = [client.get(f"{base_url}{path}") for path in COMMON_API_PATHS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for path, resp in zip(COMMON_API_PATHS, results):
            if isinstance(resp, httpx.Response) and resp.status_code in [200, 201, 401, 403]:
                # Endpoint exists!
                method = "POST" if "login" in path or "register" in path else "GET"
                discovered_endpoints.append({
                    "path": path,
                    "method": method,
                    "summary": f"Discovered Endpoint ({path})",
                    "description": f"Probed status code {resp.status_code}",
                    "parameters": [],
                    "auth_required": resp.status_code in [401, 403],
                    "source": "crawler"
                })

    return discovered_endpoints
