/**
 * THE PERSONAL SIGNAL — CLIENT CONTROLLER
 * Single-Page Broadsheet Newspaper with Modern Circular Typography
 */

let state = {
  currentCategory: "All",
  searchQuery: "",
  unreadOnly: false,
  currentPage: 1,
  perPage: 5,
  totalPages: 1,
  totalCount: 0,
  unreadCount: 0,
  articles: [],
  vaultCount: 0,
  rightPane: "wire", // "wire" or "history"
  historyArticles: [],
  historyCount: 0
};

// DOM References
const currentDateDisplay = document.getElementById("currentDateDisplay");
const unreadCountText = document.getElementById("unreadCountText");
const unreadToggleBtn = document.getElementById("unreadToggleBtn");
const unreadOnlyCheckbox = document.getElementById("unreadOnlyCheckbox");
const sectionTabs = document.getElementById("sectionTabs");
const searchInput = document.getElementById("searchInput");
const clearSearchBtn = document.getElementById("clearSearchBtn");
const vaultBadge = document.getElementById("vaultBadge");

const leftColArticles = document.getElementById("leftColArticles");
const centerColArticle = document.getElementById("centerColArticle");
const rightColArticles = document.getElementById("rightColArticles");
const rightTabWire = document.getElementById("rightTabWire");
const rightTabHistory = document.getElementById("rightTabHistory");
const historyCountBadge = document.getElementById("historyCountBadge");

const prevPageBtn = document.getElementById("prevPageBtn");
const nextPageBtn = document.getElementById("nextPageBtn");
const pageIndicatorText = document.getElementById("pageIndicatorText");

const refreshFeedsBtn = document.getElementById("refreshFeedsBtn");
const analyzeCustomBtn = document.getElementById("analyzeCustomBtn");
const settingsBtn = document.getElementById("settingsBtn");

// Modals
const articleModalOverlay = document.getElementById("articleModalOverlay");
const closeArticleModalBtn = document.getElementById("closeArticleModalBtn");
const modalStoryBody = document.getElementById("modalStoryBody");

const customModalOverlay = document.getElementById("customModalOverlay");
const closeCustomModalBtn = document.getElementById("closeCustomModalBtn");
const cancelCustomBtn = document.getElementById("cancelCustomBtn");
const customAnalysisForm = document.getElementById("customAnalysisForm");

const settingsModalOverlay = document.getElementById("settingsModalOverlay");
const closeSettingsModalBtn = document.getElementById("closeSettingsModalBtn");
const cancelSettingsBtn = document.getElementById("cancelSettingsBtn");
const saveSettingsBtn = document.getElementById("saveSettingsBtn");
const geminiApiKeyInput = document.getElementById("geminiApiKeyInput");
const sourcesTags = document.getElementById("sourcesTags");

// Toast
const newspaperToast = document.getElementById("newspaperToast");

// =====================================================================
// INITIALIZATION
// =====================================================================

document.addEventListener("DOMContentLoaded", () => {
  initDateDisplay();
  setupEventListeners();
  loadFeed();
  loadSettingsInfo();
});

function initDateDisplay() {
  const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  currentDateDisplay.textContent = new Date().toLocaleDateString('en-US', options);
}

function setupEventListeners() {
  // Navigation Tabs
  sectionTabs.addEventListener("click", (e) => {
    const btn = e.target.closest(".section-tab");
    if (!btn) return;
    
    document.querySelectorAll(".section-tab").forEach(t => t.classList.remove("active"));
    btn.classList.add("active");

    state.currentCategory = btn.dataset.category;
    state.currentPage = 1;
    loadFeed();
  });

  // Unread Toggle
  unreadToggleBtn.addEventListener("click", () => {
    state.unreadOnly = !state.unreadOnly;
    unreadOnlyCheckbox.checked = state.unreadOnly;
    state.currentPage = 1;
    loadFeed();
  });

  unreadOnlyCheckbox.addEventListener("change", (e) => {
    state.unreadOnly = e.target.checked;
    state.currentPage = 1;
    loadFeed();
  });

  // Search input
  let searchTimeout = null;
  searchInput.addEventListener("input", (e) => {
    const val = e.target.value.trim();
    state.searchQuery = val;
    clearSearchBtn.style.display = val ? "block" : "none";

    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      state.currentPage = 1;
      loadFeed();
    }, 300);
  });

  clearSearchBtn.addEventListener("click", () => {
    searchInput.value = "";
    state.searchQuery = "";
    clearSearchBtn.style.display = "none";
    state.currentPage = 1;
    loadFeed();
  });

  // Pagination navigation
  prevPageBtn.addEventListener("click", () => {
    if (state.currentPage > 1) {
      state.currentPage--;
      loadFeed();
    }
  });

  nextPageBtn.addEventListener("click", () => {
    if (state.currentPage < state.totalPages) {
      state.currentPage++;
      loadFeed();
    }
  });

  // Right Column View Switching (Wire vs History)
  if (rightTabWire && rightTabHistory) {
    rightTabWire.addEventListener("click", () => setRightPane("wire"));
    rightTabHistory.addEventListener("click", () => setRightPane("history"));
  }

  // Keyboard navigation: Left / Right arrows turn pages
  document.addEventListener("keydown", (e) => {
    if (articleModalOverlay.classList.contains("active") || 
        customModalOverlay.classList.contains("active") || 
        settingsModalOverlay.classList.contains("active")) {
      return;
    }

    if (e.key === "ArrowLeft" && state.currentPage > 1) {
      state.currentPage--;
      loadFeed();
    } else if (e.key === "ArrowRight" && state.currentPage < state.totalPages) {
      state.currentPage++;
      loadFeed();
    }
  });

  // Refresh feeds
  refreshFeedsBtn.addEventListener("click", async () => {
    const icon = refreshFeedsBtn.querySelector("i");
    icon.classList.add("fa-spin");
    showToast("Refreshing feeds...");

    try {
      await fetch("/api/feed/refresh", { method: "POST" });
      setTimeout(async () => {
        await loadFeed();
        icon.classList.remove("fa-spin");
        showToast("Feeds refreshed.");
      }, 2500);
    } catch (err) {
      icon.classList.remove("fa-spin");
      showToast("Unable to refresh feeds right now.");
    }
  });

  // Custom analysis modal
  analyzeCustomBtn.addEventListener("click", () => customModalOverlay.classList.add("active"));
  closeCustomModalBtn.addEventListener("click", () => customModalOverlay.classList.remove("active"));
  cancelCustomBtn.addEventListener("click", () => customModalOverlay.classList.remove("active"));

  customAnalysisForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const url = document.getElementById("customUrlInput").value.trim();
    const title = document.getElementById("customTitleInput").value.trim();
    const text = document.getElementById("customTextInput").value.trim();

    if (!url && !title && !text) {
      alert("Please provide at least a URL, Title, or Story text.");
      return;
    }

    const submitBtn = document.getElementById("submitCustomBtn");
    submitBtn.textContent = "Analyzing...";
    submitBtn.disabled = true;

    try {
      const resp = await fetch("/api/analyze-custom", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, title, text })
      });
      const data = await resp.json();

      customModalOverlay.classList.remove("active");
      customAnalysisForm.reset();
      showToast("Story analyzed and added.");

      await loadFeed();
      if (data.article) {
        openStoryModal(data.article);
      }
    } catch (err) {
      showToast("Error processing submission.");
    } finally {
      submitBtn.textContent = "Analyze Opportunity";
      submitBtn.disabled = false;
    }
  });

  // Settings modal
  settingsBtn.addEventListener("click", () => settingsModalOverlay.classList.add("active"));
  closeSettingsModalBtn.addEventListener("click", () => settingsModalOverlay.classList.remove("active"));
  cancelSettingsBtn.addEventListener("click", () => settingsModalOverlay.classList.remove("active"));

  saveSettingsBtn.addEventListener("click", async () => {
    const key = geminiApiKeyInput.value.trim();
    try {
      await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ gemini_api_key: key })
      });
      showToast("Settings saved.");
      settingsModalOverlay.classList.remove("active");
      loadSettingsInfo();
    } catch (err) {
      showToast("Failed to save settings.");
    }
  });

  // Story Modal
  closeArticleModalBtn.addEventListener("click", () => articleModalOverlay.classList.remove("active"));
  articleModalOverlay.addEventListener("click", (e) => {
    if (e.target === articleModalOverlay) {
      articleModalOverlay.classList.remove("active");
    }
  });
}

// =====================================================================
// DATA LOADING & PAGINATION
// =====================================================================

async function loadFeed() {
  try {
    let url = `/api/feed?page=${state.currentPage}&per_page=${state.perPage}`;
    if (state.currentCategory) {
      url += `&category=${encodeURIComponent(state.currentCategory)}`;
    }
    if (state.searchQuery) {
      url += `&search=${encodeURIComponent(state.searchQuery)}`;
    }
    if (state.unreadOnly) {
      url += `&unread_only=true`;
    }

    const resp = await fetch(url);
    const data = await resp.json();

    state.articles = data.articles || [];
    state.totalPages = data.total_pages || 1;
    state.totalCount = data.total_count || 0;
    state.unreadCount = data.unread_count || 0;
    state.historyCount = data.history_count || 0;

    // Update unread count
    unreadCountText.textContent = `${state.unreadCount} New`;
    if (historyCountBadge) {
      historyCountBadge.textContent = state.historyCount;
    }

    // Update pagination controls
    updatePaginationUI();

    // Render the broadsheet page
    renderBroadsheetPage(state.articles);

    // Update idea vault count
    fetchVaultCount();
  } catch (err) {
    console.error("Feed error:", err);
  }
}

async function fetchVaultCount() {
  try {
    const r = await fetch("/api/feed?category=Vault&per_page=1");
    const d = await r.json();
    state.vaultCount = d.total_count || 0;
    vaultBadge.textContent = state.vaultCount;
  } catch (e) {}
}

function updatePaginationUI() {
  pageIndicatorText.textContent = `Page ${state.currentPage} of ${state.totalPages}`;
  prevPageBtn.disabled = state.currentPage <= 1;
  nextPageBtn.disabled = state.currentPage >= state.totalPages;
}

// =====================================================================
// BROADSHEET RENDERER (FITS ONE PAGE)
// =====================================================================

function renderBroadsheetPage(articles) {
  if (!articles || articles.length === 0) {
    renderEmptyPage();
    return;
  }

  const leadArticle = articles[0];
  const leftArticles = articles.slice(1, 3);
  const rightArticles = articles.slice(3, 5);

  // 1. Center Hero Column
  renderCenterHero(leadArticle);

  // 2. Left Column
  renderLeftColumn(leftArticles);

  // 3. Right Column (Active tab determines Wire vs History)
  if (state.rightPane === "history") {
    loadAndRenderHistory();
  } else {
    renderRightColumn(rightArticles);
  }
}

function renderCenterHero(article) {
  if (!article) {
    centerColArticle.innerHTML = `<div style="padding: 20px; color: var(--ink-muted);">No stories on this page.</div>`;
    return;
  }

  const analysis = article.analysis || {};
  const tags = analysis.tags || ["#Business"];
  const score = analysis.signal_score ? analysis.signal_score.toFixed(1) : "9.5";
  const isUnreadClass = !article.is_read ? "is-unread" : "";

  centerColArticle.innerHTML = `
    <article class="center-hero-card ${isUnreadClass}" onclick="openStoryModalById('${article.id}')">
      <div>
        <div class="hero-header-line">
          <span style="color: var(--pompeian-red); font-weight: 700; text-transform: uppercase;">${article.source_category}</span>
          <span class="hero-score-badge">★ ${score}</span>
        </div>

        <h2 class="hero-headline">${article.title}</h2>
        <p class="hero-lede">${article.summary}</p>

        ${analysis.why_it_matters ? `
          <div class="hero-why-box">
            <strong>WHY IT MATTERS</strong>
            ${analysis.why_it_matters}
          </div>
        ` : ""}

        ${analysis.business_opportunity ? `
          <div class="hero-opportunity-box">
            <strong>BUSINESS OPPORTUNITY</strong>
            ${analysis.business_opportunity}
          </div>
        ` : ""}

        <div class="hero-tags-row">
          ${tags.map(t => `<span class="hero-tag">${t}</span>`).join("")}
        </div>
      </div>

      <div class="hero-action-bar">
        <span>${article.source_name} • ${article.published_at || "Today"}</span>
        <button class="btn-open-story">
          <span>Read Story</span> <i class="fa-solid fa-arrow-right"></i>
        </button>
      </div>
    </article>
  `;
}

function renderLeftColumn(articles) {
  if (!articles || articles.length === 0) {
    leftColArticles.innerHTML = `<div style="padding: 10px; color: var(--ink-muted); font-size: 0.8rem;">No additional stories on this page.</div>`;
    return;
  }

  leftColArticles.innerHTML = articles.map(art => {
    const analysis = art.analysis || {};
    const isUnreadClass = !art.is_read ? "is-unread" : "";
    return `
      <div class="newspaper-card ${isUnreadClass}" onclick="openStoryModalById('${art.id}')">
        <div>
          <div class="card-kicker-line">
            <span class="card-category-tag">${art.source_category}</span>
            <span>•</span>
            <span>${art.source_name}</span>
          </div>
          <h3 class="card-title">${art.title}</h3>
          <p class="card-lead-text">${art.summary}</p>
          
          ${analysis.business_opportunity ? `
            <div class="card-opportunity-strip">
              <strong>OPPORTUNITY</strong>
              ${analysis.business_opportunity}
            </div>
          ` : ""}
        </div>

        <div class="card-footer-meta">
          <span>${art.published_at || "Recent"}</span>
          <span class="click-hint">Read →</span>
        </div>
      </div>
    `;
  }).join("");
}

function setRightPane(pane) {
  state.rightPane = pane;
  if (rightTabWire && rightTabHistory) {
    rightTabWire.classList.toggle("active", pane === "wire");
    rightTabHistory.classList.toggle("active", pane === "history");
  }
  if (pane === "history") {
    loadAndRenderHistory();
  } else {
    const rightArticles = state.articles.slice(3, 5);
    renderRightColumn(rightArticles);
  }
}

function renderRightColumn(articles) {
  if (state.rightPane === "history") {
    loadAndRenderHistory();
    return;
  }

  if (!articles || articles.length === 0) {
    rightColArticles.innerHTML = `<div style="padding: 10px; color: var(--ink-muted); font-size: 0.8rem;">Stories continue on the next page.</div>`;
    return;
  }

  rightColArticles.innerHTML = articles.map(art => {
    const analysis = art.analysis || {};
    const isUnreadClass = !art.is_read ? "is-unread" : "";
    return `
      <div class="newspaper-card ${isUnreadClass}" onclick="openStoryModalById('${art.id}')">
        <div>
          <div class="card-kicker-line">
            <span class="card-category-tag">${art.source_category}</span>
            <span>•</span>
            <span>${art.source_name}</span>
          </div>
          <h3 class="card-title">${art.title}</h3>
          <p class="card-lead-text">${art.summary}</p>
          
          ${analysis.market_gap ? `
            <div class="card-opportunity-strip" style="border-left-color: var(--pompeian-red);">
              <strong style="color: var(--pompeian-red);">MARKET GAP</strong>
              ${analysis.market_gap}
            </div>
          ` : ""}
        </div>

        <div class="card-footer-meta">
          <span>${art.published_at || "Recent"}</span>
          <span class="click-hint">Read →</span>
        </div>
      </div>
    `;
  }).join("");
}

async function loadAndRenderHistory() {
  try {
    const resp = await fetch("/api/history?limit=30");
    const data = await resp.json();
    const historyItems = data.history || [];
    state.historyArticles = historyItems;
    state.historyCount = data.count || historyItems.length;

    if (historyCountBadge) {
      historyCountBadge.textContent = state.historyCount;
    }

    if (!historyItems || historyItems.length === 0) {
      rightColArticles.innerHTML = `
        <div class="empty-history-box">
          <i class="fa-solid fa-clock-rotate-left"></i>
          <p>No Reading History Yet</p>
          <small>Stories you open or read will automatically be archived here so you never lose any insight or business opportunity.</small>
        </div>
      `;
      return;
    }

    rightColArticles.innerHTML = historyItems.map(art => {
      const analysis = art.analysis || {};
      const readDate = art.read_at ? formatTimeAgo(art.read_at) : (art.published_at || "Read");
      const isSaved = art.is_saved;

      return `
        <div class="newspaper-card history-card" onclick="openStoryModalById('${art.id}')">
          <div>
            <div class="card-kicker-line">
              <span class="card-category-tag">${art.source_category || "Insight"}</span>
              <span>•</span>
              <span class="history-time-meta"><i class="fa-regular fa-clock"></i> ${readDate}</span>
              ${isSaved ? `<span class="history-vault-indicator"><i class="fa-solid fa-bookmark"></i> Vault</span>` : ""}
            </div>
            <h3 class="card-title">${art.title}</h3>
            ${analysis.business_opportunity ? `
              <div class="card-opportunity-strip">
                <strong>OPPORTUNITY</strong>
                ${analysis.business_opportunity}
              </div>
            ` : (analysis.key_takeaway ? `
              <p class="card-lead-text" style="font-style: italic;">"${analysis.key_takeaway}"</p>
            ` : `
              <p class="card-lead-text">${art.summary || ""}</p>
            `)}
          </div>
          <div class="card-footer-meta">
            <span>${art.source_name || "Archive"}</span>
            <span class="click-hint">Review →</span>
          </div>
        </div>
      `;
    }).join("");
  } catch (err) {
    console.error("Error loading history:", err);
    rightColArticles.innerHTML = `<div style="padding: 10px; color: var(--ink-muted); font-size: 0.8rem;">Could not load history.</div>`;
  }
}

function formatTimeAgo(dateStr) {
  if (!dateStr) return "Recently";
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return "Recently";
    const now = new Date();
    const diffSec = Math.floor((now - d) / 1000);
    if (diffSec < 60) return "Just now";
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffHr = Math.floor(diffMin / 60);
    if (diffHr < 24) return `${diffHr}h ago`;
    const diffDays = Math.floor(diffHr / 24);
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays}d ago`;
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  } catch (e) {
    return "Recently";
  }
}

function renderEmptyPage() {
  centerColArticle.innerHTML = `
    <div class="center-hero-card" style="text-align: center; justify-content: center; align-items: center; padding: 40px 20px;">
      <i class="fa-solid fa-newspaper" style="font-size: 2.2rem; color: var(--mineral-gray-dark); margin-bottom: 12px;"></i>
      <h2 class="hero-headline" style="font-size: 1.35rem;">No Stories Found</h2>
      <p class="hero-lede" style="font-size: 0.88rem; max-width: 380px; margin: 0 auto;">All stories have been read, or no matches were found.</p>
      <button class="btn-newspaper-primary" style="margin-top: 14px;" onclick="resetFilters()">
        View Front Page
      </button>
    </div>
  `;
  leftColArticles.innerHTML = "";
  rightColArticles.innerHTML = "";
}

function resetFilters() {
  state.unreadOnly = false;
  unreadOnlyCheckbox.checked = false;
  state.searchQuery = "";
  searchInput.value = "";
  state.currentCategory = "All";
  document.querySelectorAll(".section-tab").forEach(t => {
    t.classList.toggle("active", t.dataset.category === "All");
  });
  state.currentPage = 1;
  loadFeed();
}

// =====================================================================
// FULL STORY MODAL
// =====================================================================

function openStoryModalById(articleId) {
  const art = state.articles.find(a => a.id === articleId) || 
              (state.historyArticles && state.historyArticles.find(a => a.id === articleId));
  if (art) {
    openStoryModal(art);
  }
}

async function openStoryModal(art) {
  const analysis = art.analysis || {};
  const tags = analysis.tags || [];
  const affected = analysis.affected_players || [];

  modalStoryBody.innerHTML = `
    <div class="modal-meta-top">
      <span class="modal-category">${art.source_category}</span>
      <span class="modal-score">★ ${analysis.signal_score ? analysis.signal_score.toFixed(1) : "9.0"}</span>
    </div>

    <h2 class="modal-title">${art.title}</h2>
    
    <div class="modal-source-row">
      Published by <strong>${art.source_name}</strong> • ${art.published_at || "Recent"} • 
      <a href="${art.url}" target="_blank" rel="noopener noreferrer">Read Original <i class="fa-solid fa-arrow-up-right-from-square"></i></a>
    </div>

    <!-- Key Takeaway -->
    ${analysis.key_takeaway ? `
      <div class="modal-section-card" style="border-left: 4px solid var(--ink-primary); background: var(--paper-cream);">
        <div class="modal-section-title" style="color: var(--ink-primary);"><i class="fa-solid fa-bullseye"></i> Key Takeaway</div>
        <div class="modal-section-text" style="font-weight: 600;">${analysis.key_takeaway}</div>
      </div>
    ` : ""}

    <!-- Why It Matters -->
    <div class="modal-section-card why-card">
      <div class="modal-section-title"><i class="fa-solid fa-circle-exclamation"></i> Why It Matters</div>
      <div class="modal-section-text">${analysis.why_it_matters || "Strategic indicator in this industry."}</div>
    </div>

    <!-- Business Opportunity -->
    <div class="modal-section-card opportunity-card">
      <div class="modal-section-title"><i class="fa-solid fa-lightbulb"></i> Business Opportunity</div>
      <div class="modal-section-text" style="font-weight: 500;">${analysis.business_opportunity || "Provides opportunity for workflow automation and niche market entry."}</div>
    </div>

    <!-- Market Gap -->
    <div class="modal-section-card">
      <div class="modal-section-title" style="color: var(--ink-muted);"><i class="fa-solid fa-chart-pie"></i> Market Gap</div>
      <div class="modal-section-text">${analysis.market_gap || "Incumbent providers have not resolved this friction."}</div>
    </div>

    <!-- Companies & Sectors Involved -->
    ${affected.length > 0 ? `
      <div class="modal-section-card">
        <div class="modal-section-title" style="color: var(--ink-muted);"><i class="fa-solid fa-building"></i> Companies &amp; Sectors Involved</div>
        <div class="modal-section-text">
          <ul style="padding-left: 20px;">
            ${affected.map(p => `<li>${p}</li>`).join("")}
          </ul>
        </div>
      </div>
    ` : ""}

    <!-- Story Summary -->
    <div class="modal-section-card">
      <div class="modal-section-title" style="color: var(--ink-muted);"><i class="fa-solid fa-newspaper"></i> Story Summary</div>
      <div class="modal-section-text">${art.summary}</div>
    </div>

    <!-- Personal Notes & Ideas -->
    <div class="scratchpad-area">
      <div class="modal-section-title" style="color: var(--pompeian-red);"><i class="fa-solid fa-pen-nib"></i> Personal Notes &amp; Ideas</div>
      <p style="font-size: 0.78rem; color: var(--ink-muted);">Jot down notes or brainstorming angles. Saving records this to your Idea Vault.</p>
      <textarea id="modalUserNotes" rows="3" placeholder="Write ideas, execution notes, or who to connect with...">${art.user_notes || ""}</textarea>
      
      <div class="modal-action-row">
        <button class="btn-newspaper-primary" onclick="saveNotesAndBookmark('${art.id}')">
          <i class="fa-solid fa-bookmark"></i> Save to Idea Vault
        </button>
      </div>
    </div>
  `;

  articleModalOverlay.classList.add("active");

  // Automatically mark as read/viewed and track in reading history
  if (!art.is_read) {
    try {
      art.is_read = true;
      const resp = await fetch(`/api/articles/${art.id}/read`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_read: true })
      });
      const data = await resp.json();
      state.unreadCount = data.unread_count;
      unreadCountText.textContent = `${state.unreadCount} New`;
      if (data.history_count !== undefined) {
        state.historyCount = data.history_count;
        if (historyCountBadge) {
          historyCountBadge.textContent = state.historyCount;
        }
      }

      // Update card visual
      const cards = document.querySelectorAll(`[onclick*="${art.id}"]`);
      cards.forEach(c => c.classList.remove("is-unread"));

      if (state.rightPane === "history") {
        loadAndRenderHistory();
      }
    } catch (e) {
      console.error("Mark read error:", e);
    }
  }
}

async function saveNotesAndBookmark(articleId) {
  const notes = document.getElementById("modalUserNotes").value.trim();
  try {
    await fetch("/api/vault/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ article_id: articleId, notes: notes })
    });
    showToast("Saved to Idea Vault.");
    articleModalOverlay.classList.remove("active");
    fetchVaultCount();
    if (state.rightPane === "history") {
      loadAndRenderHistory();
    }
  } catch (err) {
    showToast("Error saving notes.");
  }
}

// =====================================================================
// SETTINGS
// =====================================================================

async function loadSettingsInfo() {
  try {
    const [settingsResp, sourcesResp] = await Promise.all([
      fetch("/api/settings"),
      fetch("/api/sources")
    ]);
    
    const settingsData = await settingsResp.json();
    const sourcesData = await sourcesResp.json();

    if (settingsData.gemini_key_preview) {
      geminiApiKeyInput.placeholder = `Active key: ${settingsData.gemini_key_preview}`;
    }

    if (sourcesData.sources) {
      sourcesTags.innerHTML = sourcesData.sources.map(s => `
        <span>${s.name} (${s.category})</span>
      `).join("");
    }
  } catch (err) {
    console.error("Settings load error:", err);
  }
}

function showToast(msg) {
  newspaperToast.textContent = msg;
  newspaperToast.classList.add("show");
  setTimeout(() => newspaperToast.classList.remove("show"), 2500);
}
