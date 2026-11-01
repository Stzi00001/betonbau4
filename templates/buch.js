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
  fctmVon: fck => ({20: 2.2, 25: 2.6, 30: 2.9, 35: 3.2, 40: 3.5, 45: 3.8, 50: 4.1})[fck] ?? 0.3 * Math.pow(fck, 2 / 3),
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
    B.eingaben.forEach(e => { const v = gespeichert[e.id];
      if (e.typ === "auswahl" ? e.werte.includes(v) : Number.isFinite(v) && v >= grenze(e, -1) && v <= grenze(e, 1)) p[e.id] = v; });
    const NUM = B.eingaben.filter(e => e.typ !== "auswahl"), SEL = B.eingaben.filter(e => e.typ === "auswahl");
    let modus = store.get("buch-modus", "alle"), k = 1, stufe = 0;   /* stufe des aktuellen Schritts: 0 Aufgabe, 1 Tipp, 2 Lösung */

    el.innerHTML = `
    <div class="bb-top"><button class="back" id="bb-zur" type="button">← Beispiel wählen</button>
      <div class="seg" id="bb-sel">${BB.beispiele.map((b, i) => `<button type="button" data-k="${i}" class="${i === wahl ? "on" : ""}">${esc(b.titel)}</button>`).join("")}</div></div>
    <div class="bb-head"><span class="label">${esc(BB.quelle)} · ${esc(B.abschnitt)}</span><h3>${esc(B.untertitel)}</h3><p>${B.aufgabe}</p></div>
    <div class="bb-grid">
      <figure class="bb-sys"><svg id="bb-svg" viewBox="0 0 720 360" role="img" aria-label="Statisches System mit Lasten und Querschnitt"></svg>
        <figcaption class="bb-fest" id="bb-fest"></figcaption></figure>
      <div class="panel bb-in"><h3>Ausgangswerte</h3><p class="bb-hint">Spielraum ±10 % um die Buchwerte</p>
        ${SEL.map(e => `<div class="bb-sl bb-sel" data-e="${e.id}"><label for="bb-${e.id}">${e.label}</label>
          <select id="bb-${e.id}">${e.werte.map(w => `<option ${w === p[e.id] ? "selected" : ""}>${esc(w)}</option>`).join("")}</select>
          <div class="bb-rg"><span>Buch: ${esc(e.wert)}</span><span class="bb-dev" id="bb-d-${e.id}"></span></div></div>`).join("")}
        ${NUM.map(e => `<div class="bb-sl" data-e="${e.id}">
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
      <div class="row bb-nav" id="bb-nav"><button class="btn" id="bb-next" type="button">Tipp anzeigen</button><button class="btn ghost" id="bb-loes" type="button">Lösung zeigen</button><button class="btn ghost" id="bb-allk" type="button">Alle Schritte zeigen</button><span class="label" id="bb-cnt"></span></div>
    </section>`;

    $("#bb-zur").onclick = () => { waehlen(); window.scrollTo(0, 0); };
    el.querySelectorAll("#bb-sel button").forEach(b => b.onclick = () => { wahl = +b.dataset.k; zeigen(); });
    $("#bb-reset").onclick = () => { store.set(key, {}); B.eingaben.forEach(e => { p[e.id] = e.wert; $("#bb-" + e.id).value = e.wert; }); sofort(); rechnen(); };
    el.querySelectorAll("#bb-modus button").forEach(b => b.onclick = () => { modus = b.dataset.m; store.set("buch-modus", modus); k = 1; stufe = 0; sichtbar(); });
    const weiter = () => {
      const N = el.querySelectorAll(".bb-step").length;
      if (stufe < 2) stufe++; else if (k < N){ k++; stufe = 0; }
      if (stufe === 1 && !el.querySelectorAll(".bb-step")[k - 1]?.querySelector(".bb-tipp")?.textContent.trim()) stufe = 2;
      sichtbar();
      const s = el.querySelectorAll(".bb-step")[k - 1];
      if (s) (stufe === 0 ? s : s.querySelector(stufe === 1 ? ".bb-tipp" : ".bb-loes") || s).scrollIntoView({behavior: "smooth", block: "nearest"});
    };
    $("#bb-next").onclick = weiter;
    $("#bb-loes").onclick = () => { stufe = 2; sichtbar(); };
    $("#bb-allk").onclick = () => { modus = "alle"; store.set("buch-modus", modus); sichtbar(); };
    let timer;
    B.eingaben.forEach(e => $("#bb-" + e.id).addEventListener(e.typ === "auswahl" ? "change" : "input", ev => {
      p[e.id] = e.typ === "auswahl" ? ev.target.value : +ev.target.value; store.set(key, p); sofort();
      clearTimeout(timer); timer = setTimeout(rechnen, 180);
    }));
    tex(el.querySelector(".bb-head")); tex(el.querySelector(".bb-in"));
    sofort(); rechnen();

    function ctxNeu(){
      const ctx = {...MATHCTX, ...BUCHFN, ...B.konstanten, ...p}, digits = {};
      B.eingaben.forEach(e => digits[e.id] = e.d ?? 0);
      compute(B.schritte, ctx, digits);
      return {ctx, digits};
    }
    /* Anzeige der Regler und Skizze sofort, Rechenweg kurz verzögert (MathJax) */
    function sofort(){
      SEL.forEach(e => {
        const geaendert = p[e.id] !== e.wert;
        $("#bb-d-" + e.id).textContent = geaendert ? "geändert" : "Buchwert";
        el.querySelector(`.bb-sl[data-e="${e.id}"]`).classList.toggle("chg", geaendert);
      });
      $("#bb-fest").innerHTML = B.fest.map(([a, b]) => {
        const g = a === "Beton" && p.beton && p.beton !== B.eingaben.find(e => e.id === "beton").wert;
        return `<span class="${g ? "chg" : ""}"><b>${esc(a)}</b> ${esc(a === "Beton" && p.beton ? b.replace(/C\d+\/\d+/, p.beton) : b)}</span>`;
      }).join("");
      NUM.forEach(e => {
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
        const formeln = (arr, cls) => arr.length ? `<div class="${cls}">${arr.map(x => `<div>$\\displaystyle ${fill(x, ctx, digits)}$</div>`).join("")}</div>` : "";
        const ansatz = e.length ? formeln(f, "rw-f") : "", loesung = e.length ? formeln(e, "rw-e") : formeln(f, "rw-e");
        const tipp = (st.text ? `<p>${fill(st.text, ctx, digits)}</p>` : "") + ansatz;
        return kopf + `<section class="rw-step bb-step" data-ab="${esc(st.abschnitt)}"><h4><span class="rw-n">${n}</span><span>${esc(st.titel)}</span><span class="rw-q">Buch S. ${st.seite}</span></h4>
          ${st.frage ? `<p class="bb-frage"><b>Aufgabe:</b> ${fill(st.frage, ctx, digits)}</p>` : ""}
          <div class="bb-tipp">${tipp ? `<span class="bb-tag">Tipp</span>${tipp}` : ""}</div>
          <div class="bb-loes"><span class="bb-tag">Lösung</span>${loesung}
            ${st.notiz ? `<p class="bb-notiz"><b>Hinweis zum Buch:</b> ${esc(st.notiz)}</p>` : ""}</div>
        </section>`;
      }).join("");
      sichtbar();
      tex($("#bb-res")); tex($("#bb-rw"));
    }
    function sichtbar(){
      const steps = [...el.querySelectorAll(".bb-step")], N = steps.length;
      if (k > N) k = N;
      const alle = modus === "alle";
      steps.forEach((s, i) => {
        s.hidden = !alle && i >= k;
        const aktiv = !alle && i === k - 1, st = aktiv ? stufe : 2;
        const tp = s.querySelector(".bb-tipp"), lo = s.querySelector(".bb-loes");
        if (tp) tp.hidden = st < 1 || !tp.textContent.trim();
        if (lo) lo.hidden = st < 2;
        s.classList.toggle("bb-aktiv", aktiv);
        s.querySelectorAll(".bb-tag").forEach(x => x.hidden = alle);
      });
      el.querySelectorAll(".bb-ab").forEach(h => h.hidden = !steps.some(s => !s.hidden && s.dataset.ab === h.dataset.ab));
      el.querySelectorAll("#bb-modus button").forEach(b => b.classList.toggle("on", b.dataset.m === modus));
      $("#bb-nav").hidden = modus === "alle";
      const tippLeer = !steps[k - 1]?.querySelector(".bb-tipp")?.textContent.trim();
      const ende = k >= N && stufe === 2;
      $("#bb-next").textContent = stufe === 0 ? (tippLeer ? "Lösung zeigen" : "Tipp anzeigen") : stufe === 1 ? "Lösung zeigen" : "Nächster Schritt";
      $("#bb-next").disabled = ende;
      $("#bb-loes").hidden = stufe !== 0 || tippLeer;
      $("#bb-cnt").textContent = `Schritt ${Math.min(k, N)} von ${N} · ${["Aufgabe", "Tipp", "Lösung"][stufe]}`;
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

/* Maßkette mit Schrägstrichen wie in Bauzeichnungen; pts in Zeichnungskoordinaten, labels zwischen den Punkten */
function bbKette(pts, fest, labels, horiz, cls = []){
  const tick = q => horiz ? `<line class="dim" x1="${q - 4}" y1="${fest + 4}" x2="${q + 4}" y2="${fest - 4}"/><line class="dim" x1="${q}" y1="${fest - 6}" x2="${q}" y2="${fest + 6}"/>`
                          : `<line class="dim" x1="${fest - 4}" y1="${q + 4}" x2="${fest + 4}" y2="${q - 4}"/><line class="dim" x1="${fest - 6}" y1="${q}" x2="${fest + 6}" y2="${q}"/>`;
  let s = horiz ? `<line class="dim" x1="${pts[0] - 6}" y1="${fest}" x2="${pts[pts.length - 1] + 6}" y2="${fest}"/>`
                : `<line class="dim" x1="${fest}" y1="${pts[0] - 6}" x2="${fest}" y2="${pts[pts.length - 1] + 6}"/>`;
  pts.forEach(q => s += tick(q));
  labels.forEach((t, i) => {
    if (t === "") return;
    const m = (pts[i] + pts[i + 1]) / 2, c = cls[i] || "";
    s += horiz ? `<text x="${m}" y="${fest - 5}" text-anchor="middle" class="dl ${c}">${t}</text>`
               : `<text x="${fest - 5}" y="${m}" text-anchor="middle" class="dl ${c}" transform="rotate(-90 ${fest - 5} ${m})">${t}</text>`;
  });
  return s;
}
const bbCm = v => fmt(v * 100, 0);

/* Abb. 2.20 sinngemäß: statisches System, QS Hauptträger, QS Konsole */
function svgTraeger(c, chg){
  const k = id => chg(id) ? "chg" : "";
  let s = BB_DEFS;
  /* statisches System */
  const x0 = 36, x1 = 326, yb = 210, L = x1 - x0, xm = (x0 + x1) / 2;
  s += `<text x="${x0 - 10}" y="24" class="ttl">statisches System</text>`;
  s += `<line class="ld" x1="${x0}" y1="148" x2="${x1}" y2="148"/>`;
  for (let i = 0; i <= 10; i++){ const x = x0 + i * L / 10; s += bbPfeil(x, 148, x, yb - 5); }
  s += bbTxt(x0, 139, "p", "Ed", `= ${fmt(c.p, 1)} kN/m`, "lt " + k("p"));
  s += bbPfeil(xm, 62, xm, yb - 4, "ld big") + bbTxt(xm + 8, 76, "F", "Ed", `= ${fmt(c.F, 0)} kN`, "lt " + k("F"));
  s += `<line class="bb-beam" x1="${x0}" y1="${yb}" x2="${x1}" y2="${yb}"/>
    <path class="bb-sup" d="M${x0} ${yb}l-10 17h20z"/><line class="bb-gnd" x1="${x0 - 15}" y1="${yb + 17}" x2="${x0 + 15}" y2="${yb + 17}"/>
    <path class="bb-sup" d="M${x1} ${yb}l-10 17h20z"/><line class="bb-gnd" x1="${x1 - 15}" y1="${yb + 23}" x2="${x1 + 15}" y2="${yb + 23}"/>`;
  const xt = xm + 40;
  s += `<path class="bb-tor" d="M${xt - 2} ${yb - 17} A 7 17 0 1 1 ${xt - 2} ${yb + 17}" marker-end="url(#bb-pk)"/>` + bbTxt(xt - 46, yb + 38, "T", "Ed", `= ${fmt(c.T, 1)} kNm`, "res-t");
  s += bbKette([x0, xm, x1], yb + 62, [`${fmt(c.l / 2, 2)} m`, `${fmt(c.l / 2, 2)} m`], true, [k("l"), k("l")]);
  s += `<text x="${xm}" y="${yb + 90}" text-anchor="middle" class="dl ${k("l")}">l = ${fmt(c.l, 2)} m</text>`;

  /* Querschnitte, maßstäblich (Maße in cm) */
  const sc = 172 / 0.88, y0 = 66, hh = c.h * sc, w = c.b * sc;
  const hx = 392, kx = hx + w + 78, kw = 0.30 * sc, kh = 0.35 * sc, yk = y0 + hh - kh;
  s += `<text x="${hx + w / 2}" y="24" text-anchor="middle" class="ttl">QS Hauptträger</text><text x="${kx + (w + kw) / 2}" y="24" text-anchor="middle" class="ttl">QS Konsole</text>`;
  s += `<rect class="conc" x="${hx}" y="${y0}" width="${w}" height="${hh}"/><rect class="hatchf" x="${hx}" y="${y0}" width="${w}" height="${hh}"/>`;
  s += bbKette([y0, y0 + hh], hx + w + 16, [bbCm(c.h)], false, [k("h")]);
  s += bbKette([hx, hx + w], y0 + hh + 18, [bbCm(c.b)], true, [k("b")]);
  const kp = `M${kx} ${y0}h${w}v${hh - kh}h${kw}v${kh}h${-w - kw}z`;
  s += `<path class="conc" d="${kp}"/><path class="hatchf" d="${kp}"/>`;
  s += bbKette([y0, y0 + hh], kx - 16, [bbCm(c.h)], false, [k("h")]);
  s += bbKette([kx, kx + w, kx + w + kw], y0 + hh + 18, [bbCm(c.b), "30"], true, [k("b"), ""]);
  s += bbKette([yk, y0 + hh], kx + w + kw + 16, ["35"], false);
  const xf = kx + w + (c.e - c.b / 2) * sc;
  s += `<rect class="plate" x="${xf - 8}" y="${yk - 3}" width="16" height="3"/>`;
  s += bbPfeil(xf, yk - 62, xf, yk - 4, "ld big") + bbTxt(xf + 7, yk - 48, "F", "Ed", "", "lt " + k("F"));
  s += bbKette([kx + w, xf], yk - 24, [bbCm(c.e - c.b / 2)], true, [k("e") || k("b")]);
  s += `<line class="axis" x1="${kx + w / 2}" y1="${y0 - 8}" x2="${kx + w / 2}" y2="${y0 + hh + 6}"/>`;
  s += `<text x="${kx + (w + kw) / 2}" y="${y0 + hh + 46}" text-anchor="middle" class="dl ${k("e")}">e = ${bbCm(c.e)} cm ab Stegachse</text>`;
  return s;
}

/* Abb. 2.23 sinngemäß: statisches System Kragarm, Lasten je Geschoss, Querschnitt Aussteifungskern */
function svgKern(c, chg){
  const k = id => chg(id) ? "chg" : "";
  const xs = 120, yg = 344, hp = 54 * c.hs / 2.5;
  let s = BB_DEFS + `<text x="20" y="18" class="ttl">statisches System</text>`;
  s += `<line class="bb-beam" x1="${xs}" y1="${yg}" x2="${xs}" y2="${yg - 5 * hp}"/>
    <rect x="${xs - 34}" y="${yg}" width="68" height="10" fill="url(#bb-hatch)"/><line class="bb-gnd" x1="${xs - 34}" y1="${yg}" x2="${xs + 34}" y2="${yg}"/>`;
  const ebenen = [yg];
  for (let i = 1; i <= 5; i++){
    const y = yg - i * hp; ebenen.push(y);
    s += bbPfeil(xs - 52, y, xs - 5, y, "ld");
    s += bbPfeil(xs + 26, y - 26, xs + 26, y - 3, "ld");
    s += `<line class="bb-flr" x1="${xs}" y1="${y}" x2="${xs + 32}" y2="${y}"/>`;
    s += `<path class="bb-tor" d="M${xs - 14} ${y - 2} A 14 6 0 1 0 ${xs + 12} ${y - 5}" marker-end="url(#bb-pk)"/>`;
    s += `<text x="${xs - 54}" y="${y - 5}" class="sm ${k("H")}">H<tspan class="ix" dy="3">Ed</tspan></text>`;
    s += `<text x="${xs + 30}" y="${y - 15}" class="sm ${k("F")}">F<tspan class="ix" dy="3">Ed</tspan></text>`;
    s += `<text x="${xs + 4}" y="${y + 17}" class="sm ${k("Tg")}">T<tspan class="ix" dy="3">Ed</tspan></text>`;
  }
  ebenen.reverse();
  s += bbKette(ebenen, xs + 72, ebenen.slice(1).map(() => ""), false);
  ebenen.slice(1).forEach((y, i) => s += `<text x="${xs + 80}" y="${(y + ebenen[i]) / 2 + 4}" class="dl ${k("hs")}">${fmt(c.hs, 2)} m</text>`);
  s += `<g><text x="268" y="70" class="ttl2">Bemessungswerte je Stockwerk</text>
    ${bbTxt(268, 94, "F", "Ed", `= ${fmt(c.F, 0)} kN`, k("F"))}
    ${bbTxt(268, 116, "H", "Ed", `= ${fmt(c.H, 0)} kN`, k("H"))}
    ${bbTxt(268, 138, "T", "Ed", `= ${fmt(c.Tg, 0)} kNm`, k("Tg"))}
    <text x="268" y="184" class="ttl2">an der Einspannung</text>
    ${bbTxt(268, 208, "M", "Ed", `= ${fmt(c.M, 0)} kNm`, "res-t")}
    ${bbTxt(268, 230, "T", "Ed", `= ${fmt(c.T, 0)} kNm`, "res-t")}
    ${bbTxt(268, 252, "V", "Ed", `= ${fmt(c.V, 0)} kN`, "res-t")}
    ${bbTxt(268, 274, "N", "Ed", `= ${fmt(c.N, 0)} kN`, "res-t")}</g>`;
  /* Querschnitt Aussteifungskern, maßstäblich, Maße in cm */
  const sc = 196 / 2.2, x0 = 474, y0 = 52, A = c.a * sc, tw = c.t * sc;
  s += `<text x="${x0}" y="24" class="ttl">Querschnitt Aussteifungskern</text>`;
  const ring = `M${x0} ${y0}h${A}v${A}h${-A}z M${x0 + tw} ${y0 + tw}v${A - 2 * tw}h${A - 2 * tw}v${-(A - 2 * tw)}z`;
  s += `<path class="conc" fill-rule="evenodd" d="${ring}"/><path class="hatchf" fill-rule="evenodd" d="${ring}"/>`;
  const ix = x0 + tw + 10, iy = y0 + tw + 22;
  s += `<text x="${ix}" y="${iy}" class="in">Beton:</text><text x="${ix}" y="${iy + 17}" class="in ${k("beton")}">${esc(c.beton)}; XC1</text>
    <text x="${ix}" y="${iy + 42}" class="in">Bewehrung:</text><text x="${ix}" y="${iy + 59}" class="in">B500 A</text>`;
  const kt = k("t"), ka = k("a");
  s += bbKette([x0, x0 + tw, x0 + A - tw, x0 + A], y0 + A + 16, [bbCm(c.t), bbCm(c.a - 2 * c.t), bbCm(c.t)], true, [kt, ka || kt, kt]);
  s += bbKette([x0, x0 + A], y0 + A + 38, [bbCm(c.a)], true, [ka]);
  s += bbKette([y0, y0 + tw, y0 + A - tw, y0 + A], x0 + A + 16, [bbCm(c.t), bbCm(c.a - 2 * c.t), bbCm(c.t)], false, [kt, ka || kt, kt]);
  s += bbKette([y0, y0 + A], x0 + A + 38, [bbCm(c.a)], false, [ka]);
  s += `<text x="${x0}" y="${y0 + A + 62}" class="dl">Maße in cm</text>`;
  return s;
}
