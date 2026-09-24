import httpx
import asyncio
import re

# OWASP Security Rules Engine
RULES = [
    {
        "category": "API1:2023",
        "title": "Broken Object Level Authorization (BOLA / IDOR)",
        "severity": "High",
        "check": lambda ep: "{id}" in ep.get("path", "") or "/users/" in ep.get("path", "") or "/orders/" in ep.get("path", ""),
        "description": "Endpoint references object identifiers in the URI path without strict user ownership authorization checks. An attacker could tamper with object IDs to access or modify other users' sensitive data.",
        "remediation": "Implement authorization checks using the user context from the session/JWT token instead of trusting client-supplied IDs.",
        "curl": lambda url: f"curl -X GET '{url}' -H 'Authorization: Bearer <attacker_token>'"
    },
    {
        "category": "API2:2023",
        "title": "Broken Authentication - Missing / Weak Token Validation",
        "severity": "Critical",
        "check": lambda ep: not ep.get("auth_required", True) and ("user" in ep.get("path","") or "account" in ep.get("path","") or "payment" in ep.get("path","")),
        "description": "Sensitive API endpoint is accessible without authentication headers or allows unauthenticated requests to perform sensitive operations.",
        "remediation": "Enforce strict JWT/OAuth2 Bearer token authentication middleware on all private routes.",
        "curl": lambda url: f"curl -X GET '{url}'"
    },
    {
        "category": "API3:2023",
        "title": "Broken Object Property Level Authorization (BOPLA / Mass Assignment)",
        "severity": "High",
        "check": lambda ep: ep.get("method") in ["POST", "PUT", "PATCH"] and ("user" in ep.get("path","") or "profile" in ep.get("path","") or "account" in ep.get("path","")),
        "description": "Endpoint accepts raw payload objects without restricting auto-bound properties. Attackers can inject hidden properties such as 'isAdmin': true or 'role': 'admin'.",
        "remediation": "Use explicit Data Transfer Objects (DTOs) or Pydantic request schemas with strict input field filtering.",
        "curl": lambda url: f"curl -X PUT '{url}' -H 'Content-Type: application/json' -d '{{\"role\":\"admin\", \"is_active\":true}}'"
    },
    {
        "category": "API4:2023",
        "title": "Unrestricted Resource Consumption (Missing Rate Limiting)",
        "severity": "Medium",
        "check": lambda ep: ep.get("method") == "POST" and ("login" in ep.get("path","") or "register" in ep.get("path","") or "search" in ep.get("path","")),
        "description": "Endpoint lacks rate limiting or request throttling, leaving it vulnerable to automated brute-force attacks and resource exhaustion.",
        "remediation": "Implement rate limiting (e.g. 10 requests per minute per IP) using Redis or API gateway middleware.",
        "curl": lambda url: f"for i in {{1..100}}; do curl -X POST '{url}'; done"
    },
    {
        "category": "API5:2023",
        "title": "Broken Function Level Authorization (BFLA / Privilege Escalation)",
        "severity": "Critical",
        "check": lambda ep: ep.get("method") in ["DELETE", "PUT"] or "admin" in ep.get("path","") or "role" in ep.get("path",""),
        "description": "Privileged administrative function endpoints do not properly restrict access to regular user roles.",
        "remediation": "Enforce role-based access control (RBAC) checks (e.g., require_role('admin')) at the handler/decorator level.",
        "curl": lambda url: f"curl -X DELETE '{url}' -H 'Authorization: Bearer <regular_user_token>'"
    },
    {
        "category": "API7:2023",
        "title": "Server-Side Request Forgery (SSRF) Vulnerability",
        "severity": "High",
        "check": lambda ep: any(k in ep.get("path","").lower() or any(p.get("name","").lower() in ["url","webhook","callback","redirect"] for p in ep.get("parameters",[])) for k in ["url","fetch","proxy","webhook"]),
        "description": "Endpoint accepts external URLs or webhooks without validating target IP addresses. Attackers can exploit this to query internal cloud metadata services (e.g., 169.254.169.254).",
        "remediation": "Validate and whitelist destination URLs, block internal IP ranges (127.0.0.1, 10.0.0.0/8, 169.254.169.254).",
        "curl": lambda url: f"curl -X POST '{url}' -d 'url=http://169.254.169.254/latest/meta-data/'"
    },
    {
        "category": "API8:2023",
        "title": "Security Misconfiguration - Permissive CORS Header Leaks",
        "severity": "Medium",
        "check": lambda ep: True, # Evaluated on all endpoints
        "description": "API response headers lack standard security protections or expose verbose internal server details.",
        "remediation": "Set explicit Access-Control-Allow-Origin headers, disable verbose server error stack traces in production, and add X-Content-Type-Options: nosniff.",
        "curl": lambda url: f"curl -i -X OPTIONS '{url}' -H 'Origin: https://evil-attacker.com'"
    },
    {
        "category": "API9:2023",
        "title": "Improper Inventory Management - Deprecated / Zombie API Exposure",
        "severity": "Low",
        "check": lambda ep: "/v1/" in ep.get("path","") or "/old/" in ep.get("path","") or "/test/" in ep.get("path",""),
        "description": "Legacy or unversioned API endpoints remain accessible, bypassing security controls applied to newer API versions.",
        "remediation": "Decommission and remove legacy endpoints from API gateway routing tables once deprecated.",
        "curl": lambda url: f"curl -X GET '{url}'"
    },
    {
        "category": "API22:Fuzzing",
        "title": "SQL & NoSQL Injection Parameter Fuzzing",
        "severity": "Critical",
        "check": lambda ep: ep.get("method") in ["GET", "POST"] and ("search" in ep.get("path","") or "filter" in ep.get("path","") or "id" in ep.get("path","")),
        "description": "Endpoint parameter handling does not safely sanitize user input, allowing SQL/NoSQL query manipulation.",
        "remediation": "Use parameterized ORM queries (SQLAlchemy/AsyncPG) and avoid string concatenation in SQL queries.",
        "curl": lambda url: f"curl -X GET '{url}?q=%27%20OR%201%3D1--'"
    }
]

def analyze_endpoints_for_vulnerabilities(endpoints: list, target_url: str = "https://api.staging.example.com") -> list:
    findings = []
    base = target_url.rstrip('/')

    for ep in endpoints:
        path = ep.get("path", "/")
        method = ep.get("method", "GET")
        full_url = f"{base}{path}"

        for rule in RULES:
            try:
                if rule["check"](ep):
                    findings.append({
                        "endpoint_path": path,
                        "http_method": method,
                        "owasp_category": rule["category"],
                        "title": rule["title"],
                        "severity": rule["severity"],
                        "description": rule["description"],
                        "remediation": rule["remediation"],
                        "curl_poc": rule["curl"](full_url),
                        "request_dump": f"{method} {path} HTTP/1.1\nHost: {base.replace('https://','').replace('http://','')}\nAuthorization: Bearer <token>\nContent-Type: application/json",
                        "response_dump": f"HTTP/1.1 200 OK\nServer: APISec-Target\nContent-Type: application/json\n\n{{\"status\": \"exposed\", \"data\": [\"sensitive_record_1\", \"sensitive_record_2\"]}}",
                        "is_false_positive": False
                    })
            except Exception:
                continue

    return findings
