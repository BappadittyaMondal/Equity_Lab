// footer.js — Footer component initialization
// Renders version, data mode status, and legal disclaimer

const API_BASE = window.API_BASE || "";

/**
 * Initialize the footer with version info, data status, and disclaimer.
 */
export function initFooter() {
  const container = document.getElementById("footer");
  if (!container) return;

  const version = window.__IERL_API_VERSION || "0.4.0";

  container.innerHTML = `
    <div class="bg-surface-low border-t border-surface-border px-4 py-3 md:ml-64 lg:mr-96">
      <div class="flex flex-col md:flex-row items-center justify-between gap-2 text-xs text-muted">
        <div class="flex items-center gap-3">
          <span class="font-mono font-semibold text-gold">IERL v${version}</span>
          <span id="footer-data-mode" class="badge badge-neutral">—</span>
        </div>
        <div class="text-center max-w-lg">
          <span class="text-muted italic">For educational and personal research purposes only. Not investment advice. All market data subject to provider terms and latency.</span>
        </div>
        <div class="font-mono text-muted">
          &copy; ${new Date().getFullYear()} IERL
        </div>
      </div>
    </div>`;

  // Update data mode badge once API responds
  updateDataModeBadge();
}

async function updateDataModeBadge() {
  const badge = document.getElementById("footer-data-mode");
  if (!badge) return;

  try {
    const resp = await fetch(`${API_BASE}/api/v1/health`);
    if (resp.ok) {
      const data = await resp.json();
      const version = data.version || "?";
      badge.textContent = `DATA: ${data.status || "UNKNOWN"}`;
      badge.className = `badge ${data.status === "ONLINE" ? "badge-success" : "badge-warning"}`;

      // Update version in footer
      const versionEl = document.querySelector("#footer .text-gold");
      if (versionEl) versionEl.textContent = `IERL v${version}`;
    } else {
      badge.textContent = "API OFFLINE";
      badge.className = "badge badge-danger";
    }
  } catch (_) {
    badge.textContent = "API OFFLINE";
    badge.className = "badge badge-danger";
  }
}
