/* ---------- Wer wird Millionär ---------- */
const STUFEN = [50,100,200,300,500,1000,2000,4000,8000,16000,32000,64000,125000,500000,1000000];
const MODES = {
  sicher: {name: "Sicherheitsvariante", safe: [4, 9], zusatz: false},
  risiko: {name: "Risikovariante", safe: [4], zusatz: true}
};
const TIERS = ["leicht", "mittel", "schwer"];
/* Je Gewinnstufe: aus welcher Schwierigkeit die drei Falschantworten kommen (0 leicht, 1 mittel, 2 schwer) */
const TIERPLAN = [[0,0,0],[0,0,0],[0,0,0],[0,0,1],[0,0,1],[0,1,1],[0,1,1],[1,1,1],[1,1,1],[1,1,1],[1,1,2],[1,1,2],[1,2,2],[2,2,2],[2,2,2]];
const euro = n => n.toLocaleString("de-DE") + " €";

const SND = {
  on: store.get("sound", false), ctx: null,
  play(seq){
    if (!this.on) return;
    try {
      this.ctx = this.ctx || new (window.AudioContext || window.webkitAudioContext)();
      const c = this.ctx; let t = c.currentTime;
      for (const [f, d, type = "sine", v = 0.08] of seq){
        const o = c.createOscillator(), g = c.createGain();
        o.type = type; o.frequency.value = f;
        g.gain.setValueAtTime(v, t); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
        o.connect(g); g.connect(c.destination); o.start(t); o.stop(t + d); t += d * 0.85;
      }
    } catch(e){}
  },
  lock(){ this.play([[196,.3,"triangle"],[185,.9,"triangle",.06]]); },
  right(){ this.play([[523,.12],[659,.12],[784,.12],[1047,.4]]); },
  wrong(){ this.play([[311,.3,"sawtooth",.04],[233,.7,"sawtooth",.04]]); },
  joker(){ this.play([[880,.08],[1320,.14]]); },
  safe(){ this.play([[523,.1],[659,.1],[784,.1],[1047,.1],[1319,.5]]); }
};

const ICON_PUB = '<svg viewBox="0 0 24 24"><circle cx="8" cy="8" r="3"/><circle cx="16" cy="8" r="3"/><path d="M2 20c0-3.3 2.7-6 6-6s6 2.7 6 6M10 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/></svg>';
const ICON_ZJ = '<svg viewBox="0 0 24 24"><circle cx="9" cy="7" r="3"/><path d="M3 21c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M17 12V3M14.5 5.5 17 3l2.5 2.5"/></svg>';
const ICON_TEL = '<svg viewBox="0 0 24 24"><path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z"/></svg>';
const ICON_SND = on => on
  ? '<svg viewBox="0 0 24 24"><path d="M4 9h4l5-4v14l-5-4H4z"/><path d="M16 9a4 4 0 0 1 0 6M19 6a8 8 0 0 1 0 12"/></svg>'
  : '<svg viewBox="0 0 24 24"><path d="M4 9h4l5-4v14l-5-4H4z"/><path d="M17 9l5 6M22 9l-5 6"/></svg>';

/* Altes Fragenformat (a[], r = Index) in das neue Format umwandeln */
function normQuiz(q){
  if (q.falsch) return q;
  return {...q, r: q.a[q.r], falsch: {mittel: q.a.filter((_, k) => k !== q.r)}};
}
/* Drei Falschantworten passend zur Gewinnstufe wählen */
function pickWrong(q, level){
  const pools = {}; TIERS.forEach(t => pools[t] = shuffle(q.falsch[t] || []));
  const out = [];
  for (const want of TIERPLAN[Math.min(level, 14)]){
    for (const t of [want, want - 1, want + 1, want - 2, want + 2].filter(x => x >= 0 && x <= 2)){
      const p = pools[TIERS[t]];
      if (p.length){ out.push({s: p.pop(), tier: t}); break; }
    }
  }
  return out;
}
const MIN_FRAGEN = 5;
/* Gewinnleiter für n Fragen: bei weniger als 15 Fragen gleichmäßig verteilt, die letzte Frage bleibt die Million */
function leiter(n){
  if (n >= 15) return STUFEN.map((_, k) => k);
  return Array.from({length: n}, (_, k) => n > 1 ? Math.round(k * 14 / (n - 1)) : 14);
}
function quizPool(t, auswahl){
  const all = t.quiz.map(normQuiz);
  return auswahl ? all.filter(q => auswahl.includes(q.teil)) : all;
}
function buildRounds(t, auswahl){
  const all = quizPool(t, auswahl), n = Math.min(15, all.length), lv = leiter(n);
  const byD = [1,2,3].map(d => shuffle(all.filter(q => (q.d || 2) === d)));
  let pick = byD.flatMap(g => g.slice(0, 5));
  if (pick.length < n) pick = pick.concat(shuffle(all.filter(q => !pick.includes(q))).slice(0, n - pick.length));
  pick = shuffle(pick).slice(0, n).sort((a, b) => (a.d || 2) - (b.d || 2));
  return pick.map((q, i) => ({q, lvl: lv[i], opts: shuffle([{s: q.r, ok: true, tier: -1}, ...pickWrong(q, lv[i])])}));
}

function confetti(host){
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const cv = document.createElement("canvas"); cv.className = "confetti"; host.appendChild(cv);
  const r = host.getBoundingClientRect(); cv.width = r.width; cv.height = r.height;
  const g = cv.getContext("2d"), cols = ["#f2c14e", "#ffffff", "#8ff0b4", "#8fb0ff"];
  const ps = Array.from({length: 140}, () => ({x: Math.random() * cv.width, y: -20 - Math.random() * cv.height * .6,
    vx: (Math.random() - .5) * 2.4, vy: 2 + Math.random() * 3, s: 5 + Math.random() * 5, c: cols[Math.random() * 4 | 0], a: Math.random() * 6}));
  let n = 0;
  (function f(){
    g.clearRect(0, 0, cv.width, cv.height);
    for (const p of ps){ p.x += p.vx; p.y += p.vy; p.a += .12; g.save(); g.translate(p.x, p.y); g.rotate(p.a); g.fillStyle = p.c; g.fillRect(-p.s/2, -p.s/4, p.s, p.s/2); g.restore(); }
    if (++n < 200) requestAnimationFrame(f); else cv.remove();
  })();
}

function Quiz(t, el){
  let rounds, i, used, history, phase, sel, mode = store.get("mode", "sicher");
  /* Kapitelauswahl (Vorlesungsteile) */
  const teileQuiz = (t.teile || []).filter(x => t.quiz.some(q => q.teil === x.id));
  const auswahlKey = "quiz-teile-" + t.id;
  let auswahl = (store.get(auswahlKey, null) || []).filter(id => teileQuiz.some(x => x.id === id));
  if (!auswahl.length) auswahl = teileQuiz.map(x => x.id);
  const aktiveAuswahl = () => teileQuiz.length > 1 ? auswahl : null;
  /* Sicherheitsstufen: erste Frage, deren Gewinnstufe die Sicherheitsstufe erreicht */
  const safeFor = m => MODES[m].safe.map(s => rounds.findIndex(r => r.lvl >= s)).filter((v, k, a) => v >= 0 && a.indexOf(v) === k && v < rounds.length - 1);
  const SAFE = () => safeFor(mode);
  const P = k => STUFEN[rounds[k].lvl];
  const recKey = "best-" + t.id;

  function shell(inner, ladder = true){
    el.innerHTML = `<div class="stage" id="stage"><span class="beam l"></span><span class="beam r"></span>${inner}${ladder ? ladderHTML() : ""}</div>`;
    tex(el);
  }
  function ladderHTML(lost = -1){
    return `<ol class="ladder" aria-label="Gewinnleiter">${rounds.map(r => STUFEN[r.lvl]).map((s, k) =>
      `<li class="${k === lost ? "lost" : k === i && phase !== "end" ? "now" : k < i ? "done" : ""} ${SAFE().includes(k) ? "safe" : ""}"><span>${k + 1}</span><span>${euro(s)}</span></li>`).join("")}</ol>`;
  }
  function miniHTML(){
    return `<div class="mini" aria-hidden="true">${rounds.map((_, k) => `<i class="${k === i ? "now" : k < i ? "done" : SAFE().includes(k) ? "safe" : ""}"></i>`).join("")}</div>`;
  }

  /* ---- Start ---- */
  function intro(){
    rounds = buildRounds(t, aktiveAuswahl()); i = 0;
    const best = store.get(recKey, 0), n = rounds.length, zuWenig = n < MIN_FRAGEN;
    const safeTxt = m => { const s = safeFor(m).map(k => euro(P(k))); return s.length === 2 ? `Sicherheitsstufen bei ${s[0]} und ${s[1]}` : s.length ? `Nur eine Sicherheitsstufe bei ${s[0]}` : "Keine Sicherheitsstufe"; };
    const card = (k, title, jok, extra) => `
      <button class="modec ${mode === k ? "on" : ""}" data-m="${k}" aria-pressed="${mode === k}">
        <span class="mt">${title}</span>
        <span class="mrow"><b>${jok}</b><span>Joker${extra}</span></span>
        <span class="mrow"><b>◆</b><span>${safeTxt(k)}</span></span>
      </button>`;
    const anz = id => t.quiz.filter(q => q.teil === id).length;
    el.innerHTML = `<div class="stage"><span class="beam l"></span><span class="beam r"></span><div class="intro">
      <span class="topic-name">Thema ${t.nr} · ${esc(t.titel)}</span>
      <h3>Wer wird<br>Millionär?</h3>
      ${teileQuiz.length > 1 ? `<div class="kapitel" role="group" aria-label="Kapitel wählen">
        <span class="klabel">Fragen aus diesen Kapiteln</span>
        <div class="kchips">${teileQuiz.map(x => `<button class="kchip ${auswahl.includes(x.id) ? "on" : ""}" data-k="${x.id}" aria-pressed="${auswahl.includes(x.id)}" type="button"><span class="kbox" aria-hidden="true">${auswahl.includes(x.id) ? "✓" : ""}</span>${esc(x.titel)}<span class="kanz">${anz(x.id)}</span></button>`).join("")}</div>
        <span class="khint" id="khint" aria-live="polite"></span>
      </div>` : ""}
      <p class="sub">${zuWenig ? `In der Auswahl sind nur ${n} Fragen. Für ein Spiel braucht es mindestens ${MIN_FRAGEN}.`
        : n < 15 ? `${n} Fragen von leicht bis knifflig – in der Auswahl gibt es nicht genug für 15. Die Gewinnleiter ist entsprechend verkürzt.`
        : "15 Fragen von leicht bis knifflig. Die falschen Antworten werden mit jeder Stufe ähnlicher."}</p>
      <div class="modes" role="group" aria-label="Spielvariante wählen">
        ${card("sicher", "Sicherheitsvariante", "3", ": 50:50, Publikum, Telefon")}
        ${card("risiko", "Risikovariante", "4", " inkl. Zusatzjoker aus dem Hörsaal")}
      </div>
      <div class="sbtns" style="justify-content:center"><button class="sbtn" id="go" ${zuWenig ? "disabled" : ""}>${MODES[mode].name} starten</button></div>
      <span class="topic-name">${quizPool(t, aktiveAuswahl()).length} Fragen in der Auswahl${best ? " · Rekord " + euro(best) : ""}</span>
    </div></div>`;
    tex(el);
    el.querySelectorAll(".modec").forEach(b => b.onclick = () => { mode = b.dataset.m; store.set("mode", mode); intro(); });
    el.querySelectorAll(".kchip").forEach(b => b.onclick = () => {
      const id = b.dataset.k;
      if (auswahl.includes(id)){
        if (auswahl.length === 1){ $("#khint").textContent = "Mindestens ein Kapitel muss ausgewählt bleiben."; return; }
        auswahl = auswahl.filter(x => x !== id);
      } else auswahl = teileQuiz.map(x => x.id).filter(x => x === id || auswahl.includes(x));
      store.set(auswahlKey, auswahl); intro();
    });
    $("#go").onclick = () => { if (zuWenig) return; used = {fifty: false, pub: false, tel: false, zusatz: false}; history = []; i = 0; round(); };
  }

  /* ---- Eine Frage ---- */
  function round(){
    phase = "ask"; sel = null;
    const R = rounds[i];
    shell(`<div class="main">
      <div class="hud">
        <div class="lvl"><small>${MODES[mode].name} · Frage ${i + 1} von ${rounds.length}${SAFE().includes(i) ? " · Sicherheitsstufe" : ""}</small><b>um ${euro(P(i))}</b></div>
        <div class="jk">
          <button class="jbtn" id="j50" ${used.fifty ? "disabled" : ""} aria-label="Joker 50:50" title="50:50">50:50</button>
          <button class="jbtn" id="jpub" ${used.pub ? "disabled" : ""} aria-label="Publikumsjoker" title="Publikum">${ICON_PUB}</button>
          <button class="jbtn" id="jtel" ${used.tel ? "disabled" : ""} aria-label="Telefonjoker" title="Telefon">${ICON_TEL}</button>
          ${MODES[mode].zusatz ? `<button class="jbtn" id="jzj" ${used.zusatz ? "disabled" : ""} aria-label="Zusatzjoker" title="Zusatzjoker">${ICON_ZJ}</button>` : ""}
          <button class="jbtn snd" id="snd" aria-label="Ton ${SND.on ? "aus" : "an"}" title="Ton">${ICON_SND(SND.on)}</button>
          <button class="jbtn txt" id="stop">Aussteigen</button>
        </div>
      </div>
      ${miniHTML()}
      <div class="lz qbox"><span class="e"><span class="c">${esc(R.q.f)}</span></span></div>
      <div class="answers">${R.opts.map((o, k) =>
        `<button class="lz ans" data-k="${k}"><span class="e"><span class="c"><b>${"ABCD"[k]}:</b><span>${esc(o.s)}</span></span></span></button>`).join("")}</div>
      <div id="jout"></div>
      <div id="panel"></div>
    </div>`);
    el.querySelectorAll(".ans").forEach(b => b.onclick = () => choose(+b.dataset.k));
    $("#j50").onclick = fifty; $("#jpub").onclick = pub; $("#jtel").onclick = tel;
    if ($("#jzj")) $("#jzj").onclick = zusatz;
    $("#snd").onclick = () => { SND.on = !SND.on; store.set("sound", SND.on); $("#snd").innerHTML = ICON_SND(SND.on); if (SND.on) SND.joker(); };
    $("#stop").onclick = askStop;
  }
  const ansBtn = k => el.querySelector(`.ans[data-k="${k}"]`);
  function lockUI(){ el.querySelectorAll(".ans").forEach(b => b.disabled = true); el.querySelector(".jk").classList.add("busy"); }

  function choose(k){
    if (phase !== "ask" && phase !== "confirm") return;
    if (phase === "confirm" && sel === k) return logIn();
    el.querySelectorAll(".ans").forEach(b => b.classList.remove("sel"));
    sel = k; ansBtn(k).classList.add("sel"); phase = "confirm";
    $("#panel").innerHTML = `<div class="spanel"><span class="t">Ist ${"ABCD"[k]} deine endgültige Antwort?</span>
      <div class="sbtns"><button class="sbtn" id="login">Einloggen</button><button class="sbtn ghost" id="undo">Nochmal überlegen</button></div></div>`;
    $("#login").onclick = logIn;
    $("#undo").onclick = () => { ansBtn(sel).classList.remove("sel"); sel = null; phase = "ask"; $("#panel").innerHTML = ""; };
  }

  function logIn(){
    phase = "wait"; lockUI();
    const b = ansBtn(sel); b.classList.add("lock"); SND.lock();
    $("#panel").innerHTML = `<div class="spanel"><span class="t" style="color:var(--dim)">Antwort ${"ABCD"[sel]} ist eingeloggt …</span></div>`;
    setTimeout(reveal, 1700);
  }

  function reveal(){
    const R = rounds[i], b = ansBtn(sel), rk = R.opts.findIndex(o => o.ok), right = R.opts[sel].ok;
    b.classList.remove("lock", "sel");
    const rb = ansBtn(rk); rb.classList.add("ok", "flash");
    if (!right) b.classList.add("no");
    history.push({q: R.q, chosen: R.opts[sel].s, ok: right});
    right ? SND.right() : SND.wrong();
    phase = "reveal";
    const last = i === rounds.length - 1;
    const safeNow = right && SAFE().includes(i);
    const next = right && !last ? `Weiter zur Frage um ${euro(P(i + 1))}` : right ? "Gewinn ansehen" : "Zur Auswertung";
    $("#panel").innerHTML = `
      ${safeNow ? `<div class="spanel safe"><span class="t">◆ ${euro(P(i))} sind dir sicher!</span><p>Ab jetzt fällst du bei einer falschen Antwort nicht mehr unter diesen Betrag.</p></div>` : ""}
      <div class="spanel ${right ? "good" : "bad"}">
        <span class="t">${right ? "Richtig!" : "Leider falsch."}</span>
        ${!right ? `<p>Richtig wäre <b>${"ABCD"[rk]}: ${esc(R.q.r)}</b></p>` : ""}
        ${R.q.erkl ? `<p>${R.q.erkl}</p>` : ""}
        <div class="sbtns"><button class="sbtn" id="next">${next}</button></div>
      </div>`;
    tex($("#panel"));
    if (right){
      const li = el.querySelectorAll(".ladder li")[i]; if (li){ li.classList.remove("now"); li.classList.add("done"); }
      const mi = el.querySelectorAll(".mini i")[i]; if (mi){ mi.className = "done"; }
    }
    if (safeNow){ SND.safe(); confetti($("#stage")); }
    $("#next").onclick = () => {
      if (!right) return end("falsch");
      if (last) return end("sieg");
      i++; round();
    };
    $("#next").focus({preventScroll: true});
  }

  /* ---- Joker ---- */
  function fifty(){
    if (phase !== "ask" && phase !== "confirm") return;
    used.fifty = true; $("#j50").disabled = true; SND.joker();
    const R = rounds[i];
    const wrong = shuffle(R.opts.map((o, k) => k).filter(k => !R.opts[k].ok && k !== sel)).slice(0, 2);
    wrong.forEach(k => { const b = ansBtn(k); b.classList.add("gone"); b.disabled = true; });
  }
  function pub(){
    if (phase !== "ask" && phase !== "confirm") return;
    used.pub = true; $("#jpub").disabled = true; SND.joker();
    const R = rounds[i];
    const vis = R.opts.map((o, k) => k).filter(k => !ansBtn(k).classList.contains("gone"));
    const wrong = vis.filter(k => !R.opts[k].ok);
    const hard = wrong.length ? wrong.reduce((s, k) => s + R.opts[k].tier, 0) / wrong.length : 0;
    let right = 74 - hard * 13 - (R.q.d || 2) * 4 + (Math.random() * 16 - 8);
    right = Math.max(28, Math.min(88, right));
    const w = wrong.map(k => 0.6 + R.opts[k].tier * 1.1 + Math.random());
    const sum = w.reduce((a, b) => a + b, 0) || 1;
    const v = R.opts.map(() => 0);
    vis.forEach(k => { v[k] = R.opts[k].ok ? right : (100 - right) * w[wrong.indexOf(k)] / sum; });
    $("#jout").innerHTML = `<div class="spanel"><span class="t" style="font-size:18px;color:var(--gold)">Das Publikum hat abgestimmt</span>
      <div class="bars">${v.map((x, k) => `<div><span>${vis.includes(k) ? Math.round(x) + " %" : ""}</span><i data-h="${x}"></i><b>${"ABCD"[k]}</b></div>`).join("")}</div></div>`;
    requestAnimationFrame(() => requestAnimationFrame(() => el.querySelectorAll(".bars i").forEach(b => b.style.height = (+b.dataset.h * 0.9) + "px")));
  }
  function tel(){
    if (phase !== "ask" && phase !== "confirm") return;
    used.tel = true; $("#jtel").disabled = true; SND.joker();
    $("#jout").innerHTML = `<div class="spanel"><span class="t" style="font-size:18px;color:var(--gold)">Dein Telefonjoker meint:</span><p>„${rounds[i].q.tipp || "Da bin ich mir leider auch nicht sicher."}“</p></div>`;
    tex($("#jout"));
  }
  function zusatz(){
    if (phase !== "ask" && phase !== "confirm") return;
    used.zusatz = true; $("#jzj").disabled = true; SND.joker();
    const R = rounds[i];
    const vis = R.opts.map((o, k) => k).filter(k => !ansBtn(k).classList.contains("gone"));
    const wrong = vis.filter(k => !R.opts[k].ok);
    const hard = wrong.length ? wrong.reduce((s, k) => s + R.opts[k].tier, 0) / wrong.length : 0;
    const pRight = Math.max(0.45, Math.min(0.92, 0.9 - hard * 0.13 - ((R.q.d || 2) - 1) * 0.05));
    const rk = R.opts.findIndex(o => o.ok);
    const isRight = Math.random() < pRight || !wrong.length;
    let k = rk;
    if (!isRight){
      const hardest = Math.max(...wrong.map(x => R.opts[x].tier));
      const cand = wrong.filter(x => R.opts[x].tier === hardest);
      k = cand[Math.floor(Math.random() * cand.length)];
    }
    const sure = isRight ? Math.random() < 0.6 : Math.random() < 0.35;
    const saetze = sure
      ? [`Das hatten wir genau so in der Übung. Ich bin mir ziemlich sicher: ${"ABCD"[k]}.`, `Ganz klar ${"ABCD"[k]}. Das steht so im Skript.`]
      : [`Ich würde ${"ABCD"[k]} nehmen, aber ganz sicher bin ich nicht.`, `Ich glaube, es ist ${"ABCD"[k]}. Die anderen sehen aber auch nicht ganz falsch aus.`];
    $("#jout").innerHTML = `<div class="spanel"><span class="t" style="font-size:18px;color:var(--gold)">Ein Kommilitone steht auf:</span>
      <p>„${saetze[Math.floor(Math.random() * saetze.length)]}“</p></div>`;
  }
  function askStop(){
    if (phase !== "ask" && phase !== "confirm") return;
    const g = i > 0 ? P(i - 1) : 0;
    $("#panel").innerHTML = `<div class="spanel"><span class="t">Mit ${euro(g)} aussteigen?</span>
      <div class="sbtns"><button class="sbtn" id="yes">Ja, aussteigen</button><button class="sbtn ghost" id="no">Weiterspielen</button></div></div>`;
    $("#yes").onclick = () => end("stop");
    $("#no").onclick = () => { $("#panel").innerHTML = ""; phase = "ask"; if (sel !== null){ const k = sel; sel = null; choose(k); } };
  }

  /* ---- Ende ---- */
  function end(why){
    let g = 0;
    if (why === "sieg") g = P(rounds.length - 1);
    else if (why === "stop") g = i > 0 ? P(i - 1) : 0;
    else { const s = SAFE().filter(x => x < i); g = s.length ? P(s[s.length - 1]) : 0; }
    const best = Math.max(store.get(recKey, 0), g); store.set(recKey, best);
    const nRight = history.filter(h => h.ok).length;
    const headline = why === "sieg" ? `Alle ${rounds.length} Fragen richtig!` : why === "stop" ? "Ausgestiegen" : "Spiel vorbei";
    phase = "end";
    el.innerHTML = `<div class="stage" id="stage"><span class="beam l"></span><span class="beam r"></span><div class="final">
      <span class="topic-name">${headline} · ${MODES[mode].name}${aktiveAuswahl() && auswahl.length < teileQuiz.length ? " · " + auswahl.map(id => esc(teileQuiz.find(x => x.id === id).titel)).join(", ") : ""}</span>
      <div class="big" id="amount">0 €</div>
      <span class="topic-name">${nRight} von ${history.length} beantworteten Fragen richtig · Rekord ${euro(best)}</span>
      <div class="sbtns" style="justify-content:center"><button class="sbtn" id="again">Neues Spiel</button></div>
      <div class="review">${history.map((h, k) => `<details${h.ok ? "" : " open"}>
        <summary><span class="mk ${h.ok ? "ok" : "no"}">${h.ok ? "✓" : "✗"}</span><span>${k + 1}. ${esc(h.q.f)}</span></summary>
        <div class="body">${h.ok ? "" : `<span class="lbl">Deine Antwort</span><span>${esc(h.chosen)}</span>`}
          <span class="lbl">Richtige Antwort</span><span>${esc(h.q.r)}</span>
          ${h.q.erkl ? `<span class="lbl">Erklärung</span><span>${h.q.erkl}</span>` : ""}</div></details>`).join("")}</div>
    </div></div>`;
    tex(el);
    $("#again").onclick = intro;
    const box = $("#amount"), t0 = performance.now(), dur = matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 1400;
    (function count(now){
      const p = dur ? Math.min(1, (now - t0) / dur) : 1;
      box.textContent = euro(Math.round(g * (1 - Math.pow(1 - p, 3))));
      if (p < 1) requestAnimationFrame(count);
    })(t0);
    if (g >= 16000) confetti($("#stage"));
    if (why === "sieg") SND.safe();
  }
  intro();
}
