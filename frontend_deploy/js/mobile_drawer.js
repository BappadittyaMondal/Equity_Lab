// mobile_drawer.js — Mobile navigation drawer toggle
// Controls the slide-in drawer for mobile viewports

/**
 * Initialize mobile drawer toggle functionality.
 * Attaches the global toggleMobileDrawer function for the hamburger menu.
 */
export function initMobileDrawer() {
  // Expose toggle globally so onclick attributes in header.html can call it
  window.toggleMobileDrawer = toggleMobileDrawer;
}

function toggleMobileDrawer() {
  const drawer = document.getElementById("mobile-drawer");
  const overlay = document.getElementById("drawer-overlay");

  if (!drawer || !overlay) return;

  const isOpen = drawer.classList.contains("open");

  if (isOpen) {
    drawer.classList.remove("open");
    overlay.classList.remove("open");
    document.body.style.overflow = "";
  } else {
    drawer.classList.add("open");
    overlay.classList.add("open");
    document.body.style.overflow = "hidden";

    // Populate drawer with navigation if empty
    if (!drawer.innerHTML.trim()) {
      drawer.innerHTML = `
        <div class="p-4">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-bold text-gold">IERL Command</h2>
            <button onclick="toggleMobileDrawer()" class="text-muted hover:text-gold transition-colors">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          <ul class="space-y-2 text-sm">
            <li><button class="w-full text-left btn-primary" onclick="switchView('command'); toggleMobileDrawer();">Command Center</button></li>
            <li><button class="w-full text-left btn-primary" onclick="switchView('multibagger'); toggleMobileDrawer();">Multibagger Screener</button></li>
            <li><button class="w-full text-left btn-primary" onclick="switchView('compare'); toggleMobileDrawer();">Stock Comparison</button></li>
            <li><button class="w-full text-left btn-primary" onclick="switchView('probability'); toggleMobileDrawer();">Return Probability</button></li>
            <li><button class="w-full text-left btn-primary" onclick="switchView('strategies'); toggleMobileDrawer();">Strategy Screening</button></li>
            <li><button class="w-full text-left btn-primary" onclick="switchView('aiassistant'); toggleMobileDrawer();">AI Assistant</button></li>
          </ul>
        </div>`;
    }
  }
}
