"""Bemessungstool Torsion – Quelle für content/01_torsion.json (Feld "rechner").

Rechenweg nach Skript Teil 3 (Tragmodell, Gl. 14–25) und Teil 4 (kombinierte Beanspruchung, Gl. 26–30);
jeder Schritt trägt seine Fundstelle (teil + folie bzw. quelle). Baustoffwerte und Querkraft nach Betonbau 3,
konstruktive Regeln und Verzicht auf den Nachweis vorläufig nach DIN EN 1992-1-1 + NA (folgen mit Skript Teil 5).

Jeder Schritt: titel, text, wenn (Bedingung), formel (Ansatz), einsetzen (Zahlen), werte (Berechnung).
Rechnung in den Einheiten der Eingabe (cm, kNm, kN); Umrechnung steht jeweils im Ausdruck.
Kürzel wie «TEd» → siehe tools/teil2bis4_torsion.py (SYM).

Aufruf: python tools/rechner_torsion.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from teil2bis4_torsion import expand  # noqa: E402

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
    {"id": "d1", "label": "$d_1$ Achse Längsbew.", "einheit": "cm", "default": 5, "step": 0.5, "min": 2, "d": 1},
    {"id": "beton", "label": "Beton", "typ": "auswahl", "default": "C30/37",
     "werte": ["C20/25", "C25/30", "C30/37", "C35/45", "C40/50", "C45/55", "C50/60"]},
    {"id": "T", "label": "$«TEd»$", "einheit": "kNm", "default": 40, "step": 1, "min": 0, "d": 1},
    {"id": "V", "label": "$«VEd»$", "einheit": "kN", "default": 150, "step": 1, "min": 0, "d": 1, "hinweis": "0 = reine Torsion"},
    {"id": "cot", "label": r"$\cot\theta$", "default": 1.0, "step": 0.05, "min": 1, "max": 1.75, "d": 2,
     "hinweis": r"$1{,}0 \Rightarrow \theta = 45^\circ$, empfohlen bei überwiegender Torsion (Skript Teil 3, Folie 18)"},
    {"id": "rho", "label": r"$\rho_{\mathrm{l}}$ Längsbew.", "einheit": "%", "default": 1.0, "step": 0.1, "min": 0, "d": 2,
     "hinweis": "nur für $«VRdc»$ (Verzicht auf Nachweis, vorläufig)"},
    {"id": "quer", "label": "Querschnitt", "typ": "schalter", "default": "voll",
     "optionen": [{"v": "voll", "t": "Vollquerschnitt"}, {"v": "kasten", "t": "Echter Hohlkasten"}]},
    {"id": "tefArt", "label": "Wanddicke $«tef»$", "typ": "schalter", "default": "na",
     "optionen": [{"v": "na", "t": r"$2\,d_1$ (Skript)"}, {"v": "ec2", "t": "$A/u$ (EC2, vorläufig)"}]},
]

T3, T4 = {"teil": "3"}, {"teil": "4"}
SCHRITTE = [
    {"titel": "Eingangswerte",
     "einsetzen": [
         rf"b/h = #b:0#/#h:0#{cm}, \qquad d_1 = #d1:1#{cm}",
         r"\text{Beton #beton#, Betonstahl B500}",
         rf"«TEd» = #T:1#{kNm}, \qquad «VEd» = #V:1#{kN}, \qquad \cot\theta = #cot:2#",
         {"wenn": "quer=='voll'", "t": r"\text{Vollquerschnitt}"},
         {"wenn": "quer=='kasten'", "t": r"\text{echter Hohlkasten, Wände innen und außen bewehrt}"}]},

    {"titel": "Baustoffkennwerte", "quelle": "Betonbau 3",
     "formel": [r"«fcd» = \dfrac{\alpha_{\mathrm{cc}}\,«fck»}{\gamma_{\mathrm{c}}}, \qquad «fyd» = \dfrac{f_{\mathrm{yk}}}{\gamma_{\mathrm{s}}}"],
     "einsetzen": [rf"«fcd» = \dfrac{{0{{,}}85 \cdot #fck:0#}}{{1{{,}}5}} = #fcd:2#{Nmm2}", rf"«fyd» = \dfrac{{500}}{{1{{,}}15}} = #fyd:1#{Nmm2}"],
     "werte": [{"id": "fck", "expr": "FCK(beton)", "d": 0}, {"id": "fcd", "expr": "0.85*fck/1.5", "d": 2}, {"id": "fyd", "expr": "500/1.15", "d": 1}]},

    {"titel": "Ersatzhohlkasten", **T3, "folie": "3",
     "text": "Wanddicke: doppelter Abstand der Schwerlinie der Längsbewehrung von der Bauteilaußenkante. Kernfläche und Kernumfang beziehen sich auf die Wandmittellinie.",
     "formel": [{"wenn": "tefArt=='na'", "t": r"«tef» = 2\,d_1"},
                {"wenn": "tefArt=='ec2'", "t": r"«tef» = \dfrac{A}{u} \ge 2\,d_1 \quad\text{(EC2, vorläufig)}"},
                r"«Ak» = (b - «tef»)\,(h - «tef»), \qquad «uk» = 2\,\bigl[(b - «tef») + (h - «tef»)\bigr]"],
     "einsetzen": [{"wenn": "tefArt=='na'", "t": rf"«tef» = 2 \cdot #d1:1# = #tef0:1#{cm}"},
                   {"wenn": "tefArt=='ec2'", "t": rf"«tef» = \dfrac{{#b:0# \cdot #h:0#}}{{2\,(#b:0# + #h:0#)}} = #tAu:2#{cm} \;\Rightarrow\; «tef» = \max(#tAu:2#;\,#tmin:1#) = #tef0:2#{cm}"},
                   {"wenn": "tef0>tefmax", "t": rf"«tef» \le \tfrac{{1}}{{2}}\min(b,h) = #tefmax:1#{cm} \;\Rightarrow\; «tef» = #tef:1#{cm}"},
                   rf"«Ak» = (#b:0# - #tef:1#)\,(#h:0# - #tef:1#) = #Ak:0#{cm2}",
                   rf"«uk» = 2\,\bigl[(#b:0# - #tef:1#) + (#h:0# - #tef:1#)\bigr] = #uk:1#{cm}"],
     "werte": [{"id": "tAu", "expr": "b*h/(2*(b+h))", "d": 2}, {"id": "tmin", "expr": "2*d1", "d": 1},
               {"id": "tef0", "expr": "tefArt=='na' ? 2*d1 : max(tAu, 2*d1)", "d": 2}, {"id": "tefmax", "expr": "min(b,h)/2", "d": 1},
               {"id": "tef", "expr": "min(tef0, tefmax)", "d": 1}, {"id": "Ak", "expr": "(b-tef)*(h-tef)", "d": 0},
               {"id": "uk", "expr": "2*((b-tef)+(h-tef))", "d": 1}]},

    {"titel": "Druckstrebenwinkel", **T3, "folie": "17–18",
     "text": "Bei überwiegender Torsion ist $\\theta = 45^\\circ$ wirtschaftlich: minimale Bewehrung, maximale Betontragfähigkeit.",
     "einsetzen": [r"\theta = \operatorname{arccot}(#cot:2#) = #th:1#^\circ, \qquad \cot\theta + \tan\theta = #cot:2# + #tanT:3# = #ct:3#"],
     "werte": [{"id": "th", "expr": "atan(1/cot)*180/PI", "d": 1}, {"id": "tanT", "expr": "1/cot", "d": 3},
               {"id": "ct", "expr": "cot+1/cot", "d": 3}, {"id": "sinT", "expr": "sin(atan(1/cot))", "d": 3}]},

    {"titel": "Bemessungsschubfluss – Gl. (14)", **T3, "folie": "5",
     "formel": [r"\tau\,t = «vEdT» = \dfrac{«TEd»}{2\,«Ak»}"],
     "einsetzen": [rf"«vEdT» = \dfrac{{#T:1# \cdot 10^6}}{{2 \cdot #Ak:0# \cdot 10^2}} = #v:1#{Nmm}"],
     "werte": [{"id": "v", "expr": "T*1e6/(2*Ak*100)", "d": 1}]},

    {"titel": "Schubkräfte der Wände – Gl. (15)", **T3, "folie": "6",
     "text": "Wandhöhen zwischen den Mittellinien: Seitenwand $z_1 = h - «tef»$, Gurt $z_2 = b - «tef»$.",
     "formel": [r"«VEdT» = «vEdT»\,z_i = \dfrac{«TEd»\,z_i}{2\,«Ak»}"],
     "einsetzen": [rf"\text{{Seitenwand: }} «VEdT»_{{,1}} = #v:1# \cdot #z1:1# \cdot 10 \cdot 10^{{-3}} = #VT1:1#{kN}",
                   rf"\text{{Gurt: }} «VEdT»_{{,2}} = #v:1# \cdot #z2:1# \cdot 10 \cdot 10^{{-3}} = #VT2:1#{kN}"],
     "werte": [{"id": "z1", "expr": "h-tef", "d": 1}, {"id": "z2", "expr": "b-tef", "d": 1},
               {"id": "VT1", "expr": "v*z1*10/1e3", "d": 1}, {"id": "VT2", "expr": "v*z2*10/1e3", "d": 1}]},

    {"titel": "Strebenkräfte der Seitenwand – Gl. (16) bis (18)", **T3, "folie": "8–9",
     "formel": [r"|«Fcd»| = \dfrac{«VEdT»}{\sin\theta}, \qquad «Fsld» = «VEdT»\cot\theta, \qquad «Fswd» = «VEdT»"],
     "einsetzen": [rf"|«Fcd»| = \dfrac{{#VT1:1#}}{{#sinT:3#}} = #Fc:1#{kN}",
                   rf"«Fsld» = #VT1:1# \cdot #cot:2# = #Fs:1#{kN}, \qquad «Fswd» = #VT1:1#{kN}"],
     "werte": [{"id": "Fc", "expr": "VT1/sinT", "d": 1}, {"id": "Fs", "expr": "VT1*cot", "d": 1}]},

    {"titel": "Betondruckstrebe – Gl. (20) und (23)", **T3, "folie": "10, 13, 16",
     "formel": [r"|«scd»| = \dfrac{«TEd»}{2\,«Ak»\,«tef»}\,(\cot\theta + \tan\theta), \qquad «TRdmax» = \dfrac{\nu\,«fcd»\,2\,«Ak»\,«tef»}{\cot\theta + \tan\theta}",
                {"wenn": "quer=='voll'", "t": r"\nu = 0{,}525 \quad\text{(allgemein)}"},
                {"wenn": "quer=='kasten'", "t": r"\nu = 0{,}75 \quad\text{(echter Hohlkasten)}"}],
     "einsetzen": [rf"|«scd»| = \dfrac{{#T:1# \cdot 10^6}}{{2 \cdot #Ak:0# \cdot 10^2 \cdot #tef:1# \cdot 10}} \cdot #ct:3# = #scd:2#{Nmm2} \quad (\nu\,«fcd» = #nfcd:2#{Nmm2})",
                   rf"«TRdmax» = \dfrac{{#nu:3# \cdot #fcd:2# \cdot 2 \cdot #Ak:0# \cdot 10^2 \cdot #tef:1# \cdot 10}}{{#ct:3#}} \cdot 10^{{-6}} = #TRd:1#{kNm}",
                   r"\dfrac{«TEd»}{«TRdmax»} = \dfrac{#T:1#}{#TRd:1#} = #etaT:3# \;#etaTOk#"],
     "werte": [{"id": "nu", "expr": "quer=='kasten' ? 0.75 : 0.525", "d": 3}, {"id": "nfcd", "expr": "nu*fcd", "d": 2},
               {"id": "scd", "expr": "T*1e6/(2*Ak*100*tef*10)*ct", "d": 2},
               {"id": "TRd", "expr": "nu*fcd*2*Ak*100*tef*10/ct/1e6", "d": 1}, {"id": "etaT", "expr": "T/TRd", "d": 3},
               {"id": "etaTOk", "expr": wahl("etaT<=1", r"\le 1" + OK, "> 1" + NICHT)}]},

    {"titel": "Torsionsbügel aus Gl. (25)", **T3, "folie": "15",
     "text": "Mit $«TRdsw» = «TEd»$ nach $«Asw»/«sw»$ umgestellt; bezogen auf einen Bügelschenkel. Bügel geschlossen und verankert.",
     "formel": [r"«TRdsw» = 2\,«Ak»\,\dfrac{«Asw»}{«sw»}\,«fyd»\cot\theta \;\Rightarrow\; \dfrac{«Asw»}{«sw»} = \dfrac{«TEd»}{2\,«Ak»\,«fyd»\cot\theta}"],
     "einsetzen": [rf"\dfrac{{«Asw»}}{{«sw»}} = \dfrac{{#T:1# \cdot 10^6}}{{2 \cdot #Ak:0# \cdot 10^2 \cdot #fyd:1# \cdot #cot:2#}} \cdot 10 = #asw:2#{cm2m}"],
     "werte": [{"id": "asw", "expr": "T*1e6/(2*Ak*100*fyd*cot)*10", "d": 2}]},

    {"titel": "Torsionslängsbewehrung aus Gl. (24)", **T3, "folie": "14",
     "text": "Mit $«TRdsl» = «TEd»$ nach $«Asl»$ umgestellt; gleichmäßig über den Umfang verteilen.",
     "formel": [r"«TRdsl» = 2\,«Ak»\,\dfrac{«Asl»}{«uk»}\,«fyd»\tan\theta \;\Rightarrow\; «Asl» = \dfrac{«TEd»\,«uk»\cot\theta}{2\,«Ak»\,«fyd»}"],
     "einsetzen": [rf"«Asl» = \dfrac{{#T:1# \cdot 10^6 \cdot #uk:1# \cdot 10 \cdot #cot:2#}}{{2 \cdot #Ak:0# \cdot 10^2 \cdot #fyd:1#}} \cdot 10^{{-2}} = #asl:2#{cm2}"],
     "werte": [{"id": "asl", "expr": "T*1e6*uk*10*cot/(2*Ak*100*fyd)/100", "d": 2}]},

    {"titel": "Äquivalente Normalkraft aus Torsion – Gl. (26)", **T4, "folie": "5, 7",
     "text": "Alternative zur Addition der Längsbewehrung: Torsion als zusätzliche Normalkraft in der Biegebemessung, hier mit den erforderlichen Torsionsbügeln.",
     "formel": [r"«NT» = \left(\dfrac{«TEd»}{2\,«Ak»}\right)^2 «uk»\,\dfrac{«sw»}{«Asw»\,«fyd»}"],
     "einsetzen": [rf"«NT» = #v:1#^2 \cdot \dfrac{{#uk:1# \cdot 10}}{{#asw:2# \cdot 10^{{-1}} \cdot #fyd:1#}} \cdot 10^{{-3}} = #NT:1#{kN} \quad (= «Asl»\,«fyd»)"],
     "werte": [{"id": "NT", "expr": "v*v*uk*10/(asw/10*fyd)/1e3", "d": 1}]},

    {"titel": "Konstruktive Regeln (vorläufig)", "quelle": "vorläufig nach DIN EN 1992-1-1, 9.2.3",
     "text": "Bügel geschlossen, in jeder Ecke ein Längsstab, Längsstababstand höchstens 35 cm; zusätzlich gelten die Grenzen der Querkraftbemessung.",
     "formel": [r"«sw»_{,\max} = \min\!\left(\dfrac{u}{8};\, \min(b,h)\right)"],
     "einsetzen": [rf"«sw»_{{,\max}} = \min\!\left(\dfrac{{2\,(#b:0# + #h:0#)}}{{8}};\, #bmin:0#\right) = #smax:1#{cm}"],
     "werte": [{"id": "bmin", "expr": "min(b,h)", "d": 0}, {"id": "smax", "expr": "min(2*(b+h)/8, min(b,h))", "d": 1}]},

    {"titel": "Querkraft-Druckstrebe", "wenn": "V>0", "quelle": "Betonbau 3 (Querkraft)",
     "formel": [r"d = h - d_1, \qquad z = 0{,}9\,d, \qquad «VRdmax» = \dfrac{«bw»\,z\,\nu_1\,«fcd»}{\cot\theta + \tan\theta}, \quad \nu_1 = 0{,}75"],
     "einsetzen": [rf"d = #h:0# - #d1:1# = #d:1#{cm}, \qquad z = 0{{,}}9 \cdot #d:1# = #z:2#{cm}",
                   rf"«VRdmax» = \dfrac{{#b:0# \cdot 10 \cdot #z:2# \cdot 10 \cdot 0{{,}}75 \cdot #fcd:2#}}{{#ct:3#}} \cdot 10^{{-3}} = #VRd:1#{kN}"],
     "werte": [{"id": "d", "expr": "h-d1", "d": 1}, {"id": "z", "expr": "0.9*d", "d": 2},
               {"id": "VRd", "expr": "b*10*z*10*0.75*fcd/ct/1e3", "d": 1}, {"id": "etaV", "expr": "V/VRd", "d": 3}]},

    {"titel": "Interaktion der Druckstreben – Gl. (29) bzw. (30)", "wenn": "V>0", **T4, "folie": "10–12",
     "formel": [{"wenn": "quer=='voll'", "t": r"\left(\dfrac{«TEd»}{«TRdmax»}\right)^2 + \left(\dfrac{«VEd»}{«VRdmax»}\right)^2 \le 1{,}0 \quad\text{(Vollquerschnitt)}"},
                {"wenn": "quer=='kasten'", "t": r"\dfrac{«TEd»}{«TRdmax»} + \dfrac{«VEd»}{«VRdmax»} \le 1{,}0 \quad\text{(echter Hohlkasten)}"}],
     "einsetzen": [{"wenn": "quer=='voll'", "t": r"\left(\dfrac{#T:1#}{#TRd:1#}\right)^2 + \left(\dfrac{#V:1#}{#VRd:1#}\right)^2 = #inter:3# \;#interOk#"},
                   {"wenn": "quer=='kasten'", "t": r"\dfrac{#T:1#}{#TRd:1#} + \dfrac{#V:1#}{#VRd:1#} = #inter:3# \;#interOk#"}],
     "werte": [{"id": "inter", "expr": "quer=='kasten' ? etaT+etaV : etaT**2+etaV**2", "d": 3},
               {"id": "interOk", "expr": wahl("inter<=1", r"\le 1" + OK, "> 1" + NICHT)},
               {"id": "interArt", "expr": wahl("quer=='kasten'", "linear, Gl. (30)", "quadratisch, Gl. (29)")}]},

    {"titel": "Schubflüsse in den Stegen – Gl. (27)", "wenn": "V>0", **T4, "folie": "4, 8",
     "text": "In einem Steg addieren sich die Schubflüsse aus Querkraft und Torsion, im anderen wirken sie gegeneinander.",
     "formel": [r"«vEd» = \dfrac{«VEd»}{2\,z} \pm \dfrac{«TEd»}{2\,«Ak»}"],
     "einsetzen": [rf"\dfrac{{«VEd»}}{{2\,z}} = \dfrac{{#V:1# \cdot 10^3}}{{2 \cdot #z:2# \cdot 10}} = #vV:1#{Nmm}, \qquad \dfrac{{«TEd»}}{{2\,«Ak»}} = #v:1#{Nmm}",
                   rf"«vEd»_{{,\max}} = #vV:1# + #v:1# = #vmax:1#{Nmm}, \qquad «vEd»_{{,\min}} = #vV:1# - #v:1# = #vmin:1#{Nmm}"],
     "werte": [{"id": "vV", "expr": "V*1e3/(2*z*10)", "d": 1}, {"id": "vmax", "expr": "vV+v", "d": 1}, {"id": "vmin", "expr": "vV-v", "d": 1}]},

    {"titel": "Gesamte Bügelbewehrung – Gl. (28)", "wenn": "V>0", **T4, "folie": "9",
     "text": "Querkraftbügel (Betonbau 3) beziehen sich auf beide Schenkel, Torsionsbügel auf einen Schenkel. Voraussetzung: gleicher Druckstrebenwinkel.",
     "formel": [r"\dfrac{«AswV»}{«sw»} = \dfrac{«VEd»}{z\,«fyd»\cot\theta}, \qquad \dfrac{«Aswtot»}{«sw»} = \dfrac{«AswV»}{«sw»} + 2\,\dfrac{«AswT»}{«sw»}"],
     "einsetzen": [rf"\dfrac{{«AswV»}}{{«sw»}} = \dfrac{{#V:1# \cdot 10^3}}{{#z:2# \cdot 10 \cdot #fyd:1# \cdot #cot:2#}} \cdot 10 = #aswV:2#{cm2m}",
                   rf"\dfrac{{«Aswtot»}}{{«sw»}} = #aswV:2# + 2 \cdot #asw:2# = #aswtot:2#{cm2m} \;\Rightarrow\; \text{{je Schenkel }} #aswS:2#{cm2m}"],
     "werte": [{"id": "aswV", "expr": "V*1e3/(z*10*fyd*cot)*10", "d": 2}, {"id": "aswtot", "expr": "aswV+2*asw", "d": 2},
               {"id": "aswS", "expr": "aswtot/2", "d": 2}]},

    {"titel": "Verzicht auf rechnerischen Torsionsnachweis (vorläufig)", "wenn": "V>0", "quelle": "vorläufig nach DE NA 6.3.2(5)",
     "text": "Rechteckvollquerschnitt: Sind beide Bedingungen erfüllt, genügt die Mindestbewehrung.",
     "formel": [r"«TEd» \le \dfrac{«VEd»\,«bw»}{4{,}5} \qquad\text{und}\qquad «VEd»\left(1 + \dfrac{4{,}5\,«TEd»}{«VEd»\,«bw»}\right) \le «VRdc»"],
     "einsetzen": [r"k = 1 + \sqrt{\dfrac{200}{#d:1# \cdot 10}} = #k0:3# \;\Rightarrow\; k = #k:3#, \qquad \rho_{\mathrm{l}} = #rhol:4#",
                   rf"«VRdc» = \max\!\left[0{{,}}10 \cdot #k:3# \cdot (100 \cdot #rhol:4# \cdot #fck:0#)^{{1/3}};\; \dfrac{{0{{,}}0525}}{{1{{,}}5}} \cdot #k:3#^{{3/2}} \cdot #fck:0#^{{1/2}}\right] #b:0# \cdot 10 \cdot #d:1# \cdot 10 \cdot 10^{{-3}} = #VRdc:1#{kN}",
                   rf"\dfrac{{«VEd»\,«bw»}}{{4{{,}}5}} = \dfrac{{#V:1# \cdot #bm:2#}}{{4{{,}}5}} = #g1:2#{kNm} \;#c1Txt#",
                   rf"«VEd»\left(1 + \dfrac{{4{{,}}5\,«TEd»}}{{«VEd»\,«bw»}}\right) = #g2:1#{kN} \;#c2Txt#",
                   r"\Rightarrow\; #verzichtTxt#"],
     "werte": [{"id": "k0", "expr": "1+sqrt(200/(d*10))", "d": 3}, {"id": "k", "expr": "min(k0, 2)", "d": 3},
               {"id": "rhol", "expr": "min(rho/100, 0.02)", "d": 4}, {"id": "v1", "expr": "0.1*k*cbrt(100*rhol*fck)", "d": 3},
               {"id": "vmin2", "expr": "0.0525/1.5*pow(k,1.5)*sqrt(fck)", "d": 3},
               {"id": "VRdc", "expr": "max(v1, vmin2)*b*10*d*10/1e3", "d": 1}, {"id": "bm", "expr": "b/100", "d": 2},
               {"id": "g1", "expr": "V*bm/4.5", "d": 2}, {"id": "c1", "expr": "T<=g1"},
               {"id": "c1Txt", "expr": wahl("c1", r"\ge «TEd» = #T:1#\,\mathrm{kNm}" + OK, r"< «TEd» = #T:1#\,\mathrm{kNm}" + NICHT)},
               {"id": "g2", "expr": "V*(1+4.5*T/(V*bm))", "d": 1}, {"id": "c2", "expr": "g2<=VRdc"},
               {"id": "c2Txt", "expr": wahl("c2", r"\le «VRdc» = #VRdc:1#\,\mathrm{kN}" + OK, r"> «VRdc» = #VRdc:1#\,\mathrm{kN}" + NICHT)},
               {"id": "verzicht", "expr": "c1 && c2"},
               {"id": "verzichtTxt", "expr": wahl("verzicht", r"\text{Verzicht möglich, Mindestbewehrung genügt}", r"\text{rechnerischer Torsionsnachweis erforderlich}")},
               {"id": "verzichtWort", "expr": wahl("verzicht", "nein", "ja")},
               {"id": "verzichtSub", "expr": wahl("verzicht", "Mindestbewehrung genügt (vorläufig)", "Bemessung erforderlich (vorläufig)")}]},

    {"titel": "Ergebnis",
     "einsetzen": [r"\text{Druckstrebe: } «TEd»/«TRdmax» = #etaT:3# \;#etaTOk#",
                   {"wenn": "V>0", "t": r"\text{Interaktion: } #inter:3# \;#interOk#"},
                   r"\text{Torsionsbügel: } #asw:2#\,\mathrm{cm^2/m} \text{ je Schenkel}, \qquad «sw» \le #smax:1#\,\mathrm{cm}",
                   {"wenn": "V>0", "t": r"\text{Bügel gesamt (V + T): } #aswtot:2#\,\mathrm{cm^2/m}, \text{ je Schenkel } #aswS:2#\,\mathrm{cm^2/m}"},
                   r"\text{Torsionslängsbewehrung: } «Asl» = #asl:2#\,\mathrm{cm^2} \text{ – zur Biegelängsbewehrung addieren}"]},
]

ERGEBNISSE = [
    {"titel": "Druckstrebe", "wert": "etaT*100", "d": 0, "einheit": "%", "sub": "$«TRdmax» = #TRd:1#\\,\\mathrm{kNm}$", "eta": "etaT"},
    {"titel": "Torsionsbügel je Schenkel", "wert": "asw", "d": 2, "einheit": "cm²/m", "sub": "Gl. (25), $«sw»_{,\\max} = #smax:1#\\,\\mathrm{cm}$"},
    {"titel": "Torsionslängsbewehrung", "wert": "asl", "d": 2, "einheit": "cm²", "sub": "Gl. (24), über den Umfang"},
    {"titel": "Interaktion $T + V$", "wenn": "V>0", "wert": "inter", "d": 2, "einheit": "≤ 1", "sub": "#interArt#", "eta": "inter"},
    {"titel": "Bügel gesamt", "wenn": "V>0", "wert": "aswtot", "d": 2, "einheit": "cm²/m", "sub": "Gl. (28), je Schenkel #aswS:2#"},
    {"titel": "Nachweis nötig?", "wenn": "V>0", "wert": "verzichtWort", "einheit": "", "sub": "#verzichtSub#"},
]

PRUEFUNG = [{"wenn": "2*d1 >= min(b,h)", "text": "Bitte gültige Abmessungen eingeben: $2\\,d_1$ muss kleiner als $b$ und $h$ sein."}]

RECHNER = {"typ": "torsion", "titel": "Torsionsbemessung Rechteckquerschnitt", "skizze": "rechteck_hohlkasten",
           "hinweis": ("Rechenweg nach Skript Teil 3 und 4 – Gleichungsnummern und Folien stehen bei jedem Schritt. Baustoffwerte und Querkraft "
                       "nach Betonbau 3; konstruktive Regeln und Verzicht auf den Nachweis vorläufig nach DIN EN 1992-1-1 + NA (folgen mit Skript Teil 5)."),
           "eingaben": EINGABEN, "schritte": SCHRITTE, "ergebnisse": ERGEBNISSE, "pruefung": PRUEFUNG}

if __name__ == "__main__":
    ziel = Path(__file__).resolve().parent.parent / "content" / "01_torsion.json"
    daten = json.loads(ziel.read_text(encoding="utf-8"))
    daten["rechner"] = expand(RECHNER)
    ziel.write_text(json.dumps(daten, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Rechner geschrieben: {len(SCHRITTE)} Schritte, {len(EINGABEN)} Eingaben")
