const $id = (id) => document.getElementById(id)

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function fetchWithRetry(url, options = {}, retries = 3, backoffMs = 400) {
  let lastError = null
  for (let attempt = 0; attempt <= retries; attempt += 1) {
    try {
      const response = await fetch(url, options)
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      return response
    } catch (error) {
      lastError = error
      if (attempt < retries) await sleep(backoffMs * (attempt + 1))
    }
  }
  throw lastError
}

function installResilienceHooks() {
  window.addEventListener('error', (event) => {
    console.warn('[hermes-dashboard] runtime error:', event.message || event.error)
    const toast = $id('dashboard-toast')
    if (toast) toast.textContent = 'Recovered from a client-side error'
  })

  window.addEventListener('unhandledrejection', (event) => {
    console.warn('[hermes-dashboard] unhandled rejection:', event.reason)
    const toast = $id('dashboard-toast')
    if (toast) toast.textContent = 'Recovered from a network/runtime failure'
  })
}

function renderDashboardShell() {
  const shell = $id('module-grid')
  if (!shell) return
  const status = document.createElement('div')
  status.id = 'dashboard-toast'
  status.className = 'card'
  status.textContent = 'Dashboard is in resilient mode'
  shell.parentElement?.insertBefore(status, shell)
}

function installOmegaRecoveryHooks() {
  const omegaPanel = document.querySelector('[data-omega-loop]')
  if (!omegaPanel) return
  omegaPanel.dataset.ready = 'true'
}

fetchWithRetry('./module_catalog.json', {}, 3, 300)
  .then((response) => response.json())
  .then((data) => {
    const grid = document.getElementById('module-grid')
    if (!grid) return
    grid.innerHTML = data.modules.map((module) => `
      <article class="card">
        <h2>${module.title}</h2>
        <div class="meta">${module.name} · ${module.category}</div>
        <div class="pill-row">
          ${module.capabilities.map((item) => `<span class="pill">${item}</span>`).join('')}
        </div>
        <div class="meta">Quality: ${module.quality || 'hybrid-ready'}</div>
        <div class="links">
          <a href="${module.entry}">Core</a>
          <a href="./pages/module.html?name=${module.name}">Module Page</a>
          <a href="./pages/enhanced_classic.html">Enhanced Classic UI</a>
          <a href="./pages/hest_verification.html">Hest Verification UI</a>
          <a href="./pages/enhanced_hybrid.html">Enhanced Hybrid UI</a>
          <a href="./pages/algorithms.html">Algorithms Overview</a>
          <a href="./pages/control_center.html">Control Center</a>
        </div>
      </article>
    `).join('')
    renderDashboardShell()
  })
  .catch((error) => {
    console.error('[hermes-dashboard] failed to load module catalog:', error)
    renderDashboardShell()
  })

installResilienceHooks()
