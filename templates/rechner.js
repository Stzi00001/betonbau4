/* ---------- Bemessungstool: Eingaben, Ergebnisse und vollständiger Rechenweg aus der Inhaltsdatei ---------- */
const IN_FRAME = (() => { try { return window.self !== window.top; } catch(e){ return true; } })();
function fmtVal(v, d){ return typeof v === "number" ? fmt(v, d) : String(v); }

function Rechner(t, el){
  const R = t.rechner, key = "calc2-" + t.id;
  const p = Object.assign(Object.fromEntries(R.eingaben.map(e => [e.id, e.default])), store.get(key, {}));
  const inp = e => {
    if (e.typ === "auswahl") return `<div class="fld"><label for="i-${e.id}">${e.label}</label><select id="i-${e.id}">${e.werte.map(w => `<option ${w === p[e.id] ? "selected" : ""}>${esc(w)}</option>`).join("")}</select>${e.hinweis ? `<small>${e.hinweis}</small>` : ""}</div>`;
    if (e.typ === "schalter") return `<div><span class="label">${e.label}</span><div class="seg" data-id="${e.id}">${e.optionen.map(o => `<button type="button" data-v="${o.v}" class="${o.v === p[e.id] ? "on" : ""}">${o.t}</button>`).join("")}</div></div>`;
    return `<div class="fld"><label for="i-${e.id}">${e.label}${e.einheit ? ` [${e.einheit}]` : ""}</label><input id="i-${e.id}" type="number" inputmode="decimal" step="${e.step ?? 1}" ${e.min !== undefined ? `min="${e.min}"` : ""} ${e.max !== undefined ? `max="${e.max}"` : ""} value="${p[e.id]}">${e.hinweis ? `<small>${e.hinweis}</small>` : ""}</div>`;
  };
  el.innerHTML = `${t.status !== "fertig" ? `<p class="note">Vorläufig nach DIN EN 1992-1-1 + NA (DE). Rechenweg und Annahmen werden mit dem Skript abgeglichen. Beispielwerte sind vorbelegt.</p>` : ""}
  <div class="calc">
    <div class="panel"><h3>Eingabe</h3>${R.eingaben.map(inp).join("")}
      <button class="btn ghost" id="c-reset" type="button">Beispielwerte laden</button></div>
    <div style="display:grid;gap:16px;min-width:0">
      ${R.skizze ? `<svg class="xsec" id="xsec" viewBox="0 0 360 300" role="img" aria-label="Querschnittsskizze"></svg>` : ""}
      <div class="results" id="res"></div>
    </div>
  </div>
  <section class="rw" id="rw-box">
    <div class="rw-head"><h3>Rechenweg</h3>
      <div class="row">${IN_FRAME ? "" : `<button class="btn" id="c-pdf" type="button">Rechenweg als PDF</button>`}
        ${pdfLinks(t, "rechenweg")}<button class="btn ghost" id="c-fold" type="button">Zuklappen</button></div></div>
    ${IN_FRAME ? `<p class="note">PDF-Export: in der Web-App unter ${esc((DATA.site || "").replace(/^https?:\/\//, ""))} öffnen.</p>` : ""}
    <div class="rw-doc" id="rw"></div>
  </section>`;

  R.eingaben.forEach(e => {
    if (e.typ === "schalter"){
      el.querySelectorAll(`.seg[data-id="${e.id}"] button`).forEach(b => b.onclick = () => {
        p[e.id] = b.dataset.v; el.querySelectorAll(`.seg[data-id="${e.id}"] button`).forEach(x => x.classList.toggle("on", x === b)); upd();
      });
    } else $("#i-" + e.id).addEventListener("input", upd);
  });
  $("#c-reset").onclick = () => { store.set(key, {}); Rechner(t, el); };
  $("#c-fold").onclick = () => { const d = $("#rw"); d.hidden = !d.hidden; $("#c-fold").textContent = d.hidden ? "Aufklappen" : "Zuklappen"; };
  if ($("#c-pdf")) $("#c-pdf").onclick = () => printRechenweg(t, R, ctxNow, digitsNow);
  tex(el.querySelector(".panel"));

  let ctxNow, digitsNow;
  function upd(){
    R.eingaben.filter(e => e.typ !== "schalter").forEach(e => {
      const v = $("#i-" + e.id).value;
      if (e.typ === "auswahl"){ p[e.id] = v; return; }
      let x = parseFloat(String(v).replace(",", "."));
      if (!Number.isFinite(x)) x = e.default;
      if (e.min !== undefined) x = Math.max(e.min, x);
      if (e.max !== undefined) x = Math.min(e.max, x);
      p[e.id] = x;
    });
    store.set(key, p);
    const ctx = {...MATHCTX, ...p}, digits = {};
    R.eingaben.forEach(e => { digits[e.id] = e.d ?? (Number.isInteger(p[e.id]) ? 0 : 2); });
    const bad = (R.pruefung || []).find(x => evalExpr(x.wenn, ctx));
    if (bad){ $("#res").innerHTML = `<p class="note">${bad.text}</p>`; $("#rw").innerHTML = ""; tex($("#res")); return; }
    compute(R.schritte, ctx, digits);
    ctxNow = ctx; digitsNow = digits;
    $("#res").innerHTML = (R.ergebnisse || []).filter(x => cond(x, ctx)).map(x => {
      const v = evalExpr(x.wert, ctx), eta = x.eta ? evalExpr(x.eta, ctx) : undefined;
      const cls = eta === undefined ? "" : eta <= 1 ? "ok" : "bad";
      const bar = eta === undefined ? "" : `<div class="util"><i style="width:${Math.min(eta, 1) * 100}%;background:var(${eta <= 1 ? "--good" : "--bad"})"></i></div>`;
      return `<div class="res ${cls}"><span class="label">${x.titel}</span><span class="v">${fmtVal(v, x.d ?? 2)}</span><span class="u">${esc(x.einheit || "")}${x.sub ? " · " + fill(x.sub, ctx, digits) : ""}</span>${bar}</div>`;
    }).join("");
    $("#rw").innerHTML = stepDoc(R.schritte, ctx, digits);
    if (R.skizze === "rechteck_hohlkasten") drawSec(ctx);
    tex($("#res")); tex($("#rw"));
  }
  function drawSec(c){
    const W = 360, H = 300, pad = 40, s = Math.min((W - 2*pad) / c.b, (H - 2*pad) / c.h);
    const w = c.b * s, hh = c.h * s, x0 = (W - w) / 2, y0 = (H - hh) / 2, te = c.tef * s, d1 = c.d1 * s;
    const bars = [];
    const nx = Math.max(2, Math.ceil((c.b - 2*c.d1) / 35) + 1), ny = Math.max(2, Math.ceil((c.h - 2*c.d1) / 35) + 1);
    for (let k = 0; k < nx; k++){ const x = x0 + d1 + k * (w - 2*d1) / (nx - 1); bars.push([x, y0 + d1], [x, y0 + hh - d1]); }
    for (let k = 1; k < ny - 1; k++){ const y = y0 + d1 + k * (hh - 2*d1) / (ny - 1); bars.push([x0 + d1, y], [x0 + w - d1, y]); }
    $("#xsec").innerHTML = `
      <rect class="conc" x="${x0}" y="${y0}" width="${w}" height="${hh}"/>
      <path class="wall" fill-rule="evenodd" d="M${x0} ${y0}h${w}v${hh}h${-w}z M${x0+te} ${y0+te}v${hh-2*te}h${w-2*te}v${-(hh-2*te)}z"/>
      <rect class="mid" x="${x0+te/2}" y="${y0+te/2}" width="${w-te}" height="${hh-te}"/>
      ${bars.map(([x,y]) => `<circle class="bar" cx="${x}" cy="${y}" r="3.2"/>`).join("")}
      <text x="${W/2}" y="${y0 - 10}" text-anchor="middle">b = ${fmt(c.b,0)} cm</text>
      <text x="${x0 - 10}" y="${H/2}" text-anchor="middle" transform="rotate(-90 ${x0-10} ${H/2})">h = ${fmt(c.h,0)} cm</text>
      <text x="${W/2}" y="${y0 + hh + 22}" text-anchor="middle">t<tspan font-size="9" dy="3">ef</tspan><tspan dy="-3"> = ${fmt(c.tef,1)} cm · gestrichelt: Mittellinie A</tspan><tspan font-size="9" dy="3">k</tspan></text>`;
  }
  upd();
}

/* Rechenweg drucken bzw. als PDF sichern (Browser-Dialog) */
function printRechenweg(t, R, ctx, digits){
  if (!ctx) return;
  let box = document.getElementById("printarea");
  if (!box){ box = document.createElement("div"); box.id = "printarea"; document.body.appendChild(box); }
  const datum = new Date().toLocaleDateString("de-DE");
  const eing = R.eingaben.map(e => {
    const o = e.optionen?.find(o => o.v === ctx[e.id]);
    return `<tr><td>${e.label}</td><td class="n">${o ? o.t : esc(fmtVal(ctx[e.id], digits[e.id] ?? 2))}</td><td>${esc(e.einheit || "")}</td></tr>`;
  }).join("");
  box.innerHTML = `<div class="pr-head"><span>Betonbau 4 · ${esc(t.titel)}</span><span>Rechenweg · ${datum}</span></div>
    <h1 class="pr-title">${esc(R.titel || "Bemessung")}</h1>
    <table class="pr-in"><thead><tr><th>Eingabe</th><th>Wert</th><th>Einheit</th></tr></thead><tbody>${eing}</tbody></table>
    <div class="rw-doc">${stepDoc(R.schritte, ctx, digits)}</div>
    <p class="pr-foot">Erstellt mit der Betonbau-4-Lernplattform. Ohne Gewähr – vorläufig nach DIN EN 1992-1-1 + NA (DE), Annahmen mit dem Skript abgleichen.</p>`;
  const go = () => { document.body.classList.add("printing"); setTimeout(() => { window.print(); }, 50); };
  window.addEventListener("afterprint", () => document.body.classList.remove("printing"), {once: true});
  if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([box]).then(go).catch(go); else go();
}
