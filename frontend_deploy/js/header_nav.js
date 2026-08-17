// header_nav.js – loads header component into #header-nav
export async function initHeaderNav() {
  try {
    const resp = await fetch('components/header.html');
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const html = await resp.text();
    const container = document.getElementById('header-nav');
    if (container) container.innerHTML = html;
  } catch (e) {
    console.error('Failed to load header component:', e);
  }
}
