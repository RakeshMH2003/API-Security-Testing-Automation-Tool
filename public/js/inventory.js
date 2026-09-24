let allEndpoints = [];
let currentProjectId = null;

document.addEventListener('DOMContentLoaded', () => {
  requireAuth();
  const user = getCurrentUser();
  if (user) {
    document.getElementById('sidebar-name').textContent = user.full_name;
    document.getElementById('sidebar-avatar').textContent = user.full_name.charAt(0).toUpperCase();
    document.getElementById('sidebar-role-badge').innerHTML = `<span class="badge badge-info" style="font-size:0.65rem;">${user.role}</span>`;
    if (user.role === 'admin') document.querySelectorAll('.admin-only').forEach(el => el.classList.remove('hidden'));
  }
  loadProjectsDropdown();
  updateCredentialFields();
  document.getElementById('add-auth-form').addEventListener('submit', saveAuthProfile);
});

async function loadProjectsDropdown() {
  try {
    const projects = await api.getProjects();
    const sel = document.getElementById('project-select');
    projects.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.id; opt.textContent = p.name;
      sel.appendChild(opt);
    });
  } catch(e) { showToast(e.message, 'error'); }
}

function onProjectChanged() {
  currentProjectId = document.getElementById('project-select').value;
  if (!currentProjectId) return;
  loadInventory();
  loadAuthProfiles();
}

async function loadInventory() {
  if (!currentProjectId) { showToast('Please select a project first.', 'error'); return; }
  document.getElementById('endpoint-inventory').innerHTML = `<div style="padding:2rem; text-align:center;"><i class="fa-solid fa-spinner fa-spin fa-2x text-muted"></i></div>`;
  try {
    allEndpoints = await api.getProjectEndpoints(currentProjectId);
    renderEndpoints(allEndpoints);
    updateStats(allEndpoints);
  } catch(e) {
    document.getElementById('endpoint-inventory').innerHTML = `<div style="padding:2rem; text-align:center; color:var(--danger-color);">${e.message}</div>`;
  }
}

function updateStats(endpoints) {
  document.getElementById('stat-total').textContent = endpoints.length;
  document.getElementById('stat-get').textContent = endpoints.filter(e => e.method === 'GET').length;
  document.getElementById('stat-post').textContent = endpoints.filter(e => ['POST','PUT','PATCH','DELETE'].includes(e.method)).length;
  document.getElementById('stat-auth').textContent = endpoints.filter(e => !e.auth_required).length;
}

function renderEndpoints(endpoints) {
  const container = document.getElementById('endpoint-inventory');
  if (!endpoints.length) {
    container.innerHTML = `<div style="padding:3rem; text-align:center; color:var(--text-muted);">
      <i class="fa-solid fa-inbox fa-2x" style="margin-bottom:1rem;"></i>
      <p>No endpoints in this project yet.<br>Import from OpenAPI, Postman, or run a Spider Crawl above.</p>
    </div>`;
    return;
  }
  container.innerHTML = '';
  endpoints.forEach(ep => {
    const div = document.createElement('div');
    div.className = 'ep-row';
    div.innerHTML = `
      <span class="method-badge method-${ep.method}">${ep.method}</span>
      <div style="flex:1; min-width:0;">
        <div class="ep-path">${ep.path}</div>
        <div class="ep-summary">${ep.summary || ''}</div>
      </div>
      <span class="source-badge source-${ep.source}">${ep.source}</span>
      ${ep.auth_required ? '' : '<span class="badge badge-critical" style="font-size:0.65rem;">No Auth</span>'}
      <button class="btn btn-outline btn-sm text-danger" onclick="deleteEndpointConfirm('${ep.id}')"><i class="fa-solid fa-trash"></i></button>
    `;
    container.appendChild(div);
  });
}

function filterEndpoints() {
  const q = document.getElementById('search-endpoints').value.toLowerCase();
  const filtered = allEndpoints.filter(e => e.path.toLowerCase().includes(q) || (e.summary||'').toLowerCase().includes(q) || e.method.toLowerCase().includes(q));
  renderEndpoints(filtered);
}

// --- Module 06: OpenAPI Import ---
function loadSampleOpenAPI() {
  const sample = JSON.stringify({
    openapi: "3.0.0",
    info: { title: "Sample API", version: "1.0.0" },
    security: [{ bearerAuth: [] }],
    paths: {
      "/api/v1/users": { get: { summary: "List all users", operationId: "listUsers" }, post: { summary: "Create user", operationId: "createUser" } },
      "/api/v1/users/{id}": { get: { summary: "Get user by ID", parameters: [{ name: "id", in: "path", required: true, schema: { type: "string" } }] }, put: { summary: "Update user" }, delete: { summary: "Delete user" } },
      "/api/v1/orders": { get: { summary: "List orders" }, post: { summary: "Create order" } },
      "/api/v1/payments/process": { post: { summary: "Process payment", security: [] } },
      "/api/v1/products": { get: { summary: "List products", security: [] } },
      "/api/v1/auth/login": { post: { summary: "User login", security: [] } },
      "/api/v1/auth/logout": { post: { summary: "User logout" } }
    }
  }, null, 2);
  document.getElementById('openapi-input').value = sample;
}

async function importOpenAPI() {
  if (!currentProjectId) { showToast('Select a project first!', 'error'); return; }
  const content = document.getElementById('openapi-input').value.trim();
  if (!content) { showToast('Paste an OpenAPI spec first.', 'error'); return; }
  const btn = document.getElementById('import-openapi-btn');
  showLoading(btn);
  try {
    const result = await api.importOpenAPI(currentProjectId, content);
    showToast(`✅ Imported ${result.endpoints_imported} endpoints from OpenAPI!`);
    document.getElementById('openapi-input').value = '';
    await loadInventory();
  } catch(e) { showToast(e.message, 'error'); }
  finally { hideLoading(btn, '<i class="fa-solid fa-upload"></i> Import OpenAPI Spec'); }
}

// --- Module 07: Postman Import ---
async function importPostman() {
  if (!currentProjectId) { showToast('Select a project first!', 'error'); return; }
  const content = document.getElementById('postman-input').value.trim();
  if (!content) { showToast('Paste a Postman collection first.', 'error'); return; }
  const btn = document.getElementById('import-postman-btn');
  showLoading(btn);
  try {
    const result = await api.importPostman(currentProjectId, content);
    showToast(`✅ Imported ${result.endpoints_imported} endpoints from Postman!`);
    document.getElementById('postman-input').value = '';
    await loadInventory();
  } catch(e) { showToast(e.message, 'error'); }
  finally { hideLoading(btn, '<i class="fa-solid fa-upload"></i> Import Postman Collection'); }
}

// --- Module 08: Spider Crawl ---
async function startCrawl() {
  if (!currentProjectId) { showToast('Select a project first!', 'error'); return; }
  const url = document.getElementById('crawler-url').value.trim();
  if (!url) { showToast('Enter a target URL to crawl.', 'error'); return; }
  const btn = document.getElementById('crawl-btn');
  showLoading(btn);
  try {
    const result = await api.spiderCrawl(currentProjectId, url);
    showToast(`🕷️ Crawl complete! Found ${result.endpoints_imported} endpoints.`);
    await loadInventory();
  } catch(e) { showToast(e.message, 'error'); }
  finally { hideLoading(btn, '<i class="fa-solid fa-spider"></i> Start Spider Crawl'); }
}

// --- Module 10: Auth Profiles ---
function updateCredentialFields() {
  const type = document.getElementById('auth-type')?.value || 'bearer';
  const el = document.getElementById('cred-fields');
  if (!el) return;
  const fields = {
    bearer: `<label class="form-label" style="font-size:0.75rem;">Bearer Token (JWT)</label><input id="cred-token" class="form-input" placeholder="eyJhbGciOi..." required>`,
    apikey: `<div style="display:grid; grid-template-columns:1fr 2fr; gap:0.5rem;"><div><label class="form-label" style="font-size:0.75rem;">Header Name</label><input id="cred-header" class="form-input" placeholder="X-API-Key"></div><div><label class="form-label" style="font-size:0.75rem;">API Key Value</label><input id="cred-key" class="form-input" placeholder="sk-xxxxxxxx"></div></div>`,
    basic: `<div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem;"><div><label class="form-label" style="font-size:0.75rem;">Username</label><input id="cred-user" class="form-input" placeholder="admin"></div><div><label class="form-label" style="font-size:0.75rem;">Password</label><input id="cred-pass" class="form-input" type="password" placeholder="••••••••"></div></div>`,
    oauth2: `<label class="form-label" style="font-size:0.75rem;">OAuth 2.0 Access Token</label><input id="cred-oauth" class="form-input" placeholder="Bearer ya29.a0AfH...">`
  };
  el.innerHTML = fields[type] || fields.bearer;
}

function getCredentials() {
  const type = document.getElementById('auth-type').value;
  if (type === 'bearer') return { token: document.getElementById('cred-token').value };
  if (type === 'apikey') return { header_name: document.getElementById('cred-header').value, key: document.getElementById('cred-key').value };
  if (type === 'basic') return { username: document.getElementById('cred-user').value, password: document.getElementById('cred-pass').value };
  if (type === 'oauth2') return { token: document.getElementById('cred-oauth').value };
  return {};
}

async function saveAuthProfile(e) {
  e.preventDefault();
  if (!currentProjectId) { showToast('Select a project first!', 'error'); return; }
  try {
    await api.createAuthProfile(currentProjectId, {
      name: document.getElementById('auth-name').value,
      auth_type: document.getElementById('auth-type').value,
      credentials: getCredentials(),
      is_active: true
    });
    showToast('Auth profile saved!');
    e.target.reset();
    toggleAddAuthForm();
    loadAuthProfiles();
  } catch(err) { showToast(err.message, 'error'); }
}

async function loadAuthProfiles() {
  if (!currentProjectId) return;
  const container = document.getElementById('auth-profiles-list');
  try {
    const profiles = await api.getAuthProfiles(currentProjectId);
    if (!profiles.length) { container.innerHTML = `<p class="text-muted text-sm">No auth profiles configured.</p>`; return; }
    container.innerHTML = '';
    profiles.forEach(p => {
      const div = document.createElement('div');
      div.style = 'display:flex; justify-content:space-between; align-items:center; padding:0.75rem; background:rgba(255,255,255,0.03); border:1px solid var(--border-color); border-radius:8px; margin-bottom:0.5rem;';
      div.innerHTML = `
        <div>
          <span class="badge badge-info" style="font-size:0.7rem;">${p.auth_type.toUpperCase()}</span>
          <strong style="margin-left:0.5rem;">${p.name}</strong>
        </div>
        <button class="btn btn-outline btn-sm text-danger" onclick="deleteAuthProfileConfirm('${p.id}')"><i class="fa-solid fa-trash"></i></button>
      `;
      container.appendChild(div);
    });
  } catch(e) { container.innerHTML = `<span style="color:var(--danger-color);">${e.message}</span>`; }
}

function toggleAddAuthForm() {
  const box = document.getElementById('add-auth-box');
  box.style.display = box.style.display === 'none' ? 'block' : 'none';
}

async function deleteEndpointConfirm(id) {
  if (confirm('Delete this endpoint from the inventory?')) {
    try {
      await api.deleteEndpoint(id);
      showToast('Endpoint deleted');
      loadInventory();
    } catch(e) { showToast(e.message, 'error'); }
  }
}

async function deleteAuthProfileConfirm(id) {
  if (confirm('Delete this auth profile?')) {
    try {
      await api.deleteAuthProfile(id);
      showToast('Auth profile deleted');
      loadAuthProfiles();
    } catch(e) { showToast(e.message, 'error'); }
  }
}

function switchTab(event, tabId) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  event.currentTarget.classList.add('active');
  document.getElementById(tabId).classList.add('active');
}
