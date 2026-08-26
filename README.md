# API-Security-Testing-Automation-Tool
# API Security Testing Automation Platform

An automated platform for discovering, inventorying, and security-testing APIs against the **OWASP API Security Top 10**, with developer-friendly remediation reporting.

Final-year B.Tech project (Cybersecurity).

---

## Overview

APIs are one of the most under-tested attack surfaces in modern applications. This project builds a tool that:

- Imports API definitions from **OpenAPI/Swagger** and **Postman** collections (and optionally discovers endpoints from a target's JavaScript, for authorized targets without published specs)
- Builds a structured **API inventory** (endpoints, methods, parameters, auth requirements)
- Runs controlled, safe security tests mapped to the **OWASP API Security Top 10**
- Collects evidence, deduplicates findings, and scores severity/risk
- Generates **developer-readable remediation reports** (JSON/HTML, PDF planned)
- Presents results in a security dashboard with scan history and comparison

---

## Features

- OpenAPI/Swagger and Postman collection import
- Endpoint inventory with normalized method/parameter/auth metadata
- Authentication profile manager (API keys, bearer tokens, JWT)
- Plugin-based security test engine (new OWASP checks can be added without rewriting the scanner)
- OWASP API Security Top 10 coverage: BOLA, Broken Authentication, Broken Object Property Authorization, Unrestricted Resource Consumption, Broken Function Level Authorization, SSRF, Security Misconfiguration, Improper Inventory Management, Unsafe Consumption of APIs, Injection
- Evidence collection and finding deduplication
- Severity/risk scoring
- Remediation recommendations per finding
- Scan history and scan comparison
- Audit logging

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React / Next.js, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI |
| Security Testing | Custom Python test-plugin framework, httpx |
| Database | PostgreSQL |
| Queue / Async Jobs | Redis + Celery |
| Deployment | Docker, Docker Compose |
| Reports | JSON, HTML (PDF planned) |

---

## Architecture

```
OpenAPI/Postman Spec / Authorized Target
        ↓
   API Discovery
        ↓
   API Inventory
        ↓
Authentication Profile Setup
        ↓
Scan Orchestrator → Security Test Engine (OWASP API Top 10 Plugins)
        ↓
Evidence Collection
        ↓
Finding Deduplication → Severity/Risk Scoring
        ↓
Remediation Engine
        ↓
Dashboard + Report Generator (JSON / HTML / PDF)
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+ (or use the provided Docker Compose service)

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd api-security-tool

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install

# Start services (Postgres, Redis, backend, frontend)
docker compose up --build
```

### Usage

1. Register/login and create a project
2. Add an authorized API target
3. Import an OpenAPI/Swagger spec or Postman collection
4. Configure an authentication profile for the target
5. Start a scan
6. Review findings, evidence, and severity on the dashboard
7. Generate and export a report

---

## Project Structure

```
backend/       FastAPI application, test engine, plugins
frontend/      React/Next.js dashboard
scanner/       OWASP API Top 10 test plugin modules
docs/          Architecture, API, and user documentation
docker/        Dockerfiles and Compose configuration
tests/         Unit, integration, and scanner accuracy tests
```

---

## Legal & Ethical Use

This project was developed as a final-year academic project for authorized security testing and educational purposes only. It must not be used against any system without explicit, documented authorization from the system owner. The author(s) and institution are not responsible for misuse of this tool.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Author

Rakesh M H — Final Year B.Tech, Cybersecurity
