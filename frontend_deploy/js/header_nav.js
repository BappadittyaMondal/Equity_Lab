// header_nav.js – loads header component into #header-nav and wires search input
export async function initHeaderNav() {
  try {
    const resp = await fetch('components/header.html');
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const html = await resp.text();
    const container = document.getElementById('header-nav');
    if (container) container.innerHTML = html;

    // Attach search handlers
    const searchInput = document.getElementById('header-search-input');
    const searchBtn = document.getElementById('header-search-btn');

    const handleSearch = () => {
      if (searchInput && searchInput.value.trim()) {
        const sym = searchInput.value.trim();
        if (typeof window.selectSymbol === 'function') {
          window.selectSymbol(sym);
        }
        searchInput.value = '';
      }
    };

    if (searchBtn) {
      searchBtn.addEventListener('click', handleSearch);
    }
    if (searchInput) {
      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          handleSearch();
        }
      });
    }
  } catch (e) {
    console.error('Failed to load header component:', e);
  }
}

// Global API Key Configuration Modal
window.openApiKeyModal = function() {
  const existingModal = document.getElementById("api-key-modal");
  if (existingModal) existingModal.remove();

  const currentKey = localStorage.getItem("ierl_api_key") || window.__IERL_API_KEY || "";

  const modal = document.createElement("div");
  modal.id = "api-key-modal";
  modal.className = "fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4";
  modal.innerHTML = `
    <div class="bg-surface-low border border-gold/40 rounded-xl p-6 max-w-md w-full shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b border-surface-border pb-3">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-gold">key</span>
          <h3 class="text-base font-bold text-gold font-serif">API Authentication Key</h3>
        </div>
        <button onclick="document.getElementById('api-key-modal').remove()" class="text-muted hover:text-white">
          <span class="material-symbols-outlined text-sm">close</span>
        </button>
      </div>

      <p class="text-xs text-cream-dark leading-relaxed">
        Configure your <code>X-API-Key</code> for live backend engine queries. This key will be stored locally in your browser session storage.
      </p>

      <div class="space-y-1">
        <label class="text-[11px] font-mono text-muted uppercase">Secret API Key</label>
        <input type="password" id="api-key-input" value="${currentKey}" placeholder="e.g. ierl_prod_sec_key_..."
               class="w-full px-3 py-2 text-xs font-mono bg-surface-lowest text-white rounded border border-surface-border focus:border-gold outline-none" />
      </div>

      <div class="flex items-center justify-end gap-2 pt-2">
        <button onclick="localStorage.removeItem('ierl_api_key'); window.__IERL_API_KEY = ''; document.getElementById('api-key-modal').remove(); location.reload();"
                class="px-3 py-1.5 text-xs font-mono bg-red-900/40 hover:bg-red-800/60 text-red-200 rounded border border-red-500/40">
          Clear Key
        </button>
        <button onclick="const k = document.getElementById('api-key-input').value.trim(); localStorage.setItem('ierl_api_key', k); window.__IERL_API_KEY = k; document.getElementById('api-key-modal').remove(); location.reload();"
                class="px-4 py-1.5 text-xs font-mono bg-gold/20 hover:bg-gold/30 text-gold rounded border border-gold/40 font-semibold">
          Save & Apply
        </button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
};
