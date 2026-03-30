const API = "";

const ICON_EMOJI = {
  star: "⭐",
  certificate: "📜",
  lab: "🧪",
  sparkles: "✨",
  book: "📚",
};

function setError(el, msg, hidden = false) {
  if (!el) return;
  if (!msg || hidden) {
    el.hidden = true;
    el.textContent = "";
    return;
  }
  el.hidden = false;
  el.textContent = msg;
}

function formatDetail(detail) {
  if (detail == null) return "";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((x) => {
        if (typeof x === "string") return x;
        if (x && typeof x.msg === "string") return x.msg;
        return JSON.stringify(x);
      })
      .join("; ");
  }
  if (typeof detail === "object" && typeof detail.msg === "string") return detail.msg;
  return JSON.stringify(detail);
}

let _refreshing = false;

async function tryRefreshSession() {
  if (_refreshing) return false;
  _refreshing = true;
  try {
    const res = await fetch(`${API}/auth/refresh`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
    return res.ok;
  } catch {
    return false;
  } finally {
    _refreshing = false;
  }
}

async function apiJson(path, options = {}, didRetry = false) {
  const res = await fetch(`${API}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  if (res.status === 401 && !didRetry && path !== "/auth/refresh" && path !== "/auth/token") {
    const ok = await tryRefreshSession();
    if (ok) return apiJson(path, options, true);
  }
  const ct = res.headers.get("content-type") || "";
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    if (ct.includes("application/json")) {
      try {
        const j = await res.json();
        if (j.detail) msg = formatDetail(j.detail);
      } catch {
        /* ignore */
      }
    } else {
      const txt = await res.text().catch(() => "");
      if (txt) msg = txt;
    }
    throw new Error(msg);
  }
  return res.json();
}

async function fetchPublicJson(path) {
  const res = await fetch(`${API}${path}`, { credentials: "omit" });
  const ct = res.headers.get("content-type") || "";
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    if (ct.includes("application/json")) {
      try {
        const j = await res.json();
        if (j.detail) msg = formatDetail(j.detail);
      } catch {
        /* ignore */
      }
    }
    throw new Error(msg);
  }
  return res.json();
}

function landingEl(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null && text !== "") e.textContent = text;
  return e;
}

function renderLanding(root, d) {
  root.replaceChildren();

  const brand = document.getElementById("brandTitle");
  if (brand && d.title) brand.textContent = d.title;
  if (d.title) document.title = `${d.title} — Plataforma`;

  root.appendChild(landingEl("h1", "landingTitle", d.title));
  root.appendChild(landingEl("p", "tagline", d.tagline));
  root.appendChild(landingEl("p", "muted small scopeNote", d.scope_note));

  const why = landingEl("section", "landingBlock");
  why.appendChild(landingEl("h2", null, d.why.heading));
  why.appendChild(landingEl("p", null, d.why.body));
  root.appendChild(why);

  const hg = landingEl("div", "highlightGrid");
  for (const hl of d.highlights || []) {
    const card = landingEl("article", "highlightCard");
    const ic = landingEl("div", "highlightIcon", ICON_EMOJI[hl.icon] || "•");
    card.appendChild(ic);
    card.appendChild(landingEl("h3", null, hl.title));
    card.appendChild(landingEl("p", "muted small", hl.body));
    hg.appendChild(card);
  }
  root.appendChild(hg);

  const lp = landingEl("section", "landingBlock");
  lp.appendChild(landingEl("h2", null, d.learning_path.heading));
  const trimGrid = landingEl("div", "trimesterGrid");
  for (const t of d.learning_path.trimesters || []) {
    const tb = landingEl("article", "trimesterCard");
    tb.appendChild(landingEl("h3", null, `${t.order}º trimestre — ${t.title}`));
    tb.appendChild(landingEl("p", "hours", `${t.hours} h`));
    tb.appendChild(landingEl("p", null, t.summary));
    const ul = document.createElement("ul");
    ul.className = "discList";
    for (const dis of t.disciplines) {
      const li = document.createElement("li");
      li.textContent = dis;
      ul.appendChild(li);
    }
    tb.appendChild(ul);
    trimGrid.appendChild(tb);
  }
  lp.appendChild(trimGrid);
  root.appendChild(lp);

  const aud = landingEl("section", "landingBlock");
  aud.appendChild(landingEl("h2", null, d.audience.heading));
  aud.appendChild(landingEl("p", null, d.audience.body));
  root.appendChild(aud);

  const pp = landingEl("section", "landingBlock");
  pp.appendChild(landingEl("h2", null, d.personal_prof.heading));
  pp.appendChild(landingEl("h3", "profSubtitle", d.personal_prof.subtitle));
  pp.appendChild(landingEl("p", "muted", d.personal_prof.body));
  root.appendChild(pp);

  const acc = landingEl("section", "landingBlock");
  acc.appendChild(landingEl("h2", null, d.acceleration.heading));
  acc.appendChild(landingEl("p", null, d.acceleration.body));
  root.appendChild(acc);

  const mc = landingEl("section", "landingBlock");
  mc.appendChild(landingEl("h2", null, d.microcertificates.heading));
  mc.appendChild(landingEl("p", "muted small", d.microcertificates.intro));
  const chips = landingEl("div", "chipGrid");
  for (const name of d.microcertificates.items || []) {
    const span = landingEl("span", "chip", name);
    chips.appendChild(span);
  }
  mc.appendChild(chips);
  root.appendChild(mc);

  const tp = landingEl("section", "landingBlock");
  tp.appendChild(landingEl("h2", null, d.tool_partners.heading));
  tp.appendChild(landingEl("p", "muted small", d.tool_partners.intro));
  const pg = landingEl("div", "partnerGrid");
  for (const p of d.tool_partners.items || []) {
    const card = landingEl("article", "partnerCard");
    card.appendChild(landingEl("h3", null, p.name));
    card.appendChild(landingEl("p", "muted small", p.description));
    pg.appendChild(card);
  }
  tp.appendChild(pg);
  root.appendChild(tp);

  const plat = landingEl("section", "landingBlock platformBlock");
  plat.appendChild(landingEl("h2", null, d.platform_alignment.heading));
  const pg2 = landingEl("div", "platformGrid");
  for (const it of d.platform_alignment.items || []) {
    const card = landingEl("article", "platformCard");
    card.appendChild(landingEl("h3", null, it.title));
    card.appendChild(landingEl("p", "muted small", it.body));
    pg2.appendChild(card);
  }
  plat.appendChild(pg2);
  root.appendChild(plat);
}

async function loadLanding() {
  const root = document.getElementById("landingRoot");
  const errEl = document.getElementById("landingError");
  if (!root) return;
  root.textContent = "Carregando...";
  setError(errEl, "", true);
  try {
    const data = await fetchPublicJson("/public/course-presentation");
    renderLanding(root, data);
  } catch (e) {
    const msg = e?.message || "Não foi possível carregar os textos do curso.";
    setError(errEl, msg, false);
    root.replaceChildren();
    root.appendChild(landingEl("p", "muted", "Entre com a sua conta para aceder aos módulos."));
  }
}

async function apiBlob(path) {
  const res = await fetch(`${API}${path}`, {
    credentials: "include",
  });
  const ct = res.headers.get("content-type") || "";
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    if (ct.includes("application/json")) {
      try {
        const j = await res.json();
        if (j.detail) msg = formatDetail(j.detail);
      } catch {
        /* ignore */
      }
    } else {
      const txt = await res.text().catch(() => "");
      if (txt) msg = txt;
    }
    throw new Error(msg);
  }
  return res.blob();
}

async function login(email, password) {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  const res = await fetch(`${API}/auth/token`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(formatDetail(data.detail) || "Falha no login");
  }
  return data.access_token;
}

function renderModules(modules, completedSet) {
  const list = document.getElementById("modulesList");
  list.innerHTML = "";
  if (!modules.length) {
    list.textContent = "Nenhum módulo ainda. Peça ao administrador para sincronizar o currículo.";
    return;
  }
  for (const m of modules) {
    const done = completedSet.has(m.slug);
    const item = document.createElement("div");
    item.className = "moduleItem";

    item.innerHTML = `
      <div class="moduleHeader">
        <div>
          <div class="moduleTitle">${escapeHtml(m.title)}</div>
          <div class="pill">slug: ${escapeHtml(m.slug)}</div>
        </div>
        <div>${done ? "Concluído" : "Pendente"}</div>
      </div>
      <div class="row moduleActions">
        <button class="btn" type="button" data-action="content" data-slug="${escapeHtml(m.slug)}">Ler aula</button>
        <button class="btn primary" type="button" data-action="progress" data-slug="${escapeHtml(m.slug)}" ${done ? "disabled" : ""}>
          Concluir
        </button>
      </div>
      <div class="moduleBody" id="body-${escapeHtml(m.slug)}" hidden></div>
    `;

    list.appendChild(item);
  }
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function updateProgressBar(cert) {
  const wrap = document.getElementById("progressWrap");
  const fill = document.getElementById("progressFill");
  const meta = document.getElementById("progressMeta");
  if (!cert || !cert.required || cert.required <= 0) {
    wrap.hidden = true;
    return;
  }
  wrap.hidden = false;
  const pct = Math.min(100, Math.round((cert.completed / cert.required) * 100));
  fill.style.width = `${pct}%`;
  meta.textContent = `Concluídos: ${cert.completed} / ${cert.required}`;
  const track = wrap.querySelector(".progressTrack");
  if (track) track.setAttribute("aria-valuenow", String(pct));
}

async function loadAll() {
  setError(document.getElementById("loginError"), "", true);
  setError(document.getElementById("certError"), "", true);
  const modules = await apiJson("/student/modules");
  const completed = await apiJson("/student/progress");
  const completedSet = new Set(completed);
  renderModules(modules, completedSet);

  const cert = await apiJson("/student/certificate/status");
  updateProgressBar(cert);

  const box = document.getElementById("certificateBox");
  const verifyHint = document.getElementById("verifyHint");
  if (!cert.eligible) {
    box.innerHTML = `Ainda não elegível. Conclua todos os módulos exigidos pelo currículo.`;
    verifyHint.hidden = true;
  } else if (cert.has_certificate) {
    box.innerHTML = `Certificado emitido. Serial: <b>${escapeHtml(cert.serial_number || "")}</b>`;
    verifyHint.hidden = false;
  } else {
    box.innerHTML = `Elegível. Pode gerar o certificado ou concluir o último módulo (emissão automática).`;
    verifyHint.hidden = true;
  }

  const issueBtn = document.getElementById("issueCertBtn");
  const dlBtn = document.getElementById("downloadCertBtn");
  issueBtn.disabled = !(cert.eligible && !cert.has_certificate);
  dlBtn.disabled = !cert.has_certificate;
}

async function loadModuleContent(slug) {
  const contentEl = document.getElementById(`body-${slug}`);
  const module = await apiJson(`/student/modules/${encodeURIComponent(slug)}/content`);
  contentEl.hidden = false;
  contentEl.textContent = module.body_markdown;
}

async function markProgress(slug) {
  await apiJson(`/student/progress/${encodeURIComponent(slug)}`, { method: "POST" });
  await loadAll();
}

async function issueCertificate() {
  await apiJson("/student/certificate/issue", { method: "POST" });
  await loadAll();
}

async function downloadCertificatePdf() {
  const blob = await apiBlob("/student/certificate/pdf");
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "certificado.pdf";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

async function logoutServer() {
  await fetch(`${API}/auth/logout`, { method: "POST", credentials: "include" }).catch(() => {});
}

async function boot() {
  const loginSection = document.getElementById("loginSection");
  const appSection = document.getElementById("appSection");
  const landingSection = document.getElementById("landingSection");

  try {
    await loadAll();
    loginSection.hidden = true;
    appSection.hidden = false;
    if (landingSection) landingSection.hidden = true;
  } catch (e) {
    loginSection.hidden = false;
    appSection.hidden = true;
    if (landingSection) landingSection.hidden = false;
    const msg = String(e?.message || "");
    if (
      msg.includes("401") ||
      msg.includes("Token") ||
      msg.includes("autenticad") ||
      msg.includes("Refresh")
    ) {
      setError(document.getElementById("loginError"), "", true);
    } else {
      setError(document.getElementById("loginError"), msg || "Falha ao carregar.");
    }
  }
}

document.addEventListener("submit", async (ev) => {
  if (ev.target?.id !== "loginForm") return;
  ev.preventDefault();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const err = document.getElementById("loginError");

  try {
    setError(err, "", true);
    await login(email, password);
    await boot();
  } catch (e) {
    setError(err, e?.message || "Falha no login.");
  }
});

document.addEventListener("click", async (ev) => {
  const btn = ev.target?.closest?.("button[data-action]");
  if (!btn) return;
  const action = btn.dataset.action;
  const slug = btn.dataset.slug;

  try {
    if (action === "content") await loadModuleContent(slug);
    if (action === "progress") await markProgress(slug);
  } catch (e) {
    const cer = document.getElementById("certError");
    setError(cer, e?.message || "Falha na ação.");
  }
});

document.addEventListener("DOMContentLoaded", async () => {
  await loadLanding();

  document.getElementById("logoutBtn").addEventListener("click", async () => {
    await logoutServer();
    location.reload();
  });

  document.getElementById("issueCertBtn").addEventListener("click", async () => {
    try {
      await issueCertificate();
    } catch (e) {
      setError(document.getElementById("certError"), e?.message || "Falha ao emitir certificado.");
    }
  });

  document.getElementById("downloadCertBtn").addEventListener("click", async () => {
    try {
      await downloadCertificatePdf();
    } catch (e) {
      setError(document.getElementById("certError"), e?.message || "Falha ao baixar PDF.");
    }
  });

  await boot();
});

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/ui/sw.js").catch(() => {});
}
