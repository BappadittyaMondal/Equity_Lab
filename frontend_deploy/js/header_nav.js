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
