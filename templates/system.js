/* ---------- Statisches System für das Bemessungstool: Eingabe und Darstellung angelehnt an SOFiSTiK ----------
   Texteingabe wie im Teddy (vereinfachte CADINP-Syntax):
     KNOT NR 1 X 0.0 FIX PZMX        Knoten mit Lagerbedingung
     STAB NR 1 KA 1 KE 2             Stab von Knoten KA nach KE
     LF 1 BEZ 'Bemessungslasten'     ab hier Lasten (Bemessungswerte)
     STAB 1,2 TYP PZ P1 25           Streckenlast auf Stäbe [kN/m], TYP MX = Streckentorsion [kNm/m]
     KNOT 2 TYP PZ P1 120            Knotenlast [kN], TYP MX = Torsionsmoment [kNm]
   Gerader Stabzug in X, Z nach unten. Steifigkeitsverfahren je Knoten mit w, φ (Biegung) und ϑ (Torsion),
   konstante Steifigkeiten (EI, GI_T) – damit auch Durchlaufträger und beidseitig eingespannte Systeme. */

const SYS_VORLAGEN = {
  einfeld: {t: "Einfeldträger (Gabellager)", txt:
`$ Einfeldträger mit Gabellagern, Konsollast in Feldmitte
KNOT NR 1 X 0.0 FIX PZMX
KNOT NR 2 X 3.0
KNOT NR 3 X 6.0 FIX PZMX
STAB NR 1 KA 1 KE 2
STAB NR 2 KA 2 KE 3

LF 1 BEZ 'Bemessungslasten'
STAB 1,2 TYP PZ P1 25.0      $ Gleichlast [kN/m]
STAB 1,2 TYP MX P1 2.5       $ Streckentorsion q*e [kNm/m]
KNOT 2 TYP PZ P1 120.0       $ Einzellast [kN]
KNOT 2 TYP MX P1 30.0        $ Einzeltorsion F*e [kNm]`},
  krag: {t: "Kragarm", txt:
`$ Kragarm, links eingespannt
KNOT NR 1 X 0.0 FIX F
KNOT NR 2 X 4.0
STAB NR 1 KA 1 KE 2

LF 1 BEZ 'Bemessungslasten'
STAB 1 TYP PZ P1 20.0
STAB 1 TYP MX P1 3.0
KNOT 2 TYP PZ P1 50.0
KNOT 2 TYP MX P1 15.0`},
  zweifeld: {t: "Zweifeldträger", txt:
`$ Zweifeldträger, alle Lager als Gabellager
KNOT NR 1 X 0.0 FIX PZMX
KNOT NR 2 X 5.0 FIX PZMX
KNOT NR 3 X 10.0 FIX PZMX
STAB NR 1 KA 1 KE 2
STAB NR 2 KA 2 KE 3

LF 1 BEZ 'Bemessungslasten'
STAB 1,2 TYP PZ P1 30.0
STAB 1 TYP MX P1 4.0`},
  buch: {t: "Buchbeispiel 2.6", txt:
`$ Hauptträger aus Finckh, Abschn. 2.6: F = 340 kN mit e = 0,35 m
KNOT NR 1 X 0.0 FIX PZMX
KNOT NR 2 X 2.5
KNOT NR 3 X 5.0 FIX PZMX
STAB NR 1 KA 1 KE 2
STAB NR 2 KA 2 KE 3

LF 1 BEZ 'Bemessungslasten'
STAB 1,2 TYP PZ P1 40.0
KNOT 2 TYP PZ P1 340.0
KNOT 2 TYP MX P1 119.0       $ 340 * 0.35`}
};

/* ---------- Eingabe lesen ---------- */
function sysParse(text){
  const fehler = [], kn = new Map(), st = new Map(), lasten = [];
  let imLF = false, lf = {nr: 1, bez: "Lastfall 1"};
  const zahl = (s, z, was) => { const v = parseFloat(String(s ?? "").replace(",", ".")); if (!Number.isFinite(v)) fehler.push(`Zeile ${z}: ${was} fehlt oder ist keine Zahl`); return v; };
  const liste = s => String(s).split(/[,;]/).flatMap(x => { const m = x.match(/^(\d+)-(\d+)$/); if (m){ const r = []; for (let i = +m[1]; i <= +m[2]; i++) r.push(i); return r; } return x ? [+x] : []; });
  text.split(/\r?\n/).forEach((roh, i) => {
    const z = i + 1, zeile = roh.replace(/[$!].*$/, "").trim();
    if (!zeile) return;
    const tok = zeile.match(/'[^']*'|"[^"]*"|\S+/g).map(x => x.replace(/^['"]|['"]$/g, ""));
    const bef = tok[0].toUpperCase(), rest = tok.slice(1);
    /* benannte Parameter (NR 1 X 0.0 …) oder Positionen (KNOT 1 0.0 PZMX) */
    const args = (namen, alias = {}) => {
      const o = {}, pos = [];
      for (let k = 0; k < rest.length; k++){
        let n = rest[k].toUpperCase(); n = alias[n] || n;
        if (namen.includes(n) && k + 1 < rest.length){ o[n] = rest[++k]; } else pos.push(rest[k]);
      }
      namen.forEach(n => { if (o[n] === undefined && pos.length) o[n] = pos.shift(); });
      return o;
    };
    if (bef === "LF"){ imLF = true; const a = args(["NR", "BEZ"], {NO: "NR", TITL: "BEZ"}); lf = {nr: a.NR || 1, bez: a.BEZ || "Lastfall " + (a.NR || 1)}; return; }
    if (bef === "END" || bef === "ENDE" || bef.startsWith("+PROG") || bef === "PROG" || bef === "KOPF" || bef === "HEAD") return;
    const istKnot = bef === "KNOT" || bef === "NODE", istStab = bef === "STAB" || bef === "BEAM";
    if (!istKnot && !istStab){ fehler.push(`Zeile ${z}: unbekannter Befehl „${tok[0]}“ (erlaubt: KNOT, STAB, LF)`); return; }
    if (imLF){
      const a = args(["NR", "TYP", "P1"], {NO: "NR", TYPE: "TYP", P: "P1", PA: "P1"});
      let typ = String(a.TYP || "").toUpperCase();
      typ = {PZZ: "PZ", PG: "PZ", MXX: "MX"}[typ] || typ;
      if (!["PZ", "MX"].includes(typ)){ fehler.push(`Zeile ${z}: Lasttyp „${a.TYP || ""}“ – erlaubt sind PZ und MX`); return; }
      const p = zahl(a.P1, z, "Lastwert P1"), nrn = liste(a.NR || "");
      if (!nrn.length) fehler.push(`Zeile ${z}: Nummer fehlt`);
      nrn.forEach(nr => lasten.push({art: istKnot ? "knot" : "stab", nr, typ, p, z}));
      return;
    }
    if (istKnot){
      const a = args(["NR", "X", "FIX"], {NO: "NR"});
      const nr = zahl(a.NR, z, "Knotennummer"), x = zahl(a.X, z, "X-Koordinate");
      if (kn.has(nr)) fehler.push(`Zeile ${z}: Knoten ${nr} doppelt`);
      kn.set(nr, {nr, x, fix: String(a.FIX || "").toUpperCase(), z});
    } else {
      const a = args(["NR", "KA", "KE"], {NO: "NR"});
      const nr = zahl(a.NR, z, "Stabnummer"), ka = zahl(a.KA, z, "Anfangsknoten KA"), ke = zahl(a.KE, z, "Endknoten KE");
      if (st.has(nr)) fehler.push(`Zeile ${z}: Stab ${nr} doppelt`);
      st.set(nr, {nr, ka, ke, z});
    }
  });
  for (const s of st.values()){
    if (!kn.has(s.ka) || !kn.has(s.ke)) fehler.push(`Zeile ${s.z}: Stab ${s.nr} verweist auf einen fehlenden Knoten`);
    else if (Math.abs(kn.get(s.ka).x - kn.get(s.ke).x) < 1e-9) fehler.push(`Zeile ${s.z}: Stab ${s.nr} hat die Länge 0`);
  }
  for (const l of lasten){
    if (l.art === "knot" && !kn.has(l.nr)) fehler.push(`Zeile ${l.z}: Knoten ${l.nr} gibt es nicht`);
    if (l.art === "stab" && !st.has(l.nr)) fehler.push(`Zeile ${l.z}: Stab ${l.nr} gibt es nicht`);
  }
  if (!st.size && !fehler.length) fehler.push("Es ist noch kein Stab definiert (STAB NR … KA … KE …).");
  return {kn, st, lasten, lf, fehler};
}
/* Lagerbedingungen wie in SOFiSTiK: PZ = vertikal, MY = Biegeeinspannung, MX = Torsion (Gabel); PP/F/MM als Kurzformen */
function sysFix(code){
  const c = code.toUpperCase();
  if (c === "F") return {w: true, phi: true, tx: true};
  return {w: /PZ|PP/.test(c), phi: /MY|MM/.test(c), tx: /MX|MM/.test(c)};
}

/* ---------- Steifigkeitsverfahren ---------- */
function sysLoesen(m){
  const kn = [...m.kn.values()], idx = new Map(kn.map((k, i) => [k.nr, i])), n = kn.length * 3;
  const K = Array.from({length: n}, () => new Float64Array(n)), F = new Float64Array(n);
  const stabe = [...m.st.values()].map(s => {
    let a = m.kn.get(s.ka), e = m.kn.get(s.ke); if (a.x > e.x) [a, e] = [e, a];
    const q = m.lasten.filter(l => l.art === "stab" && l.nr === s.nr && l.typ === "PZ").reduce((x, l) => x + l.p, 0);
    const mt = m.lasten.filter(l => l.art === "stab" && l.nr === s.nr && l.typ === "MX").reduce((x, l) => x + l.p, 0);
    return {nr: s.nr, a, e, L: e.x - a.x, q, mt, i: idx.get(a.nr), j: idx.get(e.nr)};
  });
  const kB = L => [[12 / L ** 3, 6 / L ** 2, -12 / L ** 3, 6 / L ** 2], [6 / L ** 2, 4 / L, -6 / L ** 2, 2 / L],
                   [-12 / L ** 3, -6 / L ** 2, 12 / L ** 3, -6 / L ** 2], [6 / L ** 2, 2 / L, -6 / L ** 2, 4 / L]];
  const feq = s => [s.q * s.L / 2, s.q * s.L ** 2 / 12, s.q * s.L / 2, -s.q * s.L ** 2 / 12];
  for (const s of stabe){
    const d = [s.i * 3, s.i * 3 + 1, s.j * 3, s.j * 3 + 1], k = kB(s.L), f = feq(s);
    for (let r = 0; r < 4; r++){ F[d[r]] += f[r]; for (let c = 0; c < 4; c++) K[d[r]][d[c]] += k[r][c]; }
    const t = [s.i * 3 + 2, s.j * 3 + 2], kt = 1 / s.L;
    K[t[0]][t[0]] += kt; K[t[1]][t[1]] += kt; K[t[0]][t[1]] -= kt; K[t[1]][t[0]] -= kt;
    F[t[0]] += s.mt * s.L / 2; F[t[1]] += s.mt * s.L / 2;
  }
  for (const l of m.lasten) if (l.art === "knot"){ const i = idx.get(l.nr); F[i * 3 + (l.typ === "PZ" ? 0 : 2)] += l.p; }
  /* Lager: gesperrte Freiheitsgrade; freie Knoten ohne Stab bekommen keine Steifigkeit */
  const frei = [];
  kn.forEach((k, i) => { const f = sysFix(k.fix); [f.w, f.phi, f.tx].forEach((g, j) => { if (!g) frei.push(i * 3 + j); }); });
  const A = frei.map(r => frei.map(c => K[r][c])), b = frei.map(r => F[r]), N = frei.length;
  /* Gauß mit Pivotsuche; singulär = kinematisch */
  const skal = Math.max(1e-12, ...A.map((r, i) => Math.abs(r[i])));
  for (let c = 0; c < N; c++){
    let p = c; for (let r = c + 1; r < N; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r;
    if (Math.abs(A[p][c]) < 1e-10 * skal) return {fehler: "Das System ist kinematisch (verschieblich oder verdrehbar). Prüfe die Lager: mindestens zwei vertikale Lager bzw. eine Einspannung, und mindestens ein Lager mit MX für die Torsion."};
    [A[c], A[p]] = [A[p], A[c]]; [b[c], b[p]] = [b[p], b[c]];
    for (let r = c + 1; r < N; r++){ const f = A[r][c] / A[c][c]; if (f) { for (let k = c; k < N; k++) A[r][k] -= f * A[c][k]; b[r] -= f * b[c]; } }
  }
  const x = new Float64Array(N);
  for (let r = N - 1; r >= 0; r--){ let s = b[r]; for (let k = r + 1; k < N; k++) s -= A[r][k] * x[k]; x[r] = s / A[r][r]; }
  const u = new Float64Array(n); frei.forEach((d, i) => u[d] = x[i]);
  /* Stabendkräfte → Schnittgrößen im Stab */
  for (const s of stabe){
    const ue = [u[s.i * 3], u[s.i * 3 + 1], u[s.j * 3], u[s.j * 3 + 1]], k = kB(s.L), f = feq(s);
    const fe = k.map((r, ri) => r.reduce((acc, kv, c) => acc + kv * ue[c], 0) - f[ri]);
    s.V0 = -fe[0]; s.M0 = fe[1];
    s.T0 = (u[s.j * 3 + 2] - u[s.i * 3 + 2]) / s.L + s.mt * s.L / 2;   /* Torsion: −(Stabendmoment am Anfang) */
  }
  /* Auflagerkräfte */
  const R = kn.map((k, i) => {
    let P = -F[i * 3], Mx = -F[i * 3 + 2];
    for (const s of stabe){
      const ue = [u[s.i * 3], u[s.i * 3 + 1], u[s.j * 3], u[s.j * 3 + 1]], kk = kB(s.L);
      const add = (row, dof) => kk[row].reduce((acc, kv, c) => acc + kv * ue[c], 0);
      if (s.i === i){ P += add(0); Mx += (u[s.i * 3 + 2] - u[s.j * 3 + 2]) / s.L; }
      if (s.j === i){ P += add(2); Mx += (u[s.j * 3 + 2] - u[s.i * 3 + 2]) / s.L; }
    }
    return {nr: k.nr, x: k.x, P: -P, Mx: -Mx, fix: sysFix(k.fix)};   /* Kraft auf das Lager */
  });
  return {stabe, R, xmin: Math.min(...kn.map(k => k.x)), xmax: Math.max(...kn.map(k => k.x))};
}
/* Schnittgrößen an der globalen Stelle x; seite +1 = rechts von Sprüngen, −1 = links */
function sysWerte(L, x, seite = 1){
  const e = 1e-9;
  let s = seite > 0 ? L.stabe.find(s => s.a.x <= x + e && x < s.e.x - e) : L.stabe.find(s => s.a.x + e < x && x <= s.e.x + e);
  if (!s) s = L.stabe.find(s => s.a.x - e <= x && x <= s.e.x + e);
  if (!s) return {V: 0, M: 0, T: 0};
  const t = x - s.a.x;
  return {V: s.V0 - s.q * t, M: s.M0 + s.V0 * t - s.q * t * t / 2, T: s.T0 - s.mt * t};
}

/* ---------- Bedienfeld ---------- */
function SystemPanel(box, id, onChange){
  const key = "sys2-" + id;
  const s = Object.assign({modus: "direkt", text: SYS_VORLAGEN.einfeld.txt, xd: 0}, store.get(key, {}));
  let modell = null, loesung = null;
  box.innerHTML = `<div class="sof-head"><h3>Schnittgrößen</h3>
      <div class="seg" id="sof-mod"><button type="button" data-m="direkt">$T_{Ed}$ und $V_{Ed}$ direkt eingeben</button><button type="button" data-m="system">Statisches System eingeben</button></div></div>
    <div id="sof-body">
      <div class="sof-in">
        <div class="sof-vorl"><span class="label">Vorlage laden</span><div class="sof-vb">${Object.entries(SYS_VORLAGEN).map(([k, v]) => `<button type="button" class="btn ghost" data-v="${k}">${esc(v.t)}</button>`).join("")}</div></div>
        <label class="label" for="sof-txt">Eingabe (wie Teddy)</label>
        <div class="sof-ed"><pre class="sof-nr" id="sof-nr" aria-hidden="true"></pre><textarea id="sof-txt" spellcheck="false" autocapitalize="off" autocomplete="off" wrap="off"></textarea></div>
        <div id="sof-err" class="sof-err" role="status"></div>
        <details class="sof-hilfe"><summary>Befehle und Lagerbedingungen</summary>
          <pre>KNOT NR 1 X 0.0 FIX PZMX    Knoten, X in m
STAB NR 1 KA 1 KE 2          Stab von Knoten 1 nach 2
LF 1 BEZ 'Text'              ab hier Lasten
STAB 1,2 TYP PZ P1 25        Streckenlast kN/m (Z nach unten)
STAB 1-3 TYP MX P1 2.5       Streckentorsion kNm/m
KNOT 2 TYP PZ P1 120         Einzellast kN
KNOT 2 TYP MX P1 30          Einzeltorsion kNm
$ Kommentar</pre>
          <p>FIX: <b>PZ</b> vertikal gehalten · <b>MY</b> Biegeeinspannung · <b>MX</b> Torsion gehalten (Gabel) · <b>F</b> voll eingespannt. Kombinationen wie <b>PZMX</b> (Gabellager) oder <b>PZMYMX</b>. Ausmittige Lasten als Torsion eingeben: $M_T = F\\cdot e$, $m_T = q\\cdot e$. Positionsangaben ohne Schlüsselwort gehen auch: <code>KNOT 1 0.0 PZMX</code>.</p></details>
        <label class="sof-f"><span>Bemessungsschnitt $x$</span><input id="sof-xd" type="number" inputmode="decimal" step="0.05" value="${s.xd}"><em>m</em></label>
        <div class="sof-vb"><button type="button" class="btn ghost" id="sof-maxT">bei max. $|T|$</button><button type="button" class="btn ghost" id="sof-maxV">bei max. $|V|$</button></div>
        <p class="sof-hint">Tipp: in die Verläufe tippen, um den Bemessungsschnitt zu setzen.</p>
      </div>
      <div class="sof-wrap"><svg class="sof" id="sof-svg" viewBox="0 0 760 600" role="img" aria-label="Statisches System mit Lasten und Schnittgrößenverläufen"></svg>
        <div id="sof-tab" class="sof-tab"></div></div>
    </div>`;
  const ta = $("#sof-txt"); ta.value = s.text;
  const nummern = () => { $("#sof-nr").textContent = ta.value.split("\n").map((_, i) => i + 1).join("\n"); $("#sof-nr").scrollTop = ta.scrollTop; };
  ta.addEventListener("scroll", () => $("#sof-nr").scrollTop = ta.scrollTop);
  const setze = () => {
    box.querySelectorAll("#sof-mod button").forEach(b => b.classList.toggle("on", b.dataset.m === s.modus));
    $("#sof-body").hidden = s.modus !== "system";
  };
  let timer;
  const rechne = () => {
    modell = sysParse(ta.value); loesung = null;
    let fehl = modell.fehler.slice();
    if (!fehl.length){ const L = sysLoesen(modell); if (L.fehler) fehl.push(L.fehler); else loesung = L; }
    $("#sof-err").innerHTML = fehl.length ? fehl.map(f => `<div>⚠ ${esc(f)}</div>`).join("") : `<div class="ok">✓ ${modell.kn.size} Knoten, ${modell.st.size} Stäbe, ${modell.lasten.length} Lasten – gerechnet</div>`;
    $("#sof-err").classList.toggle("bad", !!fehl.length);
    if (loesung) s.xd = Math.min(Math.max(s.xd, loesung.xmin), loesung.xmax);
    $("#sof-xd").value = s.xd;
    zeichne(); onChange();
  };
  const speichern = () => { s.text = ta.value; store.set(key, s); };
  ta.addEventListener("input", () => { nummern(); speichern(); clearTimeout(timer); timer = setTimeout(rechne, 250); });
  box.querySelectorAll("#sof-mod button").forEach(b => b.onclick = () => { s.modus = b.dataset.m; speichern(); setze(); rechne(); });
  box.querySelectorAll(".sof-vorl button").forEach(b => b.onclick = () => { ta.value = SYS_VORLAGEN[b.dataset.v].txt; s.xd = 0; nummern(); speichern(); rechne(); });
  $("#sof-xd").addEventListener("input", () => { const v = parseFloat($("#sof-xd").value.replace(",", ".")); if (Number.isFinite(v)){ s.xd = v; speichern(); zeichne(); onChange(); } });
  const springe = k => { if (!loesung) return; let best = 0, bx = loesung.xmin;
    for (let i = 0; i <= 400; i++){ const x = loesung.xmin + i / 400 * (loesung.xmax - loesung.xmin); for (const sd of [1, -1]){ const v = Math.abs(sysWerte(loesung, x, sd)[k]); if (v > best + 1e-9){ best = v; bx = x; } } }
    s.xd = +bx.toFixed(3); $("#sof-xd").value = s.xd; speichern(); zeichne(); onChange(); };
  $("#sof-maxT").onclick = () => springe("T"); $("#sof-maxV").onclick = () => springe("V");
  $("#sof-svg").addEventListener("click", ev => {
    if (!loesung) return;
    const r = $("#sof-svg").getBoundingClientRect(), px = (ev.clientX - r.left) / r.width * 760;
    if (px < 90 || px > 690) return;
    s.xd = +(loesung.xmin + (px - 90) / 600 * (loesung.xmax - loesung.xmin)).toFixed(2);
    $("#sof-xd").value = s.xd; speichern(); zeichne(); onChange();
  });
  function zeichne(){
    if (s.modus !== "system") return;
    if (!loesung){ $("#sof-svg").innerHTML = modell ? sysSvgModell(modell) : ""; $("#sof-tab").innerHTML = ""; return; }
    $("#sof-svg").innerHTML = sysSvg(modell, loesung, s.xd);
    $("#sof-tab").innerHTML = `<table><thead><tr><th>Knoten</th><th>x [m]</th><th>Lager</th><th>P<sub>Z</sub> [kN]</th><th>M<sub>X</sub> [kNm]</th></tr></thead><tbody>${
      loesung.R.filter(r => r.fix.w || r.fix.tx).map(r => `<tr><td>${r.nr}</td><td>${sofN(r.x, 2)}</td><td>${esc(modell.kn.get(r.nr).fix)}</td><td>${r.fix.w ? sofN(r.P) : "–"}</td><td>${r.fix.tx ? sofN(r.Mx) : "–"}</td></tr>`).join("")}</tbody></table>
      <p class="sof-hint">Lagerkräfte wie in SOFiSTiK als Kraft auf das Lager: positiv in +Z (nach unten) bzw. als Moment um +X.</p>`;
  }
  nummern(); setze(); tex(box); rechne();
  return {werte: () => {
    if (s.modus !== "system" || !loesung) return null;
    const x = Math.min(Math.max(s.xd, loesung.xmin), loesung.xmax), w = sysWerte(loesung, x, x >= loesung.xmax - 1e-9 ? -1 : 1);
    return {T: Math.abs(w.T), V: Math.abs(w.V), M: w.M, x};
  },
  /* für den PDF-Rechenweg: Eingabe, Grafik und Lagerkräfte */
  druck: () => s.modus === "system" && loesung ? {text: ta.value, svg: $("#sof-svg").innerHTML.replace(/sof-(ar|ax|mo|mr|hw)/g, "pr-$1"), tab: $("#sof-tab").innerHTML} : null};
}

/* ---------- Grafik ---------- */
const sofN = (v, d = 1) => (Math.abs(v) < 0.5 * Math.pow(10, -d) ? 0 : v).toFixed(d);
const SOF_DEFS = `<defs>
  <marker id="sof-ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="sof-ah"/></marker>
  <marker id="sof-ax" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" class="sof-axh"/></marker>
  <marker id="sof-mo" viewBox="0 0 16 10" refX="15" refY="5" markerWidth="11" markerHeight="7" orient="auto"><path d="M0 0L8 5L0 10zM7 0L15 5L7 10z" class="sof-ah"/></marker>
  <marker id="sof-mr" viewBox="0 0 16 10" refX="15" refY="5" markerWidth="11" markerHeight="7" orient="auto"><path d="M0 0L8 5L0 10zM7 0L15 5L7 10z" class="sof-rh"/></marker>
  <pattern id="sof-hw" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" class="sof-hl"/></pattern></defs>`;

function sysSvgModell(m){
  return SOF_DEFS + `<rect class="sof-bg" x="0.5" y="0.5" width="759" height="599"/><text x="380" y="300" text-anchor="middle" class="sof-tt">Eingabe unvollständig – siehe Meldungen</text>`;
}
function sysSvg(m, L, xd){
  const W = 760, x0 = 90, x1 = 690, BL = x1 - x0, l = L.xmax - L.xmin, X = x => x0 + (x - L.xmin) / l * BL;
  const mass = Math.round(l * 1000 / (BL * 0.2646));
  let o = SOF_DEFS + `<rect class="sof-bg" x="0.5" y="0.5" width="${W - 1}" height="599"/>
    <text x="12" y="17" class="sof-tt">Stabwerk · LF ${esc(String(m.lf.nr))} ${esc(m.lf.bez)}</text>
    <text x="${W - 12}" y="17" text-anchor="end" class="sof-tt">M 1 : ${mass}</text>
    <line class="sof-sep" x1="0" y1="24" x2="${W}" y2="24"/>`;
  const ys = 140, kn = [...m.kn.values()];
  /* Lasten */
  const qMax = Math.max(1e-9, ...L.stabe.map(s => Math.abs(s.q)));
  for (const s of L.stabe){
    if (s.q){
      const h = 14 + 30 * Math.abs(s.q) / qMax, top = ys - 4 - h, xa = X(s.a.x), xe = X(s.e.x), n = Math.max(2, Math.round((xe - xa) / 48));
      o += `<polygon class="sof-qf" points="${xa},${top} ${xe},${top} ${xe},${ys - 4} ${xa},${ys - 4}"/><line class="sof-ld" x1="${xa}" y1="${top}" x2="${xe}" y2="${top}"/>`;
      for (let i = 0; i <= n; i++){ const x = xa + i * (xe - xa) / n; o += s.q > 0 ? `<line class="sof-ld" x1="${x}" y1="${top}" x2="${x}" y2="${ys - 5}" marker-end="url(#sof-ar)"/>` : `<line class="sof-ld" x1="${x}" y1="${ys - 5}" x2="${x}" y2="${top}" marker-end="url(#sof-ar)"/>`; }
      o += `<text x="${(xa + xe) / 2}" y="${top - 5}" text-anchor="middle" class="sof-lv">${sofN(s.q)}</text>`;
    }
    if (s.mt){
      const xa = X(s.a.x), xe = X(s.e.x), n = Math.max(1, Math.round((xe - xa) / 70));
      for (let i = 0; i < n; i++){ const x = xa + (i + 0.5) * (xe - xa) / n; o += s.mt > 0 ? `<line class="sof-ld" x1="${x - 15}" y1="${ys + 30}" x2="${x + 15}" y2="${ys + 30}" marker-end="url(#sof-mo)"/>` : `<line class="sof-ld" x1="${x + 15}" y1="${ys + 30}" x2="${x - 15}" y2="${ys + 30}" marker-end="url(#sof-mo)"/>`; }
      o += `<text x="${(xa + xe) / 2}" y="${ys + 46}" text-anchor="middle" class="sof-lv">${sofN(s.mt, 2)}</text>`;
    }
  }
  for (const l of m.lasten.filter(l => l.art === "knot" && l.p)){
    const k = m.kn.get(l.nr), xk = X(k.x), rand = xk > x1 - 90;
    if (l.typ === "PZ") o += (l.p > 0 ? `<line class="sof-ld big" x1="${xk}" y1="${ys - 92}" x2="${xk}" y2="${ys - 5}" marker-end="url(#sof-ar)"/>` : `<line class="sof-ld big" x1="${xk}" y1="${ys - 5}" x2="${xk}" y2="${ys - 92}" marker-end="url(#sof-ar)"/>`)
      + `<text x="${rand ? xk - 6 : xk + 6}" y="${ys - 80}" text-anchor="${rand ? "end" : "start"}" class="sof-lv">${sofN(l.p)}</text>`;
    else o += `<line class="sof-ld big" x1="${l.p > 0 ? xk - 44 : xk + 44}" y1="${ys + 62}" x2="${xk}" y2="${ys + 62}" marker-end="url(#sof-mo)"/><text x="${l.p > 0 ? xk - 48 : xk + 48}" y="${ys + 66}" text-anchor="${l.p > 0 ? "end" : "start"}" class="sof-lv">${sofN(l.p)}</text>`;
  }
  /* Stäbe, Knoten, Lager */
  for (const s of L.stabe){ const xm = (X(s.a.x) + X(s.e.x)) / 2; o += `<line class="sof-st" x1="${X(s.a.x)}" y1="${ys}" x2="${X(s.e.x)}" y2="${ys}"/><rect class="sof-elb" x="${xm - 11}" y="${ys + 6}" width="22" height="13"/><text x="${xm}" y="${ys + 16}" text-anchor="middle" class="sof-knr">${s.nr}</text>`; }
  for (const k of kn){
    const xk = X(k.x), f = sysFix(k.fix);
    if (f.phi && f.w){
      const links = Math.abs(k.x - L.xmin) < 1e-9, d = links ? -1 : 1;
      o += `<rect x="${links ? xk - 14 : xk}" y="${ys - 22}" width="14" height="44" fill="url(#sof-hw)"/><line class="sof-sup" x1="${xk}" y1="${ys - 22}" x2="${xk}" y2="${ys + 22}"/>`;
      if (!f.tx) o += `<text x="${xk + d * 18}" y="${ys + 34}" text-anchor="middle" class="sof-sm">ohne MX</text>`;
    } else if (f.w){
      o += `<path class="sof-sup" d="M${xk} ${ys}l-9 15h18z"/><line class="sof-sup" x1="${xk - 13}" y1="${ys + 15}" x2="${xk + 13}" y2="${ys + 15}"/>`;
      if (f.tx) o += `<path class="sof-gab" d="M${xk - 7} ${ys - 13}v10M${xk + 7} ${ys - 13}v10"/>`;
      if (f.phi) o += `<rect x="${xk - 4}" y="${ys - 4}" width="8" height="8" class="sof-sup"/>`;
    } else if (f.tx){
      o += `<path class="sof-gab" d="M${xk - 7} ${ys - 13}v10M${xk + 7} ${ys - 13}v10"/>`;
    }
    if (k.fix) o += `<text x="${xk}" y="${ys + 30}" text-anchor="middle" class="sof-sm">${esc(k.fix)}</text>`;
    o += `<circle class="sof-kn" cx="${xk}" cy="${ys}" r="3.2"/><text x="${xk + 5}" y="${ys - 7}" class="sof-knr">${k.nr}</text>`;
  }
  /* Achsen, Bemaßung */
  const ox = 22, oy = ys + 48;
  o += `<line class="sof-axl" x1="${ox}" y1="${oy}" x2="${ox + 28}" y2="${oy}" marker-end="url(#sof-ax)"/><line class="sof-axl" x1="${ox}" y1="${oy}" x2="${ox}" y2="${oy + 28}" marker-end="url(#sof-ax)"/>
    <text x="${ox + 31}" y="${oy + 4}" class="sof-axt">X</text><text x="${ox - 3}" y="${oy + 40}" class="sof-axt">Z</text>`;
  const xs = [...new Set(kn.map(k => +k.x.toFixed(6)))].sort((a, b) => a - b), yd = ys + 86;
  o += `<line class="sof-dim" x1="${x0}" y1="${yd}" x2="${x1}" y2="${yd}"/>`;
  xs.forEach(x => o += `<line class="sof-dim" x1="${X(x)}" y1="${yd - 5}" x2="${X(x)}" y2="${yd + 5}"/>`);
  for (let i = 0; i < xs.length - 1; i++) o += `<text x="${(X(xs[i]) + X(xs[i + 1])) / 2}" y="${yd + 14}" text-anchor="middle" class="sof-sm">${sofN(xs[i + 1] - xs[i], 2)}</text>`;
  o += `<text x="${x1}" y="${yd + 28}" text-anchor="end" class="sof-sm">Lasten in kN, kN/m, kNm, kNm/m · Längen in m</text>`;

  /* Verläufe */
  const pts = [];
  for (const s of L.stabe){ const n = Math.max(8, Math.round(240 * s.L / l)); for (let i = 0; i <= n; i++) pts.push([s.a.x + s.L * i / n, s]); }
  pts.sort((a, b) => a[0] - b[0]);
  const wert = (x, s, k) => { const t = x - s.a.x; return k === "V" ? s.V0 - s.q * t : k === "M" ? s.M0 + s.V0 * t - s.q * t * t / 2 : s.T0 - s.mt * t; };
  const panel = (y0, h, titel, einheit, k, cls) => {
    const w = pts.map(([x, s]) => [x, wert(x, s, k)]);
    const max = Math.max(...w.map(v => Math.abs(v[1])), 1e-9), sc = ((h - 20) / 2 - 17) / max, yb = y0 + 20 + (h - 20) / 2;
    let p = `<line class="sof-sep" x1="0" y1="${y0}" x2="${W}" y2="${y0}"/><text x="12" y="${y0 + 15}" class="sof-tt">${titel} (${einheit})</text>`;
    const poly = w.map(([x, v]) => `${X(x)},${yb + v * sc}`).join(" ");
    p += `<polygon class="sof-fill ${cls}" points="${X(L.xmin)},${yb} ${poly} ${X(L.xmax)},${yb}"/>`;
    for (let px = x0; px <= x1; px += 7){ const x = L.xmin + (px - x0) / BL * l, v = sysWerte(L, x, 1)[k]; if (Math.abs(v * sc) > 1) p += `<line class="sof-hatch ${cls}" x1="${px}" y1="${yb}" x2="${px}" y2="${yb + v * sc}"/>`; }
    p += `<polyline class="sof-line ${cls}" points="${poly}"/><line class="sof-st thin" x1="${x0}" y1="${yb}" x2="${x1}" y2="${yb}"/>`;
    const lab = [];
    for (const s of L.stabe){ lab.push([s.a.x, wert(s.a.x, s, k), 1], [s.e.x, wert(s.e.x, s, k), -1]);
      if (k === "M" && s.q){ const t = s.V0 / s.q; if (t > 0 && t < s.L) lab.push([s.a.x + t, wert(s.a.x + t, s, k), 0]); } }
    const gesetzt = [];
    lab.sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));
    for (const [x, v, sd] of lab){
      if (Math.abs(v) < 0.05) continue;
      const px = X(x) + sd * 3, py = yb + v * sc + (v >= 0 ? 13 : -5);
      if (gesetzt.some(g => Math.abs(g[0] - px) < 38 && Math.abs(g[1] - py) < 12)) continue;
      gesetzt.push([px, py]);
      const anc = sd > 0 ? "start" : sd < 0 ? "end" : "middle";
      p += `<text x="${px}" y="${py}" text-anchor="${anc}" class="sof-val ${cls}">${sofN(v)}</text>`;
    }
    return p;
  };
  o += panel(262, 112, "Querkraft Vz in Stab", "kN", "V", "v");
  o += panel(374, 112, "Biegemoment My in Stab", "kNm", "M", "m");
  o += panel(486, 112, "Torsionsmoment Mt in Stab", "kNm", "T", "t");
  const x = Math.min(Math.max(xd, L.xmin), L.xmax), r = sysWerte(L, x, x >= L.xmax - 1e-9 ? -1 : 1), xb = X(x);
  o += `<line class="sof-bs" x1="${xb}" y1="${ys - 10}" x2="${xb}" y2="592"/>
    <text x="${xb < W / 2 ? xb + 6 : xb - 6}" y="254" text-anchor="${xb < W / 2 ? "start" : "end"}" class="sof-bst">Bemessungsschnitt x = ${sofN(x, 2)} m:  V = ${sofN(Math.abs(r.V))} kN,  T = ${sofN(Math.abs(r.T))} kNm</text>`;
  return o;
}
