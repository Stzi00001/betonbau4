# Betonbau 4 – Lernplattform

Python erzeugt aus den Inhaltsdateien eine fertige Web-App, die auf PC, iPad und iPhone läuft.

## Aufbau

```
content/          Ein JSON pro Thema (01_torsion.json, 02_..., ...)
templates/app.html  Oberfläche und Lernspiele (HTML/CSS/JS)
excel.py          Excel-Tabellen mit echten Formeln zu den Rechnern
build.py          Baut alles zusammen
dist/             Ergebnis: das hier wird veröffentlicht
```

## Bauen

```
pip install openpyxl pillow
python build.py
```

Danach `dist/index.html` im Browser öffnen.

## Neues Thema hinzufügen

1. `content/01_torsion.json` kopieren, z. B. als `content/02_durchstanzen.json`.
2. `id` (ohne Bindestrich), `nr`, `titel`, `untertitel` anpassen.
3. Lernangebote füllen – jedes Feld ist optional, fehlende Angebote werden einfach nicht angezeigt:
   - `quiz`: Fragen mit `f` (Frage), `a` (4 Antworten), `r` (Index der richtigen, 0–3), `d` (Schwierigkeit 1–3), `tipp` (Telefonjoker). Mindestens 15 Fragen für ein volles Spiel.
   - `karten`: `v` (Vorderseite), `r` (Rückseite), optional `video` mit Link und Zeitstempel:
     ```json
     {"v": "Bredtsche Formel", "r": "q = T/(2A_k)",
      "video": {"url": "https://…", "t": "12:34", "label": "VL 3"}}
     ```
     Mehrere Videos als Liste `[{…}, {…}]`. `t` als `mm:ss`, `h:mm:ss` oder Sekunden.
     YouTube, Vimeo und direkte Videodateien springen automatisch zur Stelle.
   - `paare`: `a` (Begriff), `b` (Bedeutung) für das Zuordnungsspiel
   - `formeln`: `name`, `f`, `e`
   - `mindmap`: Baum aus `t` (Text) und `c` (Unterpunkte)
   - `aufgaben`: Übungsaufgaben mit Zufallswerten und Rechenweg (Quelle für Torsion: `tools/`)
   - `rechner`: Bemessungstool mit Eingaben, Ergebnis-Kacheln und vollständigem Rechenweg
     (Quelle für Torsion: `tools/rechner_torsion.py`)
4. `python build.py` ausführen.

## Bearbeitungsmodus

In der Web-App unten auf der Startseite „Bearbeitungsmodus“ öffnen und einmalig einen GitHub-Zugangsschlüssel
eintragen (Fine-grained token, nur Repository `betonbau4`, Berechtigung „Contents: Read and write“).
Danach gibt es auf jeder Themenseite „Inhalte bearbeiten“: Karteikarten, Quizfragen, Formeln, Zuordnen-Paare
und Mindmap ändern, löschen und ergänzen, Übungsaufgaben ausblenden.

Die Änderungen werden in `content/<datei>.edits.json` gespeichert und beim Bauen über die Originalinhalte gelegt.
Gelöschtes bleibt dort vermerkt und lässt sich in der App wiederherstellen. Die Skripte in `tools/` überschreiben
diese Dateien nie.

## PDFs

`build.py` legt Druckseiten in `dist/druck/` an, `pdf.py` macht daraus PDFs
(Formelsammlung, Übungsblatt mit Lösungen, Beispielrechnung). Auf GitHub passiert das automatisch.
Lokal optional: `pip install playwright`, dann `python -m playwright install chromium` und `python pdf.py`
(oder mit installiertem Google Chrome ohne Browser-Download: `set PDF_BROWSER=chrome` und `python pdf.py`).
Den Rechenweg mit eigenen Eingaben gibt es im Bemessungstool über „Rechenweg als PDF“ (Druckdialog → „Als PDF speichern“).

## Automatisch veröffentlichen (GitHub)

Bei jeder Änderung im Repository baut GitHub die App neu und stellt sie unter
`https://<benutzername>.github.io/<repository>/` bereit (Datei `.github/workflows/deploy.yml`).
Einmalig nötig: im Repository unter Settings → Pages bei „Source“ **GitHub Actions** wählen.

Neue Inhalte: Datei in `content/` hochladen (auf github.com: „Add file“ → „Upload files“) – nach etwa einer Minute ist sie online.
Das Vorlesungsskript selbst nicht ins Repository laden, das Repository ist öffentlich.

## Auf iPad / iPhone nutzen

1. Den Ordner `dist/` kostenlos veröffentlichen, z. B. mit GitHub Pages (Repository anlegen, `dist`-Inhalt hochladen, unter Settings → Pages aktivieren) oder Netlify Drop (Ordner ins Browserfenster ziehen).
2. Den Link in Safari öffnen → Teilen → „Zum Home-Bildschirm“.
3. Die App startet dann im Vollbild mit eigenem Icon. Lernfortschritt (Karteikarten-Fächer, Quiz-Rekord, Rechnereingaben) wird auf dem jeweiligen Gerät gespeichert.
