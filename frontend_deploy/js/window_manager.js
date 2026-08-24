/**
 * window_manager.js — Multi-Window Management Engine for StockAnalyzer Dashboard
 * Enables floating, dragging, resizing, collapse/expand, maximize (Alt+Enter), Z-stacking,
 * viewport boundary clamping, touch/pointer support, and layout serialization to local storage.
 */

export class WindowManager {
  constructor() {
    this.windows = new Map();
    this.activeZIndex = 10;
    this.activeWindow = null;
    this.layoutKey = "stockanalyzer_window_layout_v1";

    this._onMouseMove = this._onMouseMove.bind(this);
    this._onMouseUp = this._onMouseUp.bind(this);
    
    this.dragState = null;
    this.resizeState = null;
  }

  init() {
    // Collect all elements with .window-panel attribute
    const panels = document.querySelectorAll(".window-panel");
    panels.forEach(el => this.registerWindow(el));

    // Global drag & resize listeners (Mouse + Pointer / Touch support)
    window.addEventListener("mousemove", this._onMouseMove);
    window.addEventListener("mouseup", this._onMouseUp);
    window.addEventListener("pointermove", this._onMouseMove);
    window.addEventListener("pointerup", this._onMouseUp);

    // Restore saved layout if available
    this.loadLayout();
  }

  registerWindow(element) {
    const id = element.id || `win_${Math.random().toString(36).substr(2, 9)}`;
    element.id = id;

    const handleStartDrag = (e) => {
      if (e.target.closest(".window-controls")) return;
      this.bringToFront(id);
      this.startDrag(id, e);
    };

    // Header dragging setup (mouse + pointer)
    const header = element.querySelector(".window-header");
    if (header) {
      header.addEventListener("mousedown", handleStartDrag);
      header.addEventListener("pointerdown", handleStartDrag);
    }

    const handleStartResize = (e) => {
      e.stopPropagation();
      this.bringToFront(id);
      this.startResize(id, e);
    };

    // Add resizer if missing
    if (!element.querySelector(".window-resizer")) {
      const resizer = document.createElement("div");
      resizer.className = "window-resizer";
      element.appendChild(resizer);
      resizer.addEventListener("mousedown", handleStartResize);
      resizer.addEventListener("pointerdown", handleStartResize);
    }

    // Add window action controls if missing
    const controls = element.querySelector(".window-controls");
    if (controls && !controls.children.length) {
      controls.innerHTML = `
        <button class="window-btn btn-min" title="Minimize/Collapse" aria-label="Minimize panel">
          <span class="material-symbols-outlined text-xs">remove</span>
        </button>
        <button class="window-btn btn-max" title="Maximize (Alt+Enter)" aria-label="Maximize panel">
          <span class="material-symbols-outlined text-xs">crop_square</span>
        </button>
      `;
    }

    // Bind header control buttons
    const minBtn = element.querySelector(".btn-min");
    if (minBtn) {
      minBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        this.toggleMinimize(id);
      });
    }

    const maxBtn = element.querySelector(".btn-max");
    if (maxBtn) {
      maxBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        this.toggleMaximize(id);
      });
    }

    // Click inside window brings to front
    element.addEventListener("mousedown", () => {
      this.bringToFront(id);
    });
    element.addEventListener("pointerdown", () => {
      this.bringToFront(id);
    });

    this.windows.set(id, {
      id,
      element,
      isMinimized: false,
      isMaximized: false,
      prevRect: null
    });
  }

  bringToFront(id) {
    const win = this.windows.get(id);
    if (!win) return;
    this.activeZIndex += 1;
    win.element.style.zIndex = this.activeZIndex;
    
    // Manage focus styling
    this.windows.forEach(w => w.element.classList.remove("focused"));
    win.element.classList.add("focused");
    this.activeWindow = id;
  }

  startDrag(id, e) {
    const win = this.windows.get(id);
    if (!win || win.isMaximized) return;

    const rect = win.element.getBoundingClientRect();
    const clientX = e.clientX ?? (e.touches && e.touches[0] ? e.touches[0].clientX : 0);
    const clientY = e.clientY ?? (e.touches && e.touches[0] ? e.touches[0].clientY : 0);

    this.dragState = {
      id,
      startX: clientX,
      startY: clientY,
      initialLeft: rect.left,
      initialTop: rect.top
    };
  }

  startResize(id, e) {
    const win = this.windows.get(id);
    if (!win || win.isMaximized || win.isMinimized) return;

    const rect = win.element.getBoundingClientRect();
    const clientX = e.clientX ?? (e.touches && e.touches[0] ? e.touches[0].clientX : 0);
    const clientY = e.clientY ?? (e.touches && e.touches[0] ? e.touches[0].clientY : 0);

    this.resizeState = {
      id,
      startX: clientX,
      startY: clientY,
      initialWidth: rect.width,
      initialHeight: rect.height
    };
  }

  _onMouseMove(e) {
    const clientX = e.clientX ?? (e.touches && e.touches[0] ? e.touches[0].clientX : 0);
    const clientY = e.clientY ?? (e.touches && e.touches[0] ? e.touches[0].clientY : 0);

    if (this.dragState) {
      const { id, startX, startY, initialLeft, initialTop } = this.dragState;
      const win = this.windows.get(id);
      if (!win) return;

      const deltaX = clientX - startX;
      const deltaY = clientY - startY;

      const winWidth = win.element.offsetWidth || 300;
      const winHeight = win.element.offsetHeight || 200;
      const maxLeft = Math.max(0, window.innerWidth - winWidth);
      const maxTop = Math.max(45, window.innerHeight - winHeight);

      const clampedLeft = Math.min(maxLeft, Math.max(0, initialLeft + deltaX));
      const clampedTop = Math.min(maxTop, Math.max(45, initialTop + deltaY));

      // Position relative to viewport with strict clamping
      win.element.style.position = "fixed";
      win.element.style.left = `${clampedLeft}px`;
      win.element.style.top = `${clampedTop}px`;
      win.element.style.margin = "0";
    }

    if (this.resizeState) {
      const { id, startX, startY, initialWidth, initialHeight } = this.resizeState;
      const win = this.windows.get(id);
      if (!win) return;

      const deltaX = clientX - startX;
      const deltaY = clientY - startY;

      const newWidth = Math.max(280, Math.min(window.innerWidth - 20, initialWidth + deltaX));
      const newHeight = Math.max(180, Math.min(window.innerHeight - 50, initialHeight + deltaY));

      win.element.style.width = `${newWidth}px`;
      win.element.style.height = `${newHeight}px`;
    }
  }

  _onMouseUp() {
    if (this.dragState || this.resizeState) {
      this.saveLayout();
    }
    this.dragState = null;
    this.resizeState = null;
  }

  toggleMinimize(id) {
    const win = this.windows.get(id);
    if (!win) return;

    win.isMinimized = !win.isMinimized;
    win.element.classList.toggle("window-minimized", win.isMinimized);
    this.saveLayout();
  }

  toggleMaximize(id) {
    const win = this.windows.get(id);
    if (!win) return;

    win.isMaximized = !win.isMaximized;
    win.element.classList.toggle("window-maximized", win.isMaximized);

    const maxIcon = win.element.querySelector(".btn-max span");
    if (maxIcon) {
      maxIcon.textContent = win.isMaximized ? "close_fullscreen" : "crop_square";
    }

    this.saveLayout();
  }

  maximizeActiveWindow() {
    if (this.activeWindow) {
      this.toggleMaximize(this.activeWindow);
    }
  }

  saveLayout() {
    const layout = {};
    this.windows.forEach((win, id) => {
      layout[id] = {
        left: win.element.style.left,
        top: win.element.style.top,
        width: win.element.style.width,
        height: win.element.style.height,
        isMinimized: win.isMinimized,
        isMaximized: win.isMaximized
      };
    });
    try {
      localStorage.setItem(this.layoutKey, JSON.stringify(layout));
    } catch (_) {}
  }

  loadLayout() {
    try {
      const data = localStorage.getItem(this.layoutKey);
      if (!data) return;
      const layout = JSON.parse(data);

      Object.keys(layout).forEach(id => {
        const win = this.windows.get(id);
        const cfg = layout[id];
        if (win && cfg) {
          if (cfg.left) win.element.style.left = cfg.left;
          if (cfg.top) win.element.style.top = cfg.top;
          if (cfg.width) win.element.style.width = cfg.width;
          if (cfg.height) win.element.style.height = cfg.height;
          if (cfg.left || cfg.top) win.element.style.position = "fixed";

          if (cfg.isMinimized) {
            win.isMinimized = true;
            win.element.classList.add("window-minimized");
          }
          if (cfg.isMaximized) {
            win.isMaximized = true;
            win.element.classList.add("window-maximized");
          }
        }
      });
    } catch (_) {}
  }

  resetLayout() {
    try {
      localStorage.removeItem(this.layoutKey);
    } catch (_) {}
    this.windows.forEach(win => {
      win.element.style.position = "";
      win.element.style.left = "";
      win.element.style.top = "";
      win.element.style.width = "";
      win.element.style.height = "";
      win.element.classList.remove("window-minimized", "window-maximized");
      win.isMinimized = false;
      win.isMaximized = false;
    });
  }
}

export const windowManager = new WindowManager();
