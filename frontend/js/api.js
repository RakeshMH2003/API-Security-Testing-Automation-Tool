const API_BASE = '/api';

class ApiClient {
  constructor() {
    this.baseUrl = API_BASE;
  }

  setToken(token) { localStorage.setItem('access_token', token); }
  getToken() { return localStorage.getItem('access_token'); }
  clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  async request(method, endpoint, body = null, requiresAuth = true) {
    const url = this.baseUrl + endpoint;
    const headers = { 'Content-Type': 'application/json' };

    if (requiresAuth) {
      const token = this.getToken();
      if (token) headers['Authorization'] = 'Bearer ' + token;
    }

    const config = { method, headers };
    if (body !== null) config.body = JSON.stringify(body);

    let response;
    try {
      response = await fetch(url, config);
    } catch (networkErr) {
      throw new Error('Cannot connect to server. Make sure the backend is running.');
    }

    if (response.status === 401 && requiresAuth) {
      this.clearTokens();
      window.location.href = 'login.html';
      throw new Error('Session expired. Please login again.');
    }

    let data;
    try {
      data = await response.json();
    } catch {
      throw new Error('Invalid response from server.');
    }

    if (!response.ok) {
      throw new Error(data.detail || data.message || ('Error ' + response.status));
    }

    return data;
  }

  async get(endpoint, requiresAuth = true) { return this.request('GET', endpoint, null, requiresAuth); }
  async post(endpoint, body, requiresAuth = false) { return this.request('POST', endpoint, body, requiresAuth); }
  async put(endpoint, body, requiresAuth = true) { return this.request('PUT', endpoint, body, requiresAuth); }
  async delete(endpoint, requiresAuth = true) { return this.request('DELETE', endpoint, null, requiresAuth); }

  // --- Auth Methods ---
  async login(email, password) {
    const data = await this.post('/auth/login', { email, password }, false);
    this.setToken(data.access_token);
    if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token);
    return data.user;
  }

  async register(email, password, full_name) {
    return await this.post('/auth/register', { email, password, full_name }, false);
  }

  async logout() {
    try { await this.post('/auth/logout', {}, true); } catch {}
    this.clearTokens();
  }

  async getMe() { return this.get('/auth/me', true); }
  async updateProfile(data) { return this.put('/auth/me', data, true); }
  async changePassword(current_password, new_password) {
    return this.put('/auth/password', { current_password, new_password }, true);
  }

  // --- Admin RBAC Methods ---
  async getUsers() { return this.get('/users', true); }
  async updateUserRole(userId, role) { return this.put('/users/' + userId + '/role', { role }, true); }
  async updateUserStatus(userId, is_active) { return this.put('/users/' + userId + '/status', { is_active }, true); }

  // --- Phase 1: Projects, Targets, Scope & Rate Limit ---
  async getProjects() { return this.get('/projects', true); }
  async createProject(data) { return this.post('/projects', data, true); }
  async getProjectDetails(id) { return this.get('/projects/' + id, true); }
  async updateProject(id, data) { return this.put('/projects/' + id, data, true); }
  async deleteProject(id) { return this.delete('/projects/' + id, true); }

  async addTarget(projectId, data) { return this.post('/projects/' + projectId + '/targets', data, true); }
  async deleteTarget(targetId) { return this.delete('/targets/' + targetId, true); }

  async addScopeRule(projectId, data) { return this.post('/projects/' + projectId + '/scope', data, true); }
  async deleteScopeRule(ruleId) { return this.delete('/scope/' + ruleId, true); }

  async updateRateLimit(projectId, data) { return this.put('/projects/' + projectId + '/rate-limit', data, true); }

  // --- Phase 2: API Discovery & Inventory (Modules 06-10) ---
  async getProjectEndpoints(projectId) { return this.get('/v1/projects/' + projectId + '/endpoints', true); }
  async addEndpoint(projectId, data) { return this.post('/v1/projects/' + projectId + '/endpoints', data, true); }
  async deleteEndpoint(endpointId) { return this.delete('/v1/endpoints/' + endpointId, true); }

  async importOpenAPI(projectId, specContent) { return this.post('/v1/projects/' + projectId + '/import/openapi', { spec_content: specContent }, true); }
  async importPostman(projectId, collectionContent) { return this.post('/v1/projects/' + projectId + '/import/postman', { collection_content: collectionContent }, true); }
  async spiderCrawl(projectId, targetUrl, depth = 2) { return this.post('/v1/projects/' + projectId + '/crawl', { target_url: targetUrl, depth }, true); }

  async getAuthProfiles(projectId) { return this.get('/v1/projects/' + projectId + '/auth-profiles', true); }
  async createAuthProfile(projectId, data) { return this.post('/v1/projects/' + projectId + '/auth-profiles', data, true); }
  async deleteAuthProfile(profileId) { return this.delete('/v1/auth-profiles/' + profileId, true); }
}

const api = new ApiClient();