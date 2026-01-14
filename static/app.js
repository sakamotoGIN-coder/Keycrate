let mode = "login";

// ---------- Helpers ----------
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (m) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[m]));
}
function token() { return localStorage.getItem("token"); }
function username() { return localStorage.getItem("username"); }

// ---------- Sidebar ----------
function openSidebar() {
  document.getElementById("sidebar")?.classList.add("open");
  document.getElementById("sidebarBackdrop")?.classList.remove("hidden");
}
function closeSidebar() {
  document.getElementById("sidebar")?.classList.remove("open");
  document.getElementById("sidebarBackdrop")?.classList.add("hidden");
}
function initSidebarBindings() {
  document.getElementById("openSidebarBtn")?.addEventListener("click", openSidebar);
  document.getElementById("closeSidebarBtn")?.addEventListener("click", closeSidebar);
  document.getElementById("sidebarBackdrop")?.addEventListener("click", closeSidebar);

  document.getElementById("vaultBtn")?.addEventListener("click", () => {
    window.location.href = "/vault-ui";
  });

  document.getElementById("generateNavBtn")?.addEventListener("click", () => {
    window.location.href = "/";
  });
}

// ---------- Auth Modal ----------
function setMode(newMode) {
  mode = newMode;
  const authTitle = document.getElementById("authTitle");
  const toggleText = document.getElementById("toggleText");
  const toggleBtn = document.getElementById("toggleModeBtn");
  const authError = document.getElementById("authError");

  if (authTitle) authTitle.textContent = mode === "login" ? "Login" : "Sign up";
  if (toggleText) toggleText.textContent = mode === "login" ? "Don't have an account?" : "Already have an account?";
  if (toggleBtn) toggleBtn.textContent = mode === "login" ? "Sign up" : "Login";
  if (authError) authError.textContent = "";
}

function showAuth() {
  const m = document.getElementById("authModal");
  if (m) m.classList.remove("hidden");
}
function hideAuth() {
  const m = document.getElementById("authModal");
  if (m) m.classList.add("hidden");
}

function renderTopbarUser() {
  const topbarRight = document.getElementById("topbarRight");
  if (!topbarRight) return;

  const u = username();
  if (!u) return;

  if (topbarRight.innerHTML.includes("logoutBtn")) return;

  topbarRight.insertAdjacentHTML("beforeend", `
    <div class="user-pill"><span>${escapeHtml(u)}</span></div>
    <button class="logout" id="logoutBtn">Logout</button>
  `);

  document.getElementById("logoutBtn")?.addEventListener("click", () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    window.location.href = "/";
  });
}

async function submitAuth() {
  const uEl = document.getElementById("username");
  const pEl = document.getElementById("password");
  const authError = document.getElementById("authError");

  const u = (uEl?.value || "").trim();
  const p = (pEl?.value || "").trim();

  if (!u || !p) {
    if (authError) authError.textContent = "Please fill in username and password.";
    return;
  }

  const url = mode === "login" ? "/auth/login" : "/auth/register";

  const res = await fetch(url, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ username: u, password: p })
  });

  if (!res.ok) {
    let msg = "Authentication failed";
    try { msg = (await res.json()).detail || msg; }
    catch { msg = await res.text(); }
    if (authError) authError.textContent = msg;
    return;
  }

  const data = await res.json();

  if (mode === "register") {
    if (authError) authError.textContent = "Registered! Please login.";
    setMode("login");
    return;
  }

  if (!data.access_token) {
    if (authError) authError.textContent = "Login succeeded but token missing.";
    return;
  }

  localStorage.setItem("token", data.access_token);
  localStorage.setItem("username", u);

  hideAuth();
  renderTopbarUser();
}

// ---------- Generate ----------
async function generate() {
  const out = document.getElementById("output");
  const hintEl = document.getElementById("hint");
  const t = token();

  if (!t) {
    showAuth();
    return;
  }

  const hint = (hintEl?.value || "").trim();
  if (!hint) {
    if (out) out.textContent = "Please enter a hint.";
    return;
  }

  if (out) out.textContent = "Generating...";

  const res = await fetch("/ai/generate", {
    method: "POST",
    headers: {
      "Content-Type":"application/json",
      "Authorization": `Bearer ${t}`
    },
    body: JSON.stringify({ hint })
  });

  if (!res.ok) {
    let msg = "Generation failed";
    try { msg = (await res.json()).detail || msg; }
    catch { msg = await res.text(); }
    if (out) out.textContent = msg;
    return;
  }

  const data = await res.json();
  if (out) out.textContent = data.password ?? "No password returned.";
}

// ---------- Copy generated ----------
async function copyGenerated() {
  const out = document.getElementById("output");
  const text = (out?.textContent || "").trim();
  if (!text || text === "—" || text === "Generating...") return;

  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const ta = document.createElement("textarea");
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    document.body.removeChild(ta);
  }
}

// ---------- Save popup ----------
function openPlatformModal() {
  const modal = document.getElementById("platformModal");
  const err = document.getElementById("platformError");
  const inp = document.getElementById("platformInput");

  if (err) err.textContent = "";
  if (inp) inp.value = "";
  if (modal) modal.classList.remove("hidden");
  inp?.focus();
}
function closePlatformModal() {
  document.getElementById("platformModal")?.classList.add("hidden");
}

async function saveToVault() {
  const t = token();
  const out = document.getElementById("output");
  const inp = document.getElementById("platformInput");
  const err = document.getElementById("platformError");

  if (!t) { showAuth(); return; }

  const platform = (inp?.value || "").trim();
  const password = (out?.textContent || "").trim();

  if (!platform) { if (err) err.textContent = "Platform is required."; return; }
  if (!password || password === "—" || password === "Generating..." || password.toLowerCase().includes("failed")) {
    if (err) err.textContent = "Generate a password first.";
    return;
  }

  const res = await fetch("/vault/save", {
    method: "POST",
    headers: {
      "Content-Type":"application/json",
      "Authorization": `Bearer ${t}`
    },
    body: JSON.stringify({ platform, password })
  });

  if (!res.ok) {
    let msg = "Save failed";
    try { msg = (await res.json()).detail || msg; }
    catch { msg = await res.text(); }
    if (err) err.textContent = msg;
    return;
  }

  closePlatformModal();
  alert("Saved to Vault!");
}

// ---------- Vault Page ----------
let _vaultEntriesCache = [];
let _revealed = new Set();
let _revealedPassword = new Map();

async function initVaultPageEnhanced() {
  initSidebarBindings();

  const t = token();
  const u = username();
  if (!t || !u) { window.location.href = "/"; return; }

  renderTopbarUser();

  document.getElementById("vaultRefreshBtn")?.addEventListener("click", loadVaultTable);
  document.getElementById("vaultSearch")?.addEventListener("input", renderVaultTable);
  document.getElementById("vaultSort")?.addEventListener("change", renderVaultTable);

  await loadVaultTable();
}

async function loadVaultTable() {
  const t = token();
  const tbody = document.getElementById("vaultTbody");
  if (!tbody) return;

  tbody.innerHTML = `<tr><td colspan="4" class="vault-empty">Loading...</td></tr>`;

  const res = await fetch("/vault/list", {
    headers: { "Authorization": `Bearer ${t}` }
  });

  if (!res.ok) {
    tbody.innerHTML = `<tr><td colspan="4" class="vault-empty">Failed to load vault.</td></tr>`;
    return;
  }

  _vaultEntriesCache = await res.json();
  renderVaultTable();
}

function renderVaultTable() {
  const tbody = document.getElementById("vaultTbody");
  if (!tbody) return;

  const search = (document.getElementById("vaultSearch")?.value || "").trim().toLowerCase();
  const sort = (document.getElementById("vaultSort")?.value || "newest");

  let rows = [..._vaultEntriesCache];

  if (search) rows = rows.filter(e => (e.platform || "").toLowerCase().includes(search));

  if (sort === "newest") rows.sort((a,b) => new Date(b.created_at) - new Date(a.created_at));
  if (sort === "oldest") rows.sort((a,b) => new Date(a.created_at) - new Date(b.created_at));
  if (sort === "az") rows.sort((a,b) => (a.platform||"").localeCompare(b.platform||""));
  if (sort === "za") rows.sort((a,b) => (b.platform||"").localeCompare(a.platform||""));

  if (!rows.length) {
    tbody.innerHTML = `<tr><td colspan="4" class="vault-empty">No matching entries.</td></tr>`;
    return;
  }

  tbody.innerHTML = rows.map(e => {
    const isRevealed = _revealed.has(e.id);
    const btnText = isRevealed ? "Hide" : "Reveal";
    const pwText = isRevealed ? escapeHtml(_revealedPassword.get(e.id) || "") : "••••••••••••";

    return `
      <tr>
        <td>${escapeHtml(e.platform)}</td>
        <td>${new Date(e.created_at).toLocaleString()}</td>
        <td><span id="pwd-${e.id}" class="vault-mask">${pwText || "••••••••••••"}</span></td>
        <td>
          <div class="vault-actions">
            <button class="ghost-btn" onclick="vaultToggle(${e.id})">${btnText}</button>
            <button class="primary-btn" onclick="vaultCopy(${e.id})">Copy</button>
            <button class="ghost-btn" onclick="vaultDelete(${e.id})">Delete</button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

async function vaultToggle(id) {
  if (_revealed.has(id)) {
    _revealed.delete(id);
    renderVaultTable();
    return;
  }

  const t = token();
  const res = await fetch(`/vault/${id}/reveal`, {
    headers: { "Authorization": `Bearer ${t}` }
  });

  if (!res.ok) return;

  const data = await res.json();
  _revealed.add(id);
  _revealedPassword.set(id, data.password);
  renderVaultTable();
}

async function vaultCopy(id) {
  if (!_revealed.has(id)) {
    await vaultToggle(id);
  }

  const pw = _revealedPassword.get(id);
  if (!pw) return;

  try { await navigator.clipboard.writeText(pw); }
  catch {
    const ta = document.createElement("textarea");
    ta.value = pw;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    document.body.removeChild(ta);
  }
}

async function vaultDelete(id) {
  const ok = confirm("Delete this password from Vault?");
  if (!ok) return;

  const t = token();
  const res = await fetch(`/vault/${id}`, {
    method: "DELETE",
    headers: { "Authorization": `Bearer ${t}` }
  });

  if (!res.ok) {
    alert("Delete failed");
    return;
  }

  _vaultEntriesCache = _vaultEntriesCache.filter(x => x.id !== id);
  _revealed.delete(id);
  _revealedPassword.delete(id);
  renderVaultTable();
}

window.initVaultPageEnhanced = initVaultPageEnhanced;

// ---------- Init on index ----------
document.addEventListener("DOMContentLoaded", () => {
  initSidebarBindings();
  setMode("login");

  document.getElementById("toggleModeBtn")?.addEventListener("click", () => {
    setMode(mode === "login" ? "register" : "login");
  });

  document.getElementById("authSubmitBtn")?.addEventListener("click", submitAuth);
  document.getElementById("username")?.addEventListener("keydown", (e) => { if (e.key === "Enter") submitAuth(); });
  document.getElementById("password")?.addEventListener("keydown", (e) => { if (e.key === "Enter") submitAuth(); });

  document.getElementById("generateBtn")?.addEventListener("click", generate);
  document.getElementById("hint")?.addEventListener("keydown", (e) => { if (e.key === "Enter") generate(); });

  document.getElementById("copyBtn")?.addEventListener("click", copyGenerated);

  document.getElementById("saveBtn")?.addEventListener("click", () => {
    if (!token()) { showAuth(); return; }
    const out = (document.getElementById("output")?.textContent || "").trim();
    if (!out || out === "—" || out === "Generating..." || out.toLowerCase().includes("failed")) {
      alert("Generate a password first.");
      return;
    }
    openPlatformModal();
  });

  document.getElementById("platformCancelBtn")?.addEventListener("click", closePlatformModal);
  document.getElementById("platformSaveBtn")?.addEventListener("click", saveToVault);
  document.getElementById("platformInput")?.addEventListener("keydown", (e) => { if (e.key === "Enter") saveToVault(); });

  if (token() && username()) {
    hideAuth();
    renderTopbarUser();
  } else {
    showAuth();
  }
});












