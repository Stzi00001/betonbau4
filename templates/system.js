/* ---------- Statisches System für das Bemessungstool (Darstellung angelehnt an Stabwerksprogramme wie SOFiSTiK) ----------
   Einfeldträger mit Gabellagern oder Kragarm; Gleichlast q und Einzellast F, jeweils mit Ausmitte e quer zur Stabachse
   → Streckentorsion m_T = q·e bzw. Einzeltorsion M_T = F·e. Liefert T_Ed und V_Ed am Bemessungsschnitt. */
const SYS_STD = {modus: "direkt", typ: "einfeld", l: 6, q: 25, eq: 0.1, F: 120, a: 3, eF: 0.25, xd: 0};

function sysSchnitt(s, x, seite = 1){
  const l = s.l, a = Math.min(Math.max(s.a, 0), l), mt = s.q * s.eq, MT = s.F * s.eF;
  const rechts = seite > 0 ? x >= a : x > a;
  if (s.typ === "krag"){
    const links = !rechts;                               /* Einspannung bei x = 0, freies Ende bei x = l */
    return {V: s.q * (l - x) + (links ? s.F : 0), M: -(s.q * (l - x) ** 2 / 2 + s.F * Math.max(0, a - x)), T: mt * (l - x) + (links ? MT : 0)};
  }
  const A = s.q * l / 2 + s.F * (l - a) / l;             /* Gabellager an beiden Enden: Torsion teilt sich nach den Abständen auf */
  return {V: A - s.q * x - (rechts ? s.F : 0), M: A * x - s.q * x * x / 2 - s.F * Math.max(0, x - a),
          T: mt * (l / 2 - x) + MT * ((l - a) / l - (rechts ? 1 : 0))};
}
function sysBemessung(s){
  const x = Math.min(Math.max(s.xd, 0), s.l), r = sysSchnitt(s, x, x >= s.l ? -1 : 1);
  return {T: Math.abs(r.T), V: Math.abs(r.V), M: r.M, x};
}

function SystemPanel(box, id, onChange){
  const key = "sys-" + id, s = Object.assign({...SYS_STD}, store.get(key, {}));
  const F = [
    ["l", "Länge $l$", "m", 0.5, 0.5], ["q", "Gleichlast $q_{Ed}$", "kN/m", 0, 1], ["eq", "Ausmitte $e_q$", "m", 0, 0.01],
    ["F", "Einzellast $F_{Ed}$", "kN", 0, 5], ["a", "Lage $a$ von links", "m", 0, 0.1], ["eF", "Ausmitte $e_F$", "m", 0, 0.01],
    ["xd", "Bemessungsschnitt $x$", "m", 0, 0.1]];
  box.innerHTML = `<div class="sof-head"><h3>Schnittgrößen</h3>
      <div class="seg" id="sof-mod"><button type="button" data-m="direkt">$T_{Ed}$ und $V_{Ed}$ direkt eingeben</button><button type="button" data-m="system">Aus statischem System</button></div></div>
    <div id="sof-body">
      <div class="sof-in">
        <div class="sof-typ"><span class="label">System</span><div class="seg" id="sof-typ"><button type="button" data-t="einfeld">Einfeldträger</button><button type="button" data-t="krag">Kragarm</button></div></div>
        ${F.map(([k, lab, u, min, st]) => `<label class="sof-f"><span>${lab}</span><input id="sof-${k}" type="number" inputmode="decimal" min="${min}" step="${st}" value="${s[k]}"><em>${u}</em></label>`).join("")}
        <p class="sof-hint">Die Ausmitte wirkt quer zur Stabachse und erzeugt Torsion: $m_T = q_{Ed}\\cdot e_q$, $M_T = F_{Ed}\\cdot e_F$. Einfeldträger mit Gabellagern, Kragarm links eingespannt.</p>
      </div>
      <div class="sof-wrap"><svg class="sof" id="sof-svg" viewBox="0 0 760 560" role="img" aria-label="Statisches System mit Lasten und Schnittgrößenverläufen"></svg></div>
    </div>`;
  const setze = () => {
    box.querySelectorAll("#sof-mod button").forEach(b => b.classList.toggle("on", b.dataset.m === s.modus));
    box.querySelectorAll("#sof-typ button").forEach(b => b.classList.toggle("on", b.dataset.t === s.typ));
    $("#sof-body").hidden = s.modus !== "system";
  };
  const lesen = () => {
    F.forEach(([k, , , min]) => { const v = parseFloat(String($("#sof-" + k).value).replace(",", ".")); if (Number.isFinite(v)) s[k] = Math.max(min, v); });
    s.l = Math.max(s.l, 0.5); s.a = Math.min(s.a, s.l); s.xd = Math.min(s.xd, s.l);
  };
  const neu = () => { lesen(); store.set(key, s); zeichne(); onChange(); };
  box.querySelectorAll("#sof-mod button").forEach(b => b.onclick = () => { s.modus = b.dataset.m; store.set(key, s); setze(); zeichne(); onChange(); });
  box.querySelectorAll("#sof-typ button").forEach(b => b.onclick = () => { s.typ = b.dataset.t; store.set(key, s); setze(); zeichne(); onChange(); });
  F.forEach(([k]) => $("#sof-" + k).addEventListener("input", neu));
  setze(); tex(box);

  function zeichne(){ if (s.modus === "system") $("#sof-svg").innerHTML = sysSvg(s); }
  zeichne();
  return {werte: () => s.modus === "system" ? sysBemessung(s) : null, zustand: () => ({...s})};
}

/* Zahlen wie in Stabwerksprogrammen: Dezimalpunkt, eine Nachkommastelle */
const sofN = (v, d = 1) => (Math.abs(v) < 0.05 ? 0 : v).toFixed(d);

function sysSvg(s){
  const W = 760, x0 = 90, x1 = 690, L = x1 - x0, l = s.l, X = x => x0 + x / l * L, a = Math.min(s.a, l);
  const mt = s.q * s.eq, MT = s.F * s.eF, mass = Math.round(l * 1000 / (L * 0.2646));
  let o = `<defs>
    <marker id="sof-ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="sof-ah"/></marker>
    <marker id="sof-ax" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" class="sof-axh"/></marker>
    <marker id="sof-mo" viewBox="0 0 16 10" refX="15" refY="5" markerWidth="11" markerHeight="7" orient="auto"><path d="M0 0L8 5L0 10zM7 0L15 5L7 10z" class="sof-ah"/></marker>
    <pattern id="sof-hw" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" class="sof-hl"/></pattern></defs>`;
  o += `<rect class="sof-bg" x="0.5" y="0.5" width="${W - 1}" height="559"/>
    <text x="12" y="17" class="sof-tt">Stabwerk · Lastfall 1 · Bemessungslasten</text>
    <text x="${W - 12}" y="17" text-anchor="end" class="sof-tt">M 1 : ${mass}</text>
    <line class="sof-sep" x1="0" y1="24" x2="${W}" y2="24"/>`;

  /* System mit Lasten */
  const ys = 132;
  if (s.q > 0){
    const top = ys - 46;
    o += `<polygon class="sof-qf" points="${x0},${top} ${x1},${top} ${x1},${ys - 4} ${x0},${ys - 4}"/>`;
    for (let i = 0; i <= 12; i++){ const x = x0 + i * L / 12; o += `<line class="sof-ld" x1="${x}" y1="${top}" x2="${x}" y2="${ys - 5}" marker-end="url(#sof-ar)"/>`; }
    o += `<line class="sof-ld" x1="${x0}" y1="${top}" x2="${x1}" y2="${top}"/><text x="${x0 + 6}" y="${top - 6}" class="sof-lv">${sofN(s.q)} kN/m</text>`;
  }
  if (mt > 0){
    for (let i = 0; i < 6; i++){ const x = x0 + (i + 0.5) * L / 6; o += `<line class="sof-ld" x1="${x - 16}" y1="${ys + 22}" x2="${x + 16}" y2="${ys + 22}" marker-end="url(#sof-mo)"/>`; }
    o += `<text x="${x0 + 6}" y="${ys + 40}" class="sof-lv">m<tspan class="sof-ix" dy="3">T</tspan><tspan dy="-3"> = ${sofN(mt, 2)} kNm/m</tspan></text>`;
  }
  if (s.F > 0){
    const xf = X(a);
    const rand = xf > x1 - 110;
    o += `<line class="sof-ld big" x1="${xf}" y1="${ys - 82}" x2="${xf}" y2="${ys - 5}" marker-end="url(#sof-ar)"/><text x="${rand ? xf - 6 : xf + 6}" y="${ys - 70}" text-anchor="${rand ? "end" : "start"}" class="sof-lv">${sofN(s.F)} kN</text>`;
    if (MT > 0) o += rand
      ? `<line class="sof-ld big" x1="${xf - 40}" y1="${ys + 36}" x2="${xf}" y2="${ys + 36}" marker-end="url(#sof-mo)"/><text x="${xf - 44}" y="${ys + 40}" text-anchor="end" class="sof-lv">M<tspan class="sof-ix" dy="3">T</tspan><tspan dy="-3"> = ${sofN(MT)} kNm</tspan></text>`
      : `<line class="sof-ld big" x1="${xf}" y1="${ys + 36}" x2="${xf + 40}" y2="${ys + 36}" marker-end="url(#sof-mo)"/><text x="${xf + 44}" y="${ys + 40}" class="sof-lv">M<tspan class="sof-ix" dy="3">T</tspan><tspan dy="-3"> = ${sofN(MT)} kNm</tspan></text>`;
  }
  o += `<line class="sof-st" x1="${x0}" y1="${ys}" x2="${x1}" y2="${ys}"/>`;
  /* Lager */
  if (s.typ === "krag"){
    o += `<rect x="${x0 - 14}" y="${ys - 24}" width="14" height="48" fill="url(#sof-hw)"/><line class="sof-sup" x1="${x0}" y1="${ys - 24}" x2="${x0}" y2="${ys + 24}"/>`;
  } else {
    for (const [x, fest] of [[x0, true], [x1, false]]){
      o += `<path class="sof-sup" d="M${x} ${ys}l-9 15h18z"/><line class="sof-sup" x1="${x - 13}" y1="${ys + 15}" x2="${x + 13}" y2="${ys + 15}"/>`;
      if (!fest) o += `<line class="sof-sup" x1="${x - 13}" y1="${ys + 20}" x2="${x + 13}" y2="${ys + 20}"/>`;
      o += `<text x="${x}" y="${ys + 34}" text-anchor="middle" class="sof-sm">Gabel</text>`;
    }
  }
  /* Knoten und Stäbe */
  const kn = [0]; if (s.F > 0 && a > 1e-6 && a < l - 1e-6) kn.push(a); kn.push(l);
  kn.forEach((x, i) => o += `<circle class="sof-kn" cx="${X(x)}" cy="${ys}" r="3.2"/><text x="${X(x) + 5}" y="${ys - 7}" class="sof-knr">${i + 1}</text>`);
  for (let i = 0; i < kn.length - 1; i++){ const xm = (X(kn[i]) + X(kn[i + 1])) / 2; o += `<rect class="sof-elb" x="${xm - 10}" y="${ys + 4}" width="20" height="13"/><text x="${xm}" y="${ys + 14}" text-anchor="middle" class="sof-knr">${i + 1}</text>`; }
  /* Koordinatensystem: X nach rechts, Z nach unten */
  const ox = 22, oy = ys + 40;
  o += `<line class="sof-axl" x1="${ox}" y1="${oy}" x2="${ox + 28}" y2="${oy}" marker-end="url(#sof-ax)"/><line class="sof-axl" x1="${ox}" y1="${oy}" x2="${ox}" y2="${oy + 28}" marker-end="url(#sof-ax)"/>
    <text x="${ox + 31}" y="${oy + 4}" class="sof-axt">X</text><text x="${ox - 3}" y="${oy + 40}" class="sof-axt">Z</text>`;
  /* Bemaßung */
  o += `<line class="sof-dim" x1="${x0}" y1="${ys + 52}" x2="${x1}" y2="${ys + 52}"/><line class="sof-dim" x1="${x0}" y1="${ys + 47}" x2="${x0}" y2="${ys + 57}"/><line class="sof-dim" x1="${x1}" y1="${ys + 47}" x2="${x1}" y2="${ys + 57}"/>
    <text x="${(x0 + x1) / 2}" y="${ys + 66}" text-anchor="middle" class="sof-sm">l = ${sofN(l, 2)} m</text>`;

  /* Schnittgrößenverläufe, positive Werte in Richtung +Z (unten) */
  const xs = []; for (let i = 0; i <= 240; i++) xs.push(i / 240 * l);
  const pts = []; xs.forEach(x => { if (s.F > 0 && Math.abs(x - a) < l / 480) return; pts.push([x, 1]); });
  if (s.F > 0){ pts.push([a, -1], [a, 1]); }
  pts.sort((p, q) => p[0] - q[0] || p[1] - q[1]);
  const panel = (y0, h, titel, einheit, k, cls) => {
    const werte = pts.map(([x, sd]) => [x, sysSchnitt(s, x, sd)[k]]);
    const max = Math.max(...werte.map(w => Math.abs(w[1])), 1e-9), sc = ((h - 20) / 2 - 17) / max, yb = y0 + 20 + (h - 20) / 2;
    let p = `<line class="sof-sep" x1="0" y1="${y0}" x2="${W}" y2="${y0}"/><text x="12" y="${y0 + 15}" class="sof-tt">${titel} (${einheit})</text>`;
    const poly = werte.map(([x, v]) => `${X(x)},${yb + v * sc}`).join(" ");
    p += `<polygon class="sof-fill ${cls}" points="${X(0)},${yb} ${poly} ${X(l)},${yb}"/>`;
    for (let px = x0; px <= x1; px += 7){ const x = (px - x0) / L * l; const v = sysSchnitt(s, x, 1)[k]; if (Math.abs(v * sc) > 1) p += `<line class="sof-hatch ${cls}" x1="${px}" y1="${yb}" x2="${px}" y2="${yb + v * sc}"/>`; }
    p += `<polyline class="sof-line ${cls}" points="${poly}"/><line class="sof-st thin" x1="${x0}" y1="${yb}" x2="${x1}" y2="${yb}"/>`;
    /* Beschriftung: Enden, Sprungstelle, Extremwert */
    const lab = [[0, werte[0][1]], [l, werte[werte.length - 1][1]]];
    if (s.F > 0 && a > 1e-6 && a < l - 1e-6){ lab.push([a, sysSchnitt(s, a, -1)[k]], [a, sysSchnitt(s, a, 1)[k]]); }
    const ex = werte.reduce((m, w) => Math.abs(w[1]) > Math.abs(m[1]) ? w : m, werte[0]); lab.push(ex);
    const gesetzt = [];
    for (const [x, v] of lab){
      if (Math.abs(v) < 0.05) continue;
      const px = X(x), py = yb + v * sc + (v >= 0 ? 13 : -5);
      if (gesetzt.some(g => Math.abs(g[0] - px) < 34 && Math.abs(g[1] - py) < 12)) continue;
      gesetzt.push([px, py]);
      const anc = x <= l * 0.02 ? "start" : x >= l * 0.98 ? "end" : "middle";
      p += `<text x="${px + (anc === "start" ? 3 : anc === "end" ? -3 : 0)}" y="${py}" text-anchor="${anc}" class="sof-val ${cls}">${sofN(v)}</text>`;
    }
    return p;
  };
  o += panel(222, 108, "Querkraft Vz in Stab, Lastfall 1", "kN", "V", "v");
  o += panel(330, 108, "Biegemoment My in Stab, Lastfall 1", "kNm", "M", "m");
  o += panel(438, 108, "Torsionsmoment Mt in Stab, Lastfall 1", "kNm", "T", "t");
  /* Bemessungsschnitt */
  const b = sysBemessung(s), xb = X(b.x);
  o += `<line class="sof-bs" x1="${xb}" y1="${ys - 10}" x2="${xb}" y2="552"/>
    <text x="${xb < W / 2 ? xb + 6 : xb - 6}" y="214" text-anchor="${xb < W / 2 ? "start" : "end"}" class="sof-bst">Bemessungsschnitt x = ${sofN(b.x, 2)} m:  V = ${sofN(b.V)} kN,  T = ${sofN(b.T)} kNm</text>`;
  return o;
}
