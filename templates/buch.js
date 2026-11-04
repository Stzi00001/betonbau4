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
    if (mu > muVon(hi)) return {w: NaN, s: NaN, xi: NaN, z: NaN};
    for (let i = 0; i < 80; i++){ const m = (lo + hi) / 2; if (muVon(m) < mu) lo = m; else hi = m; }
    const xi = (lo + hi) / 2, z = zustand(xi);
    return {w: z.aR * xi, s: sig(z.es), xi, z: 1 - z.ka * xi};
  },
  /* Expositionsklasse → Mindestbetondeckung c_min,dur, Vorhaltemaß Δc_dev [mm] und Mindestbetonfestigkeitsklasse
     (DIN EN 1992-1-1/NA, Tab. 4.4DE und E.1DE – auf diesen Werten beruhen die Zahlen im Buch) */
  expo: x => ({XC1: {cdur: 10, dc: 10, minC: "C16/20"}, XC2: {cdur: 20, dc: 15, minC: "C16/20"}, XC3: {cdur: 20, dc: 15, minC: "C20/25"},
               XC4: {cdur: 25, dc: 15, minC: "C25/30"}, XD1: {cdur: 40, dc: 15, minC: "C30/37"}, XD2: {cdur: 40, dc: 15, minC: "C35/45"},
               XS1: {cdur: 40, dc: 15, minC: "C30/37"}})[x],
  fctmVon: fck => ({20: 2.2, 25: 2.6, 30: 2.9, 35: 3.2, 40: 3.5, 45: 3.8, 50: 4.1})[fck] ?? 0.3 * Math.pow(fck, 2 / 3),
  stabA: (n, phi) => n * Math.PI * phi * phi / 400,                       /* cm² */
  stabTxt: (n, phi) => `${n}\\varnothing ${phi}`,
  /* Lagermatten (R-Matten): kleinste, die reicht */
  mattenWahl(erf){
    const M = [["R188A", 1.88], ["R257A", 2.57], ["R335A", 3.35], ["R424A", 4.24], ["R524A", 5.24]];
    const m = M.find(x => x[1] >= erf - 1e-9) || M[M.length - 1];
    return {txt: `\\text{${m[0]}}`, a: m[1]};
  },
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
        return {phi, s: sf, a: 2 * BUCHFN.stabA(1, phi) / (sf / 100), txt: `\\varnothing ${phi}/${String(sf).replace(".", "{,}")}`, dcm: (phi / 10).toFixed(1).replace(".", "{,}")};
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
    const quellen = [...new Set(BB.beispiele.map(b => `${b.quelle || BB.quelle} (${b.auflage || BB.auflage})`))];
    el.innerHTML = `<p class="note">Rechenbeispiele aus ${quellen.map(esc).join(" und ")}. Die Ausgangswerte lassen sich um ±10 % verändern; System, Rechenweg und Ergebnisse rechnen mit.</p>
    <div class="bb-wahl">${BB.beispiele.map((b, k) => `
      <button class="bb-karte" type="button" data-k="${k}">
        <svg viewBox="0 0 120 80" aria-hidden="true">${({kern: ICON_KERN, balken: ICON_BALKEN, kragarm: ICON_KRAGARM, kreuz: ICON_KREUZ, bruecke: ICON_BRUECKE})[b.system] || ICON_TRAEGER}</svg>
        <span class="label">${esc((b.quelle || BB.quelle).split(":")[0])} · ${esc(b.abschnitt)}</span>
        <h3>${esc(b.titel)}</h3>
        <p>${esc(b.untertitel)} · ${b.schritte.length} Schritte</p>
      </button>`).join("")}</div>`;
    el.querySelectorAll(".bb-karte").forEach(x => x.onclick = () => { wahl = +x.dataset.k; zeigen(); window.scrollTo(0, 0); });
  }

  function zeigen(){
    const B = BB.beispiele[wahl], key = "buch-" + t.id + "-" + B.id, W = wortlaut(B);
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
    <div class="bb-head"><span class="label">${esc(B.quelle || BB.quelle)} · ${esc(B.abschnitt)}</span><h3>${esc(B.untertitel)}</h3><p>${B.aufgabe}</p></div>
    <div class="bb-grid">
      <figure class="bb-sys"><svg id="bb-svg" viewBox="0 0 720 600" role="img" aria-label="Statisches System mit Lasten und Querschnitt"></svg>
        <svg id="bb-sg" class="bb-sg" viewBox="0 0 720 210" role="img" aria-label="Schnittgrößenverläufe"></svg>
        <figcaption class="bb-fest" id="bb-fest"></figcaption></figure>
      <div class="panel bb-in"><h3>Ausgangswerte</h3><p class="bb-hint">Spielraum ±10 % um die ${W.werte}</p>
        ${SEL.map(e => `<div class="bb-sl bb-sel" data-e="${e.id}"><label for="bb-${e.id}">${e.label}</label>
          <select id="bb-${e.id}">${e.werte.map(w => `<option ${w === p[e.id] ? "selected" : ""}>${esc(w)}</option>`).join("")}</select>
          <div class="bb-rg"><span>${W.quelle}: ${esc(e.wert)}</span><span class="bb-dev" id="bb-d-${e.id}"></span></div></div>`).join("")}
        ${NUM.map(e => `<div class="bb-sl" data-e="${e.id}">
          <label for="bb-${e.id}">${e.label}</label><output id="bb-o-${e.id}"></output>
          <input type="range" id="bb-${e.id}" min="${grenze(e, -1)}" max="${grenze(e, 1)}" step="${e.step}" value="${p[e.id]}">
          <div class="bb-rg"><span>${fmt(grenze(e, -1), e.d)}</span><span class="bb-dev" id="bb-d-${e.id}"></span><span>${fmt(grenze(e, 1), e.d)}</span></div></div>`).join("")}
        <div class="bb-btns"><button class="btn" id="bb-zufall" type="button">Zufallswerte</button><button class="btn ghost" id="bb-reset" type="button">${W.werte} laden</button></div>
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
        $("#bb-d-" + e.id).textContent = geaendert ? "geändert" : W.wert;
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
        $("#bb-d-" + e.id).textContent = geaendert ? `${dv > 0 ? "+" : "−"}${fmt(Math.abs(dv), 1)} %` : W.wert;
        el.querySelector(`.bb-sl[data-e="${e.id}"]`).classList.toggle("chg", geaendert);
      });
      const {ctx} = ctxNeu();
      $("#bb-sg").innerHTML = svgSchnitt(B, ctx).replace(/bb-(pf|pk|ms|hatch)/g, "sg-$1");
      $("#bb-svg").innerHTML = (({kern: svgKern, balken: svgBalken, kragarm: svgKragarm, kreuz: svgKreuz, bruecke: svgBruecke})[B.system] || svgTraeger)(ctx, id => { const e = B.eingaben.find(x => x.id === id); return !!e && (typeof e.wert === "string" ? p[id] !== e.wert : Math.abs(p[id] / e.wert - 1) > 0.0005); });
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
        return kopf + `<section class="rw-step bb-step" data-ab="${esc(st.abschnitt)}"><h4><span class="rw-n">${n}</span><span>${esc(st.titel)}</span><span class="rw-q">${W.seite || W.quelle + " S."} ${st.seite}${st.skript ? ` · <b class="bb-skr">${esc(st.skript)}</b>` : ""}</span></h4>
          ${st.frage ? `<p class="bb-frage"><b>Aufgabe:</b> ${fill(st.frage, ctx, digits)}</p>` : ""}
          ${(st.pruefen || []).length ? `<div class="bb-ask"><span class="bb-tag">Dein Ergebnis</span>${st.pruefen.map(q => `<div class="ask"><label for="bb-a-${n}-${q.id}">$${q.label}$</label><input id="bb-a-${n}-${q.id}" data-id="${q.id}" inputmode="decimal" autocomplete="off"><span class="unit">${esc(q.einheit)}</span><span class="mk"></span></div>`).join("")}
            <div class="row"><button class="btn ghost bb-pruef" type="button">Prüfen</button><span class="bb-fb"></span></div></div>` : ""}
          <div class="bb-tipp">${tipp ? `<span class="bb-tag">Tipp</span>${tipp}` : ""}</div>
          <div class="bb-loes"><span class="bb-tag">Lösung</span>${loesung}
            ${st.notiz ? `<p class="bb-notiz"><b>${W.hinweis}:</b> ${esc(st.notiz)}</p>` : ""}</div>
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
  const kap = (B.abschnitt.match(/\d+\.\d+/) || [B.kap || ""])[0], Q = B.quelle || BB.quelle, AUFL = B.auflage || BB.auflage;
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
    if (st.abschnitt !== ab && ab && mitLoesung && svg2 && !html.includes("bd-abb2")) html += `<figure class="bd-abb bd-abb2"><div class="bb-sys"><svg viewBox="0 0 720 210">${svg2.replace(/sg-(pf|pk|ms|hatch)/g, "p2-$1")}</svg></div><figcaption><b>Abb. 2</b>&ensp;${esc(B.abb2 || "Schnittgrößenverläufe")}</figcaption></figure>`;
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
    <div class="bd-kopf"><span>${esc(Q)} · ${esc(B.abschnitt)}</span><span>Betonbau 4 · ${mitLoesung ? "Rechenweg" : "Aufgabenblatt"} · ${datum}</span></div>
    <h2 class="bd-h2"><span>${esc(kap)}</span>${esc(B.titel)}${/torsion/i.test(B.titel) ? "" : " Torsionsbemessung"}</h2>
    <h3 class="bd-h3"><span>${esc(kap)}.1</span>Aufgabenstellung</h3>
    <p>${fill(B.aufgabe, ctx, digits)}${geaendert ? ` Die Ausgangswerte sind gegenüber ${B.wortlaut ? "der Vorgabe" : "dem Buch"} verändert (Werte siehe Tabelle).` : ""}</p>
    <figure class="bd-abb"><div class="bb-sys"><svg viewBox="0 0 720 600">${abb}</svg></div>
      <figcaption><b>Abb. 1</b>&ensp;${esc(B.untertitel)} – statisches System, Querschnitt und Lasten</figcaption></figure>
    <div class="bd-tab">${daten}${fest}</div>
    ${html}
    ${mitLoesung && anm.length ? `<div class="bd-anm">${anm.map((a, i) => `<p><sup>${i + 1}</sup> ${esc(a)}</p>`).join("")}</div>` : ""}
    ${!mitLoesung ? `<p class="bd-hinweis">Lösungen: in der Lernplattform unter Buchbeispiele mit denselben Werten (${geaendert ? "Werte wie oben einstellen" : wortlaut(B).werte}).</p>` : ""}
    <p class="bd-fuss">Rechenweg nach ${esc(Q)} (${esc(AUFL)}), erstellt mit der Betonbau-4-Lernplattform. Ohne Gewähr.</p></div>`;
  const go = () => { document.body.classList.add("printing"); setTimeout(() => window.print(), 50); };
  window.addEventListener("afterprint", () => document.body.classList.remove("printing"), {once: true});
  if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([box]).then(go).catch(go); else go();
}
function wortlaut(B){ return Object.assign({quelle: "Buch", wert: "Buchwert", werte: "Buchwerte", hinweis: "Hinweis zum Buch"}, B.wortlaut || {}); }
function grenze(e, s){ const v = e.wert * (1 + s * 0.1); return +(Math.round(v / e.step) * e.step).toFixed(6); }

/* ---------- Skizzen ---------- */
const ICON_TRAEGER = '<path d="M10 52h100" stroke-width="4"/><path d="M14 52l-6 10h12zM106 52l-6 10h12z"/><path d="M60 14v32M55 38l5 9 5-9"/><path d="M14 30h92M24 30v18M44 30v18M76 30v18M96 30v18"/>';
const ICON_BALKEN = '<path d="M10 56h100" stroke-width="4"/><path d="M14 56l-6 10h12zM106 56l-6 10h12z"/><path d="M14 28h92M26 28v20M44 28v20M62 28v20M80 28v20M98 28v20"/><path d="M48 70a12 6 0 1 0 24 0"/><path d="M72 70l-6-1M72 70l1 5"/>';
const ICON_KRAGARM = '<path d="M14 10v60" stroke-width="2"/><path d="M8 14l6-4M8 24l6-4M8 34l6-4M8 44l6-4M8 54l6-4M8 64l6-4"/><path d="M14 30L58 56h50" stroke-width="4"/><path d="M92 26v24M87 42l5 9 5-9"/>';
const ICON_KREUZ = '<path d="M14 10v44" stroke-width="2"/><path d="M8 14l6-4M8 24l6-4M8 34l6-4M8 44l6-4M8 54l6-4"/><path d="M14 24L96 70" stroke-width="4"/><path d="M40 52h72" stroke-width="4"/><path d="M42 30v18M37 40l5 9 5-9M96 50v16M91 58l5 9 5-9"/>';
const ICON_BRUECKE = '<path d="M6 22h108" stroke-width="4"/><path d="M24 24l4 26h14l4-26M74 24l4 26h14l4-26"/><path d="M20 66h80M28 60l-4 6h8zM60 60l-4 6h8zM92 60l-4 6h8z"/>';
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

/* Torsionsbalken mit Kragplatte (Wendehorst, sinngemäß): Isometrie, statisches System, Baustoffe/Lasten, Schnitt */
function svgBalken(c, chg){
  const k = id => chg(id) ? "chg" : "";
  const l = c.l, t = c.tW, b = c.b, h = c.h, hp = c.hp, lk = c.lk, xe = l + t;
  let s = BB_DEFS;

  /* Isometrie: Balkenachse frontal (y), Kragplatte nach hinten (x), Wände quer zur Balkenachse */
  const I = oblRaum([[-0.35, -t - 0.1, -1.0], [b + lk + 0.1, xe + 0.1, h + 0.75], [b + lk, -t, h + 0.75], [-0.35, xe, -1.0]], [12, 36, 432, 236]);
  s += bbU(40, 24, "Isometrie");
  const wand = y0 => I.quader(-0.35, b + 0.35, y0, y0 + t, -1.0, 0, "sup");
  s += wand(-t) + wand(l);
  s += I.quader(b, b + lk, -t, xe, h - hp, h, "neben");
  s += I.quader(0, b, -t, xe, 0, h, "haupt");
  for (let i = 0; i <= 9; i++){ const y = 0.15 + i * (l - 0.3) / 9; s += I.linie([b + lk * 0.55, y, h + 0.6], [b + lk * 0.55, y, h + 0.03], "ld thin", "bb-pf"); }
  s += I.linie([b + lk * 0.55, 0.15, h + 0.6], [b + lk * 0.55, l - 0.15, h + 0.6], "ld thin");
  s += I.text([b + lk * 0.55, l * 0.5, h + 0.6], `${bbIdx("q", "k")}= ${fmt(c.qk, 1)} kN/m²`, "lt " + k("qk"), "middle", 0, -8);
  s += I.text([b + lk * 0.2, l * 0.5, h], "Kragplatte", "lbl2", "middle", 0, 4);
  s += I.text([0, l * 0.5, h * 0.5], "Balken", "lbl2", "middle", 0, 5);
  s += I.text([-0.35, xe, -0.55], "Wand", "lbl2", "start", 6, 0);
  /* statisches System: Einfeldträger mit Gabellagern, g+q und Streckentorsion m_T */
  const S = oblRaum([[0, 0, -1.2], [c.leff, 0, -1.2], [c.leff, 0, 1.4], [0, 0, 1.2], [0, 0.6, 0], [c.leff, -0.6, 0]], [458, 34, 250, 236]);
  s += bbU(704, 24, "statisches System", "end");
  for (let i = 0; i <= 14; i++){ const x = i * c.leff / 14; s += S.linie([x, 0, 0.9], [x, 0, 0.04], "ld thin", "bb-pf"); }
  s += S.linie([0, 0, 0.9], [c.leff, 0, 0.9], "ld thin");
  s += S.text([c.leff * 0.1, 0, 0.9], `${bbIdx("g", "d")}+ ${bbIdx("q", "d")}= ${fmt(c.gd + c.qd, 2)} kN/m`, "lt " + (k("qk") || k("hp") || k("lk") || k("b") || k("h")), "start", 0, -6, OBL_ROT);
  s += S.linie([0, 0, 0], [c.leff, 0, 0], "bb-beam");
  for (const x of [0, c.leff]){
    const [px, py] = S.P(x, 0, 0);
    s += `<path class="bb-sup" d="M${px} ${py}l-8 13h16z"/><line class="bb-gnd" x1="${px - 11}" y1="${py + 13}" x2="${px + 11}" y2="${py + 13}"/>`
      + `<path class="bb-sup" d="M${px - 9} ${py - 14}v14M${px + 9} ${py - 14}v14" fill="none"/>`;            /* Gabel */
  }
  /* Streckentorsion: Momentenvektoren mit Doppelpfeil unter der Achse */
  for (let i = 1; i <= 6; i++){ const x = i * c.leff / 7; s += S.linie([x - 0.18, 0, -0.45], [x + 0.18, 0, -0.45], "ld thin", "bb-pf") + S.linie([x - 0.18, 0, -0.45], [x + 0.12, 0, -0.45], "ld thin", "bb-pf"); }
  s += S.text([c.leff * 0.5, 0, -0.45], `${bbIdx("m", "T,d")}= ${fmt(c.mT, 2)} kNm/m`, "lt " + (k("qk") || k("lk") || k("hp")), "middle", 0, 18, OBL_ROT);
  s += S.kette([[0, 0, -1.0], [c.leff, 0, -1.0]], [`${bbIdx("l", "eff")}= ${fmt(c.leff, 2)} m`], [k("l")], true, OBL_ROT);

  /* untere Reihe: Baustoffe, Lasten, Schnitt durch Balken und Platte */
  s += `<g transform="translate(0 290)">`;
  s += `<text x="20" y="40" class="in2 ${k("beton") || k("xk")}">Beton: ${esc(c.beton)}; ${esc(c.xk)}</text>
    <text x="20" y="62" class="in2">Bewehrung: B500 B</text>
    <text x="20" y="98" class="in2">Lasten Platte:</text>
    <text x="20" y="120" class="in2 gr ${k("hp")}">g<tspan class="ix" dy="4">k</tspan><tspan dy="-4"> = ${fmt(c.gkp, 2)} kN/m²</tspan></text>
    <text x="20" y="142" class="in2 gr ${k("qk")}">q<tspan class="ix" dy="4">k</tspan><tspan dy="-4"> = ${fmt(c.qk, 1)} kN/m²</tspan></text>
    <text x="20" y="178" class="in2">lichte Weite:</text>
    <text x="20" y="200" class="in2 gr ${k("l")}">l = ${fmt(c.l, 2)} m</text>`;
  const sc = 200, x0 = 300, y0 = 82, wb = b * sc, hb = h * sc, wp = lk * sc, hpp = hp * sc;
  s += bbU(x0 - 20, 30, "Querschnitt am Auflager");
  const umriss = `M${x0} ${y0}h${wb + wp}v${hpp}h${-wp}v${hb - hpp}h${-wb}z`;
  s += `<path class="conc" d="${umriss}"/><path class="hatchd" d="${umriss}"/>`;
  s += `<rect class="conc" x="${x0 - 12}" y="${y0 + hb}" width="${wb + 24}" height="60" fill="url(#bb-hatch)"/><text x="${x0 + wb / 2}" y="${y0 + hb + 50}" text-anchor="middle" class="lbl2">Wand</text>`;
  for (let i = 0; i <= 6; i++){ const x = x0 + wb + 6 + i * (wp - 12) / 6; s += bbPfeil(x, y0 - 34, x, y0 - 3, "ld thin"); }
  s += `<line class="ld thin" x1="${x0 + wb + 6}" y1="${y0 - 34}" x2="${x0 + wb + wp - 6}" y2="${y0 - 34}"/>`;
  s += `<text x="${x0 + wb + wp / 2}" y="${y0 - 40}" text-anchor="middle" class="in2 gr ${k("qk") || k("hp")}">g<tspan class="ix" dy="4">k</tspan><tspan dy="-4"> + q</tspan><tspan class="ix" dy="4">k</tspan></text>`;
  s += bbKette([x0, x0 + wb, x0 + wb + wp], y0 + hb + 78, [bbCm(b), bbCm(lk)], true, [k("b"), k("lk")]);
  s += bbKette([y0, y0 + hb], x0 - 24, [bbCm(h)], false, [k("h")]);
  s += bbKette([y0, y0 + hpp], x0 + wb + wp + 18, [bbCm(hp)], false, [k("hp")]);
  return s + `</g>`;
}

/* Kragarm mit Endausleger (Hausübung 6a, sinngemäß): Isometrie, statisches System, Baustoffe/Lasten, Schnitte 1–1 und 2–2 */
function svgKragarm(c, chg){
  const k = id => chg(id) ? "chg" : "";
  const lK = c.lK, lE = c.lE, a = c.a, bK = c.bK, bE = c.bE, h = c.h;
  let s = BB_DEFS;
  const mass = (S, p, q, t, cls, dx = 0, dy = 14) => {      /* einfache Maßlinie zwischen zwei Raumpunkten */
    const [x1, y1] = S.P(...p), [x2, y2] = S.P(...q);
    return `<line class="dim" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" marker-start="url(#bb-ms)" marker-end="url(#bb-ms)"/>`
      + `<text x="${(x1 + x2) / 2 + dx}" y="${(y1 + y2) / 2 + dy}" text-anchor="middle" class="dl ${cls}">${t}</text>`;
  };

  /* Isometrie wie im Aufgabenblatt: Wand oben links, Kragbalken schräg nach vorn, Endausleger nach rechts */
  const yQ = bE / 2, xQ = bK + lE - a;
  const I = isoRaum([[-0.7, lK + 0.4, h + 1.0], [bK + 0.7, lK + 0.4, -1.0], [bK + lE, 0, h + 1.3], [0, 0, -0.2], [bK + lE, bE, -0.2]], [12, 36, 432, 236]);
  s += bbU(40, 24, "Isometrie");
  s += I.quader(-0.7, bK + 0.7, lK, lK + 0.4, -1.0, h + 1.0, "sup");
  s += I.quader(bK, bK + lE, 0, bE, 0, h, "neben");
  s += I.quader(0, bK, 0, lK, 0, h, "haupt");
  s += I.linie([xQ, yQ, h + 1.2], [xQ, yQ, h + 0.03], "ld big", "bb-pf");
  s += I.text([xQ, yQ, h + 1.2], bbIdx("Q", "k") + `= ${fmt(c.Qk, 0)} kN`, "lt " + k("Qk"), "start", 6, 4);
  s += I.text([0, lK * 0.5, h * 0.3], "Kragbalken", "lbl2", "end", -8, 4);
  s += I.text([bK + lE * 0.5, 0, h * 0.25], "Endausleger", "lbl2", "start", 0, 18);
  s += I.text([-0.7, lK + 0.4, h + 1.0], "Wand", "lbl2", "start", 4, -6);

  /* statisches System */
  const S = isoRaum([[0, lK + 0.2, 1.3], [0, lK + 0.2, -0.9], [lE, 0, 1.6], [lE, 0, -0.9], [0, -0.4, -0.9], [lE + 0.2, 0, 0]], [458, 34, 250, 236]);
  s += bbU(704, 24, "statisches System", "end");
  s += S.linie([0, lK, 0], [0, 0, 0], "bb-beam") + S.linie([0, 0, 0], [lE, 0, 0], "bb-beam");
  const [wx, wy] = S.P(0, lK, 0);
  s += `<rect x="${wx - 9}" y="${wy - 22}" width="9" height="44" fill="url(#bb-hatch)"/><line class="bb-gnd" x1="${wx}" y1="${wy - 22}" x2="${wx}" y2="${wy + 22}"/>`;
  for (let i = 0; i <= 8; i++){ const y = 0.1 + i * (lK - 0.2) / 8; s += S.linie([0, y, 0.6], [0, y, 0.04], "ld thin", "bb-pf"); }
  s += S.linie([0, 0.1, 0.6], [0, lK - 0.1, 0.6], "ld thin");
  for (let i = 0; i <= 7; i++){ const x = 0.1 + i * (lE - 0.2) / 7; s += S.linie([x, 0, 0.6], [x, 0, 0.04], "ld thin", "bb-pf"); }
  s += S.linie([0.1, 0, 0.6], [lE - 0.1, 0, 0.6], "ld thin");
  s += S.linie([lE - a, 0, 1.45], [lE - a, 0, 0.04], "ld big", "bb-pf") + S.text([lE - a, 0, 1.45], bbIdx("Q", "Ed"), "lt " + k("Qk"), "start", 6, 4);
  s += S.text([0, lK * 0.6, 0.6], bbIdx("g", "Ed,K"), "lt " + (k("bK") || k("h")), "end", -4, -4);
  s += S.text([lE * 0.35, 0, 0.6], bbIdx("g", "Ed,E"), "lt " + (k("bE") || k("h")), "middle", 0, -8);
  s += mass(S, [0, 0, -0.6], [0, lK, -0.6], fmt(lK, 2), k("lK"), -18, 8);
  s += mass(S, [0, 0, -0.6], [lE - a, 0, -0.6], fmt(lE - a, 2), k("lE") || k("a"), 6, 16);
  s += mass(S, [lE - a, 0, -0.6], [lE, 0, -0.6], fmt(a, 2), k("a"), 6, 16);

  /* untere Reihe: Baustoffe und Lasten, Schnitte 1–1 (Kragbalken) und 2–2 (Endausleger), Maße in cm */
  s += `<g transform="translate(0 290)">`;
  s += `<text x="20" y="40" class="in2 ${k("beton") || k("xk")}">Beton: ${esc(c.beton)}; ${esc(c.xk)}</text>
    <text x="20" y="62" class="in2">Bewehrung: B500</text>
    <text x="20" y="98" class="in2">Bemessungslasten:</text>
    <text x="20" y="120" class="in2 gr ${k("bE") || k("h")}">g<tspan class="ix" dy="4">Ed,E</tspan><tspan dy="-4"> = ${fmt(c.gE, 2)} kN/m</tspan></text>
    <text x="20" y="142" class="in2 gr ${k("bK") || k("h")}">g<tspan class="ix" dy="4">Ed,K</tspan><tspan dy="-4"> = ${fmt(c.gK, 2)} kN/m</tspan></text>
    <text x="20" y="164" class="in2 gr ${k("Qk")}">Q<tspan class="ix" dy="4">Ed</tspan><tspan dy="-4"> = ${fmt(c.QEd, 1)} kN</tspan></text>`;
  const sc = 180 / 0.88, y0 = 60, hh = h * sc;
  const q1 = 300, q2 = 300 + bK * sc + 110;
  s += bbU(q1 - 10, 30, "Schnitt 1–1 (Kragbalken)") + bbU(q2 - 10, 30, "Schnitt 2–2 (Endausleger)");
  for (const [x, bw, kb] of [[q1, bK * sc, "bK"], [q2, bE * sc, "bE"]]){
    s += `<rect class="conc" x="${x}" y="${y0}" width="${bw}" height="${hh}"/><rect class="hatchd" x="${x}" y="${y0}" width="${bw}" height="${hh}"/>`;
    s += bbKette([x, x + bw], y0 + hh + 18, [bbCm(kb === "bK" ? bK : bE)], true, [k(kb)]);
    s += bbKette([y0, y0 + hh], x + bw + 16, [bbCm(h)], false, [k("h")]);
  }
  return s + `</g>`;
}

/* Kragbalken mit Querbalken (Klausur 2018, Aufg. 3, sinngemäß): Isometrie, statisches System, Lasten, Schnitte 1–1 und 2–2 */
function svgKreuz(c, chg){
  const k = id => chg(id) ? "chg" : "";
  const L = c.L, l1 = c.l1, l2 = c.l2, a1 = c.a1, a2 = c.a2, b1 = c.b1, b2 = c.b2, h = c.h;
  let s = BB_DEFS;
  const mass = (S, p, q, t, cls, dx = 0, dy = 14) => {
    const [x1, y1] = S.P(...p), [x2, y2] = S.P(...q);
    return `<line class="dim" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" marker-start="url(#bb-ms)" marker-end="url(#bb-ms)"/>`
      + `<text x="${(x1 + x2) / 2 + dx}" y="${(y1 + y2) / 2 + dy}" text-anchor="middle" class="dl ${cls}">${t}</text>`;
  };

  /* Isometrie */
  const I = isoRaum([[-0.7, L + 0.4, h + 0.6], [0.7, L + 0.4, -0.8], [-a1, l2, h + 1.3], [a2, l2, h], [0, 0, h + 1.3], [0, 0, -0.2], [-a1, l2, -0.2]], [20, 44, 420, 226]);
  s += bbU(250, 24, "Isometrie");
  s += I.quader(-0.7, 0.7, L, L + 0.4, -0.8, h + 0.6, "sup");
  s += I.quader(b2 / 2, a2, l2 - b1 / 2, l2 + b1 / 2, 0, h, "neben");
  s += I.quader(-b2 / 2, b2 / 2, l2 + b1 / 2, L, 0, h, "haupt");
  s += I.quader(-b2 / 2, b2 / 2, 0, l2 + b1 / 2, 0, h, "haupt");
  s += I.quader(-a1, -b2 / 2, l2 - b1 / 2, l2 + b1 / 2, 0, h, "neben");
  s += I.linie([-a1 + 0.08, l2, h + 1.2], [-a1 + 0.08, l2, h + 0.03], "ld big", "bb-pf") + I.text([-a1 + 0.08, l2, h + 1.2], bbIdx("Q", "k1") + `= ${fmt(c.Qk1, 0)} kN`, "lt " + k("Qk1"), "start", 6, 4);
  s += I.linie([0, 0.08, h + 1.2], [0, 0.08, h + 0.03], "ld big", "bb-pf") + I.text([0, 0.08, h + 1.2], bbIdx("Q", "k2") + `= ${fmt(c.Qk2, 0)} kN`, "lt " + k("Qk2"), "start", 6, 4);
  s += I.text([-b2 / 2, L - 0.4, 0], "Stab 2", "lbl2", "start", 4, 18);
  s += I.text([a2 * 0.6, l2 - b1 / 2, h * 0.3], "Stab 1", "lbl2", "start", 6, 14);
  s += I.text([-0.7, L, -0.8], "Wand", "lbl2", "end", -4, 0);

  /* statisches System */
  const S = isoRaum([[0, L + 0.2, 1.8], [0, L + 0.2, -0.6], [-a1, l2, 1.8], [-a1, l2, -0.6], [a2, l2, 0], [0, -0.3, 1.8], [0, -0.3, -0.6]], [450, 40, 262, 236]);
  s += bbU(704, 24, "statisches System", "end");
  s += S.linie([0, L, 0], [0, 0, 0], "bb-beam") + S.linie([-a1, l2, 0], [a2, l2, 0], "bb-beam");
  const [wx, wy] = S.P(0, L, 0);
  s += `<rect x="${wx - 9}" y="${wy - 22}" width="9" height="44" fill="url(#bb-hatch)"/><line class="bb-gnd" x1="${wx}" y1="${wy - 22}" x2="${wx}" y2="${wy + 22}"/>`;
  for (let i = 0; i <= 10; i++){ const y = 0.1 + i * (L - 0.2) / 10; s += S.linie([0, y, 0.6], [0, y, 0.04], "ld thin", "bb-pf"); }
  s += S.linie([0, 0.1, 0.6], [0, L - 0.1, 0.6], "ld thin");
  for (let i = 0; i <= 10; i++){ const x = -a1 + 0.1 + i * (a1 + a2 - 0.2) / 10; s += S.linie([x, l2, 0.6], [x, l2, 0.04], "ld thin", "bb-pf"); }
  s += S.linie([-a1 + 0.1, l2, 0.6], [a2 - 0.1, l2, 0.6], "ld thin");
  s += S.linie([-a1, l2, 1.5], [-a1, l2, 0.04], "ld big", "bb-pf") + S.text([-a1, l2, 1.5], bbIdx("Q", "d1"), "lt " + k("Qk1"), "middle", 0, -6);
  s += S.linie([0, 0, 1.5], [0, 0, 0.04], "ld big", "bb-pf") + S.text([0, 0, 1.5], bbIdx("Q", "d2"), "lt " + k("Qk2"), "middle", 0, -6);
  const lab = (p, t, cls, an, dx, dy) => S.text(p, t, "dl " + cls, an, dx, dy);
  s += lab([0, (l2 + L) / 2, 0], `l<tspan class="ix" dy="4">1</tspan><tspan dy="-4"> = ${fmt(l1, 2)}</tspan>`, k("l1"), "end", -10, 14);
  s += lab([0, l2 * 0.55, 0], `l<tspan class="ix" dy="4">2</tspan><tspan dy="-4"> = ${fmt(l2, 2)}</tspan>`, k("l2"), "end", -6, 24);
  s += lab([-a1, l2, 0], `a<tspan class="ix" dy="4">1</tspan><tspan dy="-4"> = ${fmt(a1, 2)}</tspan>`, k("a1"), "end", -10, 2);
  s += lab([a2 * 0.5, l2, 0.6], `a<tspan class="ix" dy="4">2</tspan><tspan dy="-4"> = ${fmt(a2, 2)}</tspan>`, k("a2"), "end", -4, -8);

  /* untere Reihe */
  s += `<g transform="translate(0 290)">`;
  s += `<text x="20" y="40" class="in2 ${k("beton") || k("xk")}">Beton: ${esc(c.beton)}; ${esc(c.xk)}</text>
    <text x="20" y="62" class="in2">Bewehrung: B500</text>
    <text x="20" y="98" class="in2">Bemessungslasten:</text>
    <text x="20" y="120" class="in2 gr ${k("b1") || k("h")}">g<tspan class="ix" dy="4">d1</tspan><tspan dy="-4"> = ${fmt(c.g1, 2)} kN/m</tspan></text>
    <text x="20" y="142" class="in2 gr ${k("b2") || k("h")}">g<tspan class="ix" dy="4">d2</tspan><tspan dy="-4"> = ${fmt(c.g2, 2)} kN/m</tspan></text>
    <text x="20" y="164" class="in2 gr ${k("Qk1")}">Q<tspan class="ix" dy="4">d1</tspan><tspan dy="-4"> = ${fmt(c.Q1, 0)} kN</tspan></text>
    <text x="20" y="186" class="in2 gr ${k("Qk2")}">Q<tspan class="ix" dy="4">d2</tspan><tspan dy="-4"> = ${fmt(c.Q2, 0)} kN</tspan></text>`;
  const sc = 180 / 0.66, y0 = 60, hh = h * sc;
  const q1 = 300, q2 = 300 + b1 * sc + 110;
  s += bbU(q1 - 10, 30, "Schnitt 1–1 (Stab 1)") + bbU(q2 - 10, 30, "Schnitt 2–2 (Stab 2)");
  for (const [x, bw, kb] of [[q1, b1 * sc, "b1"], [q2, b2 * sc, "b2"]]){
    s += `<rect class="conc" x="${x}" y="${y0}" width="${bw}" height="${hh}"/><rect class="hatchd" x="${x}" y="${y0}" width="${bw}" height="${hh}"/>`;
    s += bbKette([x, x + bw], y0 + hh + 18, [bbCm(kb === "b1" ? b1 : b2)], true, [k(kb)]);
    s += bbKette([y0, y0 + hh], x + bw + 16, [bbCm(h)], false, [k("h")]);
  }
  return s + `</g>`;
}

/* Plattenbalkenbrücke (DBV Beispiel 13, sinngemäß): Regelquerschnitt, Ersatzhohlkasten des Stegs, Vorgaben, Längssystem */
function svgBruecke(c, chg){
  const k = id => chg(id) ? "chg" : "";
  const bo = c.bo, bu = c.bu, h = c.h, tef = c.tef;
  let s = BB_DEFS;
  /* Regelquerschnitt (Maße wie im Buch, betrachteter Steg mit den Reglerwerten) */
  const sq = 390 / 14.05, X = 34, Y = 70, Q = (x, y) => `${(X + x * sq).toFixed(1)},${(Y + y * sq).toFixed(1)}`;
  const cL = 3.625, cR = 10.575;
  const qs = [[0, 0], [14.05, 0], [14.05, 0.25], [cR + bo / 2, 0.45], [cR + bu / 2, h], [cR - bu / 2, h], [cR - bo / 2, 0.45], [7.025, 0.30],
              [cL + bo / 2, 0.45], [cL + bu / 2, h], [cL - bu / 2, h], [cL - bo / 2, 0.45], [0, 0.25]];
  s += bbU(24, 24, "Regelquerschnitt");
  s += `<polygon class="conc" points="${qs.map(q => Q(...q)).join(" ")}"/><polygon class="hatchd" points="${qs.map(q => Q(...q)).join(" ")}"/>`;
  s += `<polygon class="sg neg" points="${[[cL - bo / 2, 0], [cL + bo / 2, 0], [cL + bu / 2, h], [cL - bu / 2, h]].map(q => Q(...q)).join(" ")}" opacity="0.55"/>`;
  s += `<text x="${X + cL * sq}" y="${Y + (h + 0.6) * sq}" text-anchor="middle" class="lbl2">Steg Nord (betrachtet)</text>`;
  s += bbKette([X, X + 14.05 * sq], Y - 18, ["14,05"], true);
  s += bbKette([Y, Y + h * sq], X - 10, [bbCm(h)], false, [k("h")]);
  for (let i = 0; i < 9; i++){ const x = X + (cL - 0.43 + i * 0.107) * sq, y = Y + (h - 0.35) * sq; s += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="1.8" class="ah"/>`; }

  /* Ersatzhohlkasten des Stegs */
  const sk = Math.min(230 / bo, 185 / h), ox = 560, oy = 58, P = (x, y) => [ox + x * sk, oy + y * sk];
  const pt = a => a.map(q => P(...q).map(v => v.toFixed(1)).join(",")).join(" ");
  const mo = (bo - tef) / 2, mu = (bu - tef) / 2, yt = tef / 2, yb = h - tef / 2;
  s += bbU(704, 24, "Ersatzhohlkasten", "end");
  s += `<polygon class="conc" points="${pt([[-bo / 2, 0], [bo / 2, 0], [bu / 2, h], [-bu / 2, h]])}"/>`;
  s += `<polygon class="sg pos" points="${pt([[-mo, yt], [mo, yt], [mu, yb], [-mu, yb]])}"/>`;
  s += `<polygon class="dim" fill="none" stroke-dasharray="5 3" points="${pt([[-bo / 2 + tef, tef], [bo / 2 - tef, tef], [bu / 2 - tef, h - tef], [-bu / 2 + tef, h - tef]])}"/>`;
  const [ax, ay] = P(0, h / 2);
  s += `<text x="${ax}" y="${ay + 5}" text-anchor="middle" class="sgv pos">A<tspan class="ix" dy="4">k</tspan><tspan dy="-4"> = ${fmt(c.Ak, 2)} m²</tspan></text>`;
  const [l1x, l1y] = P(-bo / 2, 0), [l2x] = P(bo / 2, 0), [u1x, u1y] = P(-bu / 2, h), [u2x] = P(bu / 2, h);
  s += bbKette([l1x, l2x], l1y - 14, [bbCm(bo)], true, [k("bo")]) + bbKette([u1x, u2x], u1y + 18, [bbCm(bu)], true, [k("bu")]);
  const [z1x, z1y] = P(mo, yt), [, z2y] = P(mu, yb);
  s += bbKette([z1y, z2y], l2x + 18, [bbCm(c.zi)], false);
  const [tx, ty] = P(bu / 2 - tef / 2, h * 0.8);
  s += `<text x="${tx - 6}" y="${ty}" text-anchor="end" class="dl">t<tspan class="ix" dy="4">ef</tspan><tspan dy="-4"> = ${fmt(tef * 100, 0)} cm</tspan></text>`;

  /* untere Reihe: Vorgaben und Längssystem */
  s += `<g transform="translate(0 290)">`;
  s += `<text x="20" y="34" class="in2 ${k("beton")}">Beton: ${esc(c.beton)}</text>
    <text x="20" y="56" class="in2">Bewehrung: B500, Spannglieder im Verbund</text>
    <text x="20" y="90" class="in2">Bemessungswerte an der Innenstütze:</text>
    <text x="20" y="112" class="in2 gr ${k("TEd")}">T<tspan class="ix" dy="4">Ed</tspan><tspan dy="-4"> = ${fmt(c.TEd, 0)} kNm</tspan></text>
    <text x="20" y="134" class="in2 gr ${k("VEd")}">V<tspan class="ix" dy="4">Ed</tspan><tspan dy="-4"> = ${fmt(c.VEd, 0)} kN (Auflagermitte)</tspan></text>
    <text x="20" y="156" class="in2 gr ${k("VEdr")}">V<tspan class="ix" dy="4">Ed,red</tspan><tspan dy="-4"> = ${fmt(c.VEdr, 0)} kN (im Abstand d)</tspan></text>
    <text x="20" y="178" class="in2 gr ${k("NEd")}">N<tspan class="ix" dy="4">Ed</tspan><tspan dy="-4"> = ${fmt(c.NEd, 0)} kN → σ</tspan><tspan class="ix" dy="4">cp</tspan><tspan dy="-4"> = ${fmt(c.scp, 2)} MN/m²</tspan></text>
    <text x="20" y="200" class="in2 gr ${k("z")}">z = ${fmt(c.z, 3)} m</text>`;
  const fx = 380, fy = 120, fs = 320 / 210, felder = [25, 32, 32, 32, 32, 32, 25];
  s += bbU(fx, 40, "Längssystem (Siebenfeldträger)");
  s += `<line class="bb-beam" x1="${fx}" y1="${fy}" x2="${fx + 210 * fs}" y2="${fy}"/>`;
  let xa = 0;
  [0, ...felder].forEach((f, i) => { xa += f; const x = fx + xa * fs; s += `<path class="bb-sup" d="M${x} ${fy}l-6 10h12z"/>`; });
  xa = 0;
  felder.forEach(f => { s += `<text x="${fx + (xa + f / 2) * fs}" y="${fy + 28}" text-anchor="middle" class="dl">${f}</text>`; xa += f; });
  const xs = fx + 57 * fs;
  s += bbPfeil(xs, fy - 40, xs, fy - 6, "ld") + `<text x="${xs}" y="${fy - 46}" text-anchor="middle" class="lbl2">Innenstütze</text>`;
  s += `<text x="${fx + 105 * fs}" y="${fy + 48}" text-anchor="middle" class="dl">L = 210 m</text>`;
  return s + `</g>`;
}

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
  if (B.system === "bruecke"){
    /* 1 Schubfluss im Ersatzhohlkasten, 2 Wandschubkräfte, 3 Interaktionsdiagramm */
    const tef = c.tef, bo = c.bo, bu = c.bu, h = c.h;
    const sk = Math.min(170 / bo, 140 / h), cx = 124, y0 = 52;
    const P = (x, y) => [cx + x * sk, y0 + y * sk];                 /* x ab Stegmitte, y ab Oberkante */
    const mo = (bo - tef) / 2, mu = (bu - tef) / 2, yt = tef / 2, yb = h - tef / 2;
    const pt = a => a.map(q => P(...q).map(v => v.toFixed(1)).join(",")).join(" ");
    s += `<text x="14" y="20" class="ttl-u">Schubfluss aus Torsion</text><text x="14" y="36" class="dl">q = T/(2·A_k)</text>`;
    s += `<polygon class="conc" points="${pt([[-bo / 2, 0], [bo / 2, 0], [bu / 2, h], [-bu / 2, h]])}"/>`;
    s += `<polygon class="sg neg" points="${pt([[-mo, yt], [mo, yt], [mu, yb], [-mu, yb]])}"/>`;
    const pf = (a, b) => { const [x1, y1] = P(...a), [x2, y2] = P(...b); return bbPfeil(x1, y1, x2, y2, "ld"); };
    s += pf([-mo * 0.5, yt], [mo * 0.5, yt]) + pf([(mo + mu) / 2, yt + (yb - yt) * 0.25], [(mo + mu) / 2, yt + (yb - yt) * 0.75])
       + pf([mu * 0.5, yb], [-mu * 0.5, yb]) + pf([-(mo + mu) / 2, yt + (yb - yt) * 0.75], [-(mo + mu) / 2, yt + (yb - yt) * 0.25]);
    const [qx, qy] = P(0, h / 2);
    s += `<text x="${qx}" y="${qy + 4}" text-anchor="middle" class="sgv neg">q = ${fmt(c.TEd / (2 * c.Ak), 0)} kN/m</text>`;
    /* Wandschubkräfte */
    const x2 = 260, wB = 30, H0 = 186, top = 56, vmax = Math.max(c.VTV, c.VRdcc * 1000) * 1.1, hb = v => v / vmax * (H0 - top);
    const VV = c.VEd * c.tef / c.bwn;
    s += `<text x="${x2}" y="20" class="ttl-u">Schubkraft je Wand</text><text x="${x2}" y="36" class="dl">[kN]</text>`;
    [["T", c.VT, "neg"], ["V", VV, "pos"], ["T+V", c.VTV, "neg"]].forEach(([l, v, cls], i) => {
      const x = x2 + 16 + i * (wB + 16);
      s += `<rect class="sg ${cls}" x="${x}" y="${H0 - hb(v)}" width="${wB}" height="${hb(v)}"/>`
        + `<text x="${x + wB / 2}" y="${H0 - hb(v) - 5}" text-anchor="middle" class="sgv ${cls}">${fmt(v, 0)}</text>`
        + `<text x="${x + wB / 2}" y="${H0 + 15}" text-anchor="middle" class="dl">V<tspan class="ix" dy="3">Ed,${l}</tspan></text>`;
    });
    const yR = H0 - hb(c.VRdcc * 1000);
    s += `<line class="bb-gnd" x1="${x2 + 10}" y1="${H0}" x2="${x2 + 160}" y2="${H0}"/><line class="dim" x1="${x2 + 10}" y1="${yR}" x2="${x2 + 160}" y2="${yR}" stroke-dasharray="4 3"/>`
      + `<text x="${x2 + 164}" y="${yR + 4}" class="dl">V<tspan class="ix" dy="3">Rd,cc</tspan><tspan dy="-3"> = ${fmt(c.VRdcc * 1000, 0)}</tspan></text>`;
    /* Interaktion */
    const x3 = 500, ox = x3 + 30, oy = 190, R = 140;
    s += `<text x="${x3}" y="20" class="ttl-u">Interaktion</text><text x="${x3}" y="36" class="dl">(T/T<tspan class="ix" dy="3">Rd</tspan><tspan dy="-3">)² + (V/V</tspan><tspan class="ix" dy="3">Rd</tspan><tspan dy="-3">)² ≤ 1</tspan></text>`;
    s += `<path class="sg pos" d="M${ox} ${oy}h${R}A${R} ${R} 0 0 0 ${ox} ${oy - R}z"/>`;
    s += `<line class="bb-gnd" x1="${ox}" y1="${oy}" x2="${ox + R + 14}" y2="${oy}"/><line class="bb-gnd" x1="${ox}" y1="${oy}" x2="${ox}" y2="${oy - R - 10}"/>`;
    s += `<text x="${ox + R + 14}" y="${oy + 14}" text-anchor="end" class="dl">V/V<tspan class="ix" dy="3">Rd,max</tspan></text><text x="${ox + 4}" y="${oy - R - 2}" class="dl">T/T<tspan class="ix" dy="3">Rd,max</tspan></text>`;
    const px = ox + Math.min(1.2, c.VEd / c.VRd) * R, py = oy - Math.min(1.2, c.TEd / c.TRd) * R;
    s += `<circle cx="${px}" cy="${py}" r="5" class="${c.eta <= 1 ? "pt-ok" : "pt-bad"}" fill="currentColor"/><text x="${px + 8}" y="${py - 6}" class="sgv ${c.eta <= 1 ? "pos" : "neg"}">${fmt(c.eta, 2)}</text>`;
    return s;
  }
  if (B.system === "kreuz"){
    /* Stab 2 entlang y (Spitze y = 0, Wand y = L), Stab 1 entlang x bei y = l_2: kurzer Arm −x, langer Arm +x */
    const L = c.L, l2 = c.l2, a1 = c.a1, a2 = c.a2, g1 = c.g1, g2 = c.g2;
    const V2 = y => c.Q2 + g2 * y + (y > l2 + 1e-9 ? c.F1 : 0), M2 = y => -c.Q2 * y - g2 * y * y / 2 - c.F1 * Math.max(0, y - l2);
    const N = 50, ys = [], s1 = [], s2 = [];
    for (let i = 0; i <= N; i++){ ys.push(i / N * L); s1.push(i / N * a1); s2.push(i / N * a2); }
    const tafel = (x0, titel, einheit, fn, max) => {
      const o = 0.5 * Math.max(L, a1 + a2);
      const S = isoRaum([[0, 0, o], [0, 0, -o], [0, L + 0.3, o], [0, L + 0.3, -o], [-a1, l2, o], [-a1, l2, -o], [a2, l2, o], [a2, l2, -o]], [x0 + 6, 44, 210, 156]);
      let t = `<text x="${x0}" y="20" class="ttl-u">${titel}</text><text x="${x0}" y="36" class="dl">[${einheit}]</text>`;
      t += fn(S, o / max) + S.linie([0, L, 0], [0, 0, 0], "bb-beam") + S.linie([-a1, l2, 0], [a2, l2, 0], "bb-beam");
      const [wx, wy] = S.P(0, L, 0);
      return t + `<rect x="${wx - 4}" y="${wy - 16}" width="7" height="26" fill="url(#bb-hatch)"/><line class="bb-gnd" x1="${wx - 4}" y1="${wy - 16}" x2="${wx - 4}" y2="${wy + 10}"/>`;
    };
    const f2 = (S, f, k, cls) => S.poly([[0, 0, 0], ...ys.map(y => [0, y, f(y) * k]), [0, L, 0]], "sg " + cls);
    const fa = (S, f, k, cls, kurz) => { const arr = kurz ? s1 : s2, aa = kurz ? a1 : a2, sg = kurz ? -1 : 1;
      return S.poly([[sg * aa, l2, 0], ...arr.map(q => [sg * (aa - q), l2, f(q) * k]), [0, l2, 0]], "sg " + cls); };
    const w = (S, p, t, cls, an = "start", dx = 4, dy = 0) => S.text(p, t, "sgv " + cls, an, dx, dy);
    const mV = Math.max(c.V, 1), mM = Math.max(c.M, 1), mT = Math.max(c.T, 1);
    s += tafel(14, "Querkraft", "kN", (S, k) => f2(S, y => -V2(y), k, "pos") + fa(S, q => -(c.Q1 + g1 * q), k, "pos", true) + fa(S, q => -g1 * q, k, "pos", false)
      + w(S, [0, L, -c.V * k], fmt(c.V, 0), "pos", "end", -6, 4), mV);
    s += tafel(254, "Biegemoment", "kNm", (S, k) => f2(S, y => -M2(y), k, "neg") + fa(S, q => c.Q1 * q + g1 * q * q / 2, k, "neg", true) + fa(S, q => g1 * q * q / 2, k, "neg", false)
      + w(S, [0, L, c.M * k], fmt(-c.M, 0), "neg", "end", -6, 0), mM);
    s += tafel(494, "Torsionsmoment", "kNm", (S, k) => S.poly([[0, l2, 0], [0, l2, c.T * k], [0, L, c.T * k], [0, L, 0]], "sg neg")
      + w(S, [0, (l2 + L) / 2, c.T * k], fmt(-c.T, 1), "neg", "end", -6, -4), mT);
    return s;
  }
  if (B.system === "kragarm"){
    /* Isometrie wie im Aufgabenblatt: Kragbalken entlang y (Wand bei y = l_K), Endausleger entlang x */
    const lK = c.lK, lE = c.lE, a = c.a, gE = c.gE, gK = c.gK, Q = c.QEd;
    const VEnd = q => gE * q + (q > a + 1e-9 ? Q : 0), MEnd = q => -gE * q * q / 2 - Q * Math.max(0, q - a);
    const VKr = y => c.VE + gK * y, MKr = y => -gK * y * y / 2 - c.VE * y;
    const N = 40, qE = [], yK = [];
    for (let i = 0; i <= N; i++){ qE.push(i / N * lE); yK.push(i / N * lK); }
    const tafel = (x0, titel, einheit, fn, max) => {
      const o = 0.5 * Math.max(lK, lE);
      const S = isoRaum([[0, 0, o], [0, 0, -o], [0, lK + 0.3, o], [0, lK + 0.3, -o], [lE, 0, o], [lE, 0, -o]], [x0 + 6, 44, 210, 156]);
      let t = `<text x="${x0}" y="20" class="ttl-u">${titel}</text><text x="${x0}" y="36" class="dl">[${einheit}]</text>`;
      t += fn(S, o / max) + S.linie([0, lK, 0], [0, 0, 0], "bb-beam") + S.linie([0, 0, 0], [lE, 0, 0], "bb-beam");
      const [wx, wy] = S.P(0, lK, 0);
      return t + `<rect x="${wx - 4}" y="${wy - 16}" width="7" height="26" fill="url(#bb-hatch)"/><line class="bb-gnd" x1="${wx - 4}" y1="${wy - 16}" x2="${wx - 4}" y2="${wy + 10}"/>`;
    };
    const fE = (S, f, k, cls) => S.poly([[lE, 0, 0], ...qE.map(q => [lE - q, 0, f(q) * k]), [0, 0, 0]], "sg " + cls);
    const fK = (S, f, k, cls) => S.poly([[0, 0, 0], ...yK.map(y => [0, y, f(y) * k]), [0, lK, 0]], "sg " + cls);
    const w = (S, p, t, cls, an = "start", dx = 4, dy = 0) => S.text(p, t, "sgv " + cls, an, dx, dy);
    const mV = Math.max(c.VK, 1), mM = Math.max(c.MK, Math.abs(c.ME), 1), mT = Math.max(c.T, 1);
    /* Querkraft positiv unten (blau); Momente negativ oben (rot) */
    s += tafel(14, "Querkraft", "kN", (S, k) => fE(S, q => -VEnd(q), k, "pos") + fK(S, y => -VKr(y), k, "pos")
      + w(S, [0, 0, -c.VE * k], fmt(c.VE, 1), "pos", "start", 6, 12) + w(S, [0, lK, -c.VK * k], fmt(c.VK, 1), "pos", "end", -6, 4), mV);
    s += tafel(254, "Biegemoment", "kNm", (S, k) => fE(S, q => -MEnd(q), k, "neg") + fK(S, y => -MKr(y), k, "neg")
      + w(S, [lE * 0.15, 0, -MEnd(lE * 0.85) * k], fmt(c.ME, 1), "neg", "start", 4, -8) + w(S, [0, lK, c.MK * k], fmt(-c.MK, 1), "neg", "end", -6, 0), mM);
    s += tafel(494, "Torsionsmoment", "kNm", (S, k) => S.poly([[0, 0, 0], [0, 0, c.T * k], [0, lK, c.T * k], [0, lK, 0]], "sg neg")
      + w(S, [0, lK * 0.5, c.T * k], fmt(-c.T, 1), "neg", "end", -6, -4), mT);
    return s;
  }
  if (B.system === "balken"){
    const l = c.leff, q = c.gd + c.qd, xs = []; for (let i = 0; i <= 40; i++) xs.push(i / 40 * l);
    const tafel = (x0, titel, einheit, fn, max) => {
      const o = 0.32 * l, S = oblRaum([[0, 0, o * 1.15], [0, 0, -o * 1.15], [l, 0, o * 1.15], [l, 0, -o * 1.15]], [x0 + 18, 48, 190, 148]);
      return `<text x="${x0}" y="20" class="ttl-u">${titel}</text><text x="${x0}" y="36" class="dl">[${einheit}]</text>` + fn(S, o / max) + S.linie([0, 0, 0], [l, 0, 0], "bb-beam");
    };
    const fl = (S, pk, cls) => S.poly([[pk[0][0], 0, 0], ...pk.map(([x, v]) => [x, 0, v]), [pk[pk.length - 1][0], 0, 0]], "sg " + cls);
    const w = (S, x, z, t, cls, a = "start", dx = 4, dy = 0) => S.text([x, 0, z], t, "sgv " + cls, a, dx, dy);
    s += tafel(14, "Querkraft", "kN", (S, k) => fl(S, [[0, -c.V * k], [l / 2, 0]], "pos") + fl(S, [[l / 2, 0], [l, c.V * k]], "neg")
      + w(S, 0, -c.V * k, fmt(c.V, 1), "pos", "end", -4, 4) + w(S, l, c.V * k, fmt(-c.V, 1), "neg", "start", 5, 4), c.V);
    s += tafel(254, "Biegemoment", "kNm", (S, k) => fl(S, xs.map(x => [x, -q * x * (l - x) / 2 * k]), "pos")
      + w(S, l / 2, -c.M * k, fmt(c.M, 1), "pos", "middle", 0, 16), c.M);
    s += tafel(494, "Torsionsmoment", "kNm", (S, k) => fl(S, [[0, c.T * k], [l / 2, 0]], "neg") + fl(S, [[l / 2, 0], [l, -c.T * k]], "pos")
      + w(S, 0, c.T * k, fmt(-c.T, 2), "neg", "start", 4, -4) + w(S, l, -c.T * k, fmt(c.T, 2), "pos", "start", 5, 4), c.T);
    return s;
  }
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
