/* ---------- Rechenkern: gemeinsam für Übungsaufgaben, Bemessungstool und PDF-Seiten ----------
   Ein Rechenweg besteht aus Schritten:
     {titel, text, wenn, formel: [...], einsetzen: [...], werte: [{id, expr, d, wenn, frage, label, einheit}]}
   - expr ist ein Rechenausdruck mit den bisherigen Werten als Variablen
   - formel/einsetzen sind LaTeX-Zeilen; #id# bzw. #id:2# setzt einen Wert ein (2 = Nachkommastellen)
   - eine Zeile darf auch {wenn: "Bedingung", t: "LaTeX"} sein; "wenn" gibt es auch für Schritte und Werte */
const MATHCTX = {sqrt:Math.sqrt, min:Math.min, max:Math.max, sin:Math.sin, cos:Math.cos, tan:Math.tan, atan:Math.atan,
  abs:Math.abs, pow:Math.pow, cbrt:Math.cbrt, PI:Math.PI, FCK:c => parseFloat(String(c).slice(1))};
function evalExpr(expr, ctx){
  const k = Object.keys(ctx);
  return new Function(...k, `"use strict"; return (${expr});`)(...k.map(x => ctx[x]));
}
function texNum(v, d){
  if (typeof v === "boolean") return v ? "ja" : "nein";
  if (typeof v !== "number") return String(v);
  if (!Number.isFinite(v)) return "\\text{–}";
  return v.toLocaleString("de-DE", {minimumFractionDigits:d, maximumFractionDigits:d, useGrouping:false}).replace(",", "{,}");
}
function fill(str, ctx, digits){
  let s = String(str);
  for (let pass = 0; pass < 2; pass++){       /* zweimal, damit Platzhalter in berechneten Texten auch ersetzt werden */
    s = s.replace(/#([A-Za-z_]\w*)(?::(\d))?#/g, (m, id, d) => {
      if (!(id in ctx) || id in MATHCTX) return m;
      return texNum(ctx[id], d !== undefined ? +d : (digits[id] ?? 2));
    });
  }
  return s;
}
function cond(x, ctx){ return !x || typeof x !== "object" || !x.wenn || !!evalExpr(x.wenn, ctx); }
function lines(arr, ctx){
  return (arr || []).filter(l => typeof l === "string" || cond(l, ctx)).map(l => typeof l === "string" ? l : l.t);
}
function compute(schritte, ctx, digits){
  for (const st of schritte){
    if (!cond(st, ctx)) continue;
    for (const w of st.werte || []){
      if (!cond(w, ctx)) continue;
      ctx[w.id] = evalExpr(w.expr, ctx);
      digits[w.id] = w.d ?? 2;
    }
  }
}
/* Reproduzierbarer Zufall für PDF-Übungsblätter */
function rng(seed){
  return function(){ seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}
function drawParams(params, ctx, digits, rand = Math.random){
  for (const [k, p] of Object.entries(params || {})){
    if (p.werte) ctx[k] = p.werte[Math.floor(rand() * p.werte.length)];
    else { const n = Math.round((p.max - p.min) / p.step); ctx[k] = +(p.min + Math.floor(rand() * (n + 1)) * p.step).toFixed(6); }
    digits[k] = Number.isInteger(ctx[k]) ? 0 : 1;
  }
}
/* Rechenweg als Dokument: jeder Schritt mit Ansatz und eingesetzten Zahlen */
function stepDoc(schritte, ctx, digits, start = 1){
  let n = start - 1;
  return schritte.filter(st => cond(st, ctx)).map(st => {
    n++;
    const f = lines(st.formel, ctx), e = lines(st.einsetzen, ctx);
    return `<section class="rw-step"><h4><span class="rw-n">${n}</span>${esc(st.titel)}</h4>
      ${st.text ? `<p>${fill(st.text, ctx, digits)}</p>` : ""}
      ${f.length ? `<div class="rw-f">${f.map(x => `<div>$\\displaystyle ${fill(x, ctx, digits)}$</div>`).join("")}</div>` : ""}
      ${e.length ? `<div class="rw-e">${e.map(x => `<div>$\\displaystyle ${fill(x, ctx, digits)}$</div>`).join("")}</div>` : ""}
    </section>`;
  }).join("");
}
