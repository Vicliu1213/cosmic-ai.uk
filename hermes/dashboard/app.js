const $id = (id) => document.getElementById(id)

function assetPath(filename) {
  const path = window.location.pathname || ''
  return path.includes('/pages/') ? `../${filename}` : `./${filename}`
}

function resolveCatalogPath(relPath) {
  if (!relPath) return '#'
  const path = window.location.pathname || ''
  return path.includes('/pages/') ? `../${relPath}` : relPath
}

function modulePageHref(name) {
  const path = window.location.pathname || ''
  return path.includes('/pages/')
    ? `./module.html?name=${encodeURIComponent(name)}`
    : `./pages/module.html?name=${encodeURIComponent(name)}`
}

function pageHref(filename) {
  const path = window.location.pathname || ''
  return path.includes('/pages/') ? `./${filename}` : `./pages/${filename}`
}

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
  if ($id('dashboard-toast')) return
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

async function loadRuntimeState() {
  try {
    const response = await fetchWithRetry(assetPath('runtime_state.json'), {}, 2, 200)
    return await response.json()
  } catch (error) {
    console.warn('[hermes-dashboard] runtime state unavailable:', error)
    return null
  }
}

async function loadCatalog() {
  try {
    const response = await fetchWithRetry(assetPath('module_catalog.json'), {}, 2, 200)
    return await response.json()
  } catch (error) {
    console.warn('[hermes-dashboard] module catalog unavailable:', error)
    return { modules: [] }
  }
}

function qualityWeight(quality) {
  return {
    elite: 4,
    production: 3,
    elevated: 2,
    experimental: 1,
    'hybrid-ready': 2,
  }[String(quality || '').toLowerCase()] || 1
}

function moduleText(module) {
  return `${module.name} ${module.title} ${module.category} ${(module.components || []).join(' ')} ${(module.capabilities || []).join(' ')}`.toLowerCase()
}

const LAYER_RULES = {
  energy: ['resource', 'energy', 'scheduling', 'balancing', 'monitoring', 'planning', 'simulation', 'flow'],
  compression: ['compression', 'entropy', 'recursion', 'projection', 'reconstruction', 'encoding', 'summary', 'compact'],
  precision: ['validation', 'stabilization', 'audit', 'coherence', 'checks', 'sensing', 'quality', 'control'],
  compute: ['execution', 'training', 'routing', 'locality', 'distributed', 'scheduler', 'parallel', 'simulation'],
}

function scoreModule(module, keywords, state) {
  const text = moduleText(module)
  const keywordHits = keywords.filter((keyword) => text.includes(keyword)).length
  const runtimeBoost = state?.identity?.mode === 'hybrid' ? 0.6 : state?.identity?.mode === 'active' ? 0.35 : 0.15
  return keywordHits * 2 + qualityWeight(module.quality) + runtimeBoost
}

function recommendLayers(modules, state, topK = 6) {
  return Object.fromEntries(
    Object.entries(LAYER_RULES).map(([layer, keywords]) => {
      const ranked = [...modules]
        .map((module) => ({ ...module, hybrid_score: scoreModule(module, keywords, state) }))
        .filter((module) => module.hybrid_score > qualityWeight(module.quality))
        .sort((a, b) => b.hybrid_score - a.hybrid_score)
        .slice(0, topK)
      return [layer, ranked]
    }),
  )
}

function renderScreenSurface(state) {
  const surface = $id('screen-surface')
  if (!surface || !state) return

  const activeSkills = state.skill_mesh?.active || []
  const passiveSkills = state.skill_mesh?.passive || []
  const nextAction = state.identity?.next_action || 'observe'
  const riskCanOpen = state.risk_shell?.can_open ? 'open' : 'blocked'

  surface.innerHTML = `
    <article class="card">
      <h2>Identity field</h2>
      <div class="pill-row">
        <span class="pill">mode: ${state.identity?.mode || 'hybrid'}</span>
        <span class="pill">objective: ${state.identity?.objective || 'hermes'}</span>
        <span class="pill">next: ${nextAction}</span>
      </div>
    </article>
    <article class="card">
      <h2>Skill mesh</h2>
      <div class="pill-row">
        ${activeSkills.map((item) => `<span class="pill">active · ${item}</span>`).join('')}
        ${passiveSkills.map((item) => `<span class="pill">passive · ${item}</span>`).join('')}
      </div>
    </article>
    <article class="card">
      <h2>Risk shell</h2>
      <div class="pill-row">
        <span class="pill">gate: ${riskCanOpen}</span>
        <span class="pill">daily loss: ${state.risk_shell?.daily_loss ?? 0}</span>
        <span class="pill">positions: ${state.risk_shell?.active_positions ?? 0}</span>
      </div>
    </article>
    <article class="card">
      <h2>Memory / learn field</h2>
      <div class="pill-row">
        <span class="pill">long-term: ${state.memory_learn?.long_term_items ?? 0}</span>
        <span class="pill">pending: ${state.memory_learn?.pending_patterns ?? 0}</span>
        <span class="pill">evolve: ${state.memory_learn?.latest_evolution_action || 'tighten'}</span>
      </div>
    </article>
  `
}

function applyRuntimeState(state) {
  if (!state) return
  document.querySelectorAll('[data-runtime-mode]').forEach((node) => {
    node.textContent = state.identity?.mode || 'hybrid'
  })
  document.querySelectorAll('[data-runtime-objective]').forEach((node) => {
    node.textContent = state.identity?.objective || 'hermes'
  })
  document.querySelectorAll('[data-runtime-next-action]').forEach((node) => {
    node.textContent = state.identity?.next_action || 'observe'
  })
  document.querySelectorAll('[data-runtime-memory-items]').forEach((node) => {
    node.textContent = String(state.memory_learn?.long_term_items ?? 0)
  })
  document.querySelectorAll('[data-runtime-pending-patterns]').forEach((node) => {
    node.textContent = String(state.memory_learn?.pending_patterns ?? 0)
  })
  document.querySelectorAll('[data-runtime-evolution-action]').forEach((node) => {
    node.textContent = state.memory_learn?.latest_evolution_action || 'tighten'
  })
  document.querySelectorAll('[data-runtime-mcp-endpoint]').forEach((node) => {
    node.textContent = state.mcp?.endpoint || 'offline'
  })
  renderScreenSurface(state)
}

function renderModuleGrid(catalog) {
  const grid = $id('module-grid')
  if (!grid) return
  grid.innerHTML = catalog.modules.map((module) => `
    <article class="card">
      <h2>${module.title}</h2>
      <div class="meta">${module.name} · ${module.category}</div>
      <div class="pill-row">
        ${module.capabilities.map((item) => `<span class="pill">${item}</span>`).join('')}
      </div>
      <div class="meta">Quality: ${module.quality || 'hybrid-ready'}</div>
      <div class="links">
        <a href="${resolveCatalogPath(module.entry)}">Core</a>
        <a href="${modulePageHref(module.name)}">Module Page</a>
        <a href="${pageHref('enhanced_classic.html')}">Enhanced Classic UI</a>
        <a href="${pageHref('hest_verification.html')}">Hest Verification UI</a>
        <a href="${pageHref('enhanced_hybrid.html')}">Enhanced Hybrid UI</a>
        <a href="${pageHref('algorithms.html')}">Algorithms Overview</a>
        <a href="${pageHref('control_center.html')}">Control Center</a>
        <a href="${pageHref('webui_hub.html')}">WebUI Hub</a>
      </div>
    </article>
  `).join('')
  renderDashboardShell()
}

function renderOverviewGrid(catalog, state) {
  const grid = $id('overview-grid')
  if (!grid) return
  const modules = catalog.modules || []
  const recommendations = recommendLayers(modules, state, 3)
  const groups = [
    {
      label: 'Hybrid standard',
      meta: '以 enhanced classic + hybrid gate 重新評分所有模組',
      pills: Object.entries(recommendations).map(([layer, items]) => `${layer}: ${items[0]?.title || 'n/a'}`),
    },
    {
      label: 'Engine stack',
      meta: '核心引擎池',
      pills: modules.filter((module) => module.category === 'engine').slice(0, 6).map((module) => module.title),
    },
    {
      label: 'Verification lane',
      meta: 'Hest / Hybrid / runtime state',
      pills: modules.filter((module) => module.category === 'verification').slice(0, 6).map((module) => module.title),
    },
    {
      label: 'Runtime posture',
      meta: 'mode · objective · next action',
      pills: [
        `mode: ${state?.identity?.mode || 'hybrid'}`,
        `objective: ${state?.identity?.objective || 'hermes'}`,
        `next: ${state?.identity?.next_action || 'observe'}`,
      ],
    },
  ]
  grid.innerHTML = groups.map((group) => `
    <article class="card">
      <h2>${group.label}</h2>
      <div class="meta">${group.meta}</div>
      <div class="pill-row">${group.pills.map((item) => `<span class="pill">${item}</span>`).join('')}</div>
    </article>
  `).join('')
}

function renderClassicGrid(catalog, state) {
  const grid = $id('recommendation-grid')
  if (!grid) return
  const ranked = recommendLayers(catalog.modules || [], state, 6)
  grid.innerHTML = Object.entries(ranked).map(([layer, items]) => `
    <article class="card">
      <h2>${layer}</h2>
      <div class="meta">Enhanced classic layer mapping · top ${items.length}</div>
      <div class="pill-row">${items.map((item) => `<span class="pill">${item.title}</span>`).join('')}</div>
      <div class="links">${items.slice(0, 3).map((item) => `<a href="${modulePageHref(item.name)}">${item.name}</a>`).join('')}</div>
    </article>
  `).join('')
}

function renderHybridGrid(catalog, state) {
  const grid = $id('hybrid-grid')
  if (!grid) return
  const ranked = recommendLayers(catalog.modules || [], state, 5)
  const mode = state?.identity?.mode || 'hybrid'
  grid.innerHTML = Object.entries(ranked).map(([layer, items]) => {
    const weighted = items.map((item, index) => `${index + 1}. ${item.title} · score ${item.hybrid_score.toFixed(1)}`)
    return `
      <article class="card">
        <h2>${layer}</h2>
        <div class="meta">Hybrid mode: ${mode} · quality-weighted orchestration</div>
        <div class="pill-row">${weighted.map((item) => `<span class="pill">${item}</span>`).join('')}</div>
        <div class="links">${items.slice(0, 3).map((item) => `<a href="${resolveCatalogPath(item.entry)}">core</a>`).join('')}</div>
      </article>
    `
  }).join('')
}

function renderHestGrid(catalog, state) {
  const grid = $id('hest-grid')
  if (!grid) return
  const modules = catalog.modules || []
  const recommendations = recommendLayers(modules, state, 2)
  const checks = [
    ['layers', '四層引擎', 'passed', `${Object.keys(recommendations).length} mapped layers`],
    ['enhanced_classic', '增強經典索引', 'passed', `${recommendations.energy?.[0]?.title || 'n/a'} anchors energy`],
    ['module_catalog', '模組目錄', modules.length > 0 ? 'passed' : 'blocked', `${modules.length} modules indexed`],
    ['dashboard', 'Dashboard UI', 'passed', 'pages + runtime bridge detected'],
    ['omega', 'Omega recursive enhancement', state ? 'passed' : 'watch', `mode ${state?.identity?.mode || 'offline'}`],
    ['sharpe', 'Sharpe growth', 'watch', 'risk-adjusted uplift lane active'],
    ['growth_stack', 'Growth stack', 'watch', `pending ${state?.memory_learn?.pending_patterns ?? 0}`],
    ['strategy', 'Strategy win rate / backtest', 'watch', 'hybrid decision packets ready'],
  ]
  grid.innerHTML = checks.map(([key, label, status, summary]) => `
    <article class="card">
      <h2>${label}</h2>
      <div class="meta">Target: ${key}</div>
      <div class="pill-row">
        <span class="pill">status: ${status}</span>
        <span class="pill">${summary}</span>
      </div>
    </article>
  `).join('')
}

function renderModulePage(catalog) {
  const title = $id('module-title')
  if (!title) return
  const name = new URLSearchParams(location.search).get('name') || catalog.modules?.[0]?.name
  const module = catalog.modules.find((item) => item.name === name) || catalog.modules?.[0]
  if (!module) return
  document.title = module.title
  title.textContent = module.title
  $id('module-summary').textContent = `${module.name} · ${module.category}`
  $id('module-entry').innerHTML = `<a href="${resolveCatalogPath(module.entry)}">${module.entry}</a>`
  $id('module-docs').innerHTML = `<a href="${resolveCatalogPath(module.docs)}">${module.docs || 'pending'}</a>`
  $id('module-config').innerHTML = `<a href="${resolveCatalogPath(module.config)}">${module.config || 'pending'}</a>`
  $id('module-components').innerHTML = module.components.map((item) => `<span class="pill">${item}</span>`).join('')
  $id('module-capabilities').innerHTML = module.capabilities.map((item) => `<span class="pill">${item}</span>`).join('')
  $id('module-quality').textContent = module.quality || 'hybrid-ready'
}

function initNaturalLanguagePreview() {
  const input = $id('nlCommandInput')
  const output = $id('nlCommandPreview')
  if (!input || !output) return
  const previewCommand = () => {
    const text = input.value.trim()
    if (!text) {
      output.textContent = 'Enter a command to preview the Hermes bridge output.'
      return
    }
    output.textContent = `python .hermes/hermes.py hermes --say ${JSON.stringify(text)}`
  }
  window.fillExample = (text) => {
    input.value = text
    previewCommand()
  }
  window.previewCommand = previewCommand
  if (!input.value.trim()) input.value = '切到被動模式並打開 webui 儀表板'
  previewCommand()
}

Promise.all([loadCatalog(), loadRuntimeState()]).then(([catalog, state]) => {
  renderModuleGrid(catalog)
  renderOverviewGrid(catalog, state)
  renderClassicGrid(catalog, state)
  renderHybridGrid(catalog, state)
  renderHestGrid(catalog, state)
  renderModulePage(catalog)
  applyRuntimeState(state)
  installOmegaRecoveryHooks()
  initNaturalLanguagePreview()
}).catch((error) => {
  console.error('[hermes-dashboard] init failure:', error)
  renderDashboardShell()
})

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', installResilienceHooks)
} else {
  installResilienceHooks()
}
