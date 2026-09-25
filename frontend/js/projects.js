// Projects & Target Management JS

let currentProject = null;

document.addEventListener('DOMContentLoaded', () => {
  requireAuth();
  loadProjects();

  const createForm = document.getElementById('create-project-form');
  if (createForm) {
    createForm.addEventListener('submit', handleCreateProject);
  }

  const addTargetForm = document.getElementById('add-target-form');
  if (addTargetForm) {
    addTargetForm.addEventListener('submit', handleAddTarget);
  }

  const addScopeForm = document.getElementById('add-scope-form');
  if (addScopeForm) {
    addScopeForm.addEventListener('submit', handleAddScope);
  }

  const rateLimitForm = document.getElementById('rate-limit-form');
  if (rateLimitForm) {
    rateLimitForm.addEventListener('submit', handleSaveRateLimit);
  }
});

async function loadProjects() {
  const container = document.getElementById('project-cards-container');
  if (!container) return;

  container.innerHTML = `
    <div style="grid-column: 1/-1; text-align: center; padding: 3rem;">
      <i class="fa-solid fa-spinner fa-spin fa-2x text-muted"></i>
      <p class="text-muted mt-2">Loading Projects...</p>
    </div>
  `;

  try {
    const projects = await api.getProjects();
    if (!projects || projects.length === 0) {
      container.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 3rem; background: var(--card-bg); border: 1px dashed var(--border-color); border-radius: 12px;">
          <i class="fa-solid fa-folder-open fa-3x text-muted mb-3"></i>
          <h3>No Security Projects Yet</h3>
          <p class="text-muted text-sm mb-4">Create your first API security workspace to start targeting and scanning endpoints.</p>
          <button class="btn btn-primary" onclick="openCreateProjectModal()"><i class="fa-solid fa-plus"></i> Create First Project</button>
        </div>
      `;
      return;
    }

    container.innerHTML = projects.map(p => `
      <div class="project-card fade-in">
        <div>
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
            <h3 style="margin:0; font-size:1.1rem;">${p.name}</h3>
            <span class="badge badge-info">${p.category || 'General'}</span>
          </div>
          <p class="text-muted text-sm" style="margin-bottom:1rem; min-height:2.5rem;">${p.description || 'No description provided.'}</p>
        </div>

        <div style="border-top:1px solid var(--border-color); padding-top:1rem; display:flex; gap:0.5rem;">
          <button class="btn btn-outline btn-sm w-full" onclick="openManageProjectModal('${p.id}')">
            <i class="fa-solid fa-gear"></i> Setup
          </button>
          <button class="btn btn-primary btn-sm w-full" onclick="triggerStartScan('${p.id}')">
            <i class="fa-solid fa-play"></i> Scan
          </button>
        </div>
      </div>
    `).join('');

  } catch (err) {
    container.innerHTML = `<div style="grid-column:1/-1;" class="alert alert-error">Failed to load projects: ${err.message}</div>`;
  }
}

function openCreateProjectModal() {
  openModal('create-project-modal');
}

async function handleCreateProject(e) {
  e.preventDefault();
  const name = document.getElementById('proj-name').value;
  const category = document.getElementById('proj-category').value;
  const description = document.getElementById('proj-desc').value;

  try {
    await api.createProject({ name, category, description });
    showToast('Project created successfully!', 'success');
    closeModal('create-project-modal');
    document.getElementById('create-project-form').reset();
    loadProjects();
  } catch (err) {
    showToast('Failed to create project: ' + err.message, 'error');
  }
}

async function openManageProjectModal(projectId) {
  try {
    currentProject = await api.getProjectDetails(projectId);
    document.getElementById('m-proj-name').textContent = currentProject.name;
    document.getElementById('m-proj-category').textContent = currentProject.category || 'General';

    renderTargetsList();
    renderScopeList();

    if (currentProject.rate_limit) {
      document.getElementById('rl-max-req').value = currentProject.rate_limit.max_requests_per_sec || 50;
      document.getElementById('rl-burst').value = currentProject.rate_limit.burst_limit || 100;
      document.getElementById('rl-concurrent').value = currentProject.rate_limit.concurrent_connections || 10;
    }

    openModal('manage-project-modal');
  } catch (err) {
    showToast('Error loading project details: ' + err.message, 'error');
  }
}

function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

  event.target.classList.add('active');
  document.getElementById(tabId).classList.add('active');
}

function toggleAddTargetForm() {
  const box = document.getElementById('add-target-box');
  box.style.display = box.style.display === 'none' ? 'block' : 'none';
}

function toggleAddScopeForm() {
  const box = document.getElementById('add-scope-box');
  box.style.display = box.style.display === 'none' ? 'block' : 'none';
}

async function handleAddTarget(e) {
  e.preventDefault();
  if (!currentProject) return;

  const data = {
    name: document.getElementById('targ-name').value,
    environment: document.getElementById('targ-env').value,
    base_url: document.getElementById('targ-url').value
  };

  try {
    await api.addTarget(currentProject.id, data);
    showToast('Target endpoint saved!', 'success');
    toggleAddTargetForm();
    document.getElementById('add-target-form').reset();
    currentProject = await api.getProjectDetails(currentProject.id);
    renderTargetsList();
  } catch (err) {
    showToast('Failed to add target: ' + err.message, 'error');
  }
}

async function handleAddScope(e) {
  e.preventDefault();
  if (!currentProject) return;

  const data = {
    rule_type: document.getElementById('scope-type').value,
    pattern: document.getElementById('scope-pattern').value,
    description: document.getElementById('scope-desc').value
  };

  try {
    await api.addScopeRule(currentProject.id, data);
    showToast('Scope rule saved!', 'success');
    toggleAddScopeForm();
    document.getElementById('add-scope-form').reset();
    currentProject = await api.getProjectDetails(currentProject.id);
    renderScopeList();
  } catch (err) {
    showToast('Failed to add scope rule: ' + err.message, 'error');
  }
}

async function handleSaveRateLimit(e) {
  e.preventDefault();
  if (!currentProject) return;

  const data = {
    max_requests_per_sec: parseInt(document.getElementById('rl-max-req').value),
    burst_limit: parseInt(document.getElementById('rl-burst').value),
    concurrent_connections: parseInt(document.getElementById('rl-concurrent').value)
  };

  try {
    await api.updateRateLimit(currentProject.id, data);
    showToast('Rate limit settings saved!', 'success');
  } catch (err) {
    showToast('Failed to save rate limit: ' + err.message, 'error');
  }
}

function renderTargetsList() {
  const container = document.getElementById('targets-list-container');
  if (!currentProject.targets || currentProject.targets.length === 0) {
    container.innerHTML = '<p class="text-muted text-sm" style="text-align:center; padding:1.5rem;">No target environments configured yet.</p>';
    return;
  }

  container.innerHTML = currentProject.targets.map(t => `
    <div class="target-item">
      <div>
        <strong>${t.name}</strong> <span class="env-badge env-${t.environment}">${t.environment}</span>
        <div style="font-family:monospace; font-size:0.8rem; color:var(--primary-color); margin-top:0.2rem;">${t.base_url}</div>
      </div>
      <button class="btn btn-outline btn-sm" onclick="deleteTargetItem('${t.id}')"><i class="fa-solid fa-trash text-danger"></i></button>
    </div>
  `).join('');
}

function renderScopeList() {
  const container = document.getElementById('scope-list-container');
  if (!currentProject.scope_rules || currentProject.scope_rules.length === 0) {
    container.innerHTML = '<p class="text-muted text-sm" style="text-align:center; padding:1.5rem;">No scope rules defined. All discovered endpoints will be scanned by default.</p>';
    return;
  }

  container.innerHTML = currentProject.scope_rules.map(r => `
    <div class="scope-item">
      <div>
        <span class="badge badge-${r.rule_type === 'include' ? 'success' : 'danger'}">${r.rule_type.toUpperCase()}</span>
        <code style="margin-left:0.5rem; color:#38bdf8;">${r.pattern}</code>
        ${r.description ? `<span class="text-muted text-sm" style="margin-left:0.5rem;">(${r.description})</span>` : ''}
      </div>
      <button class="btn btn-outline btn-sm" onclick="deleteScopeItem('${r.id}')"><i class="fa-solid fa-trash text-danger"></i></button>
    </div>
  `).join('');
}

async function deleteTargetItem(targetId) {
  try {
    await api.deleteTarget(targetId);
    showToast('Target deleted', 'info');
    currentProject = await api.getProjectDetails(currentProject.id);
    renderTargetsList();
  } catch (err) {
    showToast('Failed to delete target: ' + err.message, 'error');
  }
}

async function deleteScopeItem(ruleId) {
  try {
    await api.deleteScopeRule(ruleId);
    showToast('Scope rule deleted', 'info');
    currentProject = await api.getProjectDetails(currentProject.id);
    renderScopeList();
  } catch (err) {
    showToast('Failed to delete scope rule: ' + err.message, 'error');
  }
}
