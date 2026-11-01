/* ---------- Bemessungstool: Eingaben, Ergebnisse und vollständiger Rechenweg aus der Inhaltsdatei ---------- */
const IN_FRAME = (() => { try { return window.self !== window.top; } catch(e){ return true; } })();
const QSYMBOL = {
  voll: '<svg class="qsym" viewBox="0 0 40 52" aria-hidden="true"><rect class="conc" x="3" y="3" width="34" height="46" rx="1"/><rect class="core" x="10" y="10" width="20" height="32"/><path class="hatch" d="M10 18l8-8M10 28l18-18M10 38l20-20M16 42l14-14M26 42l4-4"/><path class="wall" fill-rule="evenodd" d="M3 3h34v46H3z M10 10v32h20V10z"/></svg>',
  kasten: '<svg class="qsym" viewBox="0 0 40 52" aria-hidden="true"><rect class="conc" x="3" y="3" width="34" height="46" rx="1"/><rect class="void" x="10" y="10" width="20" height="32"/><path class="wall" fill-rule="evenodd" d="M3 3h34v46H3z M10 10v32h20V10z"/></svg>'
};
function fmtVal(v, d){ return typeof v === "number" ? fmt(v, d) : String(v); }

function Rechner(t, el){
  const R = t.rechner, key = "calc2-" + t.id;
  const p = Object.assign(Object.fromEntries(R.eingaben.map(e => [e.id, e.default])), store.get(key, {}));
  const inp = e => {
    if (e.typ === "auswahl") return `<div class="fld" data-e="${e.id}"><label for="i-${e.id}">${e.label}</label><select id="i-${e.id}">${e.werte.map(w => `<option ${w === p[e.id] ? "selected" : ""}>${esc(w)}</option>`).join("")}</select>${e.hinweis ? `<small>${e.hinweis}</small>` : ""}</div>`;
    if (e.typ === "schalter"){
      const karten = e.optionen.some(o => o.symbol);
      return `<div data-e="${e.id}"><span class="label">${e.label}</span><div class="seg${karten ? " qkarten" : ""}" data-id="${e.id}" role="radiogroup" aria-label="${esc(e.label)}">${e.optionen.map(o =>
        `<button type="button" role="radio" aria-checked="${o.v === p[e.id]}" data-v="${o.v}" class="${o.v === p[e.id] ? "on" : ""}">${o.symbol ? QSYMBOL[o.symbol] || "" : ""}<span class="qt">${o.t}</span>${o.sub ? `<small>${o.sub}</small>` : ""}</button>`).join("")}</div></div>`;
    }
    return `<div class="fld" data-e="${e.id}"><label for="i-${e.id}">${e.label}${e.einheit ? ` [${e.einheit}]` : ""}</label><input id="i-${e.id}" type="number" inputmode="decimal" step="${e.step ?? 1}" ${e.min !== undefined ? `min="${e.min}"` : ""} ${e.max !== undefined ? `max="${e.max}"` : ""} value="${p[e.id]}">${e.hinweis ? `<small>${e.hinweis}</small>` : ""}</div>`;
  };
  el.innerHTML = `${R.hinweis ? `<p class="note">${esc(R.hinweis)} Beispielwerte sind vorbelegt.</p>` : ""}
  ${R.system ? `<section class="sof-box" id="sys"></section>` : ""}
  <div class="calc">
    <div class="panel"><h3>Eingabe</h3>${R.eingaben.map(inp).join("")}
      <button class="btn ghost" id="c-reset" type="button">Beispielwerte laden</button></div>
    <div style="display:grid;gap:16px;min-width:0">
      ${R.skizze ? `<figure class="xfig"><svg class="xsec" id="xsec" viewBox="0 0 420 330" role="img" aria-label="Querschnittsskizze"></svg><figcaption class="xleg" id="xleg"></figcaption></figure>` : ""}
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
        p[e.id] = b.dataset.v; el.querySelectorAll(`.seg[data-id="${e.id}"] button`).forEach(x => { x.classList.toggle("on", x === b); x.setAttribute("aria-checked", x === b); }); upd();
      });
    } else $("#i-" + e.id).addEventListener("input", upd);
  });
  $("#c-reset").onclick = () => { store.set(key, {}); Rechner(t, el); };
  $("#c-fold").onclick = () => { const d = $("#rw"); d.hidden = !d.hidden; $("#c-fold").textContent = d.hidden ? "Aufklappen" : "Zuklappen"; };
  if ($("#c-pdf")) $("#c-pdf").onclick = () => printRechenweg(t, R, ctxNow, digitsNow);
  tex(el.querySelector(".panel"));

  let ctxNow, digitsNow;
  const SYS = R.system ? SystemPanel($("#sys"), t.id, () => upd()) : null;
  function upd(){
    const sv = SYS && SYS.werte();
    ["T", "V"].forEach(id => {
      const i = $("#i-" + id); if (!i) return;
      i.readOnly = !!sv; i.classList.toggle("aus-system", !!sv);
      if (sv) i.value = +sv[id].toFixed(1);
      const w = i.closest(".fld"); let h = w.querySelector(".sys-hw");
      if (sv){ if (!h){ h = document.createElement("small"); h.className = "sys-hw"; w.appendChild(h); } h.textContent = `aus dem statischen System bei x = ${fmt(sv.x, 2)} m`; }
      else if (h) h.remove();
    });
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
    R.eingaben.filter(e => e.wenn).forEach(e => { const w = el.querySelector(`[data-e="${e.id}"]`); if (w) w.hidden = !evalExpr(e.wenn, ctx); });
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
    $("#rw").innerHTML = stepDoc(R.schritte, ctx, digits, 1, st => fundstelle(t, st));
    if (R.skizze === "rechteck_hohlkasten") drawSec(ctx);
    tex($("#res")); tex($("#rw"));
  }
  function drawSec(c){
    /* Maßstäbliche Skizze: Vollquerschnitt mit unwirksamem Kern bzw. echter Hohlkasten mit Hohlraum und zweilagiger Bewehrung */
    const kasten = c.quer === "kasten";
    const W = 420, H = 330, padL = 64, padR = 96, padT = 40, padB = 34;
    const s = Math.min((W - padL - padR) / c.b, (H - padT - padB) / c.h);
    const w = c.b * s, hh = c.h * s, x0 = padL + (W - padL - padR - w) / 2, y0 = padT + (H - padT - padB - hh) / 2;
    const te = c.tef * s, a = c.d1 * s, tw = kasten ? c.tw * s : 0;
    const r = Math.max(2.6, Math.min(4.2, s * 0.9));                       /* Stabradius in der Skizze */
    const rect = (x, y, b_, h_, cls, rx = 0) => `<rect class="${cls}" x="${x}" y="${y}" width="${Math.max(b_, 0)}" height="${Math.max(h_, 0)}" rx="${rx}"/>`;
    const lage = (o) => {                                                  /* Stäbe auf einer Bügellage im Abstand o vom Rand */
      const bw = w - 2*o, bh = hh - 2*o, out = [];
      if (bw <= 0 || bh <= 0) return out;
      const nx = Math.max(2, Math.ceil(bw / s / 35) + 1), ny = Math.max(2, Math.ceil(bh / s / 35) + 1);
      for (let k = 0; k < nx; k++){ const x = x0 + o + k * bw / (nx - 1); out.push([x, y0 + o], [x, y0 + hh - o]); }
      for (let k = 1; k < ny - 1; k++){ const y = y0 + o + k * bh / (ny - 1); out.push([x0 + o, y], [x0 + w - o, y]); }
      return out;
    };
    const buegel = (o) => rect(x0 + o - r - 1.5, y0 + o - r - 1.5, w - 2*o + 2*r + 3, hh - 2*o + 2*r + 3, "stir", r + 2);
    const buegelInnen = (o) => rect(x0 + o + r + 1.5, y0 + o + r + 1.5, w - 2*o - 2*r - 3, hh - 2*o - 2*r - 3, "stir", r + 2);
    let stabe = lage(a), innen = "";
    if (kasten){
      const oi = tw - Math.min(a, tw * 0.4);                               /* innere Lage nahe der Wandinnenseite */
      if (oi > a + 2*r) { stabe = stabe.concat(lage(oi)); innen = buegelInnen(oi); }
    }
    const pfeil = (x1, y1, x2, y2) => `<line class="dim" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" marker-start="url(#pf)" marker-end="url(#pf)"/>`;
    const sub = (t_, i_) => `${t_}<tspan class="ix" dy="3">${i_}</tspan><tspan dy="-3">`;
    const xr = x0 + w + 14;
    $("#xsec").innerHTML = `
      <defs>
        <pattern id="kern" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" class="hatch"/></pattern>
        <marker id="pf" viewBox="0 0 8 8" refX="4" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L7 4 L0 7" class="arrow"/></marker>
      </defs>
      ${rect(x0, y0, w, hh, "conc")}
      ${kasten ? rect(x0 + tw, y0 + tw, w - 2*tw, hh - 2*tw, "void") : rect(x0 + te, y0 + te, w - 2*te, hh - 2*te, "core")}
      <path class="wall" fill-rule="evenodd" d="M${x0} ${y0}h${w}v${hh}h${-w}z M${x0+te} ${y0+te}v${hh-2*te}h${w-2*te}v${-(hh-2*te)}z"/>
      ${rect(x0 + te/2, y0 + te/2, w - te, hh - te, "mid")}
      ${buegel(a)}${innen}
      ${stabe.map(([x, y]) => `<circle class="bar" cx="${x}" cy="${y}" r="${r}"/>`).join("")}
      ${kasten ? `<text class="lbl" x="${x0 + w/2}" y="${y0 + hh/2 + 4}" text-anchor="middle">Hohlraum</text>`
               : (w - 2*te > 108 && hh - 2*te > 30 ? `<text class="lbl" x="${x0 + w/2}" y="${y0 + hh/2 + 4}" text-anchor="middle">unwirksamer Kern</text>`
                 : (w - 2*te > 50 && hh - 2*te > 50 ? `<text class="lbl" x="${x0 + w/2}" y="${y0 + hh/2 + 4}" text-anchor="middle">Kern</text>` : ""))}
      ${pfeil(x0, y0 - 16, x0 + w, y0 - 16)}<text x="${x0 + w/2}" y="${y0 - 22}" text-anchor="middle">b = ${fmt(c.b, 0)} cm</text>
      ${pfeil(x0 - 18, y0, x0 - 18, y0 + hh)}<text x="${x0 - 24}" y="${y0 + hh/2}" text-anchor="middle" transform="rotate(-90 ${x0 - 24} ${y0 + hh/2})">h = ${fmt(c.h, 0)} cm</text>
      ${pfeil(xr, y0, xr, y0 + te)}<text x="${xr + 7}" y="${y0 + te/2 + 4}">${sub("t", "ef")} = ${fmt(c.tef, 1)} cm</tspan></text>
      ${kasten ? `${pfeil(xr, y0 + hh - tw, xr, y0 + hh)}<text x="${xr + 7}" y="${y0 + hh - tw/2 + 4}">t = ${fmt(c.tw, 0)} cm</text>` : ""}`;
    const sw = (cls, txt) => `<span><svg viewBox="0 0 22 12" aria-hidden="true"><rect class="${cls}" x="1" y="1" width="20" height="10"/></svg>${txt}</span>`;
    $("#xleg").innerHTML = [
      sw("wall", "wirksame Wand"),
      `<span><svg viewBox="0 0 22 12" aria-hidden="true"><line class="mid" x1="1" y1="6" x2="21" y2="6"/></svg>Mittellinie ($A_\\mathrm{k}$, $u_\\mathrm{k}$)</span>`,
      kasten ? sw("void", "Hohlraum") : sw("core", "unwirksamer Kern"),
      `<span><svg viewBox="0 0 22 12" aria-hidden="true"><circle class="bar" cx="11" cy="6" r="4"/></svg>${kasten ? "Längsstäbe innen und außen" : "Längsstäbe"}</span>`
    ].join("");
    tex($("#xleg"));
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
    <div class="rw-doc">${stepDoc(R.schritte, ctx, digits, 1, st => fundstelle(t, st))}</div>
    <p class="pr-foot">Erstellt mit der Betonbau-4-Lernplattform. Ohne Gewähr. ${esc(R.hinweis || "")}</p>`;
  const go = () => { document.body.classList.add("printing"); setTimeout(() => { window.print(); }, 50); };
  window.addEventListener("afterprint", () => document.body.classList.remove("printing"), {once: true});
  if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([box]).then(go).catch(go); else go();
}
