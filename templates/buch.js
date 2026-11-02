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
  /* Expositionsklasse → Mindestbetondeckung c_min,dur, Vorhaltemaß Δc_dev [mm] und Mindestbetonfestigkeitsklasse
     (DIN EN 1992-1-1/NA, Tab. 4.4DE und E.1DE – auf diesen Werten beruhen die Zahlen im Buch) */
  expo: x => ({XC1: {cdur: 10, dc: 10, minC: "C16/20"}, XC2: {cdur: 20, dc: 15, minC: "C16/20"}, XC3: {cdur: 20, dc: 15, minC: "C20/25"},
               XC4: {cdur: 25, dc: 15, minC: "C25/30"}, XD1: {cdur: 40, dc: 15, minC: "C30/37"}, XD2: {cdur: 40, dc: 15, minC: "C35/45"},
               XS1: {cdur: 40, dc: 15, minC: "C30/37"}})[x],
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
    let modus = store.get("buch-modus", "alle"), k = 1, stufe = 0, ctxJetzt = null;
    const richtig = new Set(), versucht = new Set();
    const FCK = MATHCTX.FCK;   /* stufe des aktuellen Schritts: 0 Aufgabe, 1 Tipp, 2 Lösung */

    el.innerHTML = `
    <div class="bb-top"><button class="back" id="bb-zur" type="button">← Beispiel wählen</button>
      <div class="seg" id="bb-sel">${BB.beispiele.map((b, i) => `<button type="button" data-k="${i}" class="${i === wahl ? "on" : ""}">${esc(b.titel)}</button>`).join("")}</div></div>
    <div class="bb-head"><span class="label">${esc(BB.quelle)} · ${esc(B.abschnitt)}</span><h3>${esc(B.untertitel)}</h3><p>${B.aufgabe}</p></div>
    <div class="bb-grid">
      <figure class="bb-sys"><svg id="bb-svg" viewBox="0 0 720 600" role="img" aria-label="Statisches System mit Lasten und Querschnitt"></svg>
        <svg id="bb-sg" class="bb-sg" viewBox="0 0 720 210" role="img" aria-label="Schnittgrößenverläufe"></svg>
        <figcaption class="bb-fest" id="bb-fest"></figcaption></figure>
      <div class="panel bb-in"><h3>Ausgangswerte</h3><p class="bb-hint">Spielraum ±10 % um die Buchwerte</p>
        ${SEL.map(e => `<div class="bb-sl bb-sel" data-e="${e.id}"><label for="bb-${e.id}">${e.label}</label>
          <select id="bb-${e.id}">${e.werte.map(w => `<option ${w === p[e.id] ? "selected" : ""}>${esc(w)}</option>`).join("")}</select>
          <div class="bb-rg"><span>Buch: ${esc(e.wert)}</span><span class="bb-dev" id="bb-d-${e.id}"></span></div></div>`).join("")}
        ${NUM.map(e => `<div class="bb-sl" data-e="${e.id}">
          <label for="bb-${e.id}">${e.label}</label><output id="bb-o-${e.id}"></output>
          <input type="range" id="bb-${e.id}" min="${grenze(e, -1)}" max="${grenze(e, 1)}" step="${e.step}" value="${p[e.id]}">
          <div class="bb-rg"><span>${fmt(grenze(e, -1), e.d)}</span><span class="bb-dev" id="bb-d-${e.id}"></span><span>${fmt(grenze(e, 1), e.d)}</span></div></div>`).join("")}
        <div class="bb-btns"><button class="btn" id="bb-zufall" type="button">Zufallswerte</button><button class="btn ghost" id="bb-reset" type="button">Buchwerte laden</button></div>
        ${SEL.length ? `<label class="bb-chk"><input type="checkbox" id="bb-zsel"> Beton und Expositionsklasse mitwürfeln</label>` : ""}</div>
    </div>
    <div class="results" id="bb-res" style="margin-top:16px"></div>
    <section class="rw">
      <div class="row bb-druck">${IN_FRAME ? `<p class="note" style="margin:0">PDF-Export: in der Web-App unter ${esc((DATA.site || "").replace(/^https?:\/\//, ""))} öffnen.</p>`
        : `<button class="btn" id="bb-pdf" type="button">Rechenweg als PDF</button><button class="btn ghost" id="bb-pdf-a" type="button">Aufgabenblatt als PDF</button>`}</div>
      <div class="rw-head"><h3>Bemessung Schritt für Schritt</h3>
        <div class="seg bb-modus" id="bb-modus"><button type="button" data-m="einzeln">Einzeln aufdecken</button><button type="button" data-m="alle">Alle Schritte</button></div></div>
      <div class="rw-doc" id="bb-rw"></div>
      <div class="row bb-nav" id="bb-nav"><button class="btn" id="bb-next" type="button">Tipp anzeigen</button><button class="btn ghost" id="bb-loes" type="button">Lösung zeigen</button><button class="btn ghost" id="bb-allk" type="button">Alle Schritte zeigen</button><span class="label" id="bb-cnt"></span></div>
      <p class="bb-score" id="bb-score"></p>
    </section>`;

    $("#bb-zur").onclick = () => { waehlen(); window.scrollTo(0, 0); };
    el.querySelectorAll("#bb-sel button").forEach(b => b.onclick = () => { wahl = +b.dataset.k; zeigen(); });
    if ($("#bb-pdf")){
      $("#bb-pdf").onclick = () => { const {ctx, digits} = ctxNeu(); druckBuch(BB, B, ctx, digits, true, $("#bb-svg").innerHTML, $("#bb-sg").innerHTML); };
      $("#bb-pdf-a").onclick = () => { const {ctx, digits} = ctxNeu(); druckBuch(BB, B, ctx, digits, false, $("#bb-svg").innerHTML); };
    }
    $("#bb-zufall").onclick = () => {
      NUM.forEach(e => {
        const lo = grenze(e, -1), n = Math.round((grenze(e, 1) - lo) / e.step);
        p[e.id] = +(lo + Math.floor(Math.random() * (n + 1)) * e.step).toFixed(6);
        $("#bb-" + e.id).value = p[e.id];
      });
      if ($("#bb-zsel") && $("#bb-zsel").checked){
        const zuf = a => a[Math.floor(Math.random() * a.length)];
        const xe = SEL.find(e => e.id === "xk"), be = SEL.find(e => e.id === "beton");
        if (xe) p.xk = zuf(xe.werte);
        if (be){ const min = xe ? FCK(BUCHFN.expo(p.xk).minC) : 0; p.beton = zuf(be.werte.filter(w => FCK(w) >= min)); }
        SEL.forEach(e => $("#bb-" + e.id).value = p[e.id]);
      }
      store.set(key, p); k = 1; stufe = 0; richtig.clear(); sofort(); rechnen();
    };
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
        const g = a === "Beton" && ["beton", "xk"].some(id => p[id] !== undefined && p[id] !== B.eingaben.find(e => e.id === id).wert);
        const txt = a === "Beton" ? b.replace(/C\d+\/\d+/, p.beton || "$&").replace(/X[CDS]\d/, p.xk || "$&") : b;
        return `<span class="${g ? "chg" : ""}"><b>${esc(a)}</b> ${esc(txt)}</span>`;
      }).join("");
      NUM.forEach(e => {
        const dv = (p[e.id] / e.wert - 1) * 100, geaendert = Math.abs(dv) > 0.05;
        $("#bb-o-" + e.id).textContent = `${fmt(p[e.id], e.d)} ${e.einheit}`;
        $("#bb-d-" + e.id).textContent = geaendert ? `${dv > 0 ? "+" : "−"}${fmt(Math.abs(dv), 1)} %` : "Buchwert";
        el.querySelector(`.bb-sl[data-e="${e.id}"]`).classList.toggle("chg", geaendert);
      });
      const {ctx} = ctxNeu();
      $("#bb-sg").innerHTML = svgSchnitt(B, ctx).replace(/bb-(pf|pk|ms|hatch)/g, "sg-$1");
      $("#bb-svg").innerHTML = (B.system === "kern" ? svgKern : svgTraeger)(ctx, id => { const e = B.eingaben.find(x => x.id === id); return !!e && (typeof e.wert === "string" ? p[id] !== e.wert : Math.abs(p[id] / e.wert - 1) > 0.0005); });
    }
    function rechnen(){
      const {ctx, digits} = ctxNeu(); ctxJetzt = ctx; richtig.clear(); versucht.clear();
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
        const formeln = (arr, cls) => arr.length ? `<div class="${cls}">${arr.map(x => `<div>$\\displaystyle ${fill(x, ctx, digits, B.einheiten)}$</div>`).join("")}</div>` : "";
        const ansatz = e.length ? formeln(f, "rw-f") : "", loesung = e.length ? formeln(e, "rw-e") : formeln(f, "rw-e");
        const tipp = (st.text ? `<p>${fill(st.text, ctx, digits)}</p>` : "") + ansatz;
        return kopf + `<section class="rw-step bb-step" data-ab="${esc(st.abschnitt)}"><h4><span class="rw-n">${n}</span><span>${esc(st.titel)}</span><span class="rw-q">Buch S. ${st.seite}${st.skript ? ` · <b class="bb-skr">${esc(st.skript)}</b>` : ""}</span></h4>
          ${st.frage ? `<p class="bb-frage"><b>Aufgabe:</b> ${fill(st.frage, ctx, digits)}</p>` : ""}
          ${(st.pruefen || []).length ? `<div class="bb-ask"><span class="bb-tag">Dein Ergebnis</span>${st.pruefen.map(q => `<div class="ask"><label for="bb-a-${n}-${q.id}">$${q.label}$</label><input id="bb-a-${n}-${q.id}" data-id="${q.id}" inputmode="decimal" autocomplete="off"><span class="unit">${esc(q.einheit)}</span><span class="mk"></span></div>`).join("")}
            <div class="row"><button class="btn ghost bb-pruef" type="button">Prüfen</button><span class="bb-fb"></span></div></div>` : ""}
          <div class="bb-tipp">${tipp ? `<span class="bb-tag">Tipp</span>${tipp}` : ""}</div>
          <div class="bb-loes"><span class="bb-tag">Lösung</span>${loesung}
            ${st.notiz ? `<p class="bb-notiz"><b>Hinweis zum Buch:</b> ${esc(st.notiz)}</p>` : ""}</div>
        </section>`;
      }).join("");
      el.querySelectorAll(".bb-ask").forEach(a => {
        a.querySelector(".bb-pruef").onclick = () => pruefe(a);
        a.querySelectorAll("input").forEach(i => i.addEventListener("keydown", ev => { if (ev.key === "Enter") pruefe(a); }));
      });
      sichtbar();
      tex($("#bb-res")); tex($("#bb-rw"));
    }
    /* eigenes Ergebnis prüfen: ±2 % (wie bei den Übungsaufgaben), Komma oder Punkt */
    function pruefe(a){
      let ok = 0, alle = 0;
      a.querySelectorAll(".ask").forEach(r => {
        const inp = r.querySelector("input"), mk = r.querySelector(".mk"), soll = ctxJetzt[inp.dataset.id];
        const raw = inp.value.trim().replace(/\s/g, "").replace(",", ".");
        inp.classList.remove("ok", "no"); mk.className = "mk"; mk.textContent = "";
        alle++;
        if (!raw) return;
        const ist = parseFloat(raw), gut = Number.isFinite(ist) && Math.abs(ist - soll) <= Math.max(Math.abs(soll) * 0.02, 0.005);
        inp.classList.add(gut ? "ok" : "no"); mk.classList.add(gut ? "ok" : "no"); mk.textContent = gut ? "✓" : "✗";
        const key = inp.id; versucht.add(key); if (gut) richtig.add(key); else richtig.delete(key);
        if (gut) ok++;
      });
      a.querySelector(".bb-fb").textContent = ok === alle ? "Alles richtig – weiter zur Lösung." : ok ? `${ok} von ${alle} richtig.` : "Noch nicht – schau dir den Tipp an.";
      a.querySelector(".bb-fb").className = "bb-fb " + (ok === alle ? "ok" : "no");
      zaehler();
    }
    function zaehler(){
      const N = el.querySelectorAll(".bb-ask .ask").length;
      $("#bb-score").textContent = versucht.size ? `Selbst gerechnet: ${richtig.size} von ${N} Werten richtig` : "";
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
        const ak = s.querySelector(".bb-ask");
        if (ak) ak.hidden = alle;
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
      zaehler();
      $("#bb-cnt").textContent = `Schritt ${Math.min(k, N)} von ${N} · ${["Aufgabe", "Tipp", "Lösung"][stufe]}`;
    }
  }
}
/* ---------- Druckansicht im Stil des Lehrbuchs (Rechenweg bzw. Aufgabenblatt) ---------- */
function druckBuch(BB, B, ctx, digits, mitLoesung, svg, svg2 = ""){
  let box = document.getElementById("printarea");
  if (!box){ box = document.createElement("div"); box.id = "printarea"; document.body.appendChild(box); }
  const kap = (B.abschnitt.match(/\d+\.\d+/) || [""])[0];
  const datum = new Date().toLocaleDateString("de-DE");
  const geaendert = B.eingaben.some(e => ctx[e.id] !== e.wert);
  const wert = e => e.typ === "auswahl" ? esc(ctx[e.id]) : `${fmt(ctx[e.id], e.d)}${e.einheit ? " " + esc(e.einheit) : ""}`;
  const daten = B.eingaben.map(e => `<span>${e.label}</span><span class="n">${wert(e)}</span>`).join("");
  const fest = B.fest.filter(([a]) => a !== "Beton").map(([a, b]) => `<span>${esc(a)}</span><span class="n">${esc(b)}</span>`).join("");
  const abb = svg.replace(/bb-(pf|pk|ms|hatch|clip)/g, "pr-$1");
  const anm = [];
  let ab = "", nr = 0, html = "";
  for (const st of B.schritte){
    if (!cond(st, ctx)) continue;
    nr++;
    if (st.abschnitt !== ab && ab && mitLoesung && svg2 && !html.includes("bd-abb2")) html += `<figure class="bd-abb bd-abb2"><div class="bb-sys"><svg viewBox="0 0 720 210">${svg2.replace(/sg-(pf|pk|ms|hatch)/g, "p2-$1")}</svg></div><figcaption><b>Abb. 2</b>&ensp;Schnittgrößenverläufe</figcaption></figure>`;
    if (st.abschnitt !== ab){ ab = st.abschnitt; const [num, ...rest] = ab.split(" "); html += `<h3 class="bd-h3"><span>${esc(num)}</span>${esc(rest.join(" "))}</h3>`; }
    if (!mitLoesung){
      html += `<div class="bd-auf"><span class="bd-nr">${nr}</span><div><p>${fill(st.frage || st.titel, ctx, digits)}</p>${(st.pruefen || []).length
        ? `<p class="bd-erg">${st.pruefen.map(q => `$${q.label}$ = <span class="bd-luecke"></span>${q.einheit ? " " + esc(q.einheit) : ""}`).join("&emsp;")}</p>` : ""}</div></div>`;
      continue;
    }
    const f = lines(st.formel, ctx), e = lines(st.einsetzen, ctx);
    let fn = "";
    if (st.notiz){ anm.push(st.notiz); fn = `<sup class="bd-fn">${anm.length}</sup>`; }
    html += `<div class="bd-step">${st.skript ? `<p class="bd-skr">${esc(st.skript)}</p>` : ""}<p>${st.text ? fill(st.text, ctx, digits) : `<b>${esc(st.titel)}</b>`}${fn}</p>
      <div class="bd-eq">${[...f, ...e].map(x => `<div>$\\displaystyle ${fill(x, ctx, digits, B.einheiten)}$</div>`).join("")}</div></div>`;
  }
  box.innerHTML = `<div class="buchdruck">
    <div class="bd-kopf"><span>${esc(BB.quelle)} · ${esc(B.abschnitt)}</span><span>Betonbau 4 · ${mitLoesung ? "Rechenweg" : "Aufgabenblatt"} · ${datum}</span></div>
    <h2 class="bd-h2"><span>${esc(kap)}</span>${esc(B.titel)} Torsionsbemessung</h2>
    <h3 class="bd-h3"><span>${esc(kap)}.1</span>Aufgabenstellung</h3>
    <p>${fill(B.aufgabe, ctx, digits)}${geaendert ? " Die Ausgangswerte sind gegenüber dem Buch verändert (Werte siehe Tabelle)." : ""}</p>
    <figure class="bd-abb"><div class="bb-sys"><svg viewBox="0 0 720 600">${abb}</svg></div>
      <figcaption><b>Abb. 1</b>&ensp;${esc(B.untertitel)} – statisches System, Querschnitt und Lasten</figcaption></figure>
    <div class="bd-tab">${daten}${fest}</div>
    ${html}
    ${mitLoesung && anm.length ? `<div class="bd-anm">${anm.map((a, i) => `<p><sup>${i + 1}</sup> ${esc(a)}</p>`).join("")}</div>` : ""}
    ${!mitLoesung ? `<p class="bd-hinweis">Lösungen: in der Lernplattform unter Buchbeispiele mit denselben Werten (${geaendert ? "Werte wie oben einstellen" : "Buchwerte"}).</p>` : ""}
    <p class="bd-fuss">Rechenweg nach ${esc(BB.quelle)} (${esc(BB.auflage)}), erstellt mit der Betonbau-4-Lernplattform. Ohne Gewähr.</p></div>`;
  const go = () => { document.body.classList.add("printing"); setTimeout(() => window.print(), 50); };
  window.addEventListener("afterprint", () => document.body.classList.remove("printing"), {once: true});
  if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([box]).then(go).catch(go); else go();
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

/* ---------- Isometrie: Quader mit Ober-, Vorder- und Seitenfläche; x nach rechts hinten, y nach links hinten, z nach oben ---------- */
const ISO_C = Math.cos(Math.PI / 6), ISO_S = 0.5;
function isoRaum(punkte, box){   /* Maßstab und Lage so wählen, dass alle Punkte in box = [x, y, w, h] passen */
  const roh = punkte.map(([x, y, z]) => [(x - y) * ISO_C, -(x + y) * ISO_S - z]);
  const u0 = Math.min(...roh.map(p => p[0])), u1 = Math.max(...roh.map(p => p[0])), v0 = Math.min(...roh.map(p => p[1])), v1 = Math.max(...roh.map(p => p[1]));
  const s = Math.min(box[2] / (u1 - u0), box[3] / (v1 - v0));
  const ox = box[0] + (box[2] - (u1 - u0) * s) / 2 - u0 * s, oy = box[1] + (box[3] - (v1 - v0) * s) / 2 - v0 * s;
  const P = (x, y, z) => [ox + (x - y) * ISO_C * s, oy - ((x + y) * ISO_S + z) * s];
  const pt = a => a.map(p => P(...p).map(v => v.toFixed(1)).join(",")).join(" ");
  return {P, s,
    quader(x0, x1, y0, y1, z0, z1, cls){
      return `<g class="iso ${cls}"><polygon class="f-l" points="${pt([[x0, y0, z0], [x0, y1, z0], [x0, y1, z1], [x0, y0, z1]])}"/>`
        + `<polygon class="f-v" points="${pt([[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1]])}"/>`
        + `<polygon class="f-o" points="${pt([[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]])}"/></g>`;
    },
    verdeckt(x0, x1, y0, y1, z0, z1){        /* Kanten eines verdeckten Quaders gestrichelt */
      const k = [[[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1], [x0, y0, z1]], [[x1, y0, z0], [x1, y0, z1]], [[x1, y1, z0], [x1, y1, z1]], [[x0, y1, z0], [x0, y1, z1]], [[x0, y1, z0], [x1, y1, z0], [x1, y0, z0]]];
      return k.map(l => `<polyline class="iso-hid" points="${pt(l)}"/>`).join("");
    },
    poly(a, cls){ return `<polygon class="${cls}" points="${pt(a)}"/>`; },
    linie(a, b, cls, marker){ const [p, q] = [P(...a), P(...b)]; return `<line class="${cls}" x1="${p[0].toFixed(1)}" y1="${p[1].toFixed(1)}" x2="${q[0].toFixed(1)}" y2="${q[1].toFixed(1)}"${marker ? ` marker-end="url(#${marker})"` : ""}/>`; },
    pfad(a, cls, marker){ return `<polyline class="${cls}" points="${pt(a)}"${marker ? ` marker-end="url(#${marker})"` : ""}/>`; },
    text(p, t, cls = "", anchor = "start", dx = 0, dy = 0){ const q = P(...p); return `<text x="${(q[0] + dx).toFixed(1)}" y="${(q[1] + dy).toFixed(1)}" text-anchor="${anchor}" class="${cls}">${t}</text>`; }
  };
}
const bbIdx = (h, i) => `${h}<tspan class="ix" dy="4">${i}</tspan><tspan dy="-4"> </tspan>`;

/* ---------- Schräge Parallelprojektion wie in den Buchabbildungen: y frontal nach rechts, x schräg nach rechts hinten, z nach oben ---------- */
const OBL_K = 0.9, OBL_W = 16 * Math.PI / 180;
function oblRaum(punkte, box){
  const roh = punkte.map(([x, y, z]) => [y + x * OBL_K * Math.cos(OBL_W), -(z + x * OBL_K * Math.sin(OBL_W))]);
  const u0 = Math.min(...roh.map(p => p[0])), u1 = Math.max(...roh.map(p => p[0])), v0 = Math.min(...roh.map(p => p[1])), v1 = Math.max(...roh.map(p => p[1]));
  const s = Math.min(box[2] / (u1 - u0), box[3] / (v1 - v0));
  const ox = box[0] + (box[2] - (u1 - u0) * s) / 2 - u0 * s, oy = box[1] + (box[3] - (v1 - v0) * s) / 2 - v0 * s;
  const P = (x, y, z) => [ox + (y + x * OBL_K * Math.cos(OBL_W)) * s, oy - (z + x * OBL_K * Math.sin(OBL_W)) * s];
  const pt = a => a.map(p => P(...p).map(v => v.toFixed(1)).join(",")).join(" ");
  const R = {P, s, pt,
    quader(x0, x1, y0, y1, z0, z1, cls){       /* sichtbar: Vorderseite (x0), Oberseite (z1), rechte Seite (y1) */
      return `<g class="iso ${cls}"><polygon class="f-l" points="${pt([[x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]])}"/>`
        + `<polygon class="f-o" points="${pt([[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]])}"/>`
        + `<polygon class="f-v" points="${pt([[x0, y0, z0], [x0, y1, z0], [x0, y1, z1], [x0, y0, z1]])}"/></g>`;
    },
    poly: (a, cls) => `<polygon class="${cls}" points="${pt(a)}"/>`,
    linie(a, b, cls, marker){ const [p, q] = [P(...a), P(...b)]; return `<line class="${cls}" x1="${p[0].toFixed(1)}" y1="${p[1].toFixed(1)}" x2="${q[0].toFixed(1)}" y2="${q[1].toFixed(1)}"${marker ? ` marker-end="url(#${marker})"` : ""}/>`; },
    text(p, t, cls = "", anchor = "start", dx = 0, dy = 0, rot = 0){ const q = P(...p), x = (q[0] + dx).toFixed(1), y = (q[1] + dy).toFixed(1);
      return `<text x="${x}" y="${y}" text-anchor="${anchor}" class="${cls}"${rot ? ` transform="rotate(${rot} ${x} ${y})"` : ""}>${t}</text>`; },
    /* Maßkette entlang a→b mit Schrägstrichen, Texte zwischen den Punkten */
    kette(pkte, labels, cls = [], unten = true, rot = 0){
      let s = `<polyline class="dim" points="${pt(pkte)}"/>`;
      pkte.forEach(p => { const [x, y] = P(...p); s += `<line class="dim" x1="${x - 4}" y1="${y + 4}" x2="${x + 4}" y2="${y - 4}"/>`; });
      labels.forEach((t, i) => { const [x1, y1] = P(...pkte[i]), [x2, y2] = P(...pkte[i + 1]), x = (x1 + x2) / 2, y = (y1 + y2) / 2;
        s += `<text x="${x}" y="${y}" dy="${unten ? 14 : -5}" text-anchor="middle" class="dl ${cls[i] || ""}"${rot ? ` transform="rotate(${rot} ${x} ${y})"` : ""}>${t}</text>`; });
      return s;
    }
  };
  return R;
}
const OBL_ROT = -Math.atan2(OBL_K * Math.sin(OBL_W), OBL_K * Math.cos(OBL_W) * 1) * 180 / Math.PI;   /* Schriftwinkel entlang der x-Achse */
const bbU = (x, y, t, anchor = "start") => `<text x="${x}" y="${y}" text-anchor="${anchor}" class="ttl-u">${t}</text>`;

/* Abb. 2.20 sinngemäß: Isometrie, statisches System, Baustoffe und Lasten, QS Hauptträger und QS Konsole */
function svgTraeger(c, chg){
  const k = id => chg(id) ? "chg" : "";
  const l = c.l, b = c.b, h = c.h, xm = l / 2, Ln = 4.6, zK = 0.35, hN = h - zK, wN = 0.3;
  let s = BB_DEFS;

  /* Isometrie */
  const I = oblRaum([[-0.2, -0.45, -0.9], [l + 0.2, b + 0.3, h + 0.9], [xm, b + Ln + 0.1, zK + hN + 0.9], [xm, b + Ln, -0.6], [-0.2, -0.3, -0.7]], [12, 36, 432, 236]);
  s += bbU(40, 24, "Isometrie");
  const auflager = (x0, x1) => I.quader(x0, x1, -0.25, b + 0.25, -0.7, 0, "sup") + I.quader(x0, x1, -0.25, -0.02, 0, h * 0.6, "sup");
  const wange = (x0, x1) => I.quader(x0, x1, b + 0.02, b + 0.25, 0, h * 0.6, "sup");
  s += auflager(l - 0.3, l + 0.15) + wange(l - 0.3, l + 0.15);
  s += auflager(-0.15, 0.3);                                                                        /* Sockel und hintere Wange links */
  s += I.quader(0, l, 0, b, 0, h, "haupt");
  for (let i = 0; i <= 12; i++){ const x = 0.15 + i * (l - 0.3) / 12; s += I.linie([x, b / 2, h + 0.75], [x, b / 2, h + 0.04], "ld thin", "bb-pf"); }
  s += I.linie([0.15, b / 2, h + 0.75], [l - 0.15, b / 2, h + 0.75], "ld thin");
  s += I.quader(xm - 0.25, xm + 0.25, b + Ln - 0.35, b + Ln + 0.05, -0.6, zK, "sup");
  s += I.quader(xm - 0.22, xm + 0.22, b + 0.02, b + 0.36, 0, zK, "haupt");                         /* Konsole */
  s += I.quader(xm - wN / 2, xm + wN / 2, b + 0.06, b + Ln, zK, zK + hN, "neben");                   /* Nebenträger */
  for (let i = 0; i <= 12; i++){ const y = b + 0.15 + i * (Ln - 0.3) / 12; s += I.linie([xm, y, zK + hN + 0.75], [xm, y, zK + hN + 0.04], "ld thin", "bb-pf"); }
  s += I.linie([xm, b + 0.15, zK + hN + 0.75], [xm, b + Ln - 0.15, zK + hN + 0.75], "ld thin");
  s += wange(-0.15, 0.3);                                                                           /* vordere Wange zuletzt */
  s += I.text([l * 0.42, b, h * 0.62], "Haupt-", "lbl2", "middle", 0, 0, OBL_ROT) + I.text([l * 0.42, b, h * 0.62], "träger", "lbl2", "middle", 6, 14, OBL_ROT);
  s += I.text([xm - wN / 2, b + Ln * 0.5, zK + hN * 0.62], "Nebenträger", "lbl2", "middle");
  const [kx, ky] = I.P(xm - 0.22, b + 0.2, 0);
  s += `<line class="dim" x1="${kx + 4}" y1="${ky - 6}" x2="${kx + 16}" y2="${ky + 10}"/><text x="${kx + 18}" y="${ky + 22}" class="lbl2">Konsole</text>`;
  const [ax, ay] = I.P(0.3, b + 0.4, -0.45);
  s += `<line class="dim" x1="${ax}" y1="${ay}" x2="${ax + 34}" y2="${ay + 16}"/><text x="${ax + 38}" y="${ay + 14}" class="lbl2">Auflagertiefe</text><text x="${ax + 38}" y="${ay + 30}" class="lbl2">t = 30 cm</text>`;

  /* statisches System */
  const S = oblRaum([[0, 0, -1.2], [l, 0, -1.2], [l, c.e + 0.35, 1.4], [0, 0, 1.2], [xm, c.e, -0.8]], [458, 34, 250, 236]);
  s += bbU(704, 24, "statisches System", "end");
  for (let i = 0; i <= 14; i++){ const x = i * l / 14; s += S.linie([x, 0, 0.9], [x, 0, 0.04], "ld thin", "bb-pf"); }
  s += S.linie([0, 0, 0.9], [l, 0, 0.9], "ld thin");
  s += S.text([l * 0.18, 0, 0.9], `${bbIdx("p", "Ed")}= ${fmt(c.p, 1)} kN/m`, "lt " + k("p"), "start", 0, -6, OBL_ROT);
  s += S.linie([0, 0, 0], [l, 0, 0], "bb-beam");
  for (const x of [0, l]){ const [px, py] = S.P(x, 0, 0); s += `<path class="bb-sup" d="M${px} ${py}l-8 13h16z"/><line class="bb-gnd" x1="${px - 11}" y1="${py + 13}" x2="${px + 11}" y2="${py + 13}"/>`; }
  s += S.linie([xm, 0, 0], [xm, c.e, 0], "arm2");
  s += S.linie([xm, c.e, 1.35], [xm, c.e, 0.04], "ld big", "bb-pf") + S.text([xm, c.e, 0.5], bbIdx("F", "Ed"), "lt " + k("F"), "start", 7, 0);
  s += S.kette([[0, 0, -0.8], [xm, 0, -0.8], [l, 0, -0.8]], [fmt(l / 2, 2), fmt(l / 2, 2)], [k("l"), k("l")], true, OBL_ROT);
  s += S.kette([[xm, 0, -0.3], [xm, c.e, -0.3]], [fmt(c.e, 3)], [k("e")], true);

  /* untere Reihe: Baustoffe, Lasten, Querschnitte (Maße in cm) */
  s += `<g transform="translate(0 290)">`;
  s += `<text x="20" y="40" class="in2 ${k("beton") || k("xk")}">Beton: ${esc(c.beton)}; ${esc(c.xk)}</text>
    <text x="20" y="62" class="in2">d<tspan class="ix" dy="4">upper</tspan><tspan dy="-4"> = 16 mm</tspan></text>
    <text x="20" y="98" class="in2">Bewehrung: B500 A</text>
    <text x="20" y="134" class="in2">Bemessungswert</text><text x="20" y="154" class="in2">der Lasten:</text>
    <text x="20" y="176" class="in2 gr ${k("F")}">F<tspan class="ix" dy="4">Ed</tspan><tspan dy="-4"> = ${fmt(c.F, 0)} kN</tspan></text>
    <text x="20" y="198" class="in2 gr ${k("p")}">p<tspan class="ix" dy="4">Ed</tspan><tspan dy="-4"> = ${fmt(c.p, 1)} kN/m</tspan></text>
    <text x="20" y="220" class="in2 gr ${k("e")}">e = ${fmt(c.e, 3)} m</text>`;
  const sc = 150 / 0.88, y0 = 60, hh = c.h * sc, w = c.b * sc;
  const hx2 = 262, kx2 = 452, kw = 0.30 * sc, kh = 0.35 * sc, yk = y0 + hh - kh;
  s += bbU(hx2 - 20, 30, "QS Hauptträger") + bbU(kx2 - 24, 30, "QS Konsole");
  s += `<rect class="conc" x="${hx2}" y="${y0}" width="${w}" height="${hh}"/><rect class="hatchd" x="${hx2}" y="${y0}" width="${w}" height="${hh}"/>`;
  s += bbKette([y0, y0 + hh], hx2 + w + 16, [bbCm(c.h)], false, [k("h")]);
  s += bbKette([hx2, hx2 + w], y0 + hh + 18, [bbCm(c.b)], true, [k("b")]);
  const kp = `M${kx2} ${y0}h${w}v${hh - kh}h${kw}v${kh}h${-w - kw}z`;
  s += `<path class="conc" d="${kp}"/><path class="hatchd" d="${kp}"/>`;
  s += bbKette([y0, y0 + hh], kx2 - 16, [bbCm(c.h)], false, [k("h")]);
  s += bbKette([kx2, kx2 + w, kx2 + w + kw], y0 + hh + 18, [bbCm(c.b), "30"], true, [k("b"), ""]);
  s += bbKette([yk, y0 + hh], kx2 + w + kw + 16, ["35"], false);
  const xf = kx2 + w + (c.e - c.b / 2) * sc;
  s += `<rect class="plate" x="${xf - 8}" y="${yk - 3}" width="16" height="3"/>`;
  s += bbPfeil(xf, yk - 58, xf, yk - 4, "ld big") + `<text x="${xf + 8}" y="${yk - 44}" class="in2 gr ${k("F")}">F<tspan class="ix" dy="4">Ed</tspan><tspan dy="-4"> = ${fmt(c.F, 0)} kN</tspan></text>`;
  s += bbKette([kx2 + w, xf], yk - 22, [bbCm(c.e - c.b / 2)], true, [k("e") || k("b")]);
  return s + `</g>`;
}

/* Abb. 2.21 bzw. 2.24 sinngemäß: Schnittgrößenverläufe, positiv blau, negativ rot */
function svgSchnitt(B, c){
  let s = BB_DEFS;
  if (B.system !== "kern"){
    const l = c.l, xm = l / 2, A = c.A, Vm = A - c.p * xm, MK = c.F * c.e;
    const Mx = x => A * x - c.p * x * x / 2 - c.F * Math.max(0, x - xm);
    const xs = []; for (let i = 0; i <= 40; i++) xs.push(i / 40 * l);
    const tafel = (x0, titel, einheit, fn, max, extra = "") => {
      const o = 0.32 * l;
      const S = oblRaum([[0, 0, o * 1.15], [0, 0, -o * 1.15], [l, 0, o * 1.15], [l, 0, -o * 1.15], [xm, c.e * 2.4, 0]], [x0 + 18, 44, 190, 156]);
      const sk = o / max;
      let t = `<text x="${x0}" y="20" class="ttl-u">${titel}</text><text x="${x0}" y="36" class="dl">[${einheit}]</text>`;
      t += fn(S, sk) + S.linie([0, 0, 0], [l, 0, 0], "bb-beam") + S.linie([xm, 0, 0], [xm, c.e * 2.4, 0], "bb-beam") + extra;   /* Konsole quer zur Achse */
      return t;
    };
    const flaeche = (S, pkte, cls) => S.poly([[pkte[0][0], 0, 0], ...pkte.map(([x, v]) => [x, 0, v]), [pkte[pkte.length - 1][0], 0, 0]], "sg " + cls);
    const wert = (S, x, z, t, cls, anchor = "start", dx = 4, dy = 0) => S.text([x, 0, z], t, "sgv " + cls, anchor, dx, dy);
    const mV = Math.max(Math.abs(A), Math.abs(Vm)), mM = Math.max(Mx(xm), MK), mT = Math.abs(c.T);
    /* Querkraft: positiv nach unten (blau), negativ nach oben (rot), Sprung um F in Feldmitte */
    s += tafel(14, "Querkraft", "kN", (S, k) => flaeche(S, [[0, -A * k], [xm, -Vm * k]], "pos") + flaeche(S, [[xm, (c.F - Vm) * k], [l, A * k]], "neg")
      + wert(S, 0, -A * k, fmt(A, 0), "pos", "end", -4, 4) + wert(S, xm, -Vm * k, fmt(Vm, 0), "pos", "end", -4, 12)
      + wert(S, xm, (c.F - Vm) * k, fmt(-(c.F - Vm), 0), "neg", "start", 9, 4) + wert(S, l, A * k, fmt(-A, 0), "neg", "start", 5, 4), mV);
    /* Biegemoment: positiv unten (blau); Konsole: Kragmoment F·e (rot, quer zum Träger) */
    s += tafel(254, "Biegemoment", "kNm", (S, k) => flaeche(S, xs.map(x => [x, -Mx(x) * k]), "pos")
      + S.poly([[xm, 0, 0], [xm, c.e * 2.4, 0], [xm, 0, MK * k]], "sg neg") + wert(S, xm, -Mx(xm) * k, fmt(Mx(xm), 0), "pos", "middle", 0, 16)
      + S.text([xm, 0, MK * k], fmt(-MK, 0), "sgv neg", "end", -4, 2), mM);
    /* Torsion: links negativ (rot), rechts positiv (blau) */
    s += tafel(494, "Torsionsmoment", "kNm", (S, k) => flaeche(S, [[0, c.T * k], [xm, c.T * k]], "neg") + flaeche(S, [[xm, -c.T * k], [l, -c.T * k]], "pos")
      + wert(S, 0, c.T * k, fmt(-c.T, 1), "neg", "start", 4, -4) + wert(S, l, -c.T * k, fmt(c.T, 1), "pos", "start", 5, 4), mT);
    return s;
  }
  /* Aussteifungskern: Treppenverläufe über die Höhe */
  const n = 5, H = 168, y0 = 196, hp = H / n;
  const spalte = (x0, titel, einheit, werte, cls, links, kurve = false) => {
    const max = Math.max(...werte.map(Math.abs)), sk = 58 / max, xa = links ? x0 + 104 : x0 + 22, sg = links ? -1 : 1;
    let t = `<text x="${x0}" y="18" class="ttl-u">${titel}</text><text x="${x0}" y="32" class="dl">[${einheit}]</text>`;
    const pts = [[xa, y0 - H]];
    if (kurve){ for (let i = 50; i >= 0; i--){ const z = i / 50 * n; let m = 0; for (let j = 1; j <= n; j++) m += Math.max(0, j - z) * c.H * c.hs; pts.push([xa + sg * m * sk, y0 - z * hp]); } }
    else { for (let i = n; i >= 1; i--){ const w = sg * Math.abs(werte[i - 1]) * sk; pts.push([xa + w, y0 - i * hp], [xa + w, y0 - (i - 1) * hp]); } }
    pts.push([xa, y0]);
    t += `<polygon class="sg ${cls}" points="${pts.map(p => p.join(",")).join(" ")}"/>`;
    t += `<line class="bb-beam" x1="${xa}" y1="${y0}" x2="${xa}" y2="${y0 - H}"/><rect x="${xa - 20}" y="${y0}" width="40" height="7" fill="url(#bb-hatch)"/><line class="bb-gnd" x1="${xa - 20}" y1="${y0}" x2="${xa + 20}" y2="${y0}"/>`;
    for (let i = 1; i <= n; i++){
      const v = kurve ? werte[i - 1] : werte[i - 1], xv = xa + (links ? -1 : 1) * Math.abs(v) * sk, yv = kurve ? y0 - (i - 1) * hp : y0 - (i - 0.5) * hp;
      t += `<text x="${links ? xv - 4 : xv + 4}" y="${yv + 4}" text-anchor="${links ? "end" : "start"}" class="sgv ${cls}">${fmt(v, 0)}</text>`;
    }
    return t;
  };
  const N = [], V = [], M = [], T = [];
  for (let i = 1; i <= n; i++){ const ob = n - i + 1; N.push(-c.F * ob); V.push(c.H * ob); T.push(c.Tg * ob); let m = 0; for (let j = i; j <= n; j++) m += (j - (i - 1)) * c.H * c.hs; M.push(-m); }
  s += spalte(8, "Normalkraft", "kN", N, "neg", true) + spalte(180, "Querkraft", "kN", V, "pos", false)
     + spalte(352, "Biegemoment", "kNm", M, "neg", true, true) + spalte(560, "Torsionsmoment", "kNm", T, "pos", false);
  return s;
}

function svgKern(c, chg){
  const k = id => chg(id) ? "chg" : "";
  let s = BB_DEFS;
  /* Gesamtgebäude: fünf Decken, Stützenraster, Kern an der Stirnseite (ausmittig) */
  const hs = c.hs, a = c.a, t = c.t, Lx = 20, Ly = 12, yk0 = (Ly - a) / 2, n = 5, d = 0.25;
  const I = isoRaum([[0, 0, 0], [Lx, 0, 0], [0, Ly, 0], [Lx, Ly, n * hs + 1], [0, 0, n * hs + 1.2]], [14, 36, 404, 254]);
  s += `<text x="20" y="24" class="ttl">Gesamtgebäude</text>`;
  s += I.poly([[0, 0, 0], [Lx, 0, 0], [Lx, Ly, 0], [0, Ly, 0]], "iso-boden");
  const stuetzen = []; for (const x of [5, 10, 15, 20]) for (const y of [0, 6, 12]) stuetzen.push([x, y]);
  const decke = z => { /* Deckenplatte als Quader, Kernbereich wird vom Kern selbst überdeckt */
    return I.quader(0, Lx, 0, Ly, z - d, z, "decke"); };
  for (let i = 1; i <= n; i++){
    const z0 = (i - 1) * hs, z1 = i * hs - d;
    stuetzen.forEach(([x, y]) => s += I.linie([x, y, z0], [x, y, z1], "iso-st"));
    s += I.quader(0, a, yk0, yk0 + a, z0, z1 + d, "kern");
    s += decke(i * hs);
    s += I.quader(0, a, yk0, yk0 + a, i * hs - d, i * hs + 0.02, "kern");
  }
  s += I.quader(0, a, yk0, yk0 + a, n * hs, n * hs + 0.6, "kern");
  const [kx1, ky1] = I.P(0, yk0 + a / 2, n * hs + 0.6);
  s += `<line class="dim" x1="${kx1}" y1="${ky1}" x2="${kx1 - 26}" y2="${ky1 - 20}"/><text x="${kx1 - 30}" y="${ky1 - 23}" text-anchor="end" class="lbl">Aussteifungskern</text>`;
  for (let i = 1; i <= n; i++){ const [px, py] = I.P(Lx, 0, i * hs - hs / 2); s += `<text x="${px + 8}" y="${py + 4}" class="dl ${k("hs")}">${fmt(hs, 2)} m</text>`; }
  for (let i = 0; i <= n; i++){ const [px, py] = I.P(Lx, 0, i * hs); s += `<line class="dim" x1="${px + 2}" y1="${py}" x2="${px + 8}" y2="${py}"/>`; }

  /* statisches System: Kragarm mit Lasten je Geschoss */
  const S = isoRaum([[0, 0, 0], [-2.2, 0, n * hs], [1.4, 1.4, n * hs + 1.2], [1, -1, 0]], [440, 40, 200, 250]);
  s += `<text x="446" y="24" class="ttl">statisches System</text>`;
  s += S.poly([[-0.9, -0.9, 0], [0.9, -0.9, 0], [0.9, 0.9, 0], [-0.9, 0.9, 0]], "iso-boden");
  s += S.linie([0, 0, 0], [0, 0, n * hs], "bb-beam");
  for (let i = 1; i <= n; i++){
    const z = i * hs;
    s += S.linie([-2, 0, z], [-0.08, 0, z], "ld", "bb-pf");
    s += S.linie([0.25, -0.25, z + 1.1], [0.25, -0.25, z + 0.08], "ld", "bb-pf");
    const ring = []; for (let j = 0; j <= 24; j++){ const f = 0.5 + j / 24 * 4.6; ring.push([0.55 * Math.cos(f), 0.55 * Math.sin(f), z - 0.15]); }
    s += S.pfad(ring, "bb-tor", "bb-pk");
    if (i === n){
      s += S.text([-2, 0, z], bbIdx("H", "Ed"), "lt " + k("H"), "end", -4, 4) + S.text([0.25, -0.25, z + 1.1], bbIdx("F", "Ed"), "lt " + k("F"), "start", 5, 6)
        + S.text([0.55, 0, z - 0.15], bbIdx("T", "Ed"), "lt " + k("Tg"), "start", 8, 10);
    }
  }
  const [sx, sy0] = S.P(0, 0, 0);
  for (let i = 0; i < n; i++){ const ya = S.P(0, 0, i * hs)[1], yb = S.P(0, 0, (i + 1) * hs)[1]; s += bbKette([yb, ya], sx + 92, [""], false) + `<text x="${sx + 100}" y="${(ya + yb) / 2 + 4}" class="dl ${k("hs")}">${fmt(hs, 2)} m</text>`; }

  /* untere Reihe: Bemessungswerte und Querschnitt, maßstäblich in cm */
  s += `<line class="dim" x1="10" y1="302" x2="710" y2="302" style="opacity:.35"/><g transform="translate(0 300)">`;
  s += `<text x="20" y="40" class="ttl2">Bemessungswerte je Stockwerk</text>
    ${bbTxt(20, 64, "F", "Ed", `= ${fmt(c.F, 0)} kN`, k("F"))}
    ${bbTxt(20, 86, "H", "Ed", `= ${fmt(c.H, 0)} kN`, k("H"))}
    ${bbTxt(20, 108, "T", "Ed", `= ${fmt(c.Tg, 0)} kNm`, k("Tg"))}
    <text x="20" y="146" class="ttl2">an der Einspannung</text>
    ${bbTxt(20, 170, "M", "Ed", `= ${fmt(c.M, 0)} kNm`, "res-t")}
    ${bbTxt(20, 192, "T", "Ed", `= ${fmt(c.T, 0)} kNm`, "res-t")}
    ${bbTxt(20, 214, "V", "Ed", `= ${fmt(c.V, 0)} kN`, "res-t")}
    ${bbTxt(20, 236, "N", "Ed", `= ${fmt(c.N, 0)} kN`, "res-t")}`;
  const sc = 196 / 2.2, x0 = 420, y0 = 52, A = c.a * sc, tw = c.t * sc;
  s += `<text x="${x0}" y="30" class="ttl">Querschnitt Aussteifungskern</text>`;
  const ringQ = `M${x0} ${y0}h${A}v${A}h${-A}z M${x0 + tw} ${y0 + tw}v${A - 2 * tw}h${A - 2 * tw}v${-(A - 2 * tw)}z`;
  s += `<path class="conc" fill-rule="evenodd" d="${ringQ}"/><path class="hatchf" fill-rule="evenodd" d="${ringQ}"/>`;
  const ix = x0 + tw + 10, iy = y0 + tw + 22;
  s += `<text x="${ix}" y="${iy}" class="in">Beton:</text><text x="${ix}" y="${iy + 17}" class="in ${k("beton") || k("xk")}">${esc(c.beton)}; ${esc(c.xk)}</text>
    <text x="${ix}" y="${iy + 42}" class="in">Bewehrung:</text><text x="${ix}" y="${iy + 59}" class="in">B500 A</text>`;
  const kt = k("t"), ka = k("a");
  s += bbKette([x0, x0 + tw, x0 + A - tw, x0 + A], y0 + A + 16, [bbCm(c.t), bbCm(c.a - 2 * c.t), bbCm(c.t)], true, [kt, ka || kt, kt]);
  s += bbKette([x0, x0 + A], y0 + A + 38, [bbCm(c.a)], true, [ka]);
  s += bbKette([y0, y0 + tw, y0 + A - tw, y0 + A], x0 + A + 16, [bbCm(c.t), bbCm(c.a - 2 * c.t), bbCm(c.t)], false, [kt, ka || kt, kt]);
  s += bbKette([y0, y0 + A], x0 + A + 38, [bbCm(c.a)], false, [ka]);
  s += `<text x="${x0}" y="${y0 + A + 62}" class="dl">Maße in cm</text>`;
  return s + `</g>`;
}
