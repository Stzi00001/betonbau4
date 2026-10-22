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
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
DIST = ROOT / "dist"
TEMPLATE = ROOT / "templates" / "app.html"

PFLICHT = ["id", "nr", "titel", "untertitel"]


def lade_themen():
    themen, fehler = [], []
    for f in sorted(CONTENT.glob("*.json")):
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
            if len(q.get("a", [])) != 4 or q.get("r") not in range(4):
                fehler.append(f"{f.name}: Quizfrage {n} braucht 4 Antworten und r = 0..3")
        if 0 < len(t.get("quiz", [])) < 15:
            print(f"Hinweis: {f.name} hat nur {len(t['quiz'])} Quizfragen, das Spiel wird kürzer als 15 Stufen.")
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
    daten = json.dumps({"themen": themen}, ensure_ascii=False)
    vorlage = TEMPLATE.read_text(encoding="utf-8")
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
        if t.get("rechner") in TABELLEN:
            ziel = DIST / f"{t['titel'].replace(' ', '_')}.xlsx"
            TABELLEN[t["rechner"]](ziel)
            print(f"Tabelle erstellt: {ziel.name}")

    print(f"Fertig: {len(themen)} Thema/Themen -> dist/index.html")


if __name__ == "__main__":
    main()
