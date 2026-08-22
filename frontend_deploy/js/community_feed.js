/**
 * community_feed.js — Community & Expert Discussion Feed for StockAnalyzer
 * Manages ticker-tagged posts, research comments, likes, bookmarks, and author follow actions.
 */

const API_BASE = window.API_BASE || "";

const DEFAULT_POSTS = [
  {
    id: 1,
    author: "Rakesh V. (Value Investor)",
    handle: "@rv_equity",
    symbol: "RELIANCE",
    time: "15m ago",
    content: "New Green Energy gigafactory commissioning timeline accelerates FCF generation capability for FY26. Accumulating on dips around ₹2900.",
    likes: 42,
    comments: 8,
    isLiked: false
  },
  {
    id: 2,
    author: "Deepak S. (Quant Trader)",
    handle: "@quant_deepak",
    symbol: "POLYCAB",
    time: "42m ago",
    content: "Massive institutional delivery volumes recorded today. Breakout above ₹6800 confirms multi-quarter cup-and-handle pattern. Target ₹7500.",
    likes: 89,
    comments: 15,
    isLiked: true
  },
  {
    id: 3,
    author: "Shruti M. (Macro Strategist)",
    handle: "@shruti_macro",
    symbol: "HAL",
    time: "1h ago",
    content: "Defence ministry export pipeline expanded by ₹25,000 Cr. HAL order book visibility exceeds 7 years. Compounding machine.",
    likes: 64,
    comments: 11,
    isLiked: false
  }
];

export async function initCommunityFeed() {
  const container = document.getElementById("community-feed-body");
  if (!container) return;

  window.submitNewPost = submitNewPost;
  window.togglePostLike = togglePostLike;

  // Attempt backend API fetch
  try {
    const resp = await fetch(`${API_BASE}/api/v1/community/posts`);
    if (resp.ok) {
      const data = await resp.json();
      if (Array.isArray(data) && data.length > 0) {
        window.__IERL_COMMUNITY_POSTS = data;
      }
    }
  } catch (_) {}

  if (!window.__IERL_COMMUNITY_POSTS) {
    window.__IERL_COMMUNITY_POSTS = DEFAULT_POSTS;
  }

  renderFeedUI();

  window.onSymbolChanged = (symbol) => {
    renderFeedUI(symbol);
  };
}

function renderFeedUI(symbolFilter = null) {
  const container = document.getElementById("community-feed-body");
  if (!container) return;

  const currentSymbol = symbolFilter || window.__IERL_SELECTED_SYMBOL || "RELIANCE";
  const posts = window.__IERL_COMMUNITY_POSTS || DEFAULT_POSTS;

  const postsHTML = posts.map(post => `
    <div class="p-3 bg-surface-lowest rounded border border-surface-border/50 space-y-2 text-xs">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 rounded-full bg-gold/20 text-gold flex items-center justify-center font-bold text-[10px]">
            ${post.author.charAt(0)}
          </div>
          <div>
            <span class="font-bold text-white">${post.author}</span>
            <span class="text-[10px] text-muted ml-1">${post.handle}</span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="badge badge-warning font-mono cursor-pointer" onclick="window.selectSymbol('${post.symbol}')">$${post.symbol}</span>
          <span class="text-[10px] text-muted">${post.time}</span>
        </div>
      </div>

      <p class="text-gray-200 leading-relaxed">${escapeHtml(post.content)}</p>

      <div class="flex items-center justify-between text-[11px] text-muted pt-1 border-t border-surface-border/30">
        <button onclick="window.togglePostLike(${post.id})" class="flex items-center gap-1 hover:text-gold ${post.isLiked ? 'text-gold font-bold' : ''}">
          <span class="material-symbols-outlined text-xs">${post.isLiked ? 'thumb_up' : 'thumb_up_off_alt'}</span> ${post.likes}
        </button>
        <span class="flex items-center gap-1 hover:text-white cursor-pointer">
          <span class="material-symbols-outlined text-xs">chat</span> ${post.comments} Comments
        </span>
        <button class="flex items-center gap-1 hover:text-gold">
          <span class="material-symbols-outlined text-xs">bookmark_border</span> Bookmark
        </button>
      </div>
    </div>
  `).join("");

  container.innerHTML = `
    <div class="flex flex-col h-full space-y-3">
      <!-- Create Post Box -->
      <div class="p-2.5 bg-surface-lowest rounded border border-surface-border space-y-2">
        <textarea id="community-post-input" rows="2" class="form-input text-xs w-full resize-none" placeholder="Share research note or ask community about ${currentSymbol}..."></textarea>
        <div class="flex justify-between items-center">
          <span class="text-[10px] text-muted font-mono">Supports #Tickers & Markdown</span>
          <button onclick="window.submitNewPost()" class="btn-primary text-xs py-1 px-3">Post Note</button>
        </div>
      </div>

      <!-- Feed List -->
      <div class="flex-1 overflow-y-auto space-y-2.5" id="community-posts-list">
        ${postsHTML}
      </div>
    </div>
  `;
}

function submitNewPost() {
  const input = document.getElementById("community-post-input");
  if (!input || !input.value.trim()) return;

  const symbol = window.__IERL_SELECTED_SYMBOL || "RELIANCE";

  const newPost = {
    id: Date.now(),
    author: "You (Senior Trader)",
    handle: "@you",
    symbol,
    time: "Just now",
    content: input.value.trim(),
    likes: 1,
    comments: 0,
    isLiked: true
  };

  window.__IERL_COMMUNITY_POSTS = window.__IERL_COMMUNITY_POSTS || DEFAULT_POSTS;
  window.__IERL_COMMUNITY_POSTS.unshift(newPost);

  // Try API post persistence if available
  fetch(`${API_BASE}/api/v1/community/posts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(newPost)
  }).catch(() => {});

  input.value = "";
  renderFeedUI();
}

function togglePostLike(id) {
  const posts = window.__IERL_COMMUNITY_POSTS || DEFAULT_POSTS;
  const post = posts.find(p => p.id === id);
  if (post) {
    post.isLiked = !post.isLiked;
    post.likes += post.isLiked ? 1 : -1;
    renderFeedUI();
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
