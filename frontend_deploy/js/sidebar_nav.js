// sidebar_nav.js – loads sidebar component into #sidebar-nav and wires navigation buttons
import { switchView } from "./main_canvas.js";

export async function initSidebar() {
  try {
    const resp = await fetch('components/sidebar.html');
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const html = await resp.text();
    const container = document.getElementById('sidebar-nav');
    if (container) container.innerHTML = html;

    // Attach click listeners to sidebar navigation buttons
    const buttons = container?.querySelectorAll("button[data-view]") || [];
    buttons.forEach(btn => {
      btn.addEventListener("click", () => {
        const view = btn.getAttribute("data-view");
        if (view) switchView(view);
      });
    });
  } catch (e) {
    console.error('Failed to load sidebar component:', e);
  }
}
