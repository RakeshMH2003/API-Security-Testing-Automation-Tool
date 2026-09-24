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
            {"id": "targ-1", "project_id": "proj-1", "name": "Staging API Gateway", "base_url": "https://api-staging.cyberstore.local", "environment": "staging", "is_active": True, "created_at": "2026-01-10T10:00:00Z"},
            {"id": "targ-2", "project_id": "proj-1", "name": "Production Gateway", "base_url": "https://api.cyberstore.local", "environment": "production", "is_active": True, "created_at": "2026-01-10T10:00:00Z"}
        ],
        "scope_rules": [
            {"id": "scope-1", "project_id": "proj-1", "rule_type": "include", "pattern": "/api/v1/.*", "description": "Include all v1 endpoints"},
            {"id": "scope-2", "project_id": "proj-1", "rule_type": "exclude", "pattern": "/api/v1/auth/logout", "description": "Exclude logout from scanning"}
        ],
        "rate_limit": {
            "id": "rl-1", "project_id": "proj-1", "max_req_per_sec": 15, "burst_limit": 30, "concurrent_connections": 5
        }
    },
    "proj-2": {
        "id": "proj-2",
        "name": "PayTech Core Gateway",
        "category": "Fintech",
        "description": "Core banking, fund transfers, merchant settlements, and webhook events.",
        "owner_id": "aaaa-bbbb-cccc-dddd",
        "created_at": "2026-01-15T14:30:00Z",
        "updated_at": "2026-01-15T14:30:00Z",
        "targets": [
            {"id": "targ-3", "project_id": "proj-2", "name": "Developer Sandbox", "base_url": "http://localhost:8080", "environment": "localhost", "is_active": True, "created_at": "2026-01-15T14:30:00Z"}
        ],
        "scope_rules": [
            {"id": "scope-3", "project_id": "proj-2", "rule_type": "include", "pattern": "/v2/payments/.*", "description": "Payment microservices"}
        ],
        "rate_limit": {
            "id": "rl-2", "project_id": "proj-2", "max_req_per_sec": 5, "burst_limit": 10, "concurrent_connections": 2
        }
    }
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
        if p in ['/api/v1/auth/register', '/api/auth/register', '/auth/register'] and method == 'POST':
            b = self.body()
            email = (b.get('email') or '').strip().lower()
            pw = b.get('password') or ''
            name = (b.get('full_name') or '').strip()
            if not email or not pw or not name: return self.json({"detail":"All fields required."}, 422)
            if email in db_users: return self.json({"detail":"Email already registered. Please login."}, 409)
            if len(pw) < 8: return self.json({"detail":"Password must be at least 8 characters."}, 422)
            db_users[email] = {"id": str(uuid.uuid4()), "email": email, "password": pw, "full_name": name, "role": "viewer", "is_active": True, "created_at": datetime.utcnow().isoformat()+"Z", "last_login": None}
            return self.json({"message": "Account created! Please login to continue."}, 201)

        if p in ['/api/v1/auth/login', '/api/auth/login', '/auth/login'] and method == 'POST':
            b = self.body()
            email = (b.get('email') or '').strip().lower()
            pw = b.get('password') or ''
            usr = db_users.get(email)
            if not usr or usr['password'] != pw: return self.json({"detail": "Invalid email or password."}, 401)
            tok = f"tok-{uuid.uuid4()}"
            db_tokens[tok] = email
            db_users[email]['last_login'] = datetime.utcnow().isoformat()+"Z"
            r = {k: v for k, v in usr.items() if k != 'password'}
            return self.json({"access_token": tok, "refresh_token": f"ref-{uuid.uuid4()}", "user": r})

        # Protected Routes require User
        if not u and not p.startswith('/css') and not p.startswith('/js') and not p.endswith('.html') and p != '/':
            if p.startswith('/api'): return self.json({"detail": "Not authenticated."}, 401)

        if p in ['/api/v1/auth/me', '/api/auth/me', '/auth/me']:
            if method == 'GET': return self.json({k: v for k, v in u.items() if k != 'password'})
            if method in ['POST', 'PUT']:
                b = self.body()
                if b.get('full_name'): db_users[u['email']]['full_name'] = b['full_name']
                return self.json({k: v for k, v in db_users[u['email']].items() if k != 'password'})

        if p in ['/api/v1/auth/logout', '/api/auth/logout', '/auth/logout'] and method == 'POST':
            a = self.headers.get('Authorization','')
            if a.startswith('Bearer '): db_tokens.pop(a[7:], None)
            return self.json({"message": "Logged out."})

        # --- USERS (RBAC) ---
        if p in ['/api/v1/users', '/api/users', '/users'] and method == 'GET':
            if u['role'] != 'admin': return self.json({"detail": "Admin privileges required."}, 403)
            return self.json([{k: v for k, v in user.items() if k != 'password'} for user in db_users.values()])

        if p.startswith('/api/v1/users/') or p.startswith('/api/users/') or p.startswith('/users/'):
            if u['role'] != 'admin': return self.json({"detail": "Admin privileges required."}, 403)
            parts = [x for x in p.split('/') if x]
            user_id = parts[-2]
            action = parts[-1]
            target_email = next((e for e, data in db_users.items() if data['id'] == user_id), None)
            if not target_email: return self.json({"detail": "User not found."}, 404)
            b = self.body()
            if action == 'role':
                db_users[target_email]['role'] = b.get('role', 'viewer')
                return self.json({"message": "Role updated."})
            elif action == 'status':
                db_users[target_email]['is_active'] = b.get('is_active', True)
                return self.json({"message": "Status updated."})

        # --- PHASE 1: PROJECTS ---
        if p in ['/api/v1/projects', '/api/projects', '/projects']:
            if method == 'GET':
                return self.json(list(db_projects.values()))
            if method == 'POST':
                b = self.body()
                new_id = f"proj-{uuid.uuid4()}"
                new_proj = {
                    "id": new_id,
                    "name": b.get("name", "New Project"),
                    "category": b.get("category", "General"),
                    "description": b.get("description", ""),
                    "owner_id": u["id"],
                    "created_at": datetime.utcnow().isoformat()+"Z",
                    "updated_at": datetime.utcnow().isoformat()+"Z",
                    "targets": [],
                    "scope_rules": [{"id": f"scope-{uuid.uuid4()}", "project_id": new_id, "rule_type": "include", "pattern": "/.*", "description": "Default include all"}],
                    "rate_limit": {"id": f"rl-{uuid.uuid4()}", "project_id": new_id, "max_req_per_sec": 10, "burst_limit": 20, "concurrent_connections": 5}
                }
                db_projects[new_id] = new_proj
                return self.json(new_proj, 201)

        # Single Project operations: /projects/{id}
        parts = [x for x in p.split('/') if x]
        if len(parts) >= 2 and parts[-2] in ['projects', 'v1'] and parts[-1] in db_projects:
            pid = parts[-1]
            if method == 'GET': return self.json(db_projects[pid])
            if method == 'PUT':
                b = self.body()
                if "name" in b: db_projects[pid]["name"] = b["name"]
                if "category" in b: db_projects[pid]["category"] = b["category"]
                if "description" in b: db_projects[pid]["description"] = b["description"]
                db_projects[pid]["updated_at"] = datetime.utcnow().isoformat()+"Z"
                return self.json(db_projects[pid])
            if method == 'DELETE':
                db_projects.pop(pid, None)
                return self.json({"message": "Project deleted successfully"})

        # Sub-resources: /projects/{id}/targets, /projects/{id}/scope, /projects/{id}/rate-limit
        if len(parts) >= 3 and parts[-3] == 'projects' and parts[-2] in db_projects:
            pid = parts[-2]
            sub = parts[-1]
            b = self.body()

            if sub == 'targets' and method == 'POST':
                tid = f"targ-{uuid.uuid4()}"
                targ = {
                    "id": tid, "project_id": pid,
                    "name": b.get("name", "New Target"),
                    "base_url": b.get("base_url", "http://localhost").rstrip('/'),
                    "environment": b.get("environment", "staging").lower(),
                    "is_active": True, "created_at": datetime.utcnow().isoformat()+"Z"
                }
                db_projects[pid]["targets"].append(targ)
                return self.json(targ, 201)

            if sub == 'scope' and method == 'POST':
                sid = f"scope-{uuid.uuid4()}"
                sc = {
                    "id": sid, "project_id": pid,
                    "rule_type": b.get("rule_type", "include").lower(),
                    "pattern": b.get("pattern", "/.*"),
                    "description": b.get("description", "")
                }
                db_projects[pid]["scope_rules"].append(sc)
                return self.json(sc, 201)

            if sub == 'rate-limit' and method == 'PUT':
                rl = db_projects[pid]["rate_limit"]
                rl["max_req_per_sec"] = b.get("max_req_per_sec", rl["max_req_per_sec"])
                rl["burst_limit"] = b.get("burst_limit", rl["burst_limit"])
                rl["concurrent_connections"] = b.get("concurrent_connections", rl["concurrent_connections"])
                return self.json(rl)

        # Target Deletion: /targets/{target_id}
        if len(parts) >= 2 and parts[-2] == 'targets' and method == 'DELETE':
            tid = parts[-1]
            for proj in db_projects.values():
                proj["targets"] = [t for t in proj["targets"] if t["id"] != tid]
            return self.json({"message": "Target deleted successfully"})

        # Scope Deletion: /scope/{rule_id}
        if len(parts) >= 2 and parts[-2] == 'scope' and method == 'DELETE':
            sid = parts[-1]
            for proj in db_projects.values():
                proj["scope_rules"] = [s for s in proj["scope_rules"] if s["id"] != sid]
            return self.json({"message": "Scope rule deleted successfully"})

        # Health
        if p in ['/api/v1/health', '/api/health', '/health']:
            return self.json({"status": "healthy", "version": "1.0.0"})

        return self.json({"detail": "Not found."}, 404)

    def do_GET(self):
        p = urlparse(self.path).path
        if p.startswith('/api') or p.startswith('/projects') or p.startswith('/users') or p.startswith('/auth'):
            return self.handle_api('GET')
        if p == '/': self.path = '/index.html'
        return super().do_GET()

    def do_POST(self):
        return self.handle_api('POST')

    def do_PUT(self):
        return self.handle_api('PUT')

    def do_DELETE(self):
        return self.handle_api('DELETE')

if __name__ == '__main__':
    os.chdir(r'd:\google antigravity\api-security-platform\frontend')
    s = HTTPServer(('localhost', 8000), H)
    print("\n  APISec Platform - Demo Server (Phase 1 Ready)")
    print("  URL:      http://localhost:8000")
    print("  Admin:    admin@security.local / Admin@1234")
    print("  Projects: http://localhost:8000/projects.html\n")
    s.serve_forever()
