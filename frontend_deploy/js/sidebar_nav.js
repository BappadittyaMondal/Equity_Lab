// sidebar_nav.js – loads sidebar component into #sidebar-nav
export async function initSidebar() {
  try {
    const resp = await fetch('components/sidebar.html');
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const html = await resp.text();
    const container = document.getElementById('sidebar-nav');
    if (container) container.innerHTML = html;
  } catch (e) {
    console.error('Failed to load sidebar component:', e);
  }
}
