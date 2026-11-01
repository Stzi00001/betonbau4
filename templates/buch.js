/* ---------- Buchbeispiele: Rechenwege aus dem Lehrbuch mit veränderbaren Ausgangswerten (±10 %) ---------- */
const BUCHFN = {
  /* Bemessungstafel Rechteck ohne Druckbewehrung: Parabel-Rechteck-Diagramm, B500 mit ansteigendem Ast
     (f_td = 1,05·f_yd bei ε_ud = 25 ‰). Liefert ω, σ_sd [N/mm²] und ξ für ein bezogenes Moment μ. */
  omegaTafel(mu){
    const eyd = 2.175, eud = 25, fyd = 435, ftd = 1.05 * 435;
    const sig = es => es <= eyd ? 200 * es : fyd + (es - eyd) / (eud - eyd) * (ftd - fyd);
    const block = ec => ec <= 2 ? {aR: ec / 12 * (6 - ec), ka: (8 - ec) / (4 * (6 - ec))}
                               : {aR: (3 * ec - 2) / (3 * ec), ka: (ec * (3 * ec - 4) + 2) / (2 * ec * (3 * ec - 2))};
    const zustand = xi => { let ec = 3.5, es = 3.5 * (1 - xi) / xi; if (es > eud){ es = eud; ec = eud * xi / (1 - xi); } return {ec, es, ...block(ec)}; };
    const muVon = xi => { const z = zustand(xi); return z.aR * xi * (1 - z.ka * xi); };
    let lo = 1e-4, hi = 0.6169;                        /* ξ bis ε_s = ε_yd */
    if (mu > muVon(hi)) return {w: NaN, s: NaN, xi: NaN};
    for (let i = 0; i < 80; i++){ const m = (lo + hi) / 2; if (muVon(m) < mu) lo = m; else hi = m; }
    const xi = (lo + hi) / 2, z = zustand(xi);
    return {w: z.aR * xi, s: sig(z.es), xi};
  },
  stabA: (n, phi) => n * Math.PI * phi * phi / 400,                       /* cm² */
  stabTxt: (n, phi) => `${n}\\varnothing ${phi}`,
  /* untere Lage: kleinste Kombination aus 2–6 Ø28 und 0–2 Ø16…Ø28, die reicht */
  wahlUnten(req){
    const opt = [];
    for (const n28 of [2, 3, 4, 5, 6]) for (const [n2, p2] of [[0, 0], [2, 16], [2, 20], [2, 25]]) {
      const A = BUCHFN.stabA(n28, 28) + (n2 ? BUCHFN.stabA(n2, p2) : 0);
      opt.push({A, txt: BUCHFN.stabTxt(n28, 28) + (n2 ? " + " + BUCHFN.stabTxt(n2, p2) : "")});
    }
    opt.sort((a, b) => a.A - b.A);
    return opt.find(o => o.A >= req - 1e-9) || opt[opt.length - 1];
  },
  /* zweischnittige Bügel: kleinster Durchmesser mit Abstand ≥ 10 cm, Abstand im Raster abgerundet und ≤ sMax */
  buegelWahl(erf, phis, sMax, raster){
    for (const phi of phis){
      const s = Math.min(raster * Math.floor(2 * BUCHFN.stabA(1, phi) / erf * 100 / raster + 1e-9), sMax);
      if (s >= 10 || phi === phis[phis.length - 1]){
        const sf = Math.max(s, raster);
        return {phi, s: sf, a: 2 * BUCHFN.stabA(1, phi) / (sf / 100), txt: `\\varnothing ${phi}/${sf}`, dcm: (phi / 10).toFixed(1).replace(".", "{,}")};
      }
    }
  },
  /* steilerer Druckstrebenwinkel in Stufen von 0,2 (wie im Buch), bis die lineare Interaktion erfüllt ist */
  cotStufe(summe, nfcd){
    for (const c of [1.8, 1.6, 1.4, 1.2, 1.0]) if (summe / (nfcd / (c + 1 / c)) <= 1) return c;
    return 1.0;
  }
};

function Buch(t, el){
  const BB = t.buchbeispiele;
  let wahl = null;                                   /* zuerst Auswahl einfach / komplex */
  waehlen();

  function waehlen(){
    el.innerHTML = `<p class="note">Rechenbeispiele aus ${esc(BB.quelle)} (${esc(BB.auflage)}). Die Ausgangswerte lassen sich um ±10 % verändern; System, Rechenweg und Ergebnisse rechnen mit.</p>
    <div class="bb-wahl">${BB.beispiele.map((b, k) => `
      <button class="bb-karte" type="button" data-k="${k}">
        <svg viewBox="0 0 120 80" aria-hidden="true">${b.system === "kern" ? ICON_KERN : ICON_TRAEGER}</svg>
        <span class="label">${esc(b.abschnitt)}</span>
        <h3>${esc(b.titel)}</h3>
        <p>${esc(b.untertitel)} · ${b.schritte.length} Schritte</p>
      </button>`).join("")}</div>`;
    el.querySelectorAll(".bb-karte").forEach(x => x.onclick = () => { wahl = +x.dataset.k; zeigen(); window.scrollTo(0, 0); });
  }

  function zeigen(){
    const B = BB.beispiele[wahl], key = "buch-" + t.id + "-" + B.id;
    const p = Object.fromEntries(B.eingaben.map(e => [e.id, e.wert]));
    const gespeichert = store.get(key, {});
    B.eingaben.forEach(e => { const v = gespeichert[e.id]; if (Number.isFinite(v) && v >= grenze(e, -1) && v <= grenze(e, 1)) p[e.id] = v; });
    let modus = store.get("buch-modus", "alle"), k = 1;

    el.innerHTML = `
    <div class="bb-top"><button class="back" id="bb-zur" type="button">← Beispiel wählen</button>
      <div class="seg" id="bb-sel">${BB.beispiele.map((b, i) => `<button type="button" data-k="${i}" class="${i === wahl ? "on" : ""}">${esc(b.titel)}</button>`).join("")}</div></div>
    <div class="bb-head"><span class="label">${esc(BB.quelle)} · ${esc(B.abschnitt)}</span><h3>${esc(B.untertitel)}</h3><p>${B.aufgabe}</p></div>
    <div class="bb-grid">
      <figure class="bb-sys"><svg id="bb-svg" viewBox="0 0 720 350" role="img" aria-label="Statisches System mit Lasten und Querschnitt"></svg>
        <figcaption class="bb-fest">${B.fest.map(([a, b]) => `<span><b>${esc(a)}</b> ${esc(b)}</span>`).join("")}</figcaption></figure>
      <div class="panel bb-in"><h3>Ausgangswerte</h3><p class="bb-hint">Spielraum ±10 % um die Buchwerte</p>
        ${B.eingaben.map(e => `<div class="bb-sl" data-e="${e.id}">
          <label for="bb-${e.id}">${e.label}</label><output id="bb-o-${e.id}"></output>
          <input type="range" id="bb-${e.id}" min="${grenze(e, -1)}" max="${grenze(e, 1)}" step="${e.step}" value="${p[e.id]}">
          <div class="bb-rg"><span>${fmt(grenze(e, -1), e.d)}</span><span class="bb-dev" id="bb-d-${e.id}"></span><span>${fmt(grenze(e, 1), e.d)}</span></div></div>`).join("")}
        <button class="btn ghost" id="bb-reset" type="button">Buchwerte laden</button></div>
    </div>
    <div class="results" id="bb-res" style="margin-top:16px"></div>
    <section class="rw">
      <div class="rw-head"><h3>Bemessung Schritt für Schritt</h3>
        <div class="seg bb-modus" id="bb-modus"><button type="button" data-m="einzeln">Einzeln aufdecken</button><button type="button" data-m="alle">Alle Schritte</button></div></div>
      <div class="rw-doc" id="bb-rw"></div>
      <div class="row bb-nav" id="bb-nav"><button class="btn" id="bb-next" type="button">Nächster Schritt</button><button class="btn ghost" id="bb-allk" type="button">Alle zeigen</button><span class="label" id="bb-cnt"></span></div>
    </section>`;

    $("#bb-zur").onclick = () => { waehlen(); window.scrollTo(0, 0); };
    el.querySelectorAll("#bb-sel button").forEach(b => b.onclick = () => { wahl = +b.dataset.k; zeigen(); });
    $("#bb-reset").onclick = () => { store.set(key, {}); B.eingaben.forEach(e => { p[e.id] = e.wert; $("#bb-" + e.id).value = e.wert; }); sofort(); rechnen(); };
    el.querySelectorAll("#bb-modus button").forEach(b => b.onclick = () => { modus = b.dataset.m; store.set("buch-modus", modus); k = 1; sichtbar(); });
    $("#bb-next").onclick = () => { k++; sichtbar(); const s = el.querySelectorAll(".bb-step")[k - 1]; if (s) s.scrollIntoView({behavior: "smooth", block: "center"}); };
    $("#bb-allk").onclick = () => { modus = "alle"; store.set("buch-modus", modus); sichtbar(); };
    let timer;
    B.eingaben.forEach(e => $("#bb-" + e.id).addEventListener("input", ev => {
      p[e.id] = +ev.target.value; store.set(key, p); sofort();
      clearTimeout(timer); timer = setTimeout(rechnen, 180);
    }));
    tex(el.querySelector(".bb-head")); tex(el.querySelector(".bb-in"));
    sofort(); rechnen();

    function ctxNeu(){
      const ctx = {...MATHCTX, ...BUCHFN, ...B.konstanten, ...p}, digits = {};
      B.eingaben.forEach(e => digits[e.id] = e.d);
      compute(B.schritte, ctx, digits);
      return {ctx, digits};
    }
    /* Anzeige der Regler und Skizze sofort, Rechenweg kurz verzögert (MathJax) */
    function sofort(){
      B.eingaben.forEach(e => {
        const dv = (p[e.id] / e.wert - 1) * 100, geaendert = Math.abs(dv) > 0.05;
        $("#bb-o-" + e.id).textContent = `${fmt(p[e.id], e.d)} ${e.einheit}`;
        $("#bb-d-" + e.id).textContent = geaendert ? `${dv > 0 ? "+" : "−"}${fmt(Math.abs(dv), 1)} %` : "Buchwert";
        el.querySelector(`.bb-sl[data-e="${e.id}"]`).classList.toggle("chg", geaendert);
      });
      const {ctx} = ctxNeu();
      $("#bb-svg").innerHTML = (B.system === "kern" ? svgKern : svgTraeger)(ctx, id => Math.abs(p[id] / B.eingaben.find(e => e.id === id).wert - 1) > 0.0005);
    }
    function rechnen(){
      const {ctx, digits} = ctxNeu();
      $("#bb-res").innerHTML = (B.ergebnisse || []).map(x => {
        const v = evalExpr(x.wert, ctx), eta = x.eta ? evalExpr(x.eta, ctx) : undefined;
        const cls = eta === undefined ? "" : eta <= 1 ? "ok" : "bad";
        const bar = eta === undefined ? "" : `<div class="util"><i style="width:${Math.min(eta, 1) * 100}%;background:var(${eta <= 1 ? "--good" : "--bad"})"></i></div>`;
        return `<div class="res ${cls}"><span class="label">${x.titel}</span><span class="v">${fmtVal(v, x.d ?? 2)}</span><span class="u">${esc(x.einheit || "")}${x.sub ? " · " + fill(x.sub, ctx, digits) : ""}</span>${bar}</div>`;
      }).join("");
      let n = 0, ab = "";
      $("#bb-rw").innerHTML = B.schritte.filter(st => cond(st, ctx)).map(st => {
        n++;
        const f = lines(st.formel, ctx), e = lines(st.einsetzen, ctx);
        const kopf = st.abschnitt !== ab ? `<h4 class="bb-ab" data-ab="${esc(st.abschnitt)}">${esc(st.abschnitt)}</h4>` : "";
        ab = st.abschnitt;
        return kopf + `<section class="rw-step bb-step" data-ab="${esc(st.abschnitt)}"><h4><span class="rw-n">${n}</span><span>${esc(st.titel)}</span><span class="rw-q">Buch S. ${st.seite}</span></h4>
          ${st.text ? `<p>${fill(st.text, ctx, digits)}</p>` : ""}
          ${f.length ? `<div class="rw-f">${f.map(x => `<div>$\\displaystyle ${fill(x, ctx, digits)}$</div>`).join("")}</div>` : ""}
          ${e.length ? `<div class="rw-e">${e.map(x => `<div>$\\displaystyle ${fill(x, ctx, digits)}$</div>`).join("")}</div>` : ""}
          ${st.notiz ? `<p class="bb-notiz"><b>Hinweis zum Buch:</b> ${esc(st.notiz)}</p>` : ""}
        </section>`;
      }).join("");
      sichtbar();
      tex($("#bb-res")); tex($("#bb-rw"));
    }
    function sichtbar(){
      const steps = [...el.querySelectorAll(".bb-step")], N = steps.length;
      if (k > N) k = N;
      const alle = modus === "alle" || k >= N;
      steps.forEach((s, i) => s.hidden = !alle && i >= k);
      el.querySelectorAll(".bb-ab").forEach(h => h.hidden = !steps.some(s => !s.hidden && s.dataset.ab === h.dataset.ab));
      el.querySelectorAll("#bb-modus button").forEach(b => b.classList.toggle("on", b.dataset.m === modus));
      $("#bb-nav").hidden = modus === "alle";
      $("#bb-next").disabled = k >= N;
      $("#bb-cnt").textContent = `Schritt ${Math.min(k, N)} von ${N}`;
    }
  }
}
function grenze(e, s){ const v = e.wert * (1 + s * 0.1); return +(Math.round(v / e.step) * e.step).toFixed(6); }

/* ---------- Skizzen ---------- */
const ICON_TRAEGER = '<path d="M10 52h100" stroke-width="4"/><path d="M14 52l-6 10h12zM106 52l-6 10h12z"/><path d="M60 14v32M55 38l5 9 5-9"/><path d="M14 30h92M24 30v18M44 30v18M76 30v18M96 30v18"/>';
const ICON_KERN = '<path d="M30 74h40M50 74V10" stroke-width="4"/><path d="M14 22h30M38 18l6 4-6 4M14 46h30M38 42l6 4-6 4"/><rect x="78" y="22" width="34" height="34"/><rect x="85" y="29" width="20" height="20"/>';

function bbTxt(x, y, haupt, index, wert, cls = "", anchor = "start"){
  return `<text x="${x}" y="${y}" text-anchor="${anchor}" class="${cls}">${haupt}${index ? `<tspan class="ix" dy="4">${index}</tspan><tspan dy="-4"> </tspan>` : " "}${wert}</text>`;
}
function bbPfeil(x1, y1, x2, y2, cls = "ld"){ return `<line class="${cls}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" marker-end="url(#bb-pf)"/>`; }
function bbMass(x1, y1, x2, y2, text, quer = false){
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
  const tx = quer ? `<text x="${mx - 8}" y="${my}" text-anchor="middle" transform="rotate(-90 ${mx - 8} ${my})">${text}</text>`
                  : `<text x="${mx}" y="${my - 6}" text-anchor="middle">${text}</text>`;
  return `<line class="dim" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" marker-start="url(#bb-ms)" marker-end="url(#bb-ms)"/>${tx}`;
}
const BB_DEFS = `<defs>
  <marker id="bb-pf" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="ah"/></marker>
  <marker id="bb-pk" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="ahk"/></marker>
  <marker id="bb-ms" viewBox="0 0 8 8" refX="4" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1L7 4L0 7" class="dh"/></marker>
  <pattern id="bb-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" class="hl"/></pattern></defs>`;

function svgTraeger(c, chg){
  const k = id => chg(id) ? " chg" : "";
  const x0 = 40, x1 = 420, yb = 200, L = x1 - x0;
  let s = BB_DEFS + `<text x="${x0}" y="24" class="ttl">Statisches System</text>`;
  /* Streckenlast */
  s += `<line class="ld" x1="${x0}" y1="140" x2="${x1}" y2="140"/>`;
  for (let i = 0; i <= 12; i++){ const x = x0 + i * L / 12; s += bbPfeil(x, 140, x, yb - 6); }
  s += bbTxt(x0, 132, "p", "Ed", `= ${fmt(c.p, 1)} kN/m`, "lt" + k("p"));
  /* Einzellast in Feldmitte */
  const xm = (x0 + x1) / 2;
  s += bbPfeil(xm, 48, xm, yb - 4, "ld big") + bbTxt(xm + 8, 62, "F", "Ed", `= ${fmt(c.F, 0)} kN`, "lt" + k("F"));
  /* Träger, Lager */
  s += `<line class="bb-beam" x1="${x0}" y1="${yb}" x2="${x1}" y2="${yb}"/>
    <path class="bb-sup" d="M${x0} ${yb}l-11 18h22z"/><line class="bb-gnd" x1="${x0 - 16}" y1="${yb + 18}" x2="${x0 + 16}" y2="${yb + 18}"/>
    <path class="bb-sup" d="M${x1} ${yb}l-11 18h22z"/><line class="bb-gnd" x1="${x1 - 16}" y1="${yb + 24}" x2="${x1 + 16}" y2="${yb + 24}"/>`;
  /* Torsion in Feldmitte */
  const xt = xm + 46;
  s += `<path class="bb-tor" d="M${xt - 2} ${yb - 19} A 8 19 0 1 1 ${xt - 2} ${yb + 19}" marker-end="url(#bb-pk)"/>` + bbTxt(xt + 14, yb + 34, "T", "Ed", `= ${fmt(c.T, 1)} kNm`, "res-t");
  /* Maße */
  s += bbMass(x0, yb + 70, xm, yb + 70, `${fmt(c.l / 2, 2)} m`) + bbMass(xm, yb + 70, x1, yb + 70, `${fmt(c.l / 2, 2)} m`);
  s += `<text x="${(x0 + x1) / 2}" y="${yb + 100}" text-anchor="middle" class="${k("l").trim()}">l = ${fmt(c.l, 2)} m</text>`;
  /* Querschnitt mit Konsole, maßstäblich */
  const sc = 190 / 0.88, qx = 500, qy = 80, w = c.b * sc, hh = c.h * sc, kw = 0.30 * sc, kh = 0.35 * sc;
  s += `<text x="${qx}" y="24" class="ttl">Querschnitt mit Konsole</text>
    <path class="conc" d="M${qx} ${qy}h${w}v${hh - kh}h${kw}v${kh}h${-w - kw}z"/>
    <rect class="hatchf" x="${qx}" y="${qy}" width="${w + kw}" height="${hh}" clip-path="url(#bb-clip)"/>
    <clipPath id="bb-clip"><path d="M${qx} ${qy}h${w}v${hh - kh}h${kw}v${kh}h${-w - kw}z"/></clipPath>
    <line class="axis" x1="${qx + w / 2}" y1="${qy - 14}" x2="${qx + w / 2}" y2="${qy + hh + 10}"/>`;
  const xf = qx + w / 2 + c.e * sc;
  s += bbPfeil(xf, qy + hh - kh - 70, xf, qy + hh - kh - 2, "ld big") + bbTxt(xf + 6, qy + hh - kh - 54, "F", "Ed", "", "lt" + k("F"));
  s += bbMass(qx + w / 2, qy + hh + 22, xf, qy + hh + 22, `e = ${fmt(c.e, 3)} m`).replace("<text", `<text class="${k("e").trim()}"`);
  s += `<line class="dim" x1="${xf}" y1="${qy + hh - kh}" x2="${xf}" y2="${qy + hh + 28}" stroke-dasharray="3 3"/>`;
  s += bbMass(qx, qy + hh + 56, qx + w, qy + hh + 56, `b = ${fmt(c.b, 2)} m`).replace("<text", `<text class="${k("b").trim()}"`);
  s += bbMass(qx - 14, qy, qx - 14, qy + hh, `h = ${fmt(c.h, 2)} m`, true).replace("<text", `<text class="${k("h").trim()}"`);
  return s;
}

function svgKern(c, chg){
  const k = id => chg(id) ? " chg" : "";
  const xs = 180, yg = 340, hp = 52 * c.hs / 2.5;
  let s = BB_DEFS + `<text x="30" y="24" class="ttl">Statisches System</text>`;
  s += `<line class="bb-beam" x1="${xs}" y1="${yg}" x2="${xs}" y2="${yg - 5 * hp}"/>
    <rect x="${xs - 40}" y="${yg}" width="80" height="12" fill="url(#bb-hatch)"/><line class="bb-gnd" x1="${xs - 40}" y1="${yg}" x2="${xs + 40}" y2="${yg}"/>`;
  for (let i = 1; i <= 5; i++){
    const y = yg - i * hp;
    s += `<line class="bb-flr" x1="${xs - 26}" y1="${y}" x2="${xs + 26}" y2="${y}"/>`;
    s += bbPfeil(xs - 66, y, xs - 6, y, "ld");
    s += bbPfeil(xs + 36, y - 30, xs + 36, y - 3, "ld");
    s += `<line class="bb-flr" x1="${xs}" y1="${y}" x2="${xs + 40}" y2="${y}"/>`;
    s += `<path class="bb-tor" d="M${xs - 17} ${y - 2} A 17 7 0 1 0 ${xs + 15} ${y - 5}" marker-end="url(#bb-pk)"/>`;
    if (i === 5){
      s += bbTxt(xs - 70, y - 8, "H", "Ed", "", "lt" + k("H")) + bbTxt(xs + 42, y - 18, "F", "Ed", "", "lt" + k("F")) + bbTxt(xs + 22, y + 26, "T", "Ed", "", "lt" + k("Tg"));
    }
    s += `<line class="dim" x1="${xs - 96}" y1="${y + hp}" x2="${xs - 96}" y2="${y}" marker-start="url(#bb-ms)" marker-end="url(#bb-ms)"/><line class="dim" x1="${xs - 102}" y1="${y}" x2="${xs - 90}" y2="${y}"/>`;
    s += `<text x="${xs - 104}" y="${y + hp / 2 + 4}" text-anchor="end" class="${k("hs").trim()}">${fmt(c.hs, 2)} m</text>`;
  }
  s += `<g class="bb-leg"><text x="300" y="70" class="ttl2">je Geschoss</text>
    ${bbTxt(300, 94, "F", "Ed", `= ${fmt(c.F, 0)} kN`, k("F").trim())}
    ${bbTxt(300, 116, "H", "Ed", `= ${fmt(c.H, 0)} kN`, k("H").trim())}
    ${bbTxt(300, 138, "T", "Ed", `= ${fmt(c.Tg, 0)} kNm`, k("Tg").trim())}
    <text x="300" y="172" class="ttl2">an der Einspannung</text>
    ${bbTxt(300, 196, "M", "Ed", `= ${fmt(c.M, 0)} kNm`, "res-t")}
    ${bbTxt(300, 218, "T", "Ed", `= ${fmt(c.T, 0)} kNm`, "res-t")}
    ${bbTxt(300, 240, "V", "Ed", `= ${fmt(c.V, 0)} kN`, "res-t")}
    ${bbTxt(300, 262, "N", "Ed", `= ${fmt(c.N, 0)} kN`, "res-t")}</g>`;
  /* Kastenquerschnitt, maßstäblich */
  const sc = 180 / 2.2, qx = 490, qy = 74, A = c.a * sc, tw = c.t * sc;
  s += `<text x="${qx}" y="24" class="ttl">Querschnitt Kern</text>
    <path class="conc" fill-rule="evenodd" d="M${qx} ${qy}h${A}v${A}h${-A}z M${qx + tw} ${qy + tw}v${A - 2 * tw}h${A - 2 * tw}v${-(A - 2 * tw)}z"/>
    <path class="hatchf" fill-rule="evenodd" d="M${qx} ${qy}h${A}v${A}h${-A}z M${qx + tw} ${qy + tw}v${A - 2 * tw}h${A - 2 * tw}v${-(A - 2 * tw)}z"/>
    <rect class="mid" x="${qx + tw / 2}" y="${qy + tw / 2}" width="${A - tw}" height="${A - tw}"/>`;
  s += bbMass(qx, qy + A + 22, qx + A, qy + A + 22, `b = ${fmt(c.a, 2)} m`).replace("<text", `<text class="${k("a").trim()}"`);
  s += `<line class="dim" x1="${qx}" y1="${qy - 12}" x2="${qx + tw}" y2="${qy - 12}"/><line class="dim" x1="${qx}" y1="${qy - 17}" x2="${qx}" y2="${qy - 7}"/><line class="dim" x1="${qx + tw}" y1="${qy - 17}" x2="${qx + tw}" y2="${qy - 7}"/>`
     + `<text x="${qx + tw + 6}" y="${qy - 8}" class="${k("t").trim()}">t = ${fmt(c.t, 3)} m</text>`;
  s += `<text x="${qx + A / 2}" y="${qy + A / 2 + 4}" text-anchor="middle" class="lbl">Hohlraum</text>`;
  return s;
}
