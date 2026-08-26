function formatDate(isoString) {
  const date = new Date(isoString);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatDateTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
}

function timeAgo(isoString) {
  const date = new Date(isoString);
  const now = new Date();
  const seconds = Math.round((now - date) / 1000);
  
  const minutes = Math.round(seconds / 60);
  const hours = Math.round(minutes / 60);
  const days = Math.round(hours / 24);
  
  if (seconds < 60) return 'just now';
  if (minutes < 60) return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
  if (hours < 24) return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
  if (days < 30) return `${days} day${days !== 1 ? 's' : ''} ago`;
  return formatDate(isoString);
}

function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

function truncate(str, length) {
  if (!str) return '';
  if (str.length <= length) return str;
  return str.substring(0, length) + '...';
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied to clipboard', 'info');
  }).catch(err => {
    console.error('Failed to copy', err);
    showToast('Failed to copy', 'error');
  });
}

function debounce(fn, delay) {
  let timeoutId;
  return function(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
}

function showLoading(element) {
  element.dataset.originalText = element.innerHTML;
  element.innerHTML = '<span class="spinner"></span>';
  element.disabled = true;
}

function hideLoading(element) {
  if (element.dataset.originalText) {
    element.innerHTML = element.dataset.originalText;
  }
  element.disabled = false;
}

function createElement(tag, className, innerHTML) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (innerHTML) el.innerHTML = innerHTML;
  return el;
}

function showModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
  }
}

function hideModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('hidden');
    modal.style.display = 'none';
  }
}

function getRoleBadgeHTML(role) {
  const roleColors = {
    'admin': 'badge-critical',
    'security_engineer': 'badge-high',
    'developer': 'badge-medium',
    'viewer': 'badge-info'
  };
  const colorClass = roleColors[role] || 'badge-info';
  return `<span class="badge ${colorClass}">${role.replace('_', ' ')}</span>`;
}

function getSeverityBadgeHTML(severity) {
  const sevLower = severity.toLowerCase();
  const colorClass = `badge-${sevLower}`;
  return `<span class="badge ${colorClass}">${capitalize(severity)}</span>`;
}
