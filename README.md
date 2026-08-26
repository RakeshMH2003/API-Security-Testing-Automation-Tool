# 🛡️ APISec Platform

**Professional API Security Testing Automation Tool**

Automatically discover APIs, test for OWASP API Security Top 10 vulnerabilities, collect evidence, and generate developer-friendly remediation reports.

---

## 🚀 Features (Module 01 — User Management)

- ✅ User Registration & Login with JWT Authentication
- ✅ Role-Based Access Control (Admin, Analyst, Developer, Viewer)
- ✅ Admin-only panel (hidden from regular users)
- ✅ Password strength validation
- ✅ Secure logout with token blacklisting
- ✅ Modern dark cybersecurity themed UI
- ✅ Fully responsive (mobile + desktop)

---

## 🗂️ Project Structure

```
api-security-platform/
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── auth/              # Module 01: User Management
│   │   │   ├── models.py      # SQLAlchemy User + TokenBlacklist models
│   │   │   ├── schemas.py     # Pydantic request/response schemas
│   │   │   ├── router.py      # Auth API endpoints
│   │   │   ├── service.py     # Business logic
│   │   │   └── utils.py       # JWT + bcrypt helpers
│   │   ├── core/
│   │   │   ├── security.py    # JWT middleware
│   │   │   └── deps.py        # Shared dependencies
│   │   ├── config.py          # Settings from .env
│   │   ├── database.py        # SQLAlchemy async engine
│   │   └── main.py            # FastAPI application
│   ├── mock_server.py         # Demo server (no DB needed)
│   ├── create_tables.py       # DB initialization script
│   ├── start.py               # Production server start
│   └── requirements.txt
│
├── frontend/                  # Vanilla HTML/CSS/JS
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── dashboard.html         # Main dashboard (protected)
│   ├── profile.html           # User profile (protected)
│   ├── css/
│   │   ├── style.css          # Global dark theme styles
│   │   └── auth.css           # Auth page styles
│   └── js/
│       ├── api.js             # API client (fetch wrapper)
│       ├── auth.js            # Auth utilities
│       └── utils.js           # Helper functions
│
├── .env.example               # Environment variables template
└── README.md
```

---

## ⚡ Quick Start (Demo Mode)

No database or Python packages needed — runs with built-in mock server.

```powershell
# Clone the repo
git clone https://github.com/YOUR_USERNAME/api-security-platform.git
cd api-security-platform

# Start the demo server (uses Python standard library only)
python backend/mock_server.py

# Open in browser
start http://localhost:8000
```

**Demo Credentials:**
| Role | Email | Password |
|:--|:--|:--|
| Admin | `admin@security.local` | `Admin@1234` |
| Regular User | Register at `/register.html` | Your choice |

---

## 🔧 Production Setup (FastAPI + PostgreSQL)

```powershell
# 1. Create virtual environment
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and configure environment
Copy-Item ..\.env.example ..\.env
# Edit .env with your PostgreSQL credentials

# 4. Initialize database
python create_tables.py

# 5. Start server
python start.py
```

API docs available at: **http://localhost:8000/docs**

---

## 🔐 API Endpoints (Module 01)

| Method | Endpoint | Description | Auth |
|:--|:--|:--|:--|
| `POST` | `/api/v1/auth/register` | Register new user | Public |
| `POST` | `/api/v1/auth/login` | Login, returns JWT | Public |
| `POST` | `/api/v1/auth/logout` | Invalidate token | Required |
| `GET` | `/api/v1/auth/me` | Get current user | Required |
| `PUT` | `/api/v1/auth/me` | Update profile | Required |
| `PUT` | `/api/v1/auth/password` | Change password | Required |
| `GET` | `/api/v1/health` | Health check | Public |

---

## 🗺️ Roadmap — 34 Modules

- [x] **Module 01** — User Management & JWT Auth
- [ ] **Module 02** — RBAC (Role-Based Access Control)
- [ ] **Module 03** — Project Management
- [ ] **Module 04** — API Target Management
- [ ] **Module 05** — Scope Management
- [ ] **Module 06** — OpenAPI/Swagger Importer
- [ ] **Module 07** — Postman Importer
- [ ] **Module 08** — API Discovery Engine
- [ ] **Module 09** — API Inventory
- [ ] **Module 10** — Authentication Profiles
- [ ] **Modules 11-34** — Scan Engine, OWASP Tests, Findings, Reports, CI/CD...

---

## 🛡️ Security Notice

> This platform is built **exclusively for authorized security testing**.
> Always obtain written permission before scanning any API.
> Unauthorized testing is illegal and unethical.

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.
