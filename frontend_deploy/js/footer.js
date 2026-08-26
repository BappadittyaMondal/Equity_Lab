// footer.js — Footer Component Helper

export function initFooter() {
  const footerEl = document.getElementById("footer");
  if (!footerEl) return;
  footerEl.innerHTML = `<footer class="py-2 px-4 text-center text-xs text-muted font-mono">IERL Equity Intelligence OS v1.0.0</footer>`;
}
