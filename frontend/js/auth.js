function isAuthenticated() {
  return !!localStorage.getItem('access_token');
}

function getCurrentUser() {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
}

function setCurrentUser(user) {
  localStorage.setItem('user', JSON.stringify(user));
}

function clearCurrentUser() {
  localStorage.removeItem('user');
}

function redirectToLogin() {
  window.location.href = 'login.html';
}

function redirectToDashboard() {
  window.location.href = 'dashboard.html';
}

function requireAuth() {
  if (!isAuthenticated()) {
    redirectToLogin();
  }
}

function requireGuest() {
  if (isAuthenticated()) {
    redirectToDashboard();
  }
}

function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  const icon = type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle';
  
  toast.innerHTML = `
    <i class="fa-solid fa-${icon}"></i>
    <span>${message}</span>
  `;
  
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'fadeOut 0.3s forwards';
    setTimeout(() => {
      if(container.contains(toast)) container.removeChild(toast);
    }, 300);
  }, 3000);
}

function checkPasswordStrength(password) {
  let score = 0;
  if (!password) return { score: 0, label: '', color: 'var(--border-color)' };
  
  if (password.length > 7) score += 1;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score += 1;
  if (/\d/.test(password)) score += 1;
  if (/[^A-Za-z0-9]/.test(password)) score += 1;
  
  const colors = ['var(--border-color)', 'var(--danger-color)', 'var(--warning-color)', 'var(--info-color)', 'var(--success-color)'];
  const labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
  
  return {
    score: score,
    label: labels[score],
    color: colors[score]
  };
}

async function handleLogout() {
  api.logout();
  clearCurrentUser();
  redirectToLogin();
}
