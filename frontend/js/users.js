document.addEventListener('DOMContentLoaded', () => {
  requireAuth();
  
  const user = getCurrentUser();
  if (user.role !== 'admin') {
    showToast('Unauthorized. Admin access required.', 'error');
    setTimeout(() => { window.location.href = 'dashboard.html'; }, 1500);
    return;
  }

  // Populate sidebar
  document.getElementById('sidebar-name').textContent = user.full_name;
  document.getElementById('sidebar-avatar').textContent = user.full_name.charAt(0).toUpperCase();
  document.getElementById('sidebar-role-badge').innerHTML = `<span class="badge badge-info" style="font-size:0.65rem;">${user.role}</span>`;
  
  loadUsers();
});

async function loadUsers() {
  const tbody = document.getElementById('users-tbody');
  tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;"><i class="fa-solid fa-spinner fa-spin"></i> Loading users...</td></tr>';
  
  try {
    const users = await api.getUsers();
    renderUsers(users);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--danger-color);">${err.message}</td></tr>`;
    showToast(err.message, 'error');
  }
}

function renderUsers(users) {
  const tbody = document.getElementById('users-tbody');
  tbody.innerHTML = '';
  
  const currentUser = getCurrentUser();

  users.forEach(u => {
    const isMe = u.email === currentUser.email;
    const date = new Date(u.created_at).toLocaleDateString();
    const statusClass = u.is_active ? 'status-active' : 'status-inactive';
    const statusText = u.is_active ? 'Active' : 'Disabled';
    
    // Role options
    const roles = ['viewer', 'developer', 'analyst', 'admin'];
    let roleSelect = `<select class="role-select" onchange="changeRole('${u.id}', this.value)" ${isMe ? 'disabled' : ''}>`;
    roles.forEach(r => {
      roleSelect += `<option value="${r}" ${u.role === r ? 'selected' : ''}>${r.charAt(0).toUpperCase() + r.slice(1)}</option>`;
    });
    roleSelect += `</select>`;

    // Status toggle button
    const actionBtn = isMe ? `<span class="text-muted text-sm">Current User</span>` : 
      `<button class="btn ${u.is_active ? 'btn-danger' : 'btn-primary'} btn-sm" onclick="toggleStatus('${u.id}', ${!u.is_active})">
        ${u.is_active ? 'Disable' : 'Enable'}
      </button>`;

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>
        <div class="font-semibold">${u.full_name}</div>
        <div class="text-sm text-muted">${u.id.substring(0,8)}...</div>
      </td>
      <td>${u.email}</td>
      <td>${roleSelect}</td>
      <td><span class="status-badge ${statusClass}">${statusText}</span></td>
      <td>${date}</td>
      <td>${actionBtn}</td>
    `;
    tbody.appendChild(tr);
  });
}

async function changeRole(userId, newRole) {
  try {
    await api.updateUserRole(userId, newRole);
    showToast('User role updated successfully');
  } catch (err) {
    showToast(err.message, 'error');
    loadUsers(); // reload to revert select
  }
}

async function toggleStatus(userId, newStatus) {
  try {
    await api.updateUserStatus(userId, newStatus);
    showToast(`User account ${newStatus ? 'enabled' : 'disabled'}`);
    loadUsers(); // reload to update UI
  } catch (err) {
    showToast(err.message, 'error');
  }
}
