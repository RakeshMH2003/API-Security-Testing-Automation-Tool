const API_BASE = 'http://localhost:8000/api/v1';

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
    const url = `${this.baseUrl}${endpoint}`;
    const headers = { 'Content-Type': 'application/json' };

    if (requiresAuth) {
      const token = this.getToken();
      if (token) headers['Authorization'] = `Bearer ${token}`;
    }

    const config = { method, headers };
    if (body !== null) config.body = JSON.stringify(body);

    let response;
    try {
      response = await fetch(url, config);
    } catch (networkErr) {
      throw new Error('Cannot connect to server. Make sure the backend is running.');
    }

    // Handle 401 — only redirect on protected routes
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
      throw new Error(data.detail || data.message || `Error ${response.status}`);
    }

    return data;
  }

  async get(endpoint, requiresAuth = true) { return this.request('GET', endpoint, null, requiresAuth); }
  async post(endpoint, body, requiresAuth = false) { return this.request('POST', endpoint, body, requiresAuth); }
  async put(endpoint, body, requiresAuth = true) { return this.request('PUT', endpoint, body, requiresAuth); }
  async delete(endpoint, requiresAuth = true) { return this.request('DELETE', endpoint, null, requiresAuth); }

  // --- Auth Methods ---

  // LOGIN: sends JSON {email, password}
  async login(email, password) {
    const data = await this.post('/auth/login', { email, password }, false);
    // Store token and user
    this.setToken(data.access_token);
    if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token);
    return data.user;
  }

  // REGISTER: sends JSON {email, password, full_name}
  // Does NOT auto-login — returns success message only
  async register(email, password, full_name) {
    return await this.post('/auth/register', { email, password, full_name }, false);
  }

  // LOGOUT: calls backend then clears tokens
  async logout() {
    try {
      await this.post('/auth/logout', {}, true);
    } catch {}
    this.clearTokens();
  }

  async getMe() { return this.get('/auth/me', true); }
  async updateProfile(data) { return this.put('/auth/me', data, true); }
  async changePassword(current_password, new_password) {
    return this.put('/auth/password', { current_password, new_password }, true);
  }
}

const api = new ApiClient();
