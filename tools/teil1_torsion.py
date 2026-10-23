"""Torsion, Skript Teil 1 „Mechanische Grundlagen“ – Karteikarten, Formeln, Paare, Mindmap, Übungsaufgaben.

Quelle: Vorlesungsskript Betonbau IV, Grundlagen der Torsionsbemessung, Teil 1 (nach Finckh,
Stahlbetonkonstruktion 2, Kap. 2.1). Gleichungsnummern wie im Skript.
Bestehende Bemessungsinhalte werden als Teil "B" (vorläufig nach EC2) markiert.

Aufruf: python tools/teil1_torsion.py   (mehrfach ausführbar, ersetzt jeweils die Teil-1-Inhalte)
"""
import json
from pathlib import Path

Ak, IT, th, ph = r"A_{\mathrm{k}}", r"I_T", r"\vartheta", r"\varphi"

TEILE = [
    {"id": "1", "titel": "Teil 1 · Mechanische Grundlagen", "quelle": "Skript Teil 1"},
    {"id": "B", "titel": "Bemessung (vorläufig nach EC2)"},
]

KARTEN = [
    {"v": "Torsionsmoment am abgewinkelten Kragträger",
     "r": "Eine Einzellast $F$ am Ende des Querarms verdreht den Hauptträger um seine Längsachse. Mit dem Hebelarm $e$: $T = F \\cdot e$, Bezeichnung $M_x = M_T = T$."},
    {"v": "Schubmittelpunkt",
     "r": "Bezugspunkt des Torsionsmoments (Drehmittelpunkt); er erfährt bei Torsion keine Verschiebung. Nur bei zweifach symmetrischen Querschnitten fällt er mit dem Schwerpunkt zusammen."},
    {"v": "Exzentrische Streckenlast",
     "r": "Auch eine exzentrisch zum Schubmittelpunkt angreifende Last erzeugt Torsion. Kragträger mit Streckenlast $p$, Exzentrizität $e$, Länge $l$: $T = p \\cdot e \\cdot l$ an der Einspannung."},
    {"v": "Kombinierte Beanspruchung",
     "r": "Reine Torsion ist selten; meist wirken Torsion, Biegung und Querkraft gemeinsam. Bemessung zunächst getrennt, Wechselwirkungen anschließend mit vereinfachten Interaktionsregeln."},
    {"v": "Verwölbung",
     "r": "Geschlossenes Rohr: keine zusätzliche Längsverwölbung. Längs aufgeschnittenes Rohr: zusätzliche Verwölbung. Wird die Verwölbung behindert, entstehen Spannungen in Trägerlängsrichtung."},
    {"v": "St.-Venantsche Torsion",
     "r": "Primäre Torsion: Das Torsionsmoment wird ausschließlich durch Schubspannungen $\\tau$ übertragen. Im Stahlbetonbau üblich, weil die Verwölbung gering ist und Rissbildung die Wölbbehinderung abbaut."},
    {"v": "Gleitung $\\gamma$",
     "r": "Ein rechteckiges Oberflächenelement verformt sich zum Parallelogramm. Gl. (1): $\\gamma = \\dfrac{d\\varphi}{dx} \\cdot R$"},
    {"v": "Gl. (2): Schubspannung und Gleitung",
     "r": "$\\tau = G \\cdot \\gamma = G \\cdot \\vartheta \\cdot R$ mit Schubmodul $G$ und Verdrillung $\\vartheta = d\\varphi/dx$ (Verdrillung pro Längeneinheit)."},
    {"v": "Torsionsmoment im Kreisquerschnitt",
     "r": "Gl. (3): Integration über Kreisringe $dA = 2\\pi r\\,dr$ ergibt $T = G \\cdot \\vartheta \\cdot \\pi \\dfrac{R^4}{2}$."},
    {"v": "Schubspannung im Kreisquerschnitt",
     "r": "Gl. (4): $\\tau(r) = \\dfrac{T}{I_T} \\cdot r$ mit $I_T = \\pi R^4/2$, linear über den Radius. Gl. (5): $\\max\\tau = \\dfrac{T}{I_T} \\cdot R$ am Außenradius."},
    {"v": "Hauptspannungen infolge Torsion",
     "r": "Schiefe Hauptspannungen unter $45^\\circ$ und $135^\\circ$: Zug in Drehrichtung, Druck in Gegenrichtung. Sie verlaufen wendelförmig um den Stab und sind an der Außenfläche am größten. Risse entstehen beim Überschreiten der Betonzugfestigkeit."},
    {"v": "Dünnwandiger geschlossener Hohlquerschnitt",
     "r": "Vereinfachend konstante Schubspannung über die Wandstärke $t$. Der Wandabschnitt $t \\cdot ds$ liefert $dT = r \\cdot \\tau \\cdot t \\cdot ds$; Gl. (6): $T = \\tau \\cdot t \\oint r \\cdot ds$."},
    {"v": "Konturintegral und Kernfläche",
     "r": f"Gl. (7): $d{Ak} = \\tfrac{{1}}{{2}}\\,r \\cdot ds \\;\\Rightarrow\\; \\oint r \\cdot ds = 2 \\cdot {Ak}$. ${Ak}$ ist die von den Wandmittellinien umschlossene Kernfläche."},
    {"v": "1. Bredtsche Formel",
     "r": f"Gl. (8): $\\tau = \\dfrac{{T}}{{t \\cdot 2 \\cdot {Ak}}}$ für dünnwandige geschlossene Querschnitte ($T$ Torsionsmoment, $t$ Wandstärke, ${Ak}$ Kernfläche)."},
]

FORMELN = [
    {"name": "Torsionsmoment, abgewinkelter Kragträger", "f": "T = F \\cdot e", "e": "Einzellast $F$, Hebelarm $e$"},
    {"name": "Gleitung", "gl": "1", "f": "\\gamma = \\dfrac{d\\varphi}{dx} \\cdot R", "e": "aus $\\gamma \\cdot dx = d\\varphi \\cdot R$"},
    {"name": "Schubspannung und Gleitung", "gl": "2", "f": "\\tau = G \\cdot \\gamma = G \\cdot \\dfrac{d\\varphi}{dx} \\cdot R = G \\cdot \\vartheta \\cdot R",
     "e": "$G$ Schubmodul, $\\vartheta = d\\varphi/dx$ Verdrillung pro Längeneinheit"},
    {"name": "Torsionsmoment, Kreisquerschnitt", "gl": "3", "f": "T = \\int_0^R \\tau \\cdot 2\\pi r^2\\,dr = G \\cdot \\vartheta \\cdot \\pi \\dfrac{R^4}{2}",
     "e": "Integration über Kreisringe $dA = 2\\pi r\\,dr$"},
    {"name": "Schubspannungsverteilung, Kreis", "gl": "4", "f": "\\tau(r) = \\dfrac{T}{\\pi R^4/2} \\cdot r = \\dfrac{T}{I_T} \\cdot r", "e": "linear über den Radius"},
    {"name": "Maximale Schubspannung, Kreis", "gl": "5", "f": "\\max\\tau = \\dfrac{T}{\\pi R^4/2} \\cdot R = \\dfrac{T}{I_T} \\cdot R", "e": "am Außenradius $R$"},
    {"name": "Torsionsmoment, Hohlquerschnitt", "gl": "6", "f": "T = \\oint \\tau \\cdot t \\cdot r \\cdot ds = \\tau \\cdot t \\oint r \\cdot ds",
     "e": "Integration entlang der Wandmittellinie, $\\tau$ konstant über $t$"},
    {"name": "Konturintegral und Kernfläche", "gl": "7", "f": f"d{Ak} = \\dfrac{{1}}{{2}}\\,r \\cdot ds \\;\\Rightarrow\\; \\oint r \\cdot ds = 2 \\cdot {Ak}",
     "e": f"${Ak}$: von den Wandmittellinien umschlossene Kernfläche"},
    {"name": "1. Bredtsche Formel", "gl": "8", "f": f"\\tau = \\dfrac{{T}}{{t \\cdot \\oint r \\cdot ds}} = \\dfrac{{T}}{{t \\cdot 2 \\cdot {Ak}}}",
     "e": "dünnwandiger geschlossener Hohlquerschnitt, $t$ Wandstärke"},
]

PAARE = [
    {"a": "$\\vartheta$", "b": "Verdrillung pro Längeneinheit"},
    {"a": "$G$", "b": "Schubmodul"},
    {"a": "$\\gamma$", "b": "Gleitung"},
    {"a": "$I_T = \\pi R^4/2$", "b": "Torsionsträgheitsmoment des Kreises"},
    {"a": "Schubmittelpunkt", "b": "Bezugspunkt des Torsionsmoments"},
    {"a": "$45^\\circ$ / $135^\\circ$", "b": "Richtung der Hauptspannungen"},
    {"a": "$T = F \\cdot e$", "b": "Torsion am abgewinkelten Kragträger"},
    {"a": "$\\oint r \\cdot ds$", "b": f"Doppelte Kernfläche"},
    {"a": "St.-Venant", "b": "Torsion ohne Wölbbehinderung"},
]

MINDMAP = {"t": "Mechanische Grundlagen", "c": [
    {"t": "Entstehung", "c": [{"t": "Kragträger: $T = F \\cdot e$"}, {"t": "exzentrische Last: $T = p \\cdot e \\cdot l$"},
                              {"t": "Bezug: Schubmittelpunkt"}, {"t": "meist kombiniert mit $M$ und $V$"}]},
    {"t": "Verwölbung", "c": [{"t": "geschlossen: keine Längsverwölbung"}, {"t": "offen: zusätzliche Verwölbung"},
                              {"t": "behindert → Längsspannungen"}, {"t": "St.-Venant: nur Schubspannungen"}]},
    {"t": "Kreisquerschnitt", "c": [{"t": "(1) $\\gamma = \\vartheta \\cdot R$"}, {"t": "(2) $\\tau = G \\cdot \\vartheta \\cdot R$"},
                                    {"t": "(3) $T = G \\cdot \\vartheta \\cdot I_T$"}, {"t": "(5) $\\max\\tau = \\dfrac{T}{I_T} \\cdot R$"}]},
    {"t": "Hauptspannungen", "c": [{"t": "unter $45^\\circ$ und $135^\\circ$"}, {"t": "wendelförmig, außen am größten"},
                                   {"t": "Risse bei Überschreiten der Betonzugfestigkeit"}]},
    {"t": "Hohlquerschnitt", "c": [{"t": f"(7) $\\oint r \\cdot ds = 2 \\cdot {Ak}$"}, {"t": f"(8) Bredt: $\\tau = \\dfrac{{T}}{{t \\cdot 2 \\cdot {Ak}}}$"}]},
]}

kNm, cm, Nmm2 = r"\,\mathrm{kNm}", r"\,\mathrm{cm}", r"\,\mathrm{N/mm^2}"

AUFGABEN = [
    {"titel": "Kragträger mit Kreisquerschnitt", "teil": "1",
     "text": "Ein abgewinkelter Kragträger mit Kreisquerschnitt (Radius $R = #R:0#\\,\\mathrm{cm}$) wird am Ende des Querarms durch $F = #F:0#\\,\\mathrm{kN}$ mit dem Hebelarm $e = #e:2#\\,\\mathrm{m}$ belastet. Schubmodul im ungerissenen Zustand $G = #G:0#\\,\\mathrm{N/mm^2}$. Ermitteln Sie Torsionsmoment, Schubspannungen, Gleitung und Verdrillung.",
     "params": {"R": {"min": 15, "max": 30, "step": 5}, "F": {"min": 10, "max": 60, "step": 5},
                "e": {"min": 0.5, "max": 1.5, "step": 0.25}, "G": {"werte": [12900, 13750, 14200]}},
     "schritte": [
         {"titel": "Torsionsmoment", "text": "Die Last am Querarm wirkt mit dem Hebelarm $e$ um die Längsachse des Hauptträgers.",
          "formel": ["T = F \\cdot e"], "einsetzen": [f"T = #F:0# \\cdot #e:2# = #T:2#{kNm}"],
          "werte": [{"id": "T", "expr": "F*e", "d": 2, "frage": True, "label": "T", "einheit": "kNm"}]},
         {"titel": "Torsionsträgheitsmoment", "formel": ["I_T = \\dfrac{\\pi R^4}{2}"],
          "einsetzen": ["I_T = \\dfrac{\\pi \\cdot #R:0#^4}{2} = #IT:0#\\,\\mathrm{cm^4}"],
          "werte": [{"id": "IT", "expr": "PI*R**4/2", "d": 0, "frage": True, "label": "I_T", "einheit": "cm⁴"}]},
         {"titel": "Maximale Schubspannung – Gl. (5)", "text": "Die größte Schubspannung tritt am Außenradius auf.",
          "formel": ["\\max\\tau = \\dfrac{T}{I_T} \\cdot R"],
          "einsetzen": [f"\\max\\tau = \\dfrac{{#T:2# \\cdot 10^6}}{{#IT:0# \\cdot 10^4}} \\cdot #R:0# \\cdot 10 = #tmax:2#{Nmm2}"],
          "werte": [{"id": "tmax", "expr": "T*1e6/(IT*1e4)*R*10", "d": 2, "frage": True, "label": "\\max\\tau", "einheit": "N/mm²"}]},
         {"titel": "Schubspannung bei halbem Radius – Gl. (4)", "text": "Die Schubspannung wächst linear mit dem Radius.",
          "formel": ["\\tau(r) = \\dfrac{T}{I_T} \\cdot r"],
          "einsetzen": [f"\\tau(R/2) = \\dfrac{{#T:2# \\cdot 10^6}}{{#IT:0# \\cdot 10^4}} \\cdot #r2:1# \\cdot 10 = #th2:2#{Nmm2}"],
          "werte": [{"id": "r2", "expr": "R/2", "d": 1},
                    {"id": "th2", "expr": "T*1e6/(IT*1e4)*r2*10", "d": 2, "frage": True, "label": "\\tau(R/2)", "einheit": "N/mm²"}]},
         {"titel": "Gleitung am Außenrand – Gl. (2)", "formel": ["\\gamma = \\dfrac{\\tau}{G}"],
          "einsetzen": ["\\gamma = \\dfrac{#tmax:2#}{#G:0#} = #gam:3# \\cdot 10^{-3}"],
          "werte": [{"id": "gam", "expr": "tmax/G*1000", "d": 3, "frage": True, "label": "\\gamma \\cdot 10^{3}", "einheit": "–"}]},
         {"titel": "Verdrillung – Gl. (3)", "text": "Gl. (3) nach $\\vartheta$ umgestellt.",
          "formel": ["\\vartheta = \\dfrac{d\\varphi}{dx} = \\dfrac{T}{G \\cdot I_T}"],
          "einsetzen": ["\\vartheta = \\dfrac{#T:2# \\cdot 10^6}{#G:0# \\cdot #IT:0# \\cdot 10^4} \\cdot 10^3 = #thm:3# \\cdot 10^{-3}\\,\\mathrm{rad/m}"],
          "werte": [{"id": "thm", "expr": "T*1e6/(G*IT*1e4)*1e6", "d": 3, "frage": True, "label": "\\vartheta \\cdot 10^{3}", "einheit": "rad/m"}]},
     ]},

    {"titel": "Hohlkasten mit exzentrischer Last", "teil": "1",
     "text": "Ein Kragträger mit dünnwandigem Rechteck-Hohlquerschnitt (Außenmaße $b/h = #b:0#/#h:0#\\,\\mathrm{cm}$, Wandstärke $t = #t:0#\\,\\mathrm{cm}$, Länge $l = #l:1#\\,\\mathrm{m}$) trägt eine Streckenlast $p = #p:0#\\,\\mathrm{kN/m}$, die mit $e = #e:2#\\,\\mathrm{m}$ exzentrisch zum Schubmittelpunkt angreift. Ermitteln Sie das Torsionsmoment an der Einspannung und die Schubspannung in der Wand nach der 1. Bredtschen Formel.",
     "params": {"b": {"min": 40, "max": 80, "step": 10}, "h": {"min": 60, "max": 120, "step": 10}, "t": {"werte": [12, 15, 18, 20]},
                "l": {"min": 3, "max": 6, "step": 0.5}, "p": {"min": 20, "max": 60, "step": 5}, "e": {"min": 0.5, "max": 1.5, "step": 0.25}},
     "schritte": [
         {"titel": "Torsionsmoment an der Einspannung", "text": "Die exzentrische Last erzeugt ein Streckentorsionsmoment $p \\cdot e$; an der Einspannung summiert es sich über die Länge $l$.",
          "formel": ["T = p \\cdot e \\cdot l"], "einsetzen": [f"T = #p:0# \\cdot #e:2# \\cdot #l:1# = #T:2#{kNm}"],
          "werte": [{"id": "T", "expr": "p*e*l", "d": 2, "frage": True, "label": "T", "einheit": "kNm"}]},
         {"titel": "Kernfläche", "text": "Die Kernfläche wird von den Wandmittellinien umschlossen, also von jeder Seite eine halbe Wandstärke nach innen.",
          "formel": [f"{Ak} = (b - t) \\cdot (h - t)"],
          "einsetzen": [f"{Ak} = (#b:0# - #t:0#) \\cdot (#h:0# - #t:0#) = #Ak:0#\\,\\mathrm{{cm^2}}"],
          "werte": [{"id": "Ak", "expr": "(b-t)*(h-t)", "d": 0, "frage": True, "label": Ak, "einheit": "cm²"}]},
         {"titel": "Konturintegral – Gl. (7)", "formel": [f"\\oint r \\cdot ds = 2 \\cdot {Ak}"],
          "einsetzen": ["\\oint r \\cdot ds = 2 \\cdot #Ak:0# = #rds:0#\\,\\mathrm{cm^2}"],
          "werte": [{"id": "rds", "expr": "2*Ak", "d": 0}]},
         {"titel": "Schubspannung – 1. Bredtsche Formel, Gl. (8)",
          "formel": [f"\\tau = \\dfrac{{T}}{{t \\cdot 2 \\cdot {Ak}}}"],
          "einsetzen": [f"\\tau = \\dfrac{{#T:2# \\cdot 10^6}}{{#t:0# \\cdot 10 \\cdot 2 \\cdot #Ak:0# \\cdot 10^2}} = #tau:2#{Nmm2}"],
          "werte": [{"id": "tau", "expr": "T*1e6/(t*10*2*Ak*100)", "d": 2, "frage": True, "label": "\\tau", "einheit": "N/mm²"}]},
         {"titel": "Schubfluss", "text": "Das Produkt aus Schubspannung und Wandstärke ist entlang der Wand konstant.",
          "formel": [f"\\tau \\cdot t = \\dfrac{{T}}{{2 \\cdot {Ak}}}"],
          "einsetzen": ["\\tau \\cdot t = #tau:2# \\cdot #t:0# \\cdot 10 = #q:1#\\,\\mathrm{N/mm}"],
          "werte": [{"id": "q", "expr": "tau*t*10", "d": 1, "frage": True, "label": "\\tau \\cdot t", "einheit": "N/mm"}]},
     ]},
]


def tag(items, teil):
    for x in items:
        x["teil"] = teil
    return items


if __name__ == "__main__":
    ziel = Path(__file__).resolve().parent.parent / "content" / "01_torsion.json"
    d = json.loads(ziel.read_text(encoding="utf-8"))

    d["untertitel"] = ("Mechanische Grundlagen, Tragverhalten unter reiner Torsion, Tragmodell und Bemessungsregeln, "
                       "Überlagerung mit Biegung und Querkraft")
    d["status"] = "teilweise"
    d["statusText"] = ("Teil 1 (Mechanische Grundlagen) ist mit dem Skript abgeglichen. Die Bemessungsinhalte sind noch "
                       "vorläufig nach DIN EN 1992-1-1 + NA und werden mit den nächsten Skriptteilen angepasst.")
    d["teile"] = TEILE

    alt = lambda liste: [x for x in liste if x.get("teil") != "1"]
    karten_b = alt(d["karten"])
    # Bisherige Karten, die Teil 1 jetzt abdeckt, entfallen
    karten_b = [k for k in karten_b if k["v"] not in ("Bredtsche Formel", "Rissbild bei Torsion")]
    d["karten"] = tag([dict(k) for k in KARTEN], "1") + tag(karten_b, k_b := "B")
    d["formeln"] = tag([dict(f) for f in FORMELN], "1") + tag(alt(d["formeln"]), "B")
    d["paare"] = tag([dict(p) for p in PAARE], "1") + tag(alt(d["paare"]), "B")
    d["aufgaben"] = [dict(a) for a in AUFGABEN] + [dict(a, teil="B") for a in d["aufgaben"] if a.get("teil") != "1"]

    mm = d["mindmap"]
    mm["c"] = [b for b in mm["c"] if b["t"] != MINDMAP["t"]]
    mm["c"].insert(0, MINDMAP)

    ziel.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Teil 1: {len(KARTEN)} Karten, {len(FORMELN)} Formeln, {len(PAARE)} Paare, {len(AUFGABEN)} Aufgaben")
    print(f"Gesamt: {len(d['karten'])} Karten, {len(d['formeln'])} Formeln, {len(d['paare'])} Paare, {len(d['aufgaben'])} Aufgaben")
