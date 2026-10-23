"""Betonbau 4 Lernplattform – Build-Skript.

Liest alle Themen aus content/*.json, prüft sie und erzeugt:
  dist/index.html            -> komplette Web-App (offline-fähig, iPad/iPhone-Homescreen)
  dist/manifest.webmanifest  -> App-Manifest
  dist/icon-180.png, icon-512.png
  dist/<Thema>_Bemessung.xlsx -> Tabellenkalkulation mit Formeln (falls Rechner vorhanden)
  artifact.html              -> Variante zur Vorschau als Claude-Artifact

Aufruf:  python build.py
Neues Thema: einfach content/02_<name>.json nach dem Muster von 01_torsion.json anlegen.
"""
import hashlib
import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
DIST = ROOT / "dist"
TEMPLATE = ROOT / "templates" / "app.html"

PFLICHT = ["id", "nr", "titel", "untertitel"]


def repo_name():
    return os.environ.get("GITHUB_REPOSITORY", "Stzi00001/betonbau4")


def _uid(*teile):
    return hashlib.sha1("|".join(map(str, teile)).encode("utf-8")).hexdigest()[:8]


SCHLUESSEL = {"karten": lambda x: x["v"], "quiz": lambda x: x["f"], "formeln": lambda x: x["name"],
              "paare": lambda x: x["a"] + "|" + x["b"], "aufgaben": lambda x: x["titel"]}


def ids_vergeben(t):
    """Stabile IDs je Inhalt, damit Bearbeitungen dem richtigen Eintrag zugeordnet bleiben."""
    alle = {}
    for typ, key in SCHLUESSEL.items():
        gesehen = set()
        for x in t.get(typ, []):
            u = _uid(typ, key(x))
            while u in gesehen:
                u = _uid(u, "x")
            gesehen.add(u)
            x["uid"] = u
        alle[typ] = gesehen
    knoten = set()

    def mm(n, pfad):
        n["uid"] = _uid("mindmap", *pfad, n["t"])
        knoten.add(n["uid"])
        for c in n.get("c", []):
            mm(c, pfad + [n["t"]])
    if t.get("mindmap"):
        mm(t["mindmap"], [])
    alle["mindmap"] = knoten
    return alle


def bearbeitungen_laden(f, t, uids):
    """content/<datei>.edits.json – im Bearbeitungsmodus der App gespeicherte Änderungen."""
    pfad = f.with_name(f.stem + ".edits.json")
    if not pfad.exists():
        return {}
    try:
        e = json.loads(pfad.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        print(f"Warnung: {pfad.name} ist kein gültiges JSON und wird ignoriert ({err})")
        return {}
    for typ, eintraege in e.items():
        if typ.startswith("_") or not isinstance(eintraege, dict):
            continue
        weg = [u for u in eintraege if u not in uids.get(typ, set())]
        if weg:
            print(f"Hinweis: {pfad.name}: {len(weg)} Bearbeitung(en) in '{typ}' passen zu keinem Inhalt mehr (Original geändert?)")
    anz = sum(len(v) for k, v in e.items() if not k.startswith("_") and isinstance(v, dict))
    anz += sum(len(v) for v in e.get("_neu", {}).values())
    if anz:
        print(f"Bearbeitungen angewendet: {pfad.name} ({anz})")
    return e


def site_url():
    """Adresse der veröffentlichten Seite (auf GitHub automatisch aus dem Repository-Namen)."""
    owner, name = repo_name().split("/", 1)
    return f"https://{owner.lower()}.github.io/{name}/"


def pdf_liste(t):
    """Welche PDFs es für ein Thema gibt (Dateiname = <id>-<art>.pdf)."""
    arten = []
    if t.get("formeln"):
        arten.append(("formelsammlung", "Formelsammlung"))
    if t.get("aufgaben"):
        arten.append(("uebungsblatt", "Übungsblatt mit Lösungen"))
    if isinstance(t.get("rechner"), dict):
        arten.append(("rechenweg", "Beispielrechnung"))
    return [{"art": a, "titel": n, "datei": f"{t['id']}-{a}.pdf"} for a, n in arten]


def lade_themen():
    themen, fehler = [], []
    for f in sorted(CONTENT.glob("*.json")):
        if f.name.endswith(".edits.json"):
            continue
        try:
            t = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fehler.append(f"{f.name}: kein gültiges JSON ({e})")
            continue
        for k in PFLICHT:
            if k not in t:
                fehler.append(f"{f.name}: Feld '{k}' fehlt")
        if "-" in t.get("id", ""):
            fehler.append(f"{f.name}: id darf keinen Bindestrich enthalten")
        for n, q in enumerate(t.get("quiz", []), 1):
            if "falsch" in q:
                falsch = [x for k in ("leicht", "mittel", "schwer") for x in q["falsch"].get(k, [])]
                if not q.get("r") or len(falsch) < 3:
                    fehler.append(f"{f.name}: Quizfrage {n} braucht 'r' und mindestens 3 Falschantworten")
                schwer = q["falsch"].get("schwer") or q["falsch"].get("mittel") or []
                if schwer and len(q["r"]) > 1.4 * max(len(x) for x in schwer):
                    print(f"Hinweis: {f.name}, Frage {n}: richtige Antwort deutlich länger als die Falschantworten")
            elif len(q.get("a", [])) != 4 or q.get("r") not in range(4):
                fehler.append(f"{f.name}: Quizfrage {n} braucht 4 Antworten und r = 0..3")
        for d in (1, 2, 3):
            anz = sum(q.get("d", 2) == d for q in t.get("quiz", []))
            if t.get("quiz") and anz < 5:
                print(f"Hinweis: {f.name} hat nur {anz} Fragen der Schwierigkeit {d} (empfohlen: mindestens 5).")
        if 0 < len(t.get("quiz", [])) < 15:
            print(f"Hinweis: {f.name} hat nur {len(t['quiz'])} Quizfragen, das Spiel wird kürzer als 15 Stufen.")
        t["datei"] = f.stem
        t["edits"] = bearbeitungen_laden(f, t, ids_vergeben(t))
        themen.append(t)
    if fehler:
        print("Fehler in den Inhalten:\n  " + "\n  ".join(fehler))
        sys.exit(1)
    return sorted(themen, key=lambda t: t["nr"])


PWA_HEAD = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Betonbau 4">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}[hidden]{display:none!important}</style>
</head>
<body>
"""
PWA_FOOT = "\n</body>\n</html>\n"


def icon(pfad: Path, groesse: int):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (groesse, groesse), "#172025")
    d = ImageDraw.Draw(img)
    m = groesse // 8
    d.rectangle([m, groesse - m * 3, groesse - m, groesse - m * 2], fill="#e2a90a")
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", int(groesse * 0.42))
    except OSError:
        font = ImageFont.load_default()
    d.text((groesse / 2, groesse * 0.42), "B4", fill="#e8eae9", font=font, anchor="mm")
    img.save(pfad)


def main():
    themen = lade_themen()
    for t in themen:
        t["pdfs"] = pdf_liste(t)
    daten = json.dumps({"themen": themen, "site": site_url(), "repo": repo_name()}, ensure_ascii=False)
    engine = (TEMPLATE.parent / "engine.js").read_text(encoding="utf-8")
    vorlage = TEMPLATE.read_text(encoding="utf-8")
    vorlage = (vorlage.replace("/*__ENGINE_JS__*/", engine)
                      .replace("/*__RECHNER_JS__*/", (TEMPLATE.parent / "rechner.js").read_text(encoding="utf-8"))
                      .replace("/*__EDITOR_JS__*/", (TEMPLATE.parent / "editor.js").read_text(encoding="utf-8")))
    vorlage = (vorlage.replace("/*__QUIZ_CSS__*/", (TEMPLATE.parent / "quiz.css").read_text(encoding="utf-8"))
                      .replace("/*__QUIZ_JS__*/", (TEMPLATE.parent / "quiz.js").read_text(encoding="utf-8")))
    seite = vorlage.replace("/*__CONTENT__*/null", daten)

    DIST.mkdir(exist_ok=True)
    (DIST / "index.html").write_text(PWA_HEAD + seite + PWA_FOOT, encoding="utf-8")
    (ROOT / "artifact.html").write_text(seite, encoding="utf-8")

    manifest = {
        "name": "Betonbau 4 Lernplattform", "short_name": "Betonbau 4",
        "start_url": "./", "display": "standalone", "lang": "de",
        "background_color": "#e8eae9", "theme_color": "#172025",
        "icons": [{"src": "icon-180.png", "sizes": "180x180", "type": "image/png"},
                  {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"}],
    }
    (DIST / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    icon(DIST / "icon-180.png", 180)
    icon(DIST / "icon-512.png", 512)

    from excel import TABELLEN
    for t in themen:
        r = t.get("rechner")
        typ = r.get("typ") if isinstance(r, dict) else r
        if typ in TABELLEN:
            ziel = DIST / f"{t['titel'].replace(' ', '_')}.xlsx"
            TABELLEN[typ](ziel)
            print(f"Tabelle erstellt: {ziel.name}")

    # Druckseiten für die PDFs (pdf.py macht daraus PDF-Dateien)
    druck = DIST / "druck"
    druck.mkdir(exist_ok=True)
    vorlage_druck = (TEMPLATE.parent / "druck.html").read_text(encoding="utf-8").replace("/*__ENGINE_JS__*/", engine)
    heute = date.today().strftime("%d.%m.%Y")
    for t in themen:
        for pdf in t["pdfs"]:
            seite_d = (vorlage_druck.replace("__TITEL__", f"{t['titel']} – {pdf['titel']}")
                       .replace("__ART__", pdf["art"]).replace("__DATUM__", heute)
                       .replace("/*__THEMA__*/null", json.dumps(t, ensure_ascii=False)))
            (druck / f"{t['id']}-{pdf['art']}.html").write_text(seite_d, encoding="utf-8")

    print(f"Fertig: {len(themen)} Thema/Themen -> dist/index.html")


if __name__ == "__main__":
    main()
