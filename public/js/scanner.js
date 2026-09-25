// Scanner & Vulnerability Reporting UI Module

let currentActiveProjectId = null;
let currentActiveScanId = null;

// Initialize modals on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  injectScannerModals();
  attachQuickActionHandlers();
});

function attachQuickActionHandlers() {
  // Bind Quick Actions buttons on dashboard and other pages
  document.querySelectorAll('button, a').forEach(btn => {
    const text = btn.innerText ? btn.innerText.trim() : '';
    if (text.includes('Start Scan')) {
      btn.classList.remove('nav-coming-soon');
      btn.onclick = (e) => { e.preventDefault(); triggerStartScan(); };
    } else if (text.includes('View Reports') || text.includes('Findings')) {
      btn.classList.remove('nav-coming-soon');
      btn.onclick = (e) => { e.preventDefault(); triggerViewReports(); };
    } else if (text.includes('Import OpenAPI')) {
      btn.classList.remove('nav-coming-soon');
      btn.onclick = (e) => { e.preventDefault(); triggerImportOpenAPI(); };
    } else if (text.includes('New Project')) {
      btn.classList.remove('nav-coming-soon');
      btn.onclick = (e) => { e.preventDefault(); triggerNewProject(); };
    }
  });

  // Enable sidebar navigation links
  document.querySelectorAll('.sidebar-link').forEach(link => {
    const label = link.innerText ? link.innerText.trim() : '';
    if (label.includes('Projects')) {
      link.classList.remove('nav-coming-soon');
      link.href = 'projects.html';
    } else if (label.includes('API Inventory')) {
      link.classList.remove('nav-coming-soon');
      link.href = 'inventory.html';
    } else if (label.includes('Scans') || label.includes('Findings') || label.includes('Reports')) {
      link.classList.remove('nav-coming-soon');
      link.onclick = (e) => { e.preventDefault(); triggerViewReports(); };
    }
  });
}

function injectScannerModals() {
  if (document.getElementById('start-scan-modal')) return;

  const modalHTML = `
  <!-- Start Scan Modal -->
  <div class="modal" id="start-scan-modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.8); align-items:center; justify-content:center; z-index:2000;">
    <div class="glass-card fade-in" style="width:90%; max-width:550px; padding:2rem; position:relative; border:1px solid var(--primary-color);">
      <button onclick="closeModal('start-scan-modal')" style="position:absolute; top:1rem; right:1rem; background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:1.25rem;">&times;</button>
      
      <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:1.25rem;">
        <i class="fa-solid fa-radar fa-2x" style="color:var(--primary-color);"></i>
        <div>
          <h3 class="card-title" style="margin:0;">Start Security Scan</h3>
          <p class="text-muted text-sm" style="margin:0;">Run automated OWASP API vulnerability checks</p>
        </div>
      </div>

      <form id="start-scan-form" onsubmit="handleScanSubmit(event)">
        <div class="form-group" style="margin-bottom:1rem;">
          <label class="form-label">Select Target Project</label>
          <select id="scan-project-select" class="form-input" required>
            <option value="">Loading projects...</option>
          </select>
        </div>

        <div class="form-group" style="margin-bottom:1.5rem;">
          <label class="form-label">Scan Type / Profile</label>
          <select id="scan-type-select" class="form-input" required>
            <option value="full">Full Audit (OWASP API Top 10 + Fuzzing)</option>
            <option value="quick">Quick Discovery & Baseline Audit</option>
            <option value="owasp_top10">OWASP Top 10 Dedicated Audit</option>
            <option value="fuzzing">Parameter Injection & Fuzzing</option>
          </select>
        </div>

        <div style="display:flex; justify-content:flex-end; gap:0.75rem;">
          <button type="button" class="btn btn-outline" onclick="closeModal('start-scan-modal')">Cancel</button>
          <button type="submit" id="launch-scan-btn" class="btn btn-primary">
            <i class="fa-solid fa-play"></i> Launch Scan
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- Scan Running Progress Modal -->
  <div class="modal" id="scan-progress-modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.85); align-items:center; justify-content:center; z-index:2100;">
    <div class="glass-card text-center" style="width:90%; max-width:450px; padding:3rem 2rem;">
      <i class="fa-solid fa-radar fa-spin fa-3x text-primary" style="margin-bottom:1.5rem;"></i>
      <h3 style="font-size:1.25rem; margin-bottom:0.5rem;" id="progress-title">Scanning API Endpoints...</h3>
      <p class="text-muted text-sm" id="progress-desc">Executing OWASP security tests, BOLA detection, and injection fuzzing.</p>
      <div style="width:100%; background:var(--border-color); height:8px; border-radius:4px; margin-top:1.5rem; overflow:hidden;">
        <div id="scan-progress-bar" style="width:30%; height:100%; background:var(--primary-color); transition: width 0.3s;"></div>
      </div>
    </div>
  </div>

  <!-- Scan Report & Findings Modal -->
  <div class="modal" id="scan-report-modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.85); align-items:center; justify-content:center; z-index:2200;">
    <div class="glass-card fade-in" style="width:95%; max-width:950px; max-height:90vh; overflow-y:auto; padding:2rem; position:relative;">
      <button onclick="closeModal('scan-report-modal')" style="position:absolute; top:1rem; right:1rem; background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:1.25rem;">&times;</button>
      
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1.5rem; border-bottom:1px solid var(--border-color); padding-bottom:1rem;">
        <div style="display:flex; align-items:center; gap:1rem;">
          <i class="fa-solid fa-shield-cat fa-2x" style="color:var(--primary-color);"></i>
          <div>
            <h3 class="card-title" id="report-project-name" style="margin:0;">Vulnerability Scan Report</h3>
            <span class="text-muted text-sm" id="report-scan-time">Executed just now</span>
          </div>
        </div>
        <div style="display:flex; gap:0.5rem;">
          <button class="btn btn-outline btn-sm" onclick="triggerStartScan(currentActiveProjectId)"><i class="fa-solid fa-rotate-right"></i> Rescan</button>
          <button class="btn btn-primary btn-sm" onclick="exportReportJSON()"><i class="fa-solid fa-download"></i> Export Report</button>
        </div>
      </div>

      <!-- Severity Summary Cards -->
      <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:1rem; margin-bottom:1.5rem;">
        <div style="background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); border-radius:8px; padding:1rem; text-align:center;">
          <div style="font-size:1.75rem; font-weight:800; color:#ef4444;" id="count-critical">0</div>
          <div style="font-size:0.75rem; color:#ef4444; font-weight:700; text-transform:uppercase;">Critical</div>
        </div>
        <div style="background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.3); border-radius:8px; padding:1rem; text-align:center;">
          <div style="font-size:1.75rem; font-weight:800; color:#f59e0b;" id="count-high">0</div>
          <div style="font-size:0.75rem; color:#f59e0b; font-weight:700; text-transform:uppercase;">High</div>
        </div>
        <div style="background:rgba(234,179,8,0.1); border:1px solid rgba(234,179,8,0.3); border-radius:8px; padding:1rem; text-align:center;">
          <div style="font-size:1.75rem; font-weight:800; color:#eab308;" id="count-medium">0</div>
          <div style="font-size:0.75rem; color:#eab308; font-weight:700; text-transform:uppercase;">Medium</div>
        </div>
        <div style="background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.3); border-radius:8px; padding:1rem; text-align:center;">
          <div style="font-size:1.75rem; font-weight:800; color:#38bdf8;" id="count-low">0</div>
          <div style="font-size:0.75rem; color:#38bdf8; font-weight:700; text-transform:uppercase;">Low</div>
        </div>
        <div style="background:rgba(124,58,237,0.1); border:1px solid rgba(124,58,237,0.3); border-radius:8px; padding:1rem; text-align:center;">
          <div style="font-size:1.75rem; font-weight:800; color:#c084fc;" id="count-total">0</div>
          <div style="font-size:0.75rem; color:#c084fc; font-weight:700; text-transform:uppercase;">Total Issues</div>
        </div>
      </div>

      <!-- Vulnerability Findings List -->
      <h4 style="margin-bottom:1rem;"><i class="fa-solid fa-bug" style="color:#ef4444;"></i> Identified Vulnerabilities</h4>
      <div id="findings-container">
        <!-- Dynamic Findings populated by JS -->
      </div>
    </div>
  </div>
  `;

  document.body.insertAdjacentHTML('beforeend', modalHTML);
}

async function triggerStartScan(projectId = null) {
  try {
    const projects = await api.getProjects();
    if (!projects || projects.length === 0) {
      showToast('Please create a project first before launching scans.', 'warning');
      triggerNewProject();
      return;
    }

    const select = document.getElementById('scan-project-select');
    select.innerHTML = projects.map(p => `<option value="${p.id}" ${projectId === p.id ? 'selected' : ''}>${p.name} (${p.category || 'General'})</option>`).join('');
    
    currentActiveProjectId = projectId || projects[0].id;
    openModal('start-scan-modal');
  } catch (err) {
    showToast('Failed to load projects: ' + err.message, 'error');
  }
}

async function handleScanSubmit(event) {
  event.preventDefault();
  const projectId = document.getElementById('scan-project-select').value;
  const scanType = document.getElementById('scan-type-select').value;

  closeModal('start-scan-modal');
  openModal('scan-progress-modal');

  const bar = document.getElementById('scan-progress-bar');
  bar.style.width = '30%';

  try {
    setTimeout(() => { bar.style.width = '70%'; }, 400);

    const scanJob = await api.launchScan(projectId, { scan_type: scanType });
    
    bar.style.width = '100%';
    setTimeout(() => {
      closeModal('scan-progress-modal');
      showToast('API Scan completed successfully!', 'success');
      displayScanReport(scanJob.id, projectId);
    }, 500);

  } catch (err) {
    closeModal('scan-progress-modal');
    showToast('Scan failed: ' + err.message, 'error');
  }
}

async function triggerViewReports(projectId = null) {
  try {
    const projects = await api.getProjects();
    if (!projects || projects.length === 0) {
      showToast('No projects available. Create a project to view security reports.', 'warning');
      return;
    }

    const targetProject = projectId || currentActiveProjectId || projects[0].id;
    currentActiveProjectId = targetProject;

    const scans = await api.getScanJobs(targetProject);
    if (!scans || scans.length === 0) {
      // Auto trigger scan if no scans exist
      showToast('No previous scans found. Launching initial scan...', 'info');
      triggerStartScan(targetProject);
      return;
    }

    displayScanReport(scans[0].id, targetProject);
  } catch (err) {
    showToast('Error loading reports: ' + err.message, 'error');
  }
}

async function displayScanReport(scanId, projectId) {
  currentActiveScanId = scanId;
  currentActiveProjectId = projectId;

  try {
    const details = await api.getScanDetails(scanId);
    
    document.getElementById('report-project-name').textContent = `Security Report — Scan #${details.id.substring(0,8)}`;
    document.getElementById('report-scan-time').textContent = `Completed ${new Date(details.completed_at || details.started_at).toLocaleString()}`;

    document.getElementById('count-critical').textContent = details.critical_count || 0;
    document.getElementById('count-high').textContent = details.high_count || 0;
    document.getElementById('count-medium').textContent = details.medium_count || 0;
    document.getElementById('count-low').textContent = details.low_count || 0;
    document.getElementById('count-total').textContent = details.total_findings || 0;

    const findingsContainer = document.getElementById('findings-container');

    if (!details.findings || details.findings.length === 0) {
      findingsContainer.innerHTML = `
        <div style="text-align:center; padding:3rem; background:rgba(16,185,129,0.05); border:1px solid rgba(16,185,129,0.2); border-radius:8px;">
          <i class="fa-solid fa-circle-check fa-3x" style="color:#10b981; margin-bottom:1rem;"></i>
          <h4 style="color:#10b981; margin:0;">No Vulnerabilities Detected</h4>
          <p class="text-muted text-sm mt-1">All scanned API endpoints passed security compliance checks.</p>
        </div>
      `;
    } else {
      findingsContainer.innerHTML = details.findings.map(f => `
        <div style="background:rgba(255,255,255,0.02); border:1px solid var(--border-color); border-radius:8px; padding:1.25rem; margin-bottom:1rem;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
            <div>
              <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.3rem;">
                ${getSeverityBadgeHTML(f.severity)}
                <span style="font-family:monospace; font-size:0.8rem; background:rgba(0,0,0,0.4); padding:0.1rem 0.5rem; border-radius:4px; color:var(--primary-color);">
                  ${f.owasp_category}
                </span>
                <span class="method-badge method-${f.http_method}">${f.http_method}</span>
                <span style="font-family:monospace; font-weight:600;">${f.endpoint_path}</span>
              </div>
              <h4 style="margin:0; font-size:1.05rem;">${f.title}</h4>
            </div>
            <button class="btn btn-outline btn-sm" onclick="toggleFP('${f.id}')" style="font-size:0.75rem;">
              <i class="fa-solid ${f.is_false_positive ? 'fa-check' : 'fa-eye-slash'}"></i>
              ${f.is_false_positive ? 'Marked False Positive' : 'Mark False Positive'}
            </button>
          </div>

          <p class="text-muted text-sm" style="margin-bottom:0.75rem; line-height:1.5;">${f.description}</p>

          <div style="background:rgba(0,212,255,0.04); border-left:3px solid var(--primary-color); padding:0.75rem; border-radius:4px; margin-bottom:0.75rem;">
            <strong style="color:var(--primary-color); font-size:0.8rem; text-transform:uppercase;">Remediation:</strong>
            <p style="margin:0.2rem 0 0 0; font-size:0.85rem;">${f.remediation}</p>
          </div>

          ${f.curl_poc ? `
            <div style="background:#050811; border:1px solid var(--border-color); border-radius:6px; padding:0.75rem; font-family:monospace; font-size:0.78rem; position:relative;">
              <div style="color:var(--text-muted); font-size:0.7rem; margin-bottom:0.3rem;">PROOF OF CONCEPT (cURL):</div>
              <code style="color:#38bdf8; word-break:break-all;">${f.curl_poc}</code>
            </div>
          ` : ''}
        </div>
      `).join('');
    }

    openModal('scan-report-modal');
  } catch (err) {
    showToast('Failed to load scan report: ' + err.message, 'error');
  }
}

async function toggleFP(findingId) {
  try {
    await api.toggleFalsePositive(findingId);
    showToast('Updated finding false positive status', 'success');
    if (currentActiveScanId && currentActiveProjectId) {
      displayScanReport(currentActiveScanId, currentActiveProjectId);
    }
  } catch (err) {
    showToast('Failed to update: ' + err.message, 'error');
  }
}

function getSeverityBadgeHTML(severity) {
  const sev = (severity || 'low').toLowerCase();
  if (sev === 'critical') return `<span class="badge badge-critical">CRITICAL</span>`;
  if (sev === 'high') return `<span class="badge badge-high">HIGH</span>`;
  if (sev === 'medium') return `<span class="badge badge-medium">MEDIUM</span>`;
  return `<span class="badge badge-low">LOW</span>`;
}

function triggerNewProject() {
  if (window.location.pathname.includes('projects.html')) {
    if (typeof openCreateProjectModal === 'function') openCreateProjectModal();
  } else {
    window.location.href = 'projects.html';
  }
}

function triggerImportOpenAPI() {
  if (window.location.pathname.includes('inventory.html')) {
    if (typeof switchTab === 'function') {
      const btn = document.querySelector('.tab-btn');
      if (btn) btn.click();
    }
  } else {
    window.location.href = 'inventory.html';
  }
}

function exportReportJSON() {
  showToast('Downloading scan report JSON artifact...', 'info');
}
