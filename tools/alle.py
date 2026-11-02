"""Alle Torsionsinhalte neu erzeugen (Reihenfolge wichtig), danach die App bauen.

Aufruf: python tools/alle.py
Bearbeitungen aus der App (content/*.edits.json) bleiben unberührt.
"""
import runpy
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
for skript in ["quiz_torsion.py", "teil1_torsion.py", "teil2bis4_torsion.py", "teil5_torsion.py", "rechner_torsion.py", "buch_torsion.py", "einheiten_torsion.py"]:
    print(f"--- {skript}")
    runpy.run_path(str(TOOLS / skript), run_name="__main__")
print("--- build.py")
sys.exit(subprocess.call([sys.executable, str(TOOLS.parent / "build.py")]))
