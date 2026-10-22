"""PDFs aus den Druckseiten erzeugen (Formelsammlung, Übungsblatt, Beispiel-Rechenweg).

Läuft automatisch auf GitHub nach build.py. Lokal optional:
    pip install playwright
    python -m playwright install chromium
    python pdf.py
Ohne Playwright wird nur ein Hinweis ausgegeben.
"""
import sys
from pathlib import Path

DIST = Path(__file__).parent / "dist"
FUSS = ('<div style="width:100%;font-size:8px;color:#666;padding:0 15mm;display:flex;justify-content:flex-end;'
        'font-family:Arial,sans-serif">Seite <span class="pageNumber"></span> von <span class="totalPages"></span></div>')


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Hinweis: Playwright ist nicht installiert, PDFs werden übersprungen (siehe pdf.py).")
        return
    seiten = sorted((DIST / "druck").glob("*.html"))
    if not seiten:
        print("Keine Druckseiten gefunden – zuerst python build.py ausführen.")
        return
    fehler = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for s in seiten:
            page = browser.new_page()
            page.goto(s.resolve().as_uri())
            try:
                page.wait_for_function("document.body.dataset.fertig === '1'", timeout=60000)
            except Exception:
                print(f"Fehler: Formelsatz für {s.name} nicht fertig geworden (Internetverbindung?)")
                fehler += 1
                continue
            ziel = DIST / (s.stem + ".pdf")
            page.pdf(path=str(ziel), format="A4", print_background=True, display_header_footer=True,
                     header_template="<span></span>", footer_template=FUSS,
                     margin={"top": "16mm", "bottom": "18mm", "left": "15mm", "right": "15mm"})
            print(f"PDF erstellt: {ziel.name}")
            page.close()
        browser.close()
    if fehler:
        sys.exit(1)


if __name__ == "__main__":
    main()
