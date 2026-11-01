"""Bemessungstool Torsion – Quelle für content/01_torsion.json (Feld "rechner").

Rechenweg nach Skript Teil 5 (Bemessungsmodell, Gl. 31–46) mit Teil 3 (Gl. 16–18) und Teil 4 (Gl. 26–28);
jeder Schritt trägt seine Fundstelle (teil + folie bzw. quelle). Baustoffwerte und Querkraftgrößen nach Betonbau 3.

Jeder Schritt: titel, text, wenn (Bedingung), formel (Ansatz), einsetzen (Zahlen), werte (Berechnung).
Rechnung in den Einheiten der Eingabe (cm, kNm, kN); Umrechnung steht jeweils im Ausdruck.
Kürzel wie «TEd» → siehe tools/teil2bis4_torsion.py (SYM) und tools/teil5_torsion.py (SYM5).

Aufruf: python tools/rechner_torsion.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from teil5_torsion import ex as expand  # noqa: E402

kNm, kN, cm, cm2, Nmm2, Nmm = r"\,\mathrm{kNm}", r"\,\mathrm{kN}", r"\,\mathrm{cm}", r"\,\mathrm{cm^2}", r"\,\mathrm{N/mm^2}", r"\,\mathrm{N/mm}"
cm2m = r"\,\mathrm{cm^2/m}"


def js(s):
    """LaTeX-Text als JavaScript-Zeichenkette für Ausdrücke"""
    return json.dumps(expand(s), ensure_ascii=False)


def wahl(bed, ja, nein):
    return f"({bed}) ? {js(ja)} : {js(nein)}"


OK, NICHT = r"\quad\checkmark", r"\quad\text{nicht erfüllt}"

EINGABEN = [
    {"id": "b", "label": "Breite $b$", "einheit": "cm", "default": 40, "step": 1, "min": 10, "d": 0},
    {"id": "h", "label": "Höhe $h$", "einheit": "cm", "default": 60, "step": 1, "min": 10, "d": 0},
    {"id": "d1", "label": "$a$ Achse Längsbew.", "einheit": "cm", "default": 5, "step": 0.5, "min": 2, "d": 1},
    {"id": "beton", "label": "Beton", "typ": "auswahl", "default": "C30/37",
     "werte": ["C20/25", "C25/30", "C30/37", "C35/45", "C40/50", "C45/55", "C50/60", "C55/67", "C60/75"]},
    {"id": "T", "label": "$«TEd»$", "einheit": "kNm", "default": 40, "step": 1, "min": 0, "d": 1},
    {"id": "V", "label": "$«VEd»$", "einheit": "kN", "default": 150, "step": 1, "min": 0, "d": 1, "hinweis": "0 = reine Torsion"},
    {"id": "cot", "label": r"$\cot\theta$", "default": 1.0, "step": 0.05, "min": 1, "max": 3, "d": 2,
     "hinweis": r"$1{,}0$ bis $3{,}0$ nach Gl. (36); $1{,}0 \Rightarrow \theta = 45^\circ$ vereinfacht (Skript Teil 5, Folie 8)"},
    {"id": "rho", "label": r"$\rho_{\mathrm{l}}$ Längsbew.", "einheit": "%", "default": 1.0, "step": 0.1, "min": 0, "d": 2,
     "hinweis": "nur für $«VRdc»$, Gl. (46)"},
    {"id": "quer", "label": "Querschnitt", "typ": "schalter", "default": "voll",
     "optionen": [{"v": "voll", "t": "Vollquerschnitt", "symbol": "voll", "sub": "Kern unwirksam, $\\nu = 0{,}525$"},
                  {"v": "kasten", "t": "Echter Hohlkasten", "symbol": "kasten", "sub": "innen und außen bewehrt, $\\nu = 0{,}75$"}]},
    {"id": "tw", "label": "Wanddicke $t$ des Hohlkastens", "einheit": "cm", "default": 12, "step": 1, "min": 3, "d": 0, "wenn": "quer=='kasten'",
     "hinweis": "$t \\le b/6$ bzw. $h/6$: $«tef» = t$, sonst $\\min(2a;\\,t)$ – Gl. (33)"},
]

T3, T4, T5 = {"teil": "3"}, {"teil": "4"}, {"teil": "5"}
B3 = "Betonbau 3 (Querkraft)"
SCHRITTE = [
    {"titel": "Eingangswerte",
     "einsetzen": [
         rf"b/h = #b:0#/#h:0#{cm}, \qquad a = #d1:1#{cm}",
         r"\text{Beton #beton#, Betonstahl B500}",
         rf"«TEd» = #T:1#{kNm}, \qquad «VEd» = #V:1#{kN}, \qquad \cot\theta = #cot:2#",
         {"wenn": "quer=='voll'", "t": r"\text{Vollquerschnitt}"},
         {"wenn": "quer=='kasten'", "t": rf"\text{{echter Hohlkasten, Wanddicke }} t = #tw:0#{cm}\text{{, innen und außen bewehrt}}"}]},

    {"titel": "Baustoffkennwerte", "quelle": "Betonbau 3",
     "formel": [r"«fcd» = \dfrac{\alpha_{\mathrm{cc}}\,«fck»}{\gamma_{\mathrm{c}}}, \qquad «fyd» = \dfrac{f_{\mathrm{yk}}}{\gamma_{\mathrm{s}}}",
                {"wenn": "fck>50", "t": r"\nu_2 = 1{,}1 - \dfrac{«fck»}{500} \le 1 \quad\text{(ab C55/67, Skript Teil 5, Folie 10)}"}],
     "einsetzen": [rf"«fcd» = \dfrac{{0{{,}}85 \cdot #fck:0#}}{{1{{,}}5}} = #fcd:2#{Nmm2}", rf"«fyd» = \dfrac{{500}}{{1{{,}}15}} = #fyd:1#{Nmm2}",
                   {"wenn": "fck>50", "t": r"\nu_2 = 1{,}1 - \dfrac{#fck:0#}{500} = #nu2:3#"}],
     "werte": [{"id": "fck", "expr": "FCK(beton)", "d": 0}, {"id": "fcd", "expr": "0.85*fck/1.5", "d": 2}, {"id": "fyd", "expr": "500/1.15", "d": 1},
               {"id": "nu2", "expr": "min(1, 1.1-fck/500)", "d": 3}]},

    {"titel": "Ersatzhohlkasten – Gl. (33)", **T5, "folie": "5–6",
     "text": "Wanddicke aus dem doppelten Schwerpunktabstand $a$ der Längsbewehrung, höchstens die vorhandene Wanddicke. Kernfläche und Kernumfang beziehen sich auf die Wandmittellinie.",
     "formel": [r"«tefi» = 2a \le «tvorh»",
                {"wenn": "quer=='kasten'", "t": r"\text{Hohlkasten mit } t \le b/6 \text{ bzw. } h/6 \text{, beidseitig bewehrt: } «tef» = t"},
                r"«Ak» = (b - «tef»)\,(h - «tef»), \qquad «uk» = 2\,\bigl[(b - «tef») + (h - «tef»)\bigr]"],
     "einsetzen": [{"wenn": "quer=='voll'", "t": rf"«tef» = 2 \cdot #d1:1# = #tef0:1#{cm} \le «tvorh» = \tfrac{{1}}{{2}}\min(b,h) = #tvorh:1#{cm} \;\Rightarrow\; «tef» = #tef:1#{cm}"},
                   {"wenn": "quer=='kasten'", "t": rf"t = #tw:0#{cm} \;#kTxt#"},
                   rf"«Ak» = (#b:0# - #tef:1#)\,(#h:0# - #tef:1#) = #Ak:0#{cm2}",
                   rf"«uk» = 2\,\bigl[(#b:0# - #tef:1#) + (#h:0# - #tef:1#)\bigr] = #uk:1#{cm}"],
     "werte": [{"id": "tef0", "expr": "2*d1", "d": 1}, {"id": "b6", "expr": "min(b,h)/6", "d": 1},
               {"id": "tvorh", "expr": "quer=='kasten' ? tw : min(b,h)/2", "d": 1},
               {"id": "tef", "expr": "quer=='kasten' ? (tw<=b6 ? tw : min(2*d1, tw)) : min(2*d1, min(b,h)/2)", "d": 1},
               {"id": "kTxt", "expr": wahl("tw<=b6", r"\le \min(b,h)/6 = #b6:1#\,\mathrm{cm} \;\Rightarrow\; «tef» = t = #tef:1#\,\mathrm{cm}",
                                            r"> \min(b,h)/6 = #b6:1#\,\mathrm{cm} \;\Rightarrow\; «tef» = \min(2a;\,t) = #tef:1#\,\mathrm{cm}")},
               {"id": "Ak", "expr": "(b-tef)*(h-tef)", "d": 0}, {"id": "uk", "expr": "2*((b-tef)+(h-tef))", "d": 1}]},

    {"titel": "Schubfluss und Schubkräfte – Gl. (34) und (35)", **T5, "folie": "7",
     "text": "Wandhöhen zwischen den Schnittpunkten der Mittellinien: Seitenwand $z_1 = h - «tef»$, Gurt $z_2 = b - «tef»$.",
     "formel": [r"«tauti»\,«tefi» = \dfrac{«TEd»}{2\,«Ak»}, \qquad «VEdi» = \dfrac{«TEd»}{2\,«Ak»}\,z_i"],
     "einsetzen": [rf"«tauti»\,«tefi» = \dfrac{{#T:1# \cdot 10^6}}{{2 \cdot #Ak:0# \cdot 10^2}} = #v:1#{Nmm}",
                   rf"\text{{Seitenwand: }} V_{{\mathrm{{Ed}},T,1}} = #v:1# \cdot #z1:1# \cdot 10 \cdot 10^{{-3}} = #VT1:1#{kN}, \qquad \text{{Gurt: }} V_{{\mathrm{{Ed}},T,2}} = #VT2:1#{kN}"],
     "werte": [{"id": "v", "expr": "T*1e6/(2*Ak*100)", "d": 1}, {"id": "z1", "expr": "h-tef", "d": 1}, {"id": "z2", "expr": "b-tef", "d": 1},
               {"id": "VT1", "expr": "v*z1*10/1e3", "d": 1}, {"id": "VT2", "expr": "v*z2*10/1e3", "d": 1}]},

    {"titel": "Druckstrebenwinkel – Gl. (36) und (37)", **T5, "folie": "8–9",
     "text": "Vereinfacht $\\theta = 45^\\circ$. Genauer: Grenzwert für die Seitenwand mit der kombinierten Schubkraft; derselbe Winkel gilt für Querkraft- und Torsionsnachweis. $«VRdcc»$ nach Betonbau 3 für die Wand ($«bw» = «tef»$, $z = z_1$), ohne Längskraft ($«scdN» = 0$).",
     "formel": [r"«VEdTV» = «VEdT» + «VEd»\,\dfrac{«tef»}{«bw»}, \qquad «VRdcc» = 0{,}5 \cdot 0{,}48\,«fck»^{1/3}\,«tef»\,z_1",
                r"1{,}0 \le \cot\theta \le \dfrac{1{,}2 + 1{,}4\,«scdN»/«fcd»}{1 - «VRdcc»/«VEdTV»} \le 3{,}0"],
     "einsetzen": [rf"«VEdTV» = #VT1:1# + #V:1# \cdot \dfrac{{#tef:1#}}{{#bwV:0#}} = #VTV:1#{kN}, \qquad «VRdcc» = 0{{,}}24 \cdot #fck:0#^{{1/3}} \cdot #tef:1# \cdot 10 \cdot #z1:1# \cdot 10 \cdot 10^{{-3}} = #VRdcc:1#{kN}",
                   {"wenn": "VTV>VRdcc", "t": r"\cot\theta \le \dfrac{1{,}2}{1 - #VRdcc:1#/#VTV:1#} = #cotraw:2# \;\Rightarrow\; \cot\theta_{\max} = #cotmax:2#"},
                   {"wenn": "VTV<=VRdcc", "t": r"«VEdTV» \le «VRdcc» \;\Rightarrow\; \cot\theta_{\max} = 3{,}0"},
                   r"\text{gewählt: } \cot\theta = #cot:2# \;#cotOk#, \qquad \theta = #th:1#^\circ, \qquad \cot\theta + \tan\theta = #ct:3#"],
     "werte": [{"id": "bwV", "expr": "quer=='kasten' ? 2*tw : b", "d": 0}, {"id": "VTV", "expr": "VT1+V*tef/bwV", "d": 1}, {"id": "VRdcc", "expr": "0.5*0.48*cbrt(fck)*tef*10*z1*10/1e3", "d": 1},
               {"id": "cotraw", "expr": "VTV>VRdcc ? 1.2/(1-VRdcc/VTV) : 3", "d": 2}, {"id": "cotmax", "expr": "max(1, min(3, cotraw))", "d": 2},
               {"id": "cotOk", "expr": wahl("cot<=cotmax+1e-9", r"\le \cot\theta_{\max} \quad\checkmark", r"> \cot\theta_{\max} \quad\text{nicht zulässig}")},
               {"id": "th", "expr": "atan(1/cot)*180/PI", "d": 1}, {"id": "tanT", "expr": "1/cot", "d": 3},
               {"id": "ct", "expr": "cot+1/cot", "d": 3}, {"id": "sinT", "expr": "sin(atan(1/cot))", "d": 3}]},

    {"titel": "Strebenkräfte der Seitenwand – Gl. (16) bis (18)", **T3, "folie": "8–9",
     "formel": [r"|«Fcd»| = \dfrac{«VEdT»}{\sin\theta}, \qquad «Fsld» = «VEdT»\cot\theta, \qquad «Fswd» = «VEdT»"],
     "einsetzen": [rf"|«Fcd»| = \dfrac{{#VT1:1#}}{{#sinT:3#}} = #Fc:1#{kN}, \qquad «Fsld» = #VT1:1# \cdot #cot:2# = #Fs:1#{kN}, \qquad «Fswd» = #VT1:1#{kN}"],
     "werte": [{"id": "Fc", "expr": "VT1/sinT", "d": 1}, {"id": "Fs", "expr": "VT1*cot", "d": 1}]},

    {"titel": "Betondruckstreben – Gl. (38) und (31)", **T5, "folie": "10, 4",
     "formel": [r"«TRdmax» = \dfrac{\nu\,«fcd»\,2\,«Ak»\,«tef»}{\cot\theta + \tan\theta} \ge «TEd»",
                {"wenn": "quer=='voll'", "t": r"\nu = 0{,}525\,\nu_2 \quad\text{(allgemein)}"},
                {"wenn": "quer=='kasten'", "t": r"\nu = 0{,}75\,\nu_2 \quad\text{(echter Kasten, innen und außen bewehrt)}"}],
     "einsetzen": [r"\nu = #nuB:3# \cdot #nu2:3# = #nu:3#",
                   rf"«TRdmax» = \dfrac{{#nu:3# \cdot #fcd:2# \cdot 2 \cdot #Ak:0# \cdot 10^2 \cdot #tef:1# \cdot 10}}{{#ct:3#}} \cdot 10^{{-6}} = #TRd:1#{kNm}",
                   r"\dfrac{«TEd»}{«TRdmax»} = \dfrac{#T:1#}{#TRd:1#} = #etaT:3# \;#etaTOk#"],
     "werte": [{"id": "nuB", "expr": "quer=='kasten' ? 0.75 : 0.525", "d": 3}, {"id": "nu", "expr": "nuB*nu2", "d": 3},
               {"id": "TRd", "expr": "nu*fcd*2*Ak*100*tef*10/ct/1e6", "d": 1}, {"id": "etaT", "expr": "T/TRd", "d": 3},
               {"id": "etaTOk", "expr": wahl("etaT<=1", r"\le 1" + OK, "> 1" + NICHT)}]},

    {"titel": "Erforderliche Torsionsbügel – Gl. (41)", **T5, "folie": "13",
     "text": "Aus Gl. (39) mit $«TRdsw» = «TEd»$; Fläche eines Bügelschenkels pro Längeneinheit.",
     "formel": [r"\dfrac{«Aswerf»}{«sw»} = \dfrac{«TEd»}{2\,«Ak»}\,\dfrac{1}{«fyd»}\,\tan\theta"],
     "einsetzen": [rf"\dfrac{{«Aswerf»}}{{«sw»}} = \dfrac{{#T:1# \cdot 10^6}}{{2 \cdot #Ak:0# \cdot 10^2}} \cdot \dfrac{{1}}{{#fyd:1#}} \cdot #tanT:3# \cdot 10 = #asw:2#{cm2m}"],
     "werte": [{"id": "asw", "expr": "T*1e6/(2*Ak*100*fyd*cot)*10", "d": 2}]},

    {"titel": "Erforderliche Torsionslängsbewehrung – Gl. (42)", **T5, "folie": "14",
     "text": "Aus Gl. (40) mit $«TRdsl» = «TEd»$; zur Längsbewehrung aus Biegung addieren (Folie 15).",
     "formel": [r"«Aslerf» = \dfrac{«TEd»\,«uk»}{2\,«Ak»}\,\dfrac{1}{«fyd»}\,\cot\theta"],
     "einsetzen": [rf"«Aslerf» = \dfrac{{#T:1# \cdot 10^6 \cdot #uk:1# \cdot 10}}{{2 \cdot #Ak:0# \cdot 10^2}} \cdot \dfrac{{1}}{{#fyd:1#}} \cdot #cot:2# \cdot 10^{{-2}} = #asl:2#{cm2}"],
     "werte": [{"id": "asl", "expr": "T*1e6*uk*10*cot/(2*Ak*100*fyd)/100", "d": 2}]},

    {"titel": "Äquivalente Normalkraft aus Torsion – Gl. (26)", **T4, "folie": "5, 7",
     "text": "Alternative zur Addition der Längsbewehrung: Torsion als zusätzliche Normalkraft in der Biegebemessung, hier mit den erforderlichen Torsionsbügeln.",
     "formel": [r"«NT» = \left(\dfrac{«TEd»}{2\,«Ak»}\right)^2 «uk»\,\dfrac{«sw»}{«Asw»\,«fyd»}"],
     "einsetzen": [rf"«NT» = #v:1#^2 \cdot \dfrac{{#uk:1# \cdot 10}}{{#asw:2# \cdot 10^{{-1}} \cdot #fyd:1#}} \cdot 10^{{-3}} = #NT:1#{kN} \quad (= «Asl»\,«fyd»)"],
     "werte": [{"id": "NT", "expr": "v*v*uk*10/(asw/10*fyd)/1e3", "d": 1}]},

    {"titel": "Konstruktive Regeln", **T5, "folie": "18–19",
     "text": "Bügel geschlossen, nur $135^\\circ$-Haken mit Länge $> 10\\,\\varnothing$, $90^\\circ$ zur Bauteilachse; Abstände der Querkraftbewehrung zusätzlich einhalten. In jeder Ecke ein Längsstab, weitere gleichmäßig über den inneren Bügelumfang, Abstand höchstens 35 cm.",
     "formel": [r"s_{\mathrm{w},\max} = \min\!\left(\dfrac{«uk»}{8};\, \min(b,h)\right), \qquad n_{\mathrm{sl}} \ge \max\!\left(4;\; 2\left\lceil\dfrac{«uk»}{2 \cdot 35}\right\rceil\right)"],
     "einsetzen": [rf"s_{{\mathrm{{w}},\max}} = \min\!\left(\dfrac{{#uk:1#}}{{8}};\, #bmin:0#\right) = #smax:1#{cm}, \qquad n_{{\mathrm{{sl}}}} \ge #nsl:0# \text{{ Stäbe}}"],
     "werte": [{"id": "bmin", "expr": "min(b,h)", "d": 0}, {"id": "smax", "expr": "min(uk/8, min(b,h))", "d": 1},
               {"id": "nsl", "expr": "max(4, 2*Math.ceil(uk/70))", "d": 0}]},

    {"titel": "Querkraft-Druckstrebe", "wenn": "V>0", "quelle": B3,
     "formel": [r"d = h - a, \qquad z = 0{,}9\,d, \qquad «VRdmax» = \dfrac{«bw»\,z\,\nu_1\,«fcd»}{\cot\theta + \tan\theta}, \quad \nu_1 = 0{,}75\,\nu_2"],
     "einsetzen": [rf"d = #h:0# - #d1:1# = #d:1#{cm}, \qquad z = 0{{,}}9 \cdot #d:1# = #z:2#{cm}",
                   {"wenn": "quer=='kasten'", "t": rf"«bw» = 2 \cdot t = 2 \cdot #tw:0# = #bwV:0#{cm} \quad\text{{(beide Stege)}}"},
                   rf"«VRdmax» = \dfrac{{#bwV:0# \cdot 10 \cdot #z:2# \cdot 10 \cdot #nu1:3# \cdot #fcd:2#}}{{#ct:3#}} \cdot 10^{{-3}} = #VRd:1#{kN}"],
     "werte": [{"id": "d", "expr": "h-d1", "d": 1}, {"id": "z", "expr": "0.9*d", "d": 2}, {"id": "nu1", "expr": "0.75*nu2", "d": 3},
               {"id": "VRd", "expr": "bwV*10*z*10*nu1*fcd/ct/1e3", "d": 1}, {"id": "etaV", "expr": "V/VRd", "d": 3}]},

    {"titel": "Interaktion der Druckstreben – Gl. (43) bzw. (44)", "wenn": "V>0", **T5, "folie": "16",
     "formel": [{"wenn": "quer=='voll'", "t": r"\left(\dfrac{«TEd»}{«TRdmax»}\right)^2 + \left(\dfrac{«VEd»}{«VRdmax»}\right)^2 \le 1{,}0 \quad\text{(Kompaktquerschnitt)}"},
                {"wenn": "quer=='kasten'", "t": r"\dfrac{«TEd»}{«TRdmax»} + \dfrac{«VEd»}{«VRdmax»} \le 1{,}0 \quad\text{(Kastenquerschnitt)}"}],
     "einsetzen": [{"wenn": "quer=='voll'", "t": r"\left(\dfrac{#T:1#}{#TRd:1#}\right)^2 + \left(\dfrac{#V:1#}{#VRd:1#}\right)^2 = #inter:3# \;#interOk#"},
                   {"wenn": "quer=='kasten'", "t": r"\dfrac{#T:1#}{#TRd:1#} + \dfrac{#V:1#}{#VRd:1#} = #inter:3# \;#interOk#"}],
     "werte": [{"id": "inter", "expr": "quer=='kasten' ? etaT+etaV : etaT**2+etaV**2", "d": 3},
               {"id": "interOk", "expr": wahl("inter<=1", r"\le 1" + OK, "> 1" + NICHT)},
               {"id": "interArt", "expr": wahl("quer=='kasten'", "linear, Gl. (44)", "quadratisch, Gl. (43)")}]},

    {"titel": "Schubflüsse in den Stegen – Gl. (27)", "wenn": "V>0", **T4, "folie": "4, 8",
     "text": "In einem Steg addieren sich die Schubflüsse aus Querkraft und Torsion, im anderen wirken sie gegeneinander.",
     "formel": [r"«vEd» = \dfrac{«VEd»}{2\,z} \pm \dfrac{«TEd»}{2\,«Ak»}"],
     "einsetzen": [rf"\dfrac{{«VEd»}}{{2\,z}} = \dfrac{{#V:1# \cdot 10^3}}{{2 \cdot #z:2# \cdot 10}} = #vV:1#{Nmm}, \qquad \dfrac{{«TEd»}}{{2\,«Ak»}} = #v:1#{Nmm}",
                   rf"v_{{\mathrm{{Ed}},\max}} = #vV:1# + #v:1# = #vmax:1#{Nmm}, \qquad v_{{\mathrm{{Ed}},\min}} = #vV:1# - #v:1# = #vmin:1#{Nmm}"],
     "werte": [{"id": "vV", "expr": "V*1e3/(2*z*10)", "d": 1}, {"id": "vmax", "expr": "vV+v", "d": 1}, {"id": "vmin", "expr": "vV-v", "d": 1}]},

    {"titel": "Gesamte Bügelbewehrung – Gl. (28)", "wenn": "V>0", **T4, "folie": "9",
     "text": "Bügel gemäß Schubfluss addieren (Teil 5, Folie 16): Querkraftbügel (Betonbau 3) für beide Schenkel, Torsionsbügel für einen Schenkel, gleicher Druckstrebenwinkel.",
     "formel": [r"\dfrac{«AswV»}{«sw»} = \dfrac{«VEd»}{z\,«fyd»\cot\theta}, \qquad \dfrac{«Aswtot»}{«sw»} = \dfrac{«AswV»}{«sw»} + 2\,\dfrac{«AswT»}{«sw»}"],
     "einsetzen": [rf"\dfrac{{«AswV»}}{{«sw»}} = \dfrac{{#V:1# \cdot 10^3}}{{#z:2# \cdot 10 \cdot #fyd:1# \cdot #cot:2#}} \cdot 10 = #aswV:2#{cm2m}",
                   rf"\dfrac{{«Aswtot»}}{{«sw»}} = #aswV:2# + 2 \cdot #asw:2# = #aswtot:2#{cm2m} \;\Rightarrow\; \text{{je Schenkel }} #aswS:2#{cm2m}"],
     "werte": [{"id": "aswV", "expr": "V*1e3/(z*10*fyd*cot)*10", "d": 2}, {"id": "aswtot", "expr": "aswV+2*asw", "d": 2},
               {"id": "aswS", "expr": "aswtot/2", "d": 2}]},

    {"titel": "Entfall rechnerischer Bewehrung – Gl. (45) und (46)", "wenn": "V>0", **T5, "folie": "17",
     "text": "Für näherungsweise rechteckige Vollquerschnitte; $«VRdc»$ nach Betonbau 3. Die Mindestbewehrung ist in jedem Fall vorzusehen.",
     "formel": [r"«TEd» \le \dfrac{«VEd»\,«bw»}{4{,}5} \qquad\text{und}\qquad «VEd» + \dfrac{4{,}5\,«TEd»}{«bw»} \le «VRdc»"],
     "einsetzen": [r"k = 1 + \sqrt{\dfrac{200}{#d:1# \cdot 10}} = #k0:3# \;\Rightarrow\; k = #k:3#, \qquad \rho_{\mathrm{l}} = #rhol:4#",
                   rf"«VRdc» = \max\!\left[0{{,}}10 \cdot #k:3# \cdot (100 \cdot #rhol:4# \cdot #fck:0#)^{{1/3}};\; \dfrac{{0{{,}}0525}}{{1{{,}}5}} \cdot #k:3#^{{3/2}} \cdot #fck:0#^{{1/2}}\right] #b:0# \cdot 10 \cdot #d:1# \cdot 10 \cdot 10^{{-3}} = #VRdc:1#{kN}",
                   rf"\text{{Gl. (45): }} \dfrac{{«VEd»\,«bw»}}{{4{{,}}5}} = \dfrac{{#V:1# \cdot #bm:2#}}{{4{{,}}5}} = #g1:2#{kNm} \;#c1Txt#",
                   rf"\text{{Gl. (46): }} «VEd» + \dfrac{{4{{,}}5\,«TEd»}}{{«bw»}} = #V:1# + \dfrac{{4{{,}}5 \cdot #T:1#}}{{#bm:2#}} = #g2:1#{kN} \;#c2Txt#",
                   r"\Rightarrow\; #verzichtTxt#"],
     "werte": [{"id": "k0", "expr": "1+sqrt(200/(d*10))", "d": 3}, {"id": "k", "expr": "min(k0, 2)", "d": 3},
               {"id": "rhol", "expr": "min(rho/100, 0.02)", "d": 4}, {"id": "v1", "expr": "0.1*k*cbrt(100*rhol*fck)", "d": 3},
               {"id": "vmin2", "expr": "0.0525/1.5*pow(k,1.5)*sqrt(fck)", "d": 3},
               {"id": "VRdc", "expr": "max(v1, vmin2)*b*10*d*10/1e3", "d": 1}, {"id": "bm", "expr": "b/100", "d": 2},
               {"id": "g1", "expr": "V*bm/4.5", "d": 2}, {"id": "c1", "expr": "T<=g1"},
               {"id": "c1Txt", "expr": wahl("c1", r"\ge «TEd» = #T:1#\,\mathrm{kNm}" + OK, r"< «TEd» = #T:1#\,\mathrm{kNm}" + NICHT)},
               {"id": "g2", "expr": "V+4.5*T/bm", "d": 1}, {"id": "c2", "expr": "g2<=VRdc"},
               {"id": "c2Txt", "expr": wahl("c2", r"\le «VRdc» = #VRdc:1#\,\mathrm{kN}" + OK, r"> «VRdc» = #VRdc:1#\,\mathrm{kN}" + NICHT)},
               {"id": "verzicht", "expr": "quer=='voll' && c1 && c2"},
               {"id": "verzichtTxt", "expr": wahl("verzicht", r"\text{keine rechnerische Bewehrung, Mindestbewehrung vorsehen}",
                                                   r"\text{rechnerische Querkraft- und Torsionsbewehrung erforderlich}")},
               {"id": "verzichtWort", "expr": wahl("verzicht", "nein", "ja")},
               {"id": "verzichtSub", "expr": wahl("verzicht", "nur Mindestbewehrung, Gl. (45)/(46)", "Gl. (45)/(46) nicht erfüllt")}]},

    {"titel": "Ergebnis",
     "einsetzen": [r"\text{Druckstrebe: } «TEd»/«TRdmax» = #etaT:3# \;#etaTOk#, \qquad \cot\theta = #cot:2# \;#cotOk#",
                   {"wenn": "V>0", "t": r"\text{Interaktion: } #inter:3# \;#interOk#"},
                   r"\text{Torsionsbügel: } #asw:2#\,\mathrm{cm^2/m} \text{ je Schenkel}, \qquad «sw» \le #smax:1#\,\mathrm{cm}",
                   {"wenn": "V>0", "t": r"\text{Bügel gesamt (V + T): } #aswtot:2#\,\mathrm{cm^2/m}, \text{ je Schenkel } #aswS:2#\,\mathrm{cm^2/m}"},
                   r"\text{Torsionslängsbewehrung: } «Asl» = #asl:2#\,\mathrm{cm^2} \text{ auf mindestens } #nsl:0# \text{ Stäbe – zur Biegelängsbewehrung addieren}"]},
]

ERGEBNISSE = [
    {"titel": "Druckstrebe", "wert": "etaT*100", "d": 0, "einheit": "%", "sub": "Gl. (38), $«TRdmax» = #TRd:1#\\,\\mathrm{kNm}$", "eta": "etaT"},
    {"titel": "Druckstrebenwinkel", "wert": "cot", "d": 2, "einheit": "cot θ", "sub": "zulässig bis $#cotmax:2#$, Gl. (36)", "eta": "cot/cotmax"},
    {"titel": "Torsionsbügel je Schenkel", "wert": "asw", "d": 2, "einheit": "cm²/m", "sub": "Gl. (41), $s_{\\mathrm{w},\\max} = #smax:1#\\,\\mathrm{cm}$"},
    {"titel": "Torsionslängsbewehrung", "wert": "asl", "d": 2, "einheit": "cm²", "sub": "Gl. (42), mind. #nsl:0# Stäbe"},
    {"titel": "Interaktion $T + V$", "wenn": "V>0", "wert": "inter", "d": 2, "einheit": "≤ 1", "sub": "#interArt#", "eta": "inter"},
    {"titel": "Bügel gesamt", "wenn": "V>0", "wert": "aswtot", "d": 2, "einheit": "cm²/m", "sub": "Gl. (28), je Schenkel $#aswS:2#$"},
    {"titel": "Bewehrung rechnerisch nötig?", "wenn": "V>0", "wert": "verzichtWort", "einheit": "", "sub": "#verzichtSub#"},
]

PRUEFUNG = [{"wenn": "2*d1 >= min(b,h)", "text": "Bitte gültige Abmessungen eingeben: $2a$ muss kleiner als $b$ und $h$ sein."},
            {"wenn": "quer=='kasten' && 2*tw >= min(b,h)", "text": "Die Wanddicke des Hohlkastens muss kleiner als $b/2$ und $h/2$ sein."}]

RECHNER = {"typ": "torsion", "titel": "Torsionsbemessung Rechteckquerschnitt", "skizze": "rechteck_hohlkasten", "system": True,
           "hinweis": ("Rechenweg nach dem Bemessungsmodell aus Skript Teil 5 mit Teil 3 und 4 – Gleichungsnummern und Folien stehen bei jedem Schritt. "
                       "Baustoffwerte und Querkraftgrößen nach Betonbau 3."),
           "eingaben": EINGABEN, "schritte": SCHRITTE, "ergebnisse": ERGEBNISSE, "pruefung": PRUEFUNG}

if __name__ == "__main__":
    ziel = Path(__file__).resolve().parent.parent / "content" / "01_torsion.json"
    daten = json.loads(ziel.read_text(encoding="utf-8"))
    daten["rechner"] = expand(RECHNER)
    ziel.write_text(json.dumps(daten, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Rechner geschrieben: {len(SCHRITTE)} Schritte, {len(EINGABEN)} Eingaben")
