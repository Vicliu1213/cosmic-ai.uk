fetch('./module_catalog.json')
  .then((response) => response.json())
  .then((data) => {
    const grid = document.getElementById('module-grid');

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
        </div>
      </article>
    `).join('');
  });
