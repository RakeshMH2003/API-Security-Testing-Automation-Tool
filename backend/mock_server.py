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
    def do_POST(self):
        p=urlparse(self.path).path
        if p=='/api/v1/auth/register':
            b=self.body()
            email=(b.get('email') or '').strip().lower()
            pw=b.get('password') or ''
            name=(b.get('full_name') or '').strip()
            if not email or not pw or not name: return self.json({"detail":"All fields required."},422)
            if email in db_users: return self.json({"detail":"Email already registered. Please login."},409)
            if len(pw)<8: return self.json({"detail":"Password must be at least 8 characters."},422)
            db_users[email]={"id":str(uuid.uuid4()),"email":email,"password":pw,"full_name":name,"role":"viewer","is_active":True,"created_at":datetime.utcnow().isoformat()+"Z","last_login":None}
            return self.json({"message":"Account created! Please login to continue."},201)
        elif p=='/api/v1/auth/login':
            b=self.body()
            email=(b.get('email') or '').strip().lower()
            pw=b.get('password') or ''
            u=db_users.get(email)
            if not u or u['password']!=pw: return self.json({"detail":"Invalid email or password."},401)
            tok=f"tok-{uuid.uuid4()}"
            db_tokens[tok]=email
            db_users[email]['last_login']=datetime.utcnow().isoformat()+"Z"
            r={k:v for k,v in u.items() if k!='password'}
            return self.json({"access_token":tok,"refresh_token":f"ref-{uuid.uuid4()}","user":r})
        elif p=='/api/v1/auth/logout':
            a=self.headers.get('Authorization','')
            if a.startswith('Bearer '): db_tokens.pop(a[7:],None)
            return self.json({"message":"Logged out."})
        elif p=='/api/v1/auth/me':
            u=self.current_user()
            if not u: return self.json({"detail":"Not authenticated."},401)
            b=self.body()
            if b.get('full_name'): db_users[u['email']]['full_name']=b['full_name']
            return self.json({k:v for k,v in db_users[u['email']].items() if k!='password'})
        elif p.startswith('/api/v1/users/'):
            u=self.current_user()
            if not u or u['role'] != 'admin': return self.json({"detail":"Admin privileges required."},403)
            
            user_id = p.split('/')[-2]
            action = p.split('/')[-1]
            
            target_email = next((e for e, data in db_users.items() if data['id'] == user_id), None)
            if not target_email: return self.json({"detail":"User not found."},404)
            
            if action == 'role':
                b=self.body()
                new_role = b.get('role')
                if new_role not in ['admin', 'analyst', 'developer', 'viewer']:
                    return self.json({"detail":"Invalid role."},422)
                if target_email == u['email']:
                    return self.json({"detail":"Cannot change your own role."},400)
                db_users[target_email]['role'] = new_role
                return self.json({"message":"Role updated successfully.", "role": new_role})
                
            elif action == 'status':
                b=self.body()
                is_active = b.get('is_active')
                if target_email == u['email']:
                    return self.json({"detail":"Cannot disable your own account."},400)
                db_users[target_email]['is_active'] = is_active
                return self.json({"message":"Status updated successfully.", "is_active": is_active})
                
            return self.json({"detail":"Not found."},404)
        elif p=='/api/v1/auth/password':
            u=self.current_user()
            if not u: return self.json({"detail":"Not authenticated."},401)
            b=self.body()
            if u['password']!=b.get('current_password',''): return self.json({"detail":"Current password is incorrect."},400)
            np=b.get('new_password','')
            if len(np)<8: return self.json({"detail":"Password must be at least 8 chars."},422)
            db_users[u['email']]['password']=np
            return self.json({"message":"Password updated."})
        else: return self.json({"detail":"Not found."},404)
    def do_PUT(self): self.do_POST()
    def do_GET(self):
        p=urlparse(self.path).path
        if p=='/api/v1/users':
            u=self.current_user()
            if not u or u['role'] != 'admin': return self.json({"detail":"Admin privileges required."},403)
            users_list = [{k:v for k,v in user.items() if k!='password'} for user in db_users.values()]
            return self.json(users_list)
        if p=='/api/v1/auth/me':
            u=self.current_user()
            if not u: return self.json({"detail":"Not authenticated."},401)
            return self.json({k:v for k,v in u.items() if k!='password'})
        if p=='/api/v1/health': return self.json({"status":"healthy"})
        if p=='/': self.path='/index.html'
        return super().do_GET()

if __name__=='__main__':
    os.chdir(r'd:\google antigravity\api-security-platform\frontend')
    s=HTTPServer(('localhost',8000),H)
    print("\n  APISec Platform - Demo Server")
    print("  URL:      http://localhost:8000")
    print("  Admin:    admin@security.local / Admin@1234")
    print("  Register: http://localhost:8000/register.html")
    print("  Ctrl+C to stop\n")
    s.serve_forever()
