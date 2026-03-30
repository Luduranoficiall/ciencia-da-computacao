const API = "";

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

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

document.getElementById("verifyForm").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const serial = document.getElementById("serial").value.trim();
  const out = document.getElementById("verifyResult");
  const err = document.getElementById("verifyError");
  setError(err, "", true);
  out.hidden = true;

  try {
    const res = await fetch(`${API}/public/certificates/verify/${encodeURIComponent(serial)}`);
    if (!res.ok) {
      const txt = await res.text().catch(() => "");
      throw new Error(txt || `HTTP ${res.status}`);
    }
    const data = await res.json();
    out.hidden = false;
    if (data.valid) {
      out.innerHTML = `Certificado <b>válido</b>. Emitido em (UTC): <b>${escapeHtml(
        String(data.issued_at || ""),
      )}</b>`;
    } else {
      out.textContent = "Serial não encontrado ou certificado inválido.";
    }
  } catch (e) {
    setError(err, e?.message || "Falha na verificação.");
  }
});
