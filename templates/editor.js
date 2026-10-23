/* ---------- Bearbeitungsmodus: Inhalte ändern, löschen, ergänzen – gespeichert über die GitHub-API ----------
   Änderungen landen in content/<datei>.edits.json im Repository; GitHub baut danach die Seite neu. */

const GH = {
  token(){ return store.get("gh-token", ""); },
  async api(pfad, opt = {}){
    let r;
    try {
      r = await fetch("https://api.github.com" + pfad, {cache: "no-store", ...opt, headers: {
        "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": "Bearer " + this.token(), ...(opt.body ? {"Content-Type": "application/json"} : {})}});
    } catch(e){ throw ghFehler(0); }
    return r;
  },
  async lesen(pfad){
    const r = await this.api(`/repos/${DATA.repo}/contents/${pfad}?ref=main`);
    if (r.status === 404) return {sha: null, data: {}};
    if (!r.ok) throw ghFehler(r.status);
    const j = await r.json();
    return {sha: j.sha, data: JSON.parse(b64dec(j.content || "") || "{}")};
  },
  async schreiben(pfad, data, sha, nachricht){
    const body = {message: nachricht, content: b64enc(JSON.stringify(data, null, 1) + "\n"), branch: "main"};
    if (sha) body.sha = sha;
    const r = await this.api(`/repos/${DATA.repo}/contents/${pfad}`, {method: "PUT", body: JSON.stringify(body)});
    if (!r.ok) throw ghFehler(r.status);
  }
};
function ghFehler(status){
  const text = {
    0: "Keine Verbindung zu GitHub. Prüfe die Internetverbindung.",
    401: "Der Zugangsschlüssel ist ungültig oder abgelaufen. Lege unter „Bearbeitungsmodus“ einen neuen an.",
    403: "Der Zugangsschlüssel darf nicht schreiben. Er braucht bei „Contents“ die Berechtigung „Read and write“.",
    404: "Repository nicht gefunden. Der Zugangsschlüssel muss Zugriff auf „betonbau4“ haben.",
    409: "Die Datei wurde gleichzeitig geändert. Bitte noch einmal speichern.",
    422: "GitHub hat die Änderung abgelehnt. Bitte noch einmal speichern."
  }[status] || `GitHub meldet einen Fehler (${status}). Bitte später erneut versuchen.`;
  const e = new Error(text); e.status = status; return e;
}
function b64dec(s){
  const bin = atob(String(s).replace(/\s/g, ""));
  return new TextDecoder().decode(Uint8Array.from(bin, c => c.charCodeAt(0)));
}
function b64enc(str){
  const bytes = new TextEncoder().encode(str); let bin = "";
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(bin);
}
const editsPfad = B => `content/${B.datei}.edits.json`;

/* Änderung immer auf dem neuesten Stand im Repository ausführen (mehrere Geräte, gleichzeitige Builds) */
async function speichern(B, nachricht, aendern){
  let fehler;
  for (let versuch = 0; versuch < 3; versuch++){
    const {sha, data} = await GH.lesen(editsPfad(B));
    aendern(data);
    aufraeumen(data);
    try {
      await GH.schreiben(editsPfad(B), data, sha, nachricht);
      B.edits = data;
      const i = DATA.basis.indexOf(B);
      DATA.themen[i] = applyEdits(B);
      return;
    } catch(e){ fehler = e; if (e.status !== 409 && e.status !== 422) throw e; }
  }
  throw fehler;
}
function aufraeumen(d){
  for (const k of Object.keys(d)){
    if (k === "_neu"){
      for (const t of Object.keys(d._neu)) if (!d._neu[t].length) delete d._neu[t];
      if (!Object.keys(d._neu).length) delete d._neu;
    } else {
      for (const u of Object.keys(d[k])) if (!Object.keys(d[k][u]).length) delete d[k][u];
      if (!Object.keys(d[k]).length) delete d[k];
    }
  }
}
function toast(text, art = ""){
  let el = document.getElementById("toast");
  if (!el){ el = document.createElement("div"); el.id = "toast"; el.setAttribute("role", "status"); document.body.appendChild(el); }
  el.className = art; el.textContent = text; el.hidden = false;
  clearTimeout(toast.t); toast.t = setTimeout(() => { el.hidden = true; }, art === "fehler" ? 9000 : 5000);
}
const neueUid = () => "n" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);

/* ---------- Einrichtung ---------- */
function Einrichtung(app){
  const tok = GH.token();
  app.innerHTML = `<div class="crumbs" style="margin-top:20px"><button class="back" id="home">← Alle Themen</button></div>
  <div class="thead"><span class="label">Für Bearbeiter</span><h2>Bearbeitungsmodus</h2>
    <p>Inhalte ändern, löschen und ergänzen. Änderungen werden im GitHub-Repository gespeichert und sind nach etwa einer Minute für alle online.</p></div>
  ${IN_FRAME ? `<p class="note">Der Bearbeitungsmodus funktioniert nur in der Web-App unter ${esc((DATA.site || "").replace(/^https?:\/\//, ""))}.</p>` : tok ? `
    <div class="panel ed-setup"><h3>Verbunden</h3><p id="gh-wer">Zugang wird geprüft …</p>
      <p>Die Schaltfläche „Inhalte bearbeiten“ findest du jetzt auf jeder Themenseite.</p>
      <div class="row"><button class="btn" id="zu-themen">Zu den Themen</button><button class="btn ghost" id="abmelden">Zugang von diesem Gerät entfernen</button></div></div>` : `
    <div class="panel ed-setup"><h3>Einmalig einrichten</h3>
      <p>Zum Speichern braucht die App einen Zugangsschlüssel von GitHub, der nur dieses eine Repository bearbeiten darf.</p>
      <ol>
        <li>Auf github.com oben rechts auf dein Profilbild → <b>Settings</b> → ganz unten <b>Developer settings</b>.</li>
        <li><b>Personal access tokens</b> → <b>Fine-grained tokens</b> → <b>Generate new token</b>.</li>
        <li>Name z. B. „Betonbau 4 App“, Ablaufdatum nach Wunsch (z. B. 1 Jahr).</li>
        <li><b>Repository access</b>: „Only select repositories“ → <b>betonbau4</b>.</li>
        <li><b>Permissions</b> → <b>Repository permissions</b> → <b>Contents</b>: „Read and write“.</li>
        <li><b>Generate token</b>, den Schlüssel (beginnt mit <span class="mono">github_pat_</span>) kopieren und hier einfügen.</li>
      </ol>
      <div class="fld wide"><label for="gh-tok">Zugangsschlüssel</label><input id="gh-tok" type="password" autocomplete="off" spellcheck="false" placeholder="github_pat_…"></div>
      <div class="row"><button class="btn" id="verbinden">Verbinden</button><span id="gh-msg" class="ed-msg"></span></div>
      <p class="ed-hinweis">Der Schlüssel wird nur auf diesem Gerät gespeichert. Die Web-App auf dem Home-Bildschirm hat eigenen Speicher – dort den Schlüssel einmal separat eintragen.</p>
    </div>`}`;
  $("#home").onclick = () => go("");
  if ($("#verbinden")) $("#verbinden").onclick = async () => {
    const v = $("#gh-tok").value.trim(), msg = $("#gh-msg");
    if (!v){ msg.textContent = "Bitte den Zugangsschlüssel einfügen."; return; }
    msg.textContent = "Prüfe …";
    store.set("gh-token", v);
    try {
      const r = await GH.api(`/repos/${DATA.repo}/contents/content?ref=main`);
      if (!r.ok) throw ghFehler(r.status);
      toast("Verbunden. Bearbeiten ist jetzt auf jeder Themenseite möglich.");
      Einrichtung(app);
    } catch(e){ store.set("gh-token", ""); msg.textContent = e.message; }
  };
  if ($("#abmelden")) $("#abmelden").onclick = () => { store.set("gh-token", ""); toast("Zugang von diesem Gerät entfernt."); Einrichtung(app); };
  if ($("#zu-themen")) $("#zu-themen").onclick = () => go("");
  if ($("#gh-wer")) GH.api("/user").then(r => r.ok ? r.json() : Promise.reject(ghFehler(r.status)))
    .then(u => { $("#gh-wer").textContent = `Angemeldet als ${u.login}. Speichern geht in „${DATA.repo}“.`; })
    .catch(e => { if ($("#gh-wer")) $("#gh-wer").textContent = e.message; });
}

/* ---------- Was bearbeitet werden kann ---------- */
const ED_TYPEN = {
  karten: {name: "Karteikarten", titel: x => x.v, sub: x => x.r, felder: [
    {k: "v", l: "Vorderseite"}, {k: "r", l: "Rückseite", typ: "area"},
    {k: "video", l: "Video mit Zeitstempel (optional)", typ: "video"}, {k: "teil", typ: "teil"}],
    pruef: x => !x.v || !x.r ? "Vorder- und Rückseite ausfüllen." : ""},
  quiz: {name: "Quizfragen", titel: x => x.f, sub: x => "Richtig: " + x.r, felder: [
    {k: "f", l: "Frage", typ: "area"}, {k: "r", l: "Richtige Antwort"},
    {k: "falsch.leicht", l: "Falsche Antworten – leicht (offensichtlich falsch), eine pro Zeile", typ: "lines"},
    {k: "falsch.mittel", l: "Falsche Antworten – mittel (plausibel), eine pro Zeile", typ: "lines"},
    {k: "falsch.schwer", l: "Falsche Antworten – schwer (typische Fehler), eine pro Zeile", typ: "lines"},
    {k: "d", l: "Schwierigkeit", typ: "select", opt: [[1, "1 – Fragen 1 bis 5"], [2, "2 – Fragen 6 bis 10"], [3, "3 – Fragen 11 bis 15"]]},
    {k: "tipp", l: "Hinweis für den Telefonjoker"}, {k: "erkl", l: "Erklärung nach der Auflösung", typ: "area"}, {k: "teil", typ: "teil"}],
    pruef: x => {
      if (!x.f || !x.r) return "Frage und richtige Antwort ausfüllen.";
      const n = ["leicht", "mittel", "schwer"].reduce((s, k) => s + (x.falsch?.[k]?.length || 0), 0);
      return n < 3 ? "Mindestens drei falsche Antworten angeben." : "";
    }},
  formeln: {name: "Formelsammlung", titel: x => (x.gl ? `(${x.gl}) ` : "") + x.name, sub: x => `$${x.f}$`, felder: [
    {k: "name", l: "Bezeichnung"}, {k: "gl", l: "Gleichungsnummer aus dem Skript (optional)"},
    {k: "f", l: "Formel in LaTeX, ohne Dollarzeichen", typ: "area", formel: true}, {k: "e", l: "Hinweis", typ: "area"}, {k: "teil", typ: "teil"}],
    pruef: x => !x.name || !x.f ? "Bezeichnung und Formel ausfüllen." : ""},
  paare: {name: "Zuordnen", titel: x => x.a, sub: x => "→ " + x.b, felder: [
    {k: "a", l: "Begriff oder Symbol (links)"}, {k: "b", l: "Bedeutung (rechts)"}, {k: "teil", typ: "teil"}],
    pruef: x => !x.a || !x.b ? "Beide Seiten ausfüllen." : ""},
  aufgaben: {name: "Übungsaufgaben", nurAusblenden: true, titel: x => x.titel, sub: x => (x.schritte || []).length + " Schritte"},
  mindmap: {name: "Mindmap"}
};
const getPfad = (o, k) => k.split(".").reduce((a, x) => a == null ? a : a[x], o);
function setPfad(o, k, v){ const t = k.split("."); let a = o; t.slice(0, -1).forEach(x => { a[x] = a[x] && typeof a[x] === "object" ? {...a[x]} : {}; a = a[x]; }); a[t[t.length - 1]] = v; }

/* ---------- Editor ---------- */
function Editor(t, el){
  const B = DATA.basis.find(x => x.id === t.id);
  let typ = store.get("ed-typ", "karten"), suche = "", offen = null;
  if (IN_FRAME || !GH.token()){
    el.innerHTML = `<p class="note">${IN_FRAME ? `Bearbeiten funktioniert nur in der Web-App unter ${esc((DATA.site || "").replace(/^https?:\/\//, ""))}.` : "Zum Bearbeiten zuerst den Bearbeitungsmodus einrichten."}</p>
      ${IN_FRAME ? "" : `<button class="btn" id="ed-setup">Bearbeitungsmodus einrichten</button>`}`;
    if ($("#ed-setup")) $("#ed-setup").onclick = () => go("bearbeiten");
    return;
  }
  const typen = Object.keys(ED_TYPEN).filter(k => k === "mindmap" ? B.mindmap : (B[k] || []).length || (B.edits?._neu?.[k] || []).length);
  if (!typen.includes(typ)) typ = typen[0];
  const teilName = id => (B.teile || []).find(x => x.id === id)?.titel || "";
  const E = () => B.edits || {};

  function zustand(){   /* Basisliste mit Status je Eintrag */
    const m = E()[typ] || {}, neu = (E()._neu || {})[typ] || [];
    const basis = (B[typ] || []).map(x => {
      const ed = m[x.uid] || {};
      return {orig: x, akt: {...x, ...ed}, uid: x.uid, del: !!ed._del, bearb: Object.keys(ed).some(k => k !== "_del"), neu: false};
    });
    return basis.concat(neu.map(x => ({orig: null, akt: x, uid: x.uid, del: false, bearb: false, neu: true})));
  }

  function draw(){
    const T = ED_TYPEN[typ];
    el.innerHTML = `
      <div class="ed-bar">
        <div class="seg ed-tabs" role="tablist">${typen.map(k => `<button type="button" role="tab" data-t="${k}" class="${k === typ ? "on" : ""}" aria-selected="${k === typ}">${ED_TYPEN[k].name}</button>`).join("")}</div>
      </div>
      <p class="ed-hinweis">Änderungen werden sofort gespeichert und sind nach etwa einer Minute für alle online. Gelöschte Inhalte lassen sich unten wiederherstellen.</p>
      <div id="ed-body"></div>`;
    el.querySelectorAll(".ed-tabs button").forEach(b => b.onclick = () => { typ = b.dataset.t; store.set("ed-typ", typ); offen = null; suche = ""; draw(); });
    typ === "mindmap" ? drawMindmap() : drawListe();
  }

  function drawListe(){
    const T = ED_TYPEN[typ], z = zustand();
    const sichtbar = z.filter(x => !x.del), geloescht = z.filter(x => x.del);
    const q = suche.toLowerCase();
    const treffer = sichtbar.filter(x => !q || JSON.stringify(x.akt).toLowerCase().includes(q));
    $("#ed-body").innerHTML = `
      <div class="row ed-tools">${T.nurAusblenden ? "" : `<button class="btn" id="ed-neu">Neu hinzufügen</button>`}
        <input id="ed-suche" class="ed-suche" type="search" placeholder="Suchen …" value="${esc(suche)}" aria-label="Suchen">
        <span class="label">${sichtbar.length} Einträge</span></div>
      ${offen === "neu" ? `<div class="ed-item open">${formular(null)}</div>` : ""}
      <div class="ed-list">${treffer.map(x => `
        <div class="ed-item ${offen === x.uid ? "open" : ""}" data-u="${x.uid}">
          <div class="ed-head">
            <div class="ed-txt"><span class="ed-t">${esc(T.titel(x.akt) || "–")}</span><span class="ed-s">${esc(T.sub(x.akt) || "")}</span>
              <span class="ed-tags">${x.akt.teil ? `<span class="chip">${esc(teilName(x.akt.teil))}</span>` : ""}${x.bearb ? `<span class="chip warn">bearbeitet</span>` : ""}${x.neu ? `<span class="chip ok">neu</span>` : ""}</span></div>
            <div class="ed-btns">${T.nurAusblenden ? "" : `<button class="btn ghost ed-edit" type="button">${offen === x.uid ? "Schließen" : "Bearbeiten"}</button>`}
              <button class="btn bad ed-del" type="button">${T.nurAusblenden ? "Ausblenden" : "Löschen"}</button></div>
          </div>
          ${offen === x.uid ? formular(x) : ""}
        </div>`).join("") || `<p class="note">${q ? "Keine Treffer." : "Noch keine Einträge."}</p>`}</div>
      ${geloescht.length ? `<details class="ed-weg"><summary>${T.nurAusblenden ? "Ausgeblendet" : "Gelöscht"} (${geloescht.length})</summary>${geloescht.map(x => `
        <div class="ed-item" data-u="${x.uid}"><div class="ed-head"><div class="ed-txt"><span class="ed-t">${esc(T.titel(x.akt))}</span></div>
          <div class="ed-btns"><button class="btn ghost ed-restore" type="button">Wiederherstellen</button></div></div></div>`).join("")}</details>` : ""}`;
    tex($("#ed-body"));
    const body = $("#ed-body");
    if ($("#ed-neu")) $("#ed-neu").onclick = () => { offen = offen === "neu" ? null : "neu"; drawListe(); body.querySelector(".ed-item.open input, .ed-item.open textarea")?.focus(); };
    $("#ed-suche").oninput = e => { suche = e.target.value; const pos = e.target.selectionStart; drawListe(); const s = $("#ed-suche"); s.focus(); s.setSelectionRange(pos, pos); };
    body.querySelectorAll(".ed-edit").forEach(b => b.onclick = () => { const u = b.closest(".ed-item").dataset.u; offen = offen === u ? null : u; drawListe(); });
    body.querySelectorAll(".ed-del").forEach(b => b.onclick = () => loeschen(b, z.find(x => x.uid === b.closest(".ed-item").dataset.u)));
    body.querySelectorAll(".ed-restore").forEach(b => b.onclick = () => wiederherstellen(b, z.find(x => x.uid === b.closest(".ed-item").dataset.u)));
    const form = body.querySelector("form.ed-form");
    if (form) bindFormular(form, offen === "neu" ? null : z.find(x => x.uid === offen));
  }

  function formular(x){
    const T = ED_TYPEN[typ], a = x ? x.akt : {teil: (B.teile || [])[0]?.id, d: 2};
    const feld = f => {
      const id = "f-" + f.k.replace(".", "-"), v = getPfad(a, f.k);
      if (f.typ === "teil") return (B.teile || []).length ? `<div class="fld wide"><label for="${id}">Vorlesungsteil</label><select id="${id}" data-k="teil">${B.teile.map(o => `<option value="${o.id}" ${o.id === v ? "selected" : ""}>${esc(o.titel)}</option>`).join("")}</select></div>` : "";
      if (f.typ === "select") return `<div class="fld wide"><label for="${id}">${f.l}</label><select id="${id}" data-k="${f.k}" data-num="1">${f.opt.map(([o, l]) => `<option value="${o}" ${o == v ? "selected" : ""}>${l}</option>`).join("")}</select></div>`;
      if (f.typ === "video"){ const vid = [].concat(v || [])[0] || {};
        return `<fieldset class="ed-video"><legend>${f.l}</legend>
          <div class="fld wide"><label for="${id}-url">Link</label><input id="${id}-url" data-vk="url" value="${esc(vid.url || "")}" placeholder="https://…"></div>
          <div class="ed-2"><div class="fld wide"><label for="${id}-t">Zeitstempel</label><input id="${id}-t" data-vk="t" value="${esc(vid.t || "")}" placeholder="12:34"></div>
          <div class="fld wide"><label for="${id}-l">Beschriftung</label><input id="${id}-l" data-vk="label" value="${esc(vid.label || "")}" placeholder="VL 3"></div></div></fieldset>`; }
      const val = f.typ === "lines" ? (v || []).join("\n") : (v ?? "");
      const ctl = f.typ === "area" || f.typ === "lines"
        ? `<textarea id="${id}" data-k="${f.k}" ${f.typ === "lines" ? 'data-lines="1"' : ""} rows="${f.typ === "lines" ? 3 : 3}" ${f.formel ? 'class="mono" spellcheck="false"' : ""}>${esc(val)}</textarea>`
        : `<input id="${id}" data-k="${f.k}" value="${esc(val)}">`;
      return `<div class="fld wide"><label for="${id}">${f.l}</label>${ctl}<div class="ed-prev" data-for="${id}" ${f.formel ? 'data-formel="1"' : ""}></div></div>`;
    };
    return `<form class="ed-form" novalidate>
      ${T.felder.map(feld).join("")}
      <p class="ed-tipp">Formeln zwischen Dollarzeichen schreiben, z. B. <span class="mono">$T_{\\mathrm{Ed}}$</span>. Darunter erscheint die Vorschau.</p>
      <div class="row"><button class="btn" type="submit">Speichern</button><button class="btn ghost ed-cancel" type="button">Abbrechen</button>
        ${x && x.bearb ? `<button class="btn ghost ed-orig" type="button">Original wiederherstellen</button>` : ""}
        <span class="ed-msg" role="status"></span></div>
    </form>`;
  }

  function lesenFormular(form, x){
    const T = ED_TYPEN[typ], neu = x ? JSON.parse(JSON.stringify(x.akt)) : {};
    form.querySelectorAll("[data-k]").forEach(c => {
      let v = c.value;
      if (c.dataset.lines) v = v.split("\n").map(s => s.trim()).filter(Boolean);
      else if (c.dataset.num) v = +v;
      else v = v.trim();
      setPfad(neu, c.dataset.k, v);
    });
    const vf = form.querySelector(".ed-video");
    if (vf){
      const vid = {}; vf.querySelectorAll("[data-vk]").forEach(c => { if (c.value.trim()) vid[c.dataset.vk] = c.value.trim(); });
      const rest = [].concat(x?.akt.video || []).slice(1);
      if (vid.url) neu.video = rest.length ? [vid, ...rest] : vid; else if (rest.length) neu.video = rest; else delete neu.video;
    }
    if (typ === "quiz"){ neu.falsch = {...(neu.falsch || {})}; for (const k of Object.keys(neu.falsch)) if (!neu.falsch[k].length) delete neu.falsch[k]; }
    for (const k of Object.keys(neu)) if (neu[k] === "") delete neu[k];
    for (const k of ["uid", "_bearbeitet", "_neu"]) delete neu[k];
    return {neu, fehler: T.pruef ? T.pruef(neu) : ""};
  }

  function bindFormular(form, x){
    const msg = form.querySelector(".ed-msg");
    const vorschau = () => form.querySelectorAll(".ed-prev").forEach(p => {
      const c = form.querySelector("#" + p.dataset.for), v = c.value.trim();
      const zeigen = p.dataset.formel ? v : (/\$/.test(v) ? v : "");
      p.hidden = !zeigen;
      if (!zeigen) return;
      p.innerHTML = p.dataset.formel ? `$\\displaystyle ${esc(v)}$` : esc(v).replace(/\n/g, "<br>");
      tex(p);
    });
    let tmr; form.addEventListener("input", () => { clearTimeout(tmr); tmr = setTimeout(vorschau, 350); });
    vorschau();
    form.querySelector(".ed-cancel").onclick = () => { offen = null; drawListe(); };
    const orig = form.querySelector(".ed-orig");
    if (orig) orig.onclick = () => ausfuehren(orig, msg, `${ED_TYPEN[typ].name}: Original wiederhergestellt`, d => { if (d[typ]) delete d[typ][x.uid]; }, "Original wiederhergestellt.");
    form.onsubmit = ev => {
      ev.preventDefault();
      const {neu, fehler} = lesenFormular(form, x);
      if (fehler){ msg.textContent = fehler; msg.className = "ed-msg fehler"; return; }
      const titel = kurz(ED_TYPEN[typ].titel(neu));
      if (!x){
        neu.uid = neueUid();
        return ausfuehren(form.querySelector("[type=submit]"), msg, `${ED_TYPEN[typ].name}: „${titel}“ hinzugefügt`,
          d => { d._neu = d._neu || {}; (d._neu[typ] = d._neu[typ] || []).push(neu); }, "Hinzugefügt.");
      }
      if (x.neu){
        neu.uid = x.uid;
        return ausfuehren(form.querySelector("[type=submit]"), msg, `${ED_TYPEN[typ].name}: „${titel}“ geändert`,
          d => { const l = d._neu?.[typ] || []; const i = l.findIndex(y => y.uid === x.uid); if (i >= 0) l[i] = neu; else { d._neu = d._neu || {}; (d._neu[typ] = l).push(neu); } }, "Gespeichert.");
      }
      const diff = {};
      for (const k of new Set([...Object.keys(neu), ...Object.keys(x.orig)])){
        if (k === "uid" || k.startsWith("_")) continue;
        if (JSON.stringify(neu[k]) !== JSON.stringify(x.orig[k])) diff[k] = neu[k] === undefined ? null : neu[k];
      }
      return ausfuehren(form.querySelector("[type=submit]"), msg, `${ED_TYPEN[typ].name}: „${titel}“ geändert`,
        d => { d[typ] = d[typ] || {}; if (Object.keys(diff).length) d[typ][x.uid] = diff; else delete d[typ][x.uid]; }, "Gespeichert.");
    };
  }

  function loeschen(btn, x){
    if (btn.dataset.sicher !== "1"){
      btn.dataset.sicher = "1"; btn.textContent = ED_TYPEN[typ].nurAusblenden ? "Wirklich ausblenden?" : "Wirklich löschen?";
      setTimeout(() => { if (btn.isConnected && btn.dataset.sicher === "1"){ btn.dataset.sicher = ""; btn.textContent = ED_TYPEN[typ].nurAusblenden ? "Ausblenden" : "Löschen"; } }, 4000);
      return;
    }
    const titel = kurz(ED_TYPEN[typ].titel(x.akt));
    ausfuehren(btn, null, `${ED_TYPEN[typ].name}: „${titel}“ gelöscht`, d => {
      if (x.neu){ const l = d._neu?.[typ] || []; const i = l.findIndex(y => y.uid === x.uid); if (i >= 0) l.splice(i, 1); }
      else { d[typ] = d[typ] || {}; d[typ][x.uid] = {...(d[typ][x.uid] || {}), _del: true}; }
    }, x.neu ? "Gelöscht." : (ED_TYPEN[typ].nurAusblenden ? "Ausgeblendet." : "Gelöscht. Unter „Gelöscht“ wiederherstellbar."));
  }
  function wiederherstellen(btn, x){
    ausfuehren(btn, null, `${ED_TYPEN[typ].name}: „${kurz(ED_TYPEN[typ].titel(x.akt))}“ wiederhergestellt`,
      d => { if (d[typ]?.[x.uid]) delete d[typ][x.uid]._del; }, "Wiederhergestellt.");
  }

  async function ausfuehren(btn, msg, nachricht, aendern, ok){
    const alle = el.querySelectorAll("button"); alle.forEach(b => b.disabled = true);
    const alt = btn.textContent; btn.textContent = "Speichert …";
    try {
      await speichern(B, nachricht, aendern);
      alle.forEach(b => b.disabled = false);
      offen = null; toast(ok + " In etwa einer Minute für alle online.");
      typ === "mindmap" ? drawMindmap() : drawListe();
    } catch(e){
      alle.forEach(b => b.disabled = false); btn.textContent = alt;
      if (msg){ msg.textContent = e.message; msg.className = "ed-msg fehler"; } else toast(e.message, "fehler");
    }
  }

  /* ---------- Mindmap als Baum ---------- */
  function drawMindmap(){
    const m = E().mindmap || {}, nn = (E()._neu || {}).mindmap || [];
    const geloescht = [];
    const knoten = (n, tiefe, istNeu) => {
      const ed = m[n.uid] || {};
      if (ed._del){ geloescht.push({uid: n.uid, t: n.t}); return ""; }
      const text = ed.t !== undefined ? ed.t : n.t;
      const kinder = (n.c || []).map(c => knoten(c, tiefe + 1, false)).join("") +
        nn.filter(x => x.parent === n.uid).map(x => knoten({uid: x.uid, t: x.t}, tiefe + 1, true)).join("");
      const root = tiefe === 0;
      return `<li class="mm-ed" data-u="${n.uid}" data-neu="${istNeu ? 1 : ""}">
        <div class="mm-row">${offen === n.uid
          ? `<form class="mm-form"><input value="${esc(text)}" aria-label="Text"><button class="btn" type="submit">Speichern</button><button class="btn ghost mm-x" type="button">Abbrechen</button></form>`
          : `<span class="mm-t">${esc(text)}</span>${ed.t !== undefined ? `<span class="chip warn">bearbeitet</span>` : ""}${istNeu ? `<span class="chip ok">neu</span>` : ""}
            <span class="mm-btns">${root ? "" : `<button class="linkbtn mm-e" type="button">Bearbeiten</button>`}
            <button class="linkbtn mm-a" type="button">${root ? "+ Zweig" : "+ Unterpunkt"}</button>
            ${root ? "" : `<button class="linkbtn mm-d" type="button">Löschen</button>`}</span>`}</div>
        ${offen === "add:" + n.uid ? `<form class="mm-form mm-add"><input placeholder="Neuer Punkt" aria-label="Neuer Punkt"><button class="btn" type="submit">Hinzufügen</button><button class="btn ghost mm-x" type="button">Abbrechen</button></form>` : ""}
        ${kinder ? `<ul>${kinder}</ul>` : ""}</li>`;
    };
    const baum = knoten(B.mindmap, 0, false);
    $("#ed-body").innerHTML = `<ul class="mm-edtree">${baum}</ul>
      ${geloescht.length ? `<details class="ed-weg"><summary>Gelöscht (${geloescht.length})</summary>${geloescht.map(g => `
        <div class="ed-item" data-u="${g.uid}"><div class="ed-head"><div class="ed-txt"><span class="ed-t">${esc(g.t)}</span></div>
        <div class="ed-btns"><button class="btn ghost mm-r" type="button">Wiederherstellen</button></div></div></div>`).join("")}</details>` : ""}`;
    tex($("#ed-body"));
    const body = $("#ed-body"), li = b => b.closest("li.mm-ed");
    body.querySelectorAll(".mm-e").forEach(b => b.onclick = () => { offen = li(b).dataset.u; drawMindmap(); body.querySelector(".mm-form input")?.focus(); });
    body.querySelectorAll(".mm-a").forEach(b => b.onclick = () => { offen = "add:" + li(b).dataset.u; drawMindmap(); body.querySelector(".mm-add input")?.focus(); });
    body.querySelectorAll(".mm-x").forEach(b => b.onclick = () => { offen = null; drawMindmap(); });
    body.querySelectorAll(".mm-d").forEach(b => b.onclick = () => {
      if (b.dataset.sicher !== "1"){ b.dataset.sicher = "1"; b.textContent = "Mit Unterpunkten löschen?"; return; }
      const u = li(b).dataset.u, neu = li(b).dataset.neu;
      ausfuehren(b, null, `Mindmap: Punkt gelöscht`, d => {
        if (neu){
          const l = d._neu?.mindmap || [], weg = new Set([u]);
          let mehr = true; while (mehr){ mehr = false; l.forEach(x => { if (weg.has(x.parent) && !weg.has(x.uid)){ weg.add(x.uid); mehr = true; } }); }
          if (d._neu?.mindmap) d._neu.mindmap = l.filter(x => !weg.has(x.uid));
        } else { d.mindmap = d.mindmap || {}; d.mindmap[u] = {...(d.mindmap[u] || {}), _del: true}; }
      }, "Gelöscht.");
    });
    body.querySelectorAll(".mm-r").forEach(b => b.onclick = () => {
      const u = b.closest(".ed-item").dataset.u;
      ausfuehren(b, null, "Mindmap: Punkt wiederhergestellt", d => { if (d.mindmap?.[u]) delete d.mindmap[u]._del; }, "Wiederhergestellt.");
    });
    body.querySelectorAll("form.mm-form").forEach(f => f.onsubmit = ev => {
      ev.preventDefault();
      const v = f.querySelector("input").value.trim(), btn = f.querySelector("[type=submit]");
      if (!v) return;
      const node = f.closest("li.mm-ed"), u = node.dataset.u;
      if (f.classList.contains("mm-add")){
        const neu = {uid: neueUid(), parent: u, t: v};
        return ausfuehren(btn, null, `Mindmap: „${kurz(v)}“ hinzugefügt`, d => { d._neu = d._neu || {}; (d._neu.mindmap = d._neu.mindmap || []).push(neu); }, "Hinzugefügt.");
      }
      ausfuehren(btn, null, `Mindmap: „${kurz(v)}“ geändert`, d => {
        if (node.dataset.neu){ const x = (d._neu?.mindmap || []).find(y => y.uid === u); if (x) x.t = v; }
        else { d.mindmap = d.mindmap || {}; const orig = suchKnoten(B.mindmap, u)?.t;
          if (v === orig){ if (d.mindmap[u]) delete d.mindmap[u].t; } else d.mindmap[u] = {...(d.mindmap[u] || {}), t: v}; }
      }, "Gespeichert.");
    });
  }
  const suchKnoten = (n, u) => n.uid === u ? n : (n.c || []).reduce((r, c) => r || suchKnoten(c, u), null);
  const kurz = s => { s = String(s || "").replace(/\$([^$]*)\$/g, "$1").replace(/\\[a-zA-Z]+|[{}]/g, "").replace(/\s+/g, " ").trim(); return s.length > 60 ? s.slice(0, 57) + "…" : s; };

  draw();
  /* Neuesten Stand holen (z. B. Änderungen von einem anderen Gerät, die noch nicht gebaut sind) */
  GH.lesen(editsPfad(B)).then(({data}) => {
    if (JSON.stringify(data) !== JSON.stringify(B.edits || {})){
      B.edits = data; DATA.themen[DATA.basis.indexOf(B)] = applyEdits(B);
      if (el.isConnected && !offen) draw();
    }
  }).catch(() => {});
}
