import json, os, uuid
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

db_users = {
    "admin@security.local": {
        "id": "aaaa-bbbb-cccc-dddd",
        "email": "admin@security.local",
        "password": "Admin@1234",
        "full_name": "Platform Admin",
        "role": "admin",
        "is_active": True,
        "created_at": "2026-01-01T00:00:00Z",
        "last_login": None
    },
    "viewer@security.local": {
        "id": "1111-2222-3333-4444",
        "email": "viewer@security.local",
        "password": "Viewer@1234",
        "full_name": "Read-Only User",
        "role": "viewer",
        "is_active": True,
        "created_at": "2026-01-02T00:00:00Z",
        "last_login": None
    }
}

db_projects = {
    "proj-1": {
        "id": "proj-1",
        "name": "CyberStore Microservices",
        "category": "E-Commerce",
        "description": "Main e-commerce shopping cart, payment gateway, and inventory API endpoints.",
        "owner_id": "aaaa-bbbb-cccc-dddd",
        "created_at": "2026-01-10T10:00:00Z",
        "updated_at": "2026-01-10T10:00:00Z",
        "targets": [
            {"id": "targ-1", "project_id": "proj-1", "name": "Staging API Gateway", "base_url": "https://api-staging.cyberstore.local", "environment": "staging", "is_active": True, "created_at": "2026-01-10T10:00:00Z"}
        ],
        "scope_rules": [
            {"id": "scope-1", "project_id": "proj-1", "rule_type": "include", "pattern": "/api/v1/.*", "description": "Include all v1 endpoints"}
        ],
        "rate_limit": {
            "id": "rl-1", "project_id": "proj-1", "max_req_per_sec": 15, "burst_limit": 30, "concurrent_connections": 5
        }
    }
}

db_endpoints = {
    "proj-1": [
        {"id": "ep-1", "project_id": "proj-1", "path": "/api/v1/users", "method": "GET", "summary": "List all users", "auth_required": True, "source": "openapi", "created_at": "2026-01-10T10:00:00Z"},
        {"id": "ep-2", "project_id": "proj-1", "path": "/api/v1/users/{id}", "method": "GET", "summary": "Get user details", "auth_required": True, "source": "openapi", "created_at": "2026-01-10T10:00:00Z"},
        {"id": "ep-3", "project_id": "proj-1", "path": "/api/v1/orders", "method": "POST", "summary": "Create order", "auth_required": True, "source": "postman", "created_at": "2026-01-10T10:00:00Z"},
        {"id": "ep-4", "project_id": "proj-1", "path": "/api/v1/products", "method": "GET", "summary": "List products catalog", "auth_required": False, "source": "crawler", "created_at": "2026-01-10T10:00:00Z"},
        {"id": "ep-5", "project_id": "proj-1", "path": "/api/v1/auth/login", "method": "POST", "summary": "User authentication", "auth_required": False, "source": "openapi", "created_at": "2026-01-10T10:00:00Z"}
    ]
}

db_auth_profiles = {
    "proj-1": [
        {"id": "ap-1", "project_id": "proj-1", "name": "Staging Admin Token", "auth_type": "bearer", "credentials": {"token": "eyJhbGciOi..."}, "is_active": True, "created_at": "2026-01-10T10:00:00Z"}
    ]
}

db_tokens = {}

class H(SimpleHTTPRequestHandler):
    def log_message(self, f, *a): print(f"[{datetime.now().strftime('%H:%M:%S')}] {f%a}")
    def cors(self):
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS,PUT,DELETE')
        self.send_header('Access-Control-Allow-Headers','Content-Type,Authorization')
    def do_OPTIONS(self):
        self.send_response(200); self.cors(); self.end_headers()
    def json(self, d, s=200):
        b=json.dumps(d).encode()
        self.send_response(s)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(b)))
        self.cors(); self.end_headers(); self.wfile.write(b)
    def body(self):
        try:
            n=int(self.headers.get('Content-Length',0))
            return json.loads(self.rfile.read(n)) if n>0 else {}
        except: return {}
    def current_user(self):
        a=self.headers.get('Authorization','')
        if a.startswith('Bearer '):
            e=db_tokens.get(a[7:])
            if e: return db_users.get(e)
        return None

    def handle_api(self, method):
        p = urlparse(self.path).path
        u = self.current_user()

        # Public Auth Routes
        if (p.startswith('/api/v1/auth/register') or p.startswith('/api/auth/register') or p == '/auth/register') and method == 'POST':
            b = self.body()
            email = (b.get('email') or '').strip().lower()
            pw = b.get('password') or ''
            name = (b.get('full_name') or '').strip()
            if not email or not pw or not name: return self.json({"detail":"All fields required."}, 422)
            if email in db_users: return self.json({"detail":"Email registered. Please login."}, 409)
            db_users[email] = {"id": str(uuid.uuid4()), "email": email, "password": pw, "full_name": name, "role": "viewer", "is_active": True, "created_at": datetime.utcnow().isoformat()+"Z", "last_login": None}
            return self.json({"message": "Account created! Please login."}, 201)

        if (p.startswith('/api/v1/auth/login') or p.startswith('/api/auth/login') or p == '/auth/login') and method == 'POST':
            b = self.body()
            email = (b.get('email') or '').strip().lower()
            pw = b.get('password') or ''
            usr = db_users.get(email)
            if not usr or usr['password'] != pw: return self.json({"detail": "Invalid credentials."}, 401)
            tok = f"tok-{uuid.uuid4()}"
            db_tokens[tok] = email
            r = {k: v for k, v in usr.items() if k != 'password'}
            return self.json({"access_token": tok, "refresh_token": f"ref-{uuid.uuid4()}", "user": r})

        if not u and not p.startswith('/css') and not p.startswith('/js') and not p.endswith('.html') and p != '/':
            if p.startswith('/api'): return self.json({"detail": "Not authenticated."}, 401)

        if p in ['/api/v1/auth/me', '/api/auth/me', '/auth/me']:
            if method == 'GET': return self.json({k: v for k, v in u.items() if k != 'password'})

        if p in ['/api/v1/auth/logout', '/api/auth/logout', '/auth/logout'] and method == 'POST':
            return self.json({"message": "Logged out."})

        # --- USERS (RBAC) ---
        if p in ['/api/v1/users', '/api/users', '/users'] and method == 'GET':
            return self.json([{k: v for k, v in user.items() if k != 'password'} for user in db_users.values()])

        # --- PROJECTS (Phase 1) ---
        if p in ['/api/v1/projects', '/api/projects', '/projects']:
            if method == 'GET': return self.json(list(db_projects.values()))
            if method == 'POST':
                b = self.body()
                new_id = f"proj-{uuid.uuid4()}"
                new_proj = {
                    "id": new_id, "name": b.get("name", "New Project"), "category": b.get("category", "General"),
                    "description": b.get("description", ""), "owner_id": u["id"], "created_at": datetime.utcnow().isoformat()+"Z",
                    "targets": [], "scope_rules": [], "rate_limit": {"id": f"rl-{uuid.uuid4()}", "project_id": new_id, "max_req_per_sec": 10, "burst_limit": 20, "concurrent_connections": 5}
                }
                db_projects[new_id] = new_proj
                db_endpoints[new_id] = []
                db_auth_profiles[new_id] = []
                return self.json(new_proj, 201)

        # Single project details: GET/PUT/DELETE /api/projects/{id} or /api/v1/projects/{id} or /projects/{id}
        parts = [x for x in p.split('/') if x]
        if len(parts) >= 2 and parts[-2] == 'projects' and parts[-1] in db_projects:
            pid = parts[-1]
            if method == 'GET': return self.json(db_projects[pid])
            if method == 'DELETE':
                db_projects.pop(pid, None)
                return self.json({"message": "Project deleted"})

        # --- DISCOVERY & INVENTORY (Phase 2: Modules 06-10) ---

        # List endpoints for project: /api/v1/projects/{id}/endpoints or /api/projects/{id}/endpoints
        if len(parts) >= 3 and parts[-1] == 'endpoints' and parts[-3] == 'projects':
            pid = parts[-2]
            if method == 'GET': return self.json(db_endpoints.get(pid, []))
            if method == 'POST':
                b = self.body()
                ep = {"id": f"ep-{uuid.uuid4()}", "project_id": pid, "path": b.get("path","/"), "method": b.get("method","GET").upper(), "summary": b.get("summary",""), "auth_required": b.get("auth_required", True), "source": b.get("source","manual"), "created_at": datetime.utcnow().isoformat()+"Z"}
                if pid not in db_endpoints: db_endpoints[pid] = []
                db_endpoints[pid].append(ep)
                return self.json(ep, 201)

        # Delete endpoint: /api/v1/endpoints/{id} or /api/endpoints/{id}
        if len(parts) >= 2 and parts[-2] == 'endpoints' and method == 'DELETE':
            epid = parts[-1]
            for pid in db_endpoints:
                db_endpoints[pid] = [e for e in db_endpoints[pid] if e["id"] != epid]
            return self.json({"message": "Endpoint deleted"})

        # Import OpenAPI (Module 06): /api/v1/projects/{id}/import/openapi
        if len(parts) >= 4 and parts[-2] == 'import' and parts[-1] == 'openapi' and parts[-4] == 'projects':
            pid = parts[-3]
            b = self.body()
            content = b.get("spec_content", "{}")
            try: spec = json.loads(content)
            except: spec = {}
            imported = []
            paths = spec.get("paths", {})
            for path, methods in paths.items():
                for m, details in methods.items():
                    if m.lower() in ["get","post","put","delete","patch"]:
                        ep = {"id": f"ep-{uuid.uuid4()}", "project_id": pid, "path": path, "method": m.upper(), "summary": details.get("summary", f"{m.upper()} {path}"), "auth_required": bool(details.get("security")), "source": "openapi", "created_at": datetime.utcnow().isoformat()+"Z"}
                        imported.append(ep)
            if pid not in db_endpoints: db_endpoints[pid] = []
            db_endpoints[pid].extend(imported)
            return self.json({"message": f"Successfully imported {len(imported)} endpoints.", "endpoints_imported": len(imported), "endpoints": imported}, 201)

        # Import Postman (Module 07): /api/v1/projects/{id}/import/postman
        if len(parts) >= 4 and parts[-2] == 'import' and parts[-1] == 'postman' and parts[-4] == 'projects':
            pid = parts[-3]
            b = self.body()
            content = b.get("collection_content", "{}")
            try: data = json.loads(content)
            except: data = {}
            imported = []
            def parse_items(items):
                for item in items:
                    if "item" in item: parse_items(item["item"])
                    elif "request" in item:
                        req = item["request"]
                        url = req.get("url", {})
                        p_str = "/" + "/".join(url.get("path", [])) if isinstance(url, dict) else "/"
                        ep = {"id": f"ep-{uuid.uuid4()}", "project_id": pid, "path": p_str, "method": req.get("method","GET").upper(), "summary": item.get("name",""), "auth_required": bool(req.get("auth")), "source": "postman", "created_at": datetime.utcnow().isoformat()+"Z"}
                        imported.append(ep)
            parse_items(data.get("item", []))
            if pid not in db_endpoints: db_endpoints[pid] = []
            db_endpoints[pid].extend(imported)
            return self.json({"message": f"Imported {len(imported)} endpoints.", "endpoints_imported": len(imported), "endpoints": imported}, 201)

        # Spider Crawl (Module 08): /api/v1/projects/{id}/crawl
        if len(parts) >= 3 and parts[-1] == 'crawl' and parts[-3] == 'projects':
            pid = parts[-2]
            crawled = [
                {"id": f"ep-{uuid.uuid4()}", "project_id": pid, "path": "/api/v1/health", "method": "GET", "summary": "Discovered Health Endpoint", "auth_required": False, "source": "crawler", "created_at": datetime.utcnow().isoformat()+"Z"},
                {"id": f"ep-{uuid.uuid4()}", "project_id": pid, "path": "/api/v1/users", "method": "GET", "summary": "Discovered Users Endpoint", "auth_required": True, "source": "crawler", "created_at": datetime.utcnow().isoformat()+"Z"},
                {"id": f"ep-{uuid.uuid4()}", "project_id": pid, "path": "/api/v1/auth/login", "method": "POST", "summary": "Discovered Auth Login", "auth_required": False, "source": "crawler", "created_at": datetime.utcnow().isoformat()+"Z"}
            ]
            if pid not in db_endpoints: db_endpoints[pid] = []
            db_endpoints[pid].extend(crawled)
            return self.json({"message": f"Spider crawl discovered {len(crawled)} endpoints.", "endpoints_imported": len(crawled), "endpoints": crawled}, 201)

        # Auth Profiles (Module 10): /api/v1/projects/{id}/auth-profiles
        if len(parts) >= 3 and parts[-1] == 'auth-profiles' and parts[-3] == 'projects':
            pid = parts[-2]
            if method == 'GET': return self.json(db_auth_profiles.get(pid, []))
            if method == 'POST':
                b = self.body()
                ap = {"id": f"ap-{uuid.uuid4()}", "project_id": pid, "name": b.get("name","Auth Token"), "auth_type": b.get("auth_type","bearer"), "credentials": b.get("credentials",{}), "is_active": True, "created_at": datetime.utcnow().isoformat()+"Z"}
                if pid not in db_auth_profiles: db_auth_profiles[pid] = []
                db_auth_profiles[pid].append(ap)
                return self.json(ap, 201)

        # Delete Auth Profile: /api/v1/auth-profiles/{id}
        if len(parts) >= 2 and parts[-2] == 'auth-profiles' and method == 'DELETE':
            apid = parts[-1]
            for pid in db_auth_profiles:
                db_auth_profiles[pid] = [a for a in db_auth_profiles[pid] if a["id"] != apid]
            return self.json({"message": "Auth profile deleted"})

        if p in ['/api/v1/health', '/api/health', '/health']:
            return self.json({"status": "healthy", "version": "2.0.0"})

        return self.json({"detail": "Not Found"}, 404)

    def do_GET(self):
        p = urlparse(self.path).path
        if p.startswith('/api') or p.startswith('/projects') or p.startswith('/users') or p.startswith('/auth'):
            return self.handle_api('GET')
        if p == '/': self.path = '/index.html'
        return super().do_GET()

    def do_POST(self): return self.handle_api('POST')
    def do_PUT(self): return self.handle_api('PUT')
    def do_DELETE(self): return self.handle_api('DELETE')

if __name__ == '__main__':
    os.chdir(r'd:\google antigravity\api-security-platform\frontend')
    s = HTTPServer(('localhost', 8000), H)
    print("\n  APISec Platform - Demo Server (Phase 1+2 Ready)")
    print("  URL:       http://localhost:8000")
    print("  Inventory: http://localhost:8000/inventory.html\n")
    s.serve_forever()