"""Torsion, Skript Teil 5 „Bemessungsmodell“ – Karteikarten, Formeln Gl. (31)–(46), Paare, Mindmap, Aufgaben, Quiz.

Quelle: Vorlesungsskript Betonbau IV, Teil 5 (nach Finckh, Stahlbetonkonstruktion 2, Kap. 2, Abschn. 5).
Ersetzt den bisherigen Teil „B“ (vorläufig nach EC2). Querkraftgrößen (V_Rd,max, V_Rd,c, V_Rd,cc, Querkraftbügel)
stammen aus Betonbau 3 und sind als solche gekennzeichnet.

Aufruf: python tools/teil5_torsion.py   (ersetzt alle Inhalte von Teil 5)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from teil2bis4_torsion import expand, BAUSTOFFE  # noqa: E402

SYM5 = {"tefi": r"t_{\mathrm{ef},i}", "tvorh": r"t_{\mathrm{vorh}}", "VEdi": r"V_{\mathrm{Ed},i}", "tauti": r"\tau_{\mathrm{t},i}",
        "VEdTV": r"V_{\mathrm{Ed},T+V}", "VRdcc": r"V_{\mathrm{Rd,cc}}", "TRds": r"T_{\mathrm{Rd,s}}", "Aswerf": r"A_{\mathrm{sw,erf}}",
        "Aslerf": r"A_{\mathrm{sl,erf}}", "scdN": r"\sigma_{\mathrm{cd}}"}


def ex(o, im_ausdruck=False):
    """Kürzel aus Teil 2–4 und Teil 5 umwandeln. In Rechenausdrücken (JS-Zeichenketten) Backslashes verdoppeln."""
    import re
    from teil2bis4_torsion import SYM
    if isinstance(o, str):
        alle = {**SYM, **SYM5}
        return re.sub(r"«(\w+)»", lambda m: alle[m.group(1)].replace("\\", "\\\\") if im_ausdruck else alle[m.group(1)], o)
    if isinstance(o, list):
        return [ex(x, im_ausdruck) for x in o]
    if isinstance(o, dict):
        return {k: (v if k == "wenn" else ex(v, k == "expr")) for k, v in o.items()}
    return o


TEIL = {"id": "5", "titel": "Teil 5 · Bemessungsmodell", "quelle": "Skript Teil 5"}
B3 = "Betonbau 3 (Querkraft)"

KARTEN = [
    ("Nachweiskonzept – Gl. (31) und (32)", "3–4",
     "$«TEd» \\le «TRdmax»$ (Betondruckstreben) und $«TEd» \\le «TRds»$ (Bewehrung). Beide müssen erfüllt sein; maßgebend ist jeweils der kleinste Widerstand der Wände $i$."),
    ("Ersatzhohlkasten nach Bredt", "5",
     "Die Wandmittellinien umschließen die Kernfläche $«Ak»$ einschließlich innerer Hohlbereiche; $«uk»$ ist deren Umfang, $z_i$ der Abstand der Mittellinien-Schnittpunkte an den Enden der Wand $i$."),
    ("Wirksame Wanddicke – Gl. (33)", "6",
     "$«tefi» = 2a \\le «tvorh»$ mit dem Schwerpunktabstand $a$ der Längsbewehrung vom Rand. Hohlkästen mit Wanddicke $\\le b/6$ bzw. $h/6$ und beidseitiger Wandbewehrung: gesamte Wanddicke zulässig."),
    ("Schubfluss und Schubkraft – Gl. (34) und (35)", "7",
     "$«tauti»\\,«tefi» = \\dfrac{«TEd»}{2\\,«Ak»}$, $«VEdi» = «tauti»\\,«tefi»\\,z_i = \\dfrac{«TEd»}{2\\,«Ak»}\\,z_i$ mit $z_i$ zwischen den Schnittpunkten der Mittellinien."),
    ("Wahl des Druckstrebenwinkels – Gl. (36)", "8",
     "Vereinfacht $\\theta = 45^\\circ$. Genauer, abgestimmt mit der Querkraft und für beide Nachweise gleich: $1{,}0 \\le \\cot\\theta \\le \\dfrac{1{,}2 + 1{,}4\\,«scdN»/«fcd»}{1 - «VRdcc»/«VEdTV»} \\le 3{,}0$"),
    ("Kombinierte Schubkraft – Gl. (37)", "9",
     "$«VEdTV» = «VEdT» + «VEd»\\,\\dfrac{«tef»}{«bw»}$; $«VRdcc»$ aus der Querkraftbemessung, $«scdN» = N_{\\mathrm{Ed}}/A_{\\mathrm{c}} < 0{,}2\\,«fcd»$ (Druck positiv)."),
    ("Druckstrebentragfähigkeit – Gl. (38)", "10",
     "$«TRdmax» = \\dfrac{\\nu\\,«fcd»\\,2\\,«Ak»\\,«tef»}{\\cot\\theta + \\tan\\theta}$ mit $\\nu = 0{,}525$, bei echten Kästen mit innerer und äußerer Bewehrung $0{,}75$; ab C55/67 zusätzlich mal $\\nu_2 = 1{,}1 - «fck»/500 \\le 1$."),
    ("Bügel – Gl. (39) und (41)", "11, 13",
     "$«TRdsw» = 2\\,«Ak»\\,\\dfrac{«Asw»}{«sw»}\\,«fyd»\\cot\\theta$; erforderlich $\\dfrac{«Aswerf»}{«sw»} = \\dfrac{«TEd»}{2\\,«Ak»}\\,\\dfrac{1}{«fyd»}\\tan\\theta$ – für einen Bügelschenkel pro Längeneinheit."),
    ("Längsbewehrung – Gl. (40) und (42)", "12, 14",
     "$«TRdsl» = 2\\,«Ak»\\,\\dfrac{«Asl»}{«uk»}\\,«fyd»\\tan\\theta$; erforderlich $«Aslerf» = \\dfrac{«TEd»\\,«uk»}{2\\,«Ak»}\\,\\dfrac{1}{«fyd»}\\cot\\theta$. Bügel und Längsbewehrung getrennt nachweisen."),
    ("Interaktion Biegung und Torsion", "15",
     "Längsbewehrung für Biegung und Torsion getrennt ermitteln und die Flächen addieren – vereinfacht und auf der sicheren Seite (vgl. Teil 4)."),
    ("Interaktion Querkraft und Torsion – Gl. (43) und (44)", "16",
     "Kompaktquerschnitte quadratisch: $\\left(\\dfrac{«TEd»}{«TRdmax»}\\right)^2 + \\left(\\dfrac{«VEd»}{«VRdmax»}\\right)^2 \\le 1{,}0$. Kastenquerschnitte linear. Bügel gemäß Schubfluss addieren."),
    ("Entfall rechnerischer Bewehrung – Gl. (45) und (46)", "17",
     "Näherungsweise rechteckige Vollquerschnitte: $«TEd» \\le \\dfrac{«VEd»\\,«bw»}{4{,}5}$ und $«VEd» + \\dfrac{4{,}5\\,«TEd»}{«bw»} \\le «VRdc»$. Die Mindestbewehrung ist dennoch vorzusehen."),
    ("Konstruktive Regeln: Bügel", "18",
     "Bügel und Längsstäbe erforderlich. Bügel geschlossen und verankert, nur $135^\\circ$-Haken mit Länge $> 10\\,\\varnothing$, keine Winkelhaken; Bügel $90^\\circ$ zur Bauteilachse."),
    ("Konstruktive Regeln: Abstände und Längsstäbe", "19",
     "Bügelabstand höchstens $«uk»/8$ und höchstens die kleinste Querschnittsabmessung, Querkraftabstände einhalten. In jeder Ecke ein Längsstab, weitere gleichmäßig über den inneren Bügelumfang, Abstand höchstens 35 cm."),
]

FORMELN = [
    ("Nachweis der Betondruckstreben", "31", "4", r"«TEd» \le «TRdmax»", "Tragfähigkeit des Betons gegen Druckstrebenversagen"),
    ("Nachweis der Torsionsbewehrung", "32", "4", r"«TEd» \le «TRds»", "Bügel und Längsbewehrung (Zugstreben)"),
    ("Wirksame Wanddicke", "33", "6", r"«tefi» = 2a \le «tvorh»", "$a$: Schwerpunktabstand der Längsbewehrung von der Außenkante; Kasten mit $t \\le b/6$ bzw. $h/6$ und beidseitiger Bewehrung: gesamte Wanddicke"),
    ("Schubfluss der Wand", "34", "7", r"«tauti»\,«tefi» = \dfrac{«TEd»}{2\,«Ak»}", "1. Bredtsche Formel"),
    ("Schubkraft der Wand", "35", "7", r"«VEdi» = «tauti»\,«tefi»\,z_i = \dfrac{«TEd»}{2\,«Ak»}\,z_i", "$z_i$: zwischen den Schnittpunkten der Mittellinien"),
    ("Grenzen des Druckstrebenwinkels", "36", "8", r"1{,}0 \le \cot\theta \le \dfrac{1{,}2 + 1{,}4\,«scdN»/«fcd»}{1 - \dfrac{«VRdcc»}{«VEdTV»}} \le 3{,}0", "vereinfacht $\\theta = 45^\\circ$; gleicher Winkel für Querkraft und Torsion"),
    ("Kombinierte Schubkraft", "37", "9", r"«VEdTV» = «VEdT» + «VEd»\,\dfrac{«tef»}{«bw»}", "$«scdN» = N_{\\mathrm{Ed}}/A_{\\mathrm{c}} < 0{,}2\\,«fcd»$, Druck positiv"),
    ("Tragfähigkeit der Betondruckstreben", "38", "10", r"«TRdmax» = \dfrac{\nu\,«fcd»\,2\,«Ak»\,«tef»}{\cot\theta + \tan\theta}", "$\\nu = 0{,}525$; echter Kasten innen und außen bewehrt $0{,}75$; ab C55/67 $\\times\\,\\nu_2$"),
    ("Abminderung für hochfesten Beton", None, "10", r"\nu_2 = 1{,}1 - \dfrac{«fck»}{500} \le 1", "ab C55/67"),
    ("Tragfähigkeit der Bügel", "39", "11", r"«TRdsw» = 2\,«Ak»\,\dfrac{«Asw»}{«sw»}\,«fyd»\,\cot\theta", "$«Asw»$: ein Bügelschenkel, maßgebende Wand $i$"),
    ("Tragfähigkeit der Längsbewehrung", "40", "12", r"«TRdsl» = 2\,«Ak»\,\dfrac{«Asl»}{«uk»}\,«fyd»\,\tan\theta", "Bügel und Längsbewehrung getrennt nachweisen"),
    ("Erforderliche Torsionsbügel", "41", "13", r"\dfrac{«Aswerf»}{«sw»} = \dfrac{«TEd»}{2\,«Ak»}\,\dfrac{1}{«fyd»}\,\tan\theta", "ein Bügelschenkel pro Längeneinheit"),
    ("Erforderliche Torsionslängsbewehrung", "42", "14", r"«Aslerf» = \dfrac{«TEd»\,«uk»}{2\,«Ak»}\,\dfrac{1}{«fyd»}\,\cot\theta", "bei $45^\\circ$: $\\tan\\theta = \\cot\\theta = 1$"),
    ("Interaktion, Kompaktquerschnitt", "43", "16", r"\left(\dfrac{«TEd»}{«TRdmax»}\right)^2 + \left(\dfrac{«VEd»}{«VRdmax»}\right)^2 \le 1{,}0", "quadratisch"),
    ("Interaktion, Kastenquerschnitt", "44", "16", r"\dfrac{«TEd»}{«TRdmax»} + \dfrac{«VEd»}{«VRdmax»} \le 1{,}0", "linear; Bügel gemäß Schubfluss addieren"),
    ("Entfall der Bewehrung, Bedingung 1", "45", "17", r"«TEd» \le \dfrac{«VEd»\,«bw»}{4{,}5}", "näherungsweise rechteckige Vollquerschnitte"),
    ("Entfall der Bewehrung, Bedingung 2", "46", "17", r"«VEd» + \dfrac{4{,}5\,«TEd»}{«bw»} \le «VRdc»", "Mindestbewehrung dennoch vorsehen"),
    ("Größter Bügelabstand", None, "19", r"«sw» \le \min\!\left(\dfrac{«uk»}{8};\; \min(b,h)\right)", "zusätzlich Abstände der Querkraftbewehrung; Längsstäbe $\\le 35\\,\\mathrm{cm}$"),
]
FORMELN_B3 = [
    ("Querkraft-Druckstrebe", r"«VRdmax» = \dfrac{«bw»\,z\,\nu_1\,«fcd»}{\cot\theta + \tan\theta}, \qquad \nu_1 = 0{,}75\,\nu_2", "für Gl. (43)/(44)"),
    ("Querkraftbügel", r"\dfrac{«AswV»}{«sw»} = \dfrac{«VEd»}{z\,«fyd»\cot\theta}", "beide Schenkel, für Gl. (28)"),
    ("Betontraganteil", r"«VRdcc» = c \cdot 0{,}48\,«fck»^{1/3}\left(1 - 1{,}2\,\dfrac{«scdN»}{«fcd»}\right) «bw»\,z, \qquad c = 0{,}5", "für Gl. (36); bei Torsion je Wand mit $«bw» = «tef»$, $z = z_i$"),
    ("Querkraft ohne Bewehrung", r"«VRdc» = \left[0{,}10\,k\,(100\,\rho_{\mathrm{l}}\,«fck»)^{1/3}\right] «bw»\,d \;\ge\; v_{\min}\,«bw»\,d", "für Gl. (46)"),
]

PAARE = [
    ("$«uk»/8$", "Größter Abstand der Torsionsbügel", "19"), ("$35\\,\\mathrm{cm}$", "Größter Abstand der Längsstäbe", "19"),
    ("Querschnittsecke", "Mindestens ein Längsstab", "19"), ("$135^\\circ$-Haken", "Zulässige Bügelverankerung", "18"),
    ("$2a$", "Wirksame Wanddicke, Gl. (33)", "6"), ("$\\nu_2$", "Abminderung ab C55/67", "10"),
    ("$\\cot\\theta \\le 3{,}0$", "Obere Grenze des Druckstrebenwinkels", "8"), ("Gl. (45) und (46)", "Entfall rechnerischer Bewehrung", "17"),
]

MINDMAP = {"t": "Bemessungsmodell", "teil": "5", "folie": "3–19", "c": [
    {"t": "Nachweise", "folie": "3–4", "c": [{"t": "(31) $«TEd» \\le «TRdmax»$"}, {"t": "(32) $«TEd» \\le «TRds»$"}, {"t": "kleinster Wandwiderstand maßgebend"}]},
    {"t": "Ersatzhohlkasten", "folie": "5–7", "c": [{"t": "(33) $«tefi» = 2a \\le «tvorh»$"}, {"t": "Kasten $\\le b/6$, beidseitig bewehrt: ganze Wand"}, {"t": "(34) Schubfluss, (35) Schubkraft"}]},
    {"t": "Druckstrebenwinkel", "folie": "8–9", "c": [{"t": "vereinfacht $45^\\circ$"}, {"t": "(36) $1{,}0 \\le \\cot\\theta \\le 3{,}0$"}, {"t": "(37) $«VEdTV»$"}]},
    {"t": "Widerstände", "folie": "10–14", "c": [{"t": "(38) Druckstrebe, $\\nu_2$ ab C55/67"}, {"t": "(39)/(41) Bügel"}, {"t": "(40)/(42) Längsbewehrung"}]},
    {"t": "Interaktion", "folie": "15–17", "c": [{"t": "Biegung: Längsbewehrung addieren"}, {"t": "(43) Kompakt quadratisch, (44) Kasten linear"}, {"t": "(45)/(46) Entfall + Mindestbewehrung"}]},
    {"t": "Konstruktion", "folie": "18–19", "c": [{"t": "geschlossene Bügel, $135^\\circ$-Haken $> 10\\,\\varnothing$"}, {"t": "Bügel $90^\\circ$ zur Achse"}, {"t": "$«sw» \\le «uk»/8$, $\\le \\min(b,h)$"},
                                                   {"t": "Längsstab in jeder Ecke"}, {"t": "Längsstababstand $\\le 35\\,\\mathrm{cm}$"}]},
]}

# ---------------------------------------------------------------- Übungsaufgaben
kNm, kN, cm, cm2, Nmm2 = r"\,\mathrm{kNm}", r"\,\mathrm{kN}", r"\,\mathrm{cm}", r"\,\mathrm{cm^2}", r"\,\mathrm{N/mm^2}"
DM = "As1>=4.909 ? NaN : As1<=0.785 ? 10 : As1<=1.131 ? 12 : As1<=1.539 ? 14 : As1<=2.011 ? 16 : As1<=3.142 ? 20 : 25"

AUFGABEN = [
    {"titel": "Bemessung und Bewehrungswahl", "teil": "5",
     "text": "Ein Rechteckbalken $b/h = #b:0#/#h:0#\\,\\mathrm{cm}$ aus #beton# und B500 wird durch $«TEd» = #T:0#\\,\\mathrm{kNm}$ beansprucht (Gleichgewichtstorsion, Vollquerschnitt). Schwerpunktabstand der Längsbewehrung $a = #a:1#\\,\\mathrm{cm}$, $\\theta = 45^\\circ$. Führen Sie die Nachweise nach dem Bemessungsmodell und wählen Sie Bügel ($\\varnothing 10$) und Längsstäbe.",
     "params": {"b": {"min": 30, "max": 50, "step": 5}, "h": {"min": 50, "max": 80, "step": 5}, "a": {"werte": [4, 4.5, 5]},
                "beton": {"werte": ["C30/37", "C35/45", "C55/67"]}, "T": {"min": 20, "max": 60, "step": 5}},
     "schritte": [
         BAUSTOFFE,
         {"titel": "Ersatzhohlkasten – Gl. (33)", "folie": "5–6", "text": "Vollquerschnitt: die vorhandene Wanddicke begrenzt nicht.",
          "formel": [r"«tefi» = 2a \le «tvorh», \qquad «Ak» = (b - «tef»)\,(h - «tef»), \qquad «uk» = 2\,\bigl[(b - «tef») + (h - «tef»)\bigr]"],
          "einsetzen": [rf"«tef» = 2 \cdot #a:1# = #tef:1#{cm}, \qquad «Ak» = #Ak:0#{cm2}, \qquad «uk» = #uk:1#{cm}"],
          "werte": [{"id": "tef", "expr": "2*a", "d": 1, "frage": True, "label": "«tef»", "einheit": "cm"},
                    {"id": "Ak", "expr": "(b-tef)*(h-tef)", "d": 0, "frage": True, "label": "«Ak»", "einheit": "cm²"},
                    {"id": "uk", "expr": "2*((b-tef)+(h-tef))", "d": 1, "frage": True, "label": "«uk»", "einheit": "cm"}]},
         {"titel": "Schubfluss und Schubkraft – Gl. (34) und (35)", "folie": "7",
          "formel": [r"«tauti»\,«tefi» = \dfrac{«TEd»}{2\,«Ak»}, \qquad «VEdi» = \dfrac{«TEd»}{2\,«Ak»}\,z_i"],
          "einsetzen": [r"«tauti»\,«tefi» = \dfrac{#T:0# \cdot 10^6}{2 \cdot #Ak:0# \cdot 10^2} = #v:1#\,\mathrm{N/mm}",
                        rf"z_1 = #h:0# - #tef:1# = #z1:1#{cm}, \qquad «VEdi» = #v:1# \cdot #z1:1# \cdot 10 \cdot 10^{{-3}} = #V1:1#{kN}"],
          "werte": [{"id": "v", "expr": "T*1e6/(2*Ak*100)", "d": 1, "frage": True, "label": "«tauti»\\,«tefi»", "einheit": "N/mm"},
                    {"id": "z1", "expr": "h-tef", "d": 1}, {"id": "V1", "expr": "v*z1*10/1e3", "d": 1, "frage": True, "label": "«VEdi»", "einheit": "kN"}]},
         {"titel": "Betondruckstreben – Gl. (38) und (31)", "folie": "10, 4", "text": "$\\nu = 0{,}525$, ab C55/67 zusätzlich mal $\\nu_2$.",
          "formel": [r"\nu_2 = 1{,}1 - \dfrac{«fck»}{500} \le 1, \qquad «TRdmax» = \dfrac{\nu\,«fcd»\,2\,«Ak»\,«tef»}{\cot\theta + \tan\theta} \ge «TEd»"],
          "einsetzen": [r"\nu_2 = #nu2:3#, \qquad \nu = 0{,}525 \cdot #nu2:3# = #nu:3#",
                        rf"«TRdmax» = \dfrac{{#nu:3# \cdot #fcd:2# \cdot 2 \cdot #Ak:0# \cdot 10^2 \cdot #tef:1# \cdot 10}}{{2}} \cdot 10^{{-6}} = #TRd:1#{kNm} \;#ok#"],
          "werte": [{"id": "nu2", "expr": "min(1, 1.1-fck/500)", "d": 3}, {"id": "nu", "expr": "0.525*nu2", "d": 3},
                    {"id": "TRd", "expr": "nu*fcd*2*Ak*100*tef*10/2/1e6", "d": 1, "frage": True, "label": "«TRdmax»", "einheit": "kNm"},
                    {"id": "ok", "expr": "T<=TRd ? '\\\\ge «TEd» \\\\quad\\\\checkmark' : '< «TEd» \\\\quad\\\\text{nicht erfüllt}'"}]},
         {"titel": "Erforderliche Bügel – Gl. (41)", "folie": "13",
          "formel": [r"\dfrac{«Aswerf»}{«sw»} = \dfrac{«TEd»}{2\,«Ak»}\,\dfrac{1}{«fyd»}\,\tan\theta"],
          "einsetzen": [r"\dfrac{«Aswerf»}{«sw»} = \dfrac{#T:0# \cdot 10^6}{2 \cdot #Ak:0# \cdot 10^2} \cdot \dfrac{1}{#fyd:1#} \cdot 1{,}0 \cdot 10 = #asw:2#\,\mathrm{cm^2/m}"],
          "werte": [{"id": "asw", "expr": "T*1e6/(2*Ak*100)/fyd*10", "d": 2, "frage": True, "label": "«Aswerf»/«sw»", "einheit": "cm²/m"}]},
         {"titel": "Erforderliche Längsbewehrung – Gl. (42)", "folie": "14",
          "formel": [r"«Aslerf» = \dfrac{«TEd»\,«uk»}{2\,«Ak»}\,\dfrac{1}{«fyd»}\,\cot\theta"],
          "einsetzen": [r"«Aslerf» = \dfrac{#T:0# \cdot 10^6 \cdot #uk:1# \cdot 10}{2 \cdot #Ak:0# \cdot 10^2} \cdot \dfrac{1}{#fyd:1#} \cdot 1{,}0 \cdot 10^{-2} = #asl:2#\,\mathrm{cm^2}"],
          "werte": [{"id": "asl", "expr": "T*1e6*uk*10/(2*Ak*100)/fyd/100", "d": 2, "frage": True, "label": "«Aslerf»", "einheit": "cm²"}]},
         {"titel": "Bügelabstand und Bügelwahl", "folie": "19", "text": "Bügel $\\varnothing 10$ ($0{,}785\\,\\mathrm{cm^2}$ je Schenkel); Abstand auf 2,5 cm abrunden.",
          "formel": [r"s_{\mathrm{w},\max} = \min\!\left(\dfrac{«uk»}{8};\; \min(b,h)\right), \qquad s_{\mathrm{w,erf}} = \dfrac{0{,}785}{«Aswerf»/«sw»}"],
          "einsetzen": [rf"s_{{\mathrm{{w}},\max}} = \min\!\left(\dfrac{{#uk:1#}}{{8}};\; #bmin:0#\right) = #smax:1#{cm}, \qquad s_{{\mathrm{{w,erf}}}} = \dfrac{{0{{,}}785}}{{#asw:2#}} \cdot 100 = #serf:1#{cm}",
                        r"\Rightarrow\; \text{gewählt: Bügel } \varnothing 10/#s:1#\,\mathrm{cm}"],
          "werte": [{"id": "bmin", "expr": "min(b,h)", "d": 0}, {"id": "smax", "expr": "min(uk/8, min(b,h))", "d": 1, "frage": True, "label": "s_{\\mathrm{w},\\max}", "einheit": "cm"},
                    {"id": "serf", "expr": "0.785/asw*100", "d": 1}, {"id": "s", "expr": "Math.floor(min(serf, smax)/2.5)*2.5", "d": 1, "frage": True, "label": "«sw»", "einheit": "cm"}]},
         {"titel": "Längsstäbe", "folie": "19", "text": "In jeder Ecke ein Stab, weitere gleichmäßig verteilt, Abstand höchstens 35 cm; symmetrisch, also gerade Anzahl.",
          "formel": [r"n \ge \max\!\left(4;\; 2\,\left\lceil\dfrac{«uk»}{2 \cdot 35}\right\rceil\right), \qquad A_{\mathrm{s,1}} = \dfrac{«Aslerf»}{n}"],
          "einsetzen": [r"n = \max\!\left(4;\; 2\,\left\lceil\dfrac{#uk:1#}{70}\right\rceil\right) = #n:0#, \qquad A_{\mathrm{s,1}} = \dfrac{#asl:2#}{#n:0#} = #As1:3#\,\mathrm{cm^2} \;\Rightarrow\; #n:0#\,\varnothing #dm:0#"],
          "werte": [{"id": "n", "expr": "max(4, 2*Math.ceil(uk/70))", "d": 0, "frage": True, "label": "n", "einheit": "Stäbe"},
                    {"id": "As1", "expr": "asl/n", "d": 3}, {"id": "dm", "expr": DM, "d": 0, "frage": True, "label": "\\varnothing", "einheit": "mm"}]},
     ]},

    {"titel": "Entfall rechnerischer Bewehrung", "teil": "5",
     "text": "Ein Rechteckbalken $b/h = #b:0#/#h:0#\\,\\mathrm{cm}$ aus #beton# ($a = #a:1#\\,\\mathrm{cm}$, Längsbewehrungsgrad $\\rho_{\\mathrm{l}} = #rho:1#\\,\\%$) erhält $«VEd» = #V:0#\\,\\mathrm{kN}$ und $«TEd» = #T:1#\\,\\mathrm{kNm}$. Prüfen Sie, ob auf rechnerische Querkraft- und Torsionsbewehrung verzichtet werden darf.",
     "params": {"b": {"min": 25, "max": 40, "step": 5}, "h": {"min": 40, "max": 70, "step": 5}, "a": {"werte": [4, 5]},
                "beton": {"werte": ["C25/30", "C30/37"]}, "T": {"min": 0.5, "max": 4, "step": 0.5}, "V": {"min": 20, "max": 70, "step": 10}, "rho": {"werte": [0.8, 1.0, 1.5]}},
     "schritte": [
         {"titel": "Querkraftwiderstand ohne Bewehrung", "quelle": B3,
          "formel": [r"«VRdc» = \max\!\left[0{,}10\,k\,(100\,\rho_{\mathrm{l}}\,«fck»)^{1/3};\; \dfrac{0{,}0525}{1{,}5}\,k^{3/2}\,«fck»^{1/2}\right] «bw»\,d, \qquad k = 1 + \sqrt{200/d} \le 2"],
          "einsetzen": [r"d = #h:0# - #a:1# = #d:1#\,\mathrm{cm}, \qquad k = #k:3#",
                        rf"«VRdc» = \max(#v1:3#;\; #vmin:3#) \cdot #b:0# \cdot 10 \cdot #d:1# \cdot 10 \cdot 10^{{-3}} = #VRdc:1#{kN}"],
          "werte": [{"id": "fck", "expr": "FCK(beton)", "d": 0}, {"id": "d", "expr": "h-a", "d": 1}, {"id": "k", "expr": "min(1+sqrt(200/(d*10)), 2)", "d": 3},
                    {"id": "v1", "expr": "0.1*k*cbrt(100*min(rho/100,0.02)*fck)", "d": 3}, {"id": "vmin", "expr": "0.0525/1.5*pow(k,1.5)*sqrt(fck)", "d": 3},
                    {"id": "VRdc", "expr": "max(v1, vmin)*b*10*d*10/1e3", "d": 1, "frage": True, "label": "«VRdc»", "einheit": "kN"}]},
         {"titel": "Bedingung 1 – Gl. (45)", "folie": "17", "formel": [r"«TEd» \le \dfrac{«VEd»\,«bw»}{4{,}5}"],
          "einsetzen": [r"\dfrac{«VEd»\,«bw»}{4{,}5} = \dfrac{#V:0# \cdot #bm:2#}{4{,}5} = #g1:2#\,\mathrm{kNm} \;#c1Txt#"],
          "werte": [{"id": "bm", "expr": "b/100", "d": 2}, {"id": "g1", "expr": "V*bm/4.5", "d": 2, "frage": True, "label": "«VEd»\\,«bw»/4{,}5", "einheit": "kNm"},
                    {"id": "c1", "expr": "T<=g1"},
                    {"id": "c1Txt", "expr": "c1 ? '\\\\ge «TEd» = #T:1#\\\\,\\\\mathrm{kNm} \\\\quad\\\\checkmark' : '< «TEd» = #T:1#\\\\,\\\\mathrm{kNm} \\\\quad\\\\text{nicht erfüllt}'"}]},
         {"titel": "Bedingung 2 – Gl. (46)", "folie": "17", "formel": [r"«VEd» + \dfrac{4{,}5\,«TEd»}{«bw»} \le «VRdc»"],
          "einsetzen": [r"«VEd» + \dfrac{4{,}5\,«TEd»}{«bw»} = #V:0# + \dfrac{4{,}5 \cdot #T:1#}{#bm:2#} = #g2:1#\,\mathrm{kN} \;#c2Txt#"],
          "werte": [{"id": "g2", "expr": "V+4.5*T/bm", "d": 1, "frage": True, "label": "«VEd» + 4{,}5\\,«TEd»/«bw»", "einheit": "kN"},
                    {"id": "c2", "expr": "g2<=VRdc"},
                    {"id": "c2Txt", "expr": "c2 ? '\\\\le «VRdc» = #VRdc:1#\\\\,\\\\mathrm{kN} \\\\quad\\\\checkmark' : '> «VRdc» = #VRdc:1#\\\\,\\\\mathrm{kN} \\\\quad\\\\text{nicht erfüllt}'"}]},
         {"titel": "Ergebnis", "folie": "17",
          "einsetzen": [r"\Rightarrow\; \text{#fazit#}"],
          "werte": [{"id": "fazit", "expr": "c1 && c2 ? 'keine rechnerische Bewehrung – Mindestbewehrung vorsehen' : 'rechnerische Querkraft- und Torsionsbewehrung erforderlich'"}]},
     ]},
]

# ---------------------------------------------------------------- Quiz
def Q(d, folie, f, r, falsch, tipp, erkl):
    return {"d": d, "teil": "5", "folie": folie, "f": f, "r": r, "falsch": falsch, "tipp": tipp, "erkl": erkl}


QUIZ = [
    Q(1, "3", "Welche zwei Widerstände sind beim Torsionsnachweis maßgebend?", "$«TRdmax»$ und $«TRds»$",
      {"leicht": ["$M_{\\mathrm{Rd}}$ und $N_{\\mathrm{Rd}}$", "$«VRdc»$ und $M_{\\mathrm{Rd}}$", "$N_{\\mathrm{Rd}}$ und $«VRdc»$"],
       "mittel": ["$«TRdmax»$ und $«VRdc»$", "$«TRds»$ und $M_{\\mathrm{Rd}}$"]},
      "Druckstreben und Zugstreben.",
      "Folie 3–4: $«TRdmax»$ für die Betondruckstreben, Gl. (31), und $«TRds»$ für die Bewehrung, Gl. (32). Beide Nachweise müssen erfüllt sein."),
    Q(2, "3", "Welcher Widerstand ist maßgebend, wenn der Querschnitt aus mehreren Wänden besteht?", "Der kleinste Widerstand der Wände",
      {"leicht": ["Nur der Widerstand der längsten Wand"], "mittel": ["Der Mittelwert aller Wandwiderstände", "Die Summe aller Wandwiderstände"],
       "schwer": ["Der größte Widerstand der Wände", "Nur der Widerstand der oberen Wand"]},
      "Die schwächste Stelle entscheidet.",
      "Folie 3: Der jeweils kleinste maßgebende Widerstand der Wände $i$ ist zu beachten."),
    Q(2, "6", "Wie groß ist die wirksame Wanddicke $«tefi»$, Gl. (33)?", "$«tefi» = 2a \\le «tvorh»$",
      {"mittel": ["$«tefi» = a \\le «tvorh»$", "$«tefi» = A/u \\ge 2a$"],
       "schwer": ["$«tefi» = 2a \\ge «tvorh»$", "$«tefi» = 2a \\le b/6$", "$«tefi» = 3a \\le «tvorh»$"]},
      "Doppelter Schwerpunktabstand – aber nie mehr als vorhanden.",
      "Gl. (33): doppelter Schwerpunktabstand $a$ der Längsbewehrung von der Außenkante, höchstens die vorhandene Wanddicke. Die Längsbewehrung liegt dann auf der Wandmittellinie."),
    Q(3, "6", "Wann darf bei Hohlkästen die gesamte Wanddicke als $«tef»$ angesetzt werden?", "Wand $\\le b/6$ bzw. $h/6$, beidseitig bewehrt",
      {"mittel": ["Immer, sobald der Kasten geschlossen ist", "Nur bei Vorspannung der Kastenwände"],
       "schwer": ["Wand $\\ge b/6$ bzw. $h/6$, beidseitig bewehrt", "Wand $\\le b/6$ bzw. $h/6$, einseitig bewehrt", "Wand $\\le b/3$ bzw. $h/3$, beidseitig bewehrt"]},
      "Dünne Wände – und Bewehrung auf beiden Seiten.",
      "Folie 6: Bei Hohlkästen mit Wanddicken $\\le b/6$ bzw. $h/6$ und beidseitiger Wandbewehrung ist die gesamte Wanddicke zulässig."),
    Q(3, "8", "In welchen Grenzen darf $\\cot\\theta$ nach Gl. (36) liegen?", "$1{,}0 \\le \\cot\\theta \\le 3{,}0$",
      {"mittel": ["$0 \\le \\cot\\theta \\le 1{,}0$", "$1{,}0 \\le \\cot\\theta \\le 1{,}5$"],
       "schwer": ["$0{,}5 \\le \\cot\\theta \\le 2{,}0$", "$1{,}0 \\le \\cot\\theta \\le 2{,}5$", "$1{,}2 \\le \\cot\\theta \\le 3{,}0$"]},
      "Untere Grenze: $45^\\circ$.",
      "Gl. (36): $1{,}0 \\le \\cot\\theta \\le (1{,}2 + 1{,}4\\,«scdN»/«fcd»)/(1 - «VRdcc»/«VEdTV») \\le 3{,}0$. Vereinfacht gilt $\\cot\\theta = 1$."),
    Q(3, "9", "Wie wird die kombinierte Schubkraft für die Winkelwahl gebildet, Gl. (37)?", "$«VEdTV» = «VEdT» + «VEd»\\,\\dfrac{«tef»}{«bw»}$",
      {"mittel": ["$«VEdTV» = «VEdT» + «VEd»$", "$«VEdTV» = «VEdT» \\cdot «VEd»$"],
       "schwer": ["$«VEdTV» = «VEdT» + «VEd»\\,\\dfrac{«bw»}{«tef»}$", "$«VEdTV» = «VEdT» + \\dfrac{«VEd»}{2}$", "$«VEdTV» = «VEdT» - «VEd»\\,\\dfrac{«tef»}{«bw»}$"]},
      "Von der Querkraft zählt nur der Anteil in der Wanddicke.",
      "Gl. (37): Zur Torsionsschubkraft der Wand kommt der Querkraftanteil, der auf die Wanddicke $«tef»$ entfällt, $«VEd»\\,«tef»/«bw»$."),
    Q(3, "10", "Was gilt für $\\nu$ ab Festigkeitsklasse C55/67, Gl. (38)?", "Zusätzlich mal $\\nu_2 = 1{,}1 - «fck»/500 \\le 1$",
      {"mittel": ["$\\nu$ wird für hochfesten Beton verdoppelt", "Keine Änderung gegenüber C50/60"],
       "schwer": ["Zusätzlich mal $\\nu_2 = 1{,}0 - «fck»/500 \\le 1$", "Zusätzlich mal $\\nu_2 = 1{,}1 - «fck»/250 \\le 1$", "Zusätzlich mal $\\nu_2 = 1{,}1 + «fck»/500 \\ge 1$"]},
      "Hochfester Beton ist spröder – also eine Abminderung.",
      "Folie 10: Ab C55/67 wird $\\nu$ zusätzlich mit $\\nu_2 = 1{,}1 - «fck»/500 \\le 1$ multipliziert, z. B. 0,98 für C55/67."),
    Q(2, "13", "Wie lautet die erforderliche Torsionsbügelbewehrung, Gl. (41)?", "$\\dfrac{«Aswerf»}{«sw»} = \\dfrac{«TEd»}{2\\,«Ak»}\\,\\dfrac{1}{«fyd»}\\,\\tan\\theta$",
      {"mittel": ["$\\dfrac{«Aswerf»}{«sw»} = \\dfrac{«TEd»\\,«uk»}{2\\,«Ak»}\\,\\dfrac{1}{«fyd»}\\,\\tan\\theta$", "$\\dfrac{«Aswerf»}{«sw»} = \\dfrac{«TEd»}{2\\,«Ak»}\\,«fyd»\\,\\tan\\theta$"],
       "schwer": ["$\\dfrac{«Aswerf»}{«sw»} = \\dfrac{«TEd»}{«Ak»}\\,\\dfrac{1}{«fyd»}\\,\\tan\\theta$", "$\\dfrac{«Aswerf»}{«sw»} = \\dfrac{«TEd»}{2\\,«Ak»}\\,\\dfrac{1}{«fyd»}\\,\\sin\\theta$"]},
      "Gl. (39) mit $«TRdsw» = «TEd»$ umstellen; $1/\\cot\\theta = \\tan\\theta$.",
      "Gl. (41): erforderliche Fläche eines Bügelschenkels pro Längeneinheit. Bei der Längsbewehrung, Gl. (42), stehen $«uk»$ und $\\cot\\theta$."),
    Q(2, "19", "Wie sind weitere Längsstäbe neben den Eckstäben anzuordnen?", "Gleichmäßig über den inneren Bügelumfang",
      {"leicht": ["Nur unten in der Biegezugzone"], "mittel": ["Konzentriert in der Balkenmitte", "Nur an den beiden Schmalseiten"],
       "schwer": ["Gleichmäßig über den äußeren Betonumfang", "Gleichmäßig über die Kernfläche verteilt"]},
      "Innen an den Bügeln entlang.",
      "Folie 19: In jeder Ecke ein Längsstab, weitere gleichmäßig über den inneren Bügelumfang mit höchstens 35 cm Abstand."),
    Q(1, "17", "Was ist auch bei Entfall der rechnerischen Querkraft- und Torsionsbewehrung vorzusehen?", "Die Mindestbewehrung",
      {"leicht": ["Gar keine Bewehrung", "Nur eine Oberflächenbewehrung"], "mittel": ["Die volle Torsionsbewehrung", "Eine zusätzliche Vorspannung"]},
      "Folie 17, „Wichtig“.",
      "Folie 17: Auch wenn Gl. (45) und (46) erfüllt sind, ist die Mindestbewehrung vorzusehen."),
    Q(2, "18", "Unter welchem Winkel zur Bauteilachse sollen Torsionsbügel liegen?", "$90^\\circ$",
      {"leicht": ["$0^\\circ$"], "mittel": ["$45^\\circ$", "$60^\\circ$"], "schwer": ["$135^\\circ$", "$75^\\circ$"]},
      "Wie im Fachwerkmodell mit $\\alpha = 90^\\circ$.",
      "Folie 18: Bügel sollen $90^\\circ$ zur Bauteilachse bilden – wie im Raumfachwerk mit $90^\\circ$-Bügeln (Teil 3)."),
    Q(3, "17", "Wie lautet die zweite Bedingung für den Entfall der rechnerischen Bewehrung, Gl. (46)?", "$«VEd» + \\dfrac{4{,}5\\,«TEd»}{«bw»} \\le «VRdc»$",
      {"mittel": ["$«VEd» + «TEd» \\le «VRdc»$", "$«VEd» \\le «VRdmax»$"],
       "schwer": ["$«VEd» + \\dfrac{4{,}5\\,«TEd»}{«bw»} \\le «VRdmax»$", "$«VEd» + \\dfrac{«TEd»}{4{,}5\\,«bw»} \\le «VRdc»$", "$«VEd» + 4{,}5\\,«TEd»\\,«bw» \\le «VRdc»$"]},
      "Widerstand ohne Querkraftbewehrung.",
      "Gl. (46): Die Torsion wird über $4{,}5\\,«TEd»/«bw»$ in eine Ersatzquerkraft umgerechnet; die Summe muss unter $«VRdc»$ (ohne Querkraftbewehrung) bleiben."),
    Q(2, "18", "Welche Hakenform ist für Torsionsbügel zulässig?", "$135^\\circ$-Haken, Länge über $10\\,\\varnothing$",
      {"leicht": ["Gerade Enden ganz ohne Haken"], "mittel": ["$90^\\circ$-Winkelhaken, Länge $5\\,\\varnothing$", "$180^\\circ$-Haken ohne Mindestlänge"],
       "schwer": ["$135^\\circ$-Haken, Länge über $5\\,\\varnothing$", "$90^\\circ$-Winkelhaken, über $10\\,\\varnothing$"]},
      "Keine Winkelhaken.",
      "Folie 18: Torsionsbügel müssen geschlossen und verankert sein – nur $135^\\circ$-Haken mit Hakenlänge $> 10\\,\\varnothing$, keine Winkelhaken."),
]

UMBAU = {
    "Welche Bügel braucht man": {"teil": "5", "folie": "18",
        "erkl": "Folie 18: Torsionsbügel müssen geschlossen und verankert sein – $135^\\circ$-Haken mit Länge $> 10\\,\\varnothing$, keine Winkelhaken. Der Schubfluss läuft um den ganzen Querschnitt."},
    "Wo muss Torsionslängsbewehrung": {"teil": "5", "folie": "19",
        "erkl": "Folie 19: In jeder Ecke mindestens ein Längsstab; die Gurte des räumlichen Fachwerks laufen in den Ecken zusammen. Weitere Stäbe gleichmäßig über den inneren Bügelumfang."},
    "Wie groß darf der Längsabstand": {"teil": "5", "folie": "19",
        "f": "Wie groß darf der Längsabstand der Torsionsbügel höchstens sein?", "r": "$«uk»/8$",
        "falsch": {"mittel": ["$h/2$", "$300\\,\\mathrm{mm}$"], "schwer": ["$«uk»/4$", "$«uk»/10$", "$«uk»/6$"]},
        "tipp": "Ein Bruchteil des Kernumfangs.",
        "erkl": "Folie 19: höchstens $«uk»/8$, zusätzlich nicht größer als die kleinste Querschnittsabmessung und die Abstände der Querkraftbewehrung."},
    "Welchen Größtabstand": {"teil": "5", "folie": "19",
        "f": "Welchen Größtabstand dürfen die Torsionslängsstäbe untereinander haben?",
        "erkl": "Folie 19: höchstens 35 cm, gleichmäßig über den inneren Bügelumfang verteilt; in jeder Ecke mindestens ein Stab."},
    "Welche Bedingung gehört nach DE NA": {"teil": "5", "folie": "17",
        "f": "Welche Bedingung gehört zum Entfall der rechnerischen Querkraft- und Torsionsbewehrung (Gl. 45)?",
        "erkl": "Gl. (45) für näherungsweise rechteckige Vollquerschnitte; zusätzlich muss Gl. (46) $«VEd» + 4{,}5\\,«TEd»/«bw» \\le «VRdc»$ erfüllt sein. Die Mindestbewehrung ist dennoch vorzusehen."},
}


def inhalte():
    karten = [{"v": v, "r": r, "teil": "5", "folie": fo} for v, fo, r in KARTEN]
    formeln = [{"name": n, "f": f, "e": e, "teil": "5", **({"gl": g} if g else {}), "folie": fo} for n, g, fo, f, e in FORMELN]
    formeln += [{"name": n, "f": f, "e": e, "teil": "5", "quelle": B3} for n, f, e in FORMELN_B3]
    paare = [{"a": a, "b": b, "teil": "5", "folie": fo} for a, b, fo in PAARE]
    return ex(karten), ex(formeln), ex(paare), ex(MINDMAP), ex(AUFGABEN)


if __name__ == "__main__":
    ziel = Path(__file__).resolve().parent.parent / "content" / "01_torsion.json"
    d = json.loads(ziel.read_text(encoding="utf-8"))
    karten, formeln, paare, mindmap, aufgaben = inhalte()
    andere = lambda liste: [x for x in liste if x.get("teil") not in ("5", "B")]
    d["teile"] = [t for t in d["teile"] if t["id"] not in ("5", "B")] + [TEIL]
    d["karten"] = andere(d["karten"]) + karten
    d["formeln"] = andere(d["formeln"]) + formeln
    d["paare"] = andere(d["paare"]) + paare
    d["aufgaben"] = andere(d["aufgaben"]) + aufgaben
    d["mindmap"]["c"] = [b for b in d["mindmap"]["c"] if b.get("teil") not in ("5", "B")] + [mindmap]
    d["status"] = "teilweise"
    d["statusText"] = ("Skript Teil 1 bis 5 sind eingearbeitet – Gleichungsnummern und Folien wie im Skript. "
                       "Mit Teil 6 (Bemessungsbeispiel) werden Übungen und Bemessungstool noch am Beispiel abgeglichen.")
    ziel.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Teil 5: {len(karten)} Karten, {len(formeln)} Formeln, {len(paare)} Paare, {len(aufgaben)} Aufgaben")
