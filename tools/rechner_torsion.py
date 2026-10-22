"""Bemessungstool Torsion – Quelle für content/01_torsion.json (Feld "rechner").

Jeder Schritt: titel, text, wenn (Bedingung), formel (Ansatz), einsetzen (Zahlen), werte (Berechnung).
Rechnung in den Einheiten der Eingabe (cm, kNm, kN); Umrechnung steht jeweils im Ausdruck.
Vorläufig nach DIN EN 1992-1-1 + NA (DE) – Reihenfolge und Schreibweise später ans Skript anpassen.

Aufruf: python tools/rechner_torsion.py
"""
import json
from pathlib import Path

TEd, TRd = r"T_{\mathrm{Ed}}", r"T_{\mathrm{Rd,max}}"
VEd, VRd, VRdc = r"V_{\mathrm{Ed}}", r"V_{\mathrm{Rd,max}}", r"V_{\mathrm{Rd,c}}"
Ak, uk, tef = r"A_{\mathrm{k}}", r"u_{\mathrm{k}}", r"t_{\mathrm{ef}}"
fyd, fcd, fck = r"f_{\mathrm{yd}}", r"f_{\mathrm{cd}}", r"f_{\mathrm{ck}}"
Asw, Asl, bw = r"A_{\mathrm{sw}}", r"A_{\mathrm{sl}}", r"b_{\mathrm{w}}"
tau, kNm, kN, cm, cm2, Nmm2 = r"\tau_{\mathrm{t}}", r"\,\mathrm{kNm}", r"\,\mathrm{kN}", r"\,\mathrm{cm}", r"\,\mathrm{cm^2}", r"\,\mathrm{N/mm^2}"


def js(s):
    """LaTeX-Text als JavaScript-Zeichenkette für Ausdrücke"""
    return json.dumps(s, ensure_ascii=False)


def wahl(bed, ja, nein):
    return f"({bed}) ? {js(ja)} : {js(nein)}"


OK, NICHT = r"\quad\checkmark", r"\quad\text{nicht erfüllt}"

EINGABEN = [
    {"id": "b", "label": "Breite $b$", "einheit": "cm", "default": 40, "step": 1, "min": 10, "d": 0},
    {"id": "h", "label": "Höhe $h$", "einheit": "cm", "default": 60, "step": 1, "min": 10, "d": 0},
    {"id": "d1", "label": "$d_1$ Achse Längsbew.", "einheit": "cm", "default": 5, "step": 0.5, "min": 2, "d": 1},
    {"id": "beton", "label": "Beton", "typ": "auswahl", "default": "C30/37",
     "werte": ["C20/25", "C25/30", "C30/37", "C35/45", "C40/50", "C45/55", "C50/60", "C55/67", "C60/75"]},
    {"id": "T", "label": f"${TEd}$", "einheit": "kNm", "default": 40, "step": 1, "min": 0, "d": 1},
    {"id": "V", "label": f"${VEd}$", "einheit": "kN", "default": 150, "step": 1, "min": 0, "d": 1, "hinweis": "0 = reine Torsion"},
    {"id": "rho", "label": r"$\rho_{\mathrm{l}}$ Längsbew.", "einheit": "%", "default": 1.0, "step": 0.1, "min": 0, "d": 2,
     "hinweis": f"nur für ${VRdc}$ (Verzicht auf Nachweis)"},
    {"id": "cot", "label": r"$\cot\theta$", "default": 1.0, "step": 0.05, "min": 1, "max": 1.75, "d": 2,
     "hinweis": r"$1{,}0 \Rightarrow \theta = 45^\circ$ (vereinfacht für reine Torsion)"},
    {"id": "quer", "label": "Querschnitt", "typ": "schalter", "default": "voll",
     "optionen": [{"v": "voll", "t": "Vollquerschnitt"}, {"v": "kasten", "t": "Kasten"}]},
    {"id": "tefArt", "label": f"Wanddicke ${tef}$", "typ": "schalter", "default": "na",
     "optionen": [{"v": "na", "t": r"$2\,d_1$ (DE NA)"}, {"v": "ec2", "t": "$A/u$ (EC2)"}]},
]

SCHRITTE = [
    {"titel": "Eingangswerte",
     "einsetzen": [
         rf"b/h = #b:0#/#h:0#{cm}, \qquad d_1 = #d1:1#{cm}",
         r"\text{Beton #beton#, Betonstahl B500}",
         rf"{TEd} = #T:1#{kNm}, \qquad {VEd} = #V:1#{kN}, \qquad \cot\theta = #cot:2#",
         {"wenn": "quer=='voll'", "t": r"\text{Vollquerschnitt}"},
         {"wenn": "quer=='kasten'", "t": r"\text{Kastenquerschnitt, Wände beidseitig bewehrt}"}]},

    {"titel": "Baustoffkennwerte",
     "formel": [rf"{fcd} = \dfrac{{\alpha_{{\mathrm{{cc}}}}\,{fck}}}{{\gamma_{{\mathrm{{c}}}}}}, \qquad {fyd} = \dfrac{{f_{{\mathrm{{yk}}}}}}{{\gamma_{{\mathrm{{s}}}}}}",
                {"wenn": "fck>50", "t": rf"\nu_2 = 1{{,}}1 - \dfrac{{{fck}}}{{500}}"}],
     "einsetzen": [rf"{fcd} = \dfrac{{0{{,}}85 \cdot #fck:0#}}{{1{{,}}5}} = #fcd:2#{Nmm2}",
                   rf"{fyd} = \dfrac{{500}}{{1{{,}}15}} = #fyd:1#{Nmm2}",
                   {"wenn": "fck>50", "t": r"\nu_2 = 1{,}1 - \dfrac{#fck:0#}{500} = #nu2:3#"}],
     "werte": [{"id": "fck", "expr": "FCK(beton)", "d": 0},
               {"id": "fcd", "expr": "0.85*fck/1.5", "d": 2},
               {"id": "fyd", "expr": "500/1.15", "d": 1},
               {"id": "nu2", "expr": "fck>50 ? 1.1-fck/500 : 1", "d": 3}]},

    {"titel": "Ersatzhohlkasten",
     "text": "Der gerissene Vollquerschnitt wird als dünnwandiger Hohlkasten idealisiert; maßgebend ist die Wandmittellinie.",
     "formel": [{"wenn": "tefArt=='na'", "t": rf"{tef} = 2\,d_1 \quad\text{{(DE NA)}}"},
                {"wenn": "tefArt=='ec2'", "t": rf"{tef} = \dfrac{{A}}{{u}} \ge 2\,d_1 \quad\text{{(EC2)}}"},
                rf"{Ak} = (b - {tef})\,(h - {tef}), \qquad {uk} = 2\,\bigl[(b - {tef}) + (h - {tef})\bigr]"],
     "einsetzen": [{"wenn": "tefArt=='na'", "t": rf"{tef} = 2 \cdot #d1:1# = #tef0:1#{cm}"},
                   {"wenn": "tefArt=='ec2'", "t": rf"{tef} = \dfrac{{#b:0# \cdot #h:0#}}{{2\,(#b:0# + #h:0#)}} = #tAu:2#{cm} \;\Rightarrow\; {tef} = \max(#tAu:2#;\,#tmin:1#) = #tef0:2#{cm}"},
                   {"wenn": "tef0>tefmax", "t": rf"{tef} \le \tfrac{{1}}{{2}}\min(b,h) = #tefmax:1#{cm} \;\Rightarrow\; {tef} = #tef:1#{cm}"},
                   rf"{Ak} = (#b:0# - #tef:1#)\,(#h:0# - #tef:1#) = #Ak:0#{cm2}",
                   rf"{uk} = 2\,\bigl[(#b:0# - #tef:1#) + (#h:0# - #tef:1#)\bigr] = #uk:1#{cm}"],
     "werte": [{"id": "tAu", "expr": "b*h/(2*(b+h))", "d": 2},
               {"id": "tmin", "expr": "2*d1", "d": 1},
               {"id": "tef0", "expr": "tefArt=='na' ? 2*d1 : max(tAu, 2*d1)", "d": 2},
               {"id": "tefmax", "expr": "min(b,h)/2", "d": 1},
               {"id": "tef", "expr": "min(tef0, tefmax)", "d": 1},
               {"id": "Ak", "expr": "(b-tef)*(h-tef)", "d": 0},
               {"id": "uk", "expr": "2*((b-tef)+(h-tef))", "d": 1}]},

    {"titel": "Druckstrebenneigung",
     "einsetzen": [r"\theta = \operatorname{arccot}(#cot:2#) = #th:1#^\circ, \qquad \sin\theta\cos\theta = #sc:3#"],
     "werte": [{"id": "th", "expr": "atan(1/cot)*180/PI", "d": 1},
               {"id": "sc", "expr": "sin(atan(1/cot))*cos(atan(1/cot))", "d": 3}]},

    {"titel": "Schubfluss und Schubspannung",
     "text": "Bredtsche Formel; der Schubfluss ist entlang der Wand konstant.",
     "formel": [rf"{tau}\,{tef} = \dfrac{{{TEd}}}{{2\,{Ak}}}, \qquad {tau} = \dfrac{{{TEd}}}{{2\,{Ak}\,{tef}}}"],
     "einsetzen": [rf"{tau}\,{tef} = \dfrac{{#T:1# \cdot 10^6}}{{2 \cdot #Ak:0# \cdot 10^2}} = #q:1#\,\mathrm{{N/mm}}",
                   rf"{tau} = \dfrac{{#q:1#}}{{#tef:1# \cdot 10}} = #tau:2#{Nmm2}"],
     "werte": [{"id": "q", "expr": "T*1e6/(2*Ak*100)", "d": 1},
               {"id": "tau", "expr": "q/(tef*10)", "d": 2}]},

    {"titel": "Nachweis der Betondruckstreben",
     "formel": [rf"{TRd} = 2\,\nu\,\alpha_{{\mathrm{{cw}}}}\,{fcd}\,{Ak}\,{tef}\sin\theta\cos\theta",
                {"wenn": "quer=='voll'", "t": r"\nu = 0{,}525\,\nu_2 \quad\text{(Vollquerschnitt, DE NA)}, \qquad \alpha_{\mathrm{cw}} = 1{,}0"},
                {"wenn": "quer=='kasten'", "t": r"\nu = 0{,}75\,\nu_2 \quad\text{(Kasten, DE NA)}, \qquad \alpha_{\mathrm{cw}} = 1{,}0"}],
     "einsetzen": [r"\nu = #nuB:3# \cdot #nu2:3# = #nu:3#",
                   rf"{TRd} = 2 \cdot #nu:3# \cdot 1{{,}}0 \cdot #fcd:2# \cdot #Ak:0# \cdot 10^2 \cdot #tef:1# \cdot 10 \cdot #sc:3# \cdot 10^{{-6}} = #TRd:1#{kNm}",
                   rf"\dfrac{{{TEd}}}{{{TRd}}} = \dfrac{{#T:1#}}{{#TRd:1#}} = #etaT:3# \;#etaTOk#"],
     "werte": [{"id": "nuB", "expr": "quer=='kasten' ? 0.75 : 0.525", "d": 3},
               {"id": "nu", "expr": "nuB*nu2", "d": 3},
               {"id": "TRd", "expr": "2*nu*fcd*Ak*100*tef*10*sc/1e6", "d": 1},
               {"id": "etaT", "expr": "T/TRd", "d": 3},
               {"id": "etaTOk", "expr": wahl("etaT<=1", r"\le 1" + OK, "> 1" + NICHT)}]},

    {"titel": "Torsionsbügel",
     "text": "Bezogen auf einen Bügelschenkel; Bügel geschlossen und mit Haken oder Übergreifung verankert.",
     "formel": [rf"\dfrac{{{Asw}}}{{s}} = \dfrac{{{TEd}}}{{2\,{Ak}\,{fyd}\cot\theta}}"],
     "einsetzen": [rf"a_{{\mathrm{{sw}}}} = \dfrac{{#T:1# \cdot 10^6}}{{2 \cdot #Ak:0# \cdot 10^2 \cdot #fyd:1# \cdot #cot:2#}} \cdot 10 = #asw:2#\,\mathrm{{cm^2/m}}"],
     "werte": [{"id": "asw", "expr": "T*1e6/(2*Ak*100*fyd*cot)*10", "d": 2}]},

    {"titel": "Torsionslängsbewehrung",
     "text": "Gleichmäßig über den Umfang verteilen, in jeder Ecke mindestens ein Stab.",
     "formel": [rf"\sum {Asl} = \dfrac{{{TEd}\,{uk}\cot\theta}}{{2\,{Ak}\,{fyd}}}"],
     "einsetzen": [rf"\sum {Asl} = \dfrac{{#T:1# \cdot 10^6 \cdot #uk:1# \cdot 10 \cdot #cot:2#}}{{2 \cdot #Ak:0# \cdot 10^2 \cdot #fyd:1#}} \cdot 10^{{-2}} = #asl:2#{cm2}"],
     "werte": [{"id": "asl", "expr": "T*1e6*uk*10*cot/(2*Ak*100*fyd)/100", "d": 2}]},

    {"titel": "Konstruktive Regeln",
     "text": "Zusätzlich gelten die Grenzen aus der Querkraftbemessung.",
     "formel": [r"s_{\max} = \min\!\left(\dfrac{u}{8};\, \min(b,h)\right), \qquad s_{\mathrm{l,max}} = 35\,\mathrm{cm}"],
     "einsetzen": [rf"s_{{\max}} = \min\!\left(\dfrac{{2\,(#b:0# + #h:0#)}}{{8}};\, #bmin:0#\right) = #smax:1#{cm}"],
     "werte": [{"id": "bmin", "expr": "min(b,h)", "d": 0},
               {"id": "smax", "expr": "min(2*(b+h)/8, min(b,h))", "d": 1}]},

    {"titel": "Druckstrebe aus Querkraft", "wenn": "V>0",
     "formel": [r"d = h - d_1, \qquad z = 0{,}9\,d, \qquad \nu_1 = 0{,}75\,\nu_2",
                rf"{VRd} = \dfrac{{{bw}\,z\,\nu_1\,{fcd}}}{{\cot\theta + \tan\theta}}"],
     "einsetzen": [rf"d = #h:0# - #d1:1# = #d:1#{cm}, \qquad z = 0{{,}}9 \cdot #d:1# = #z:2#{cm}, \qquad \nu_1 = #nu1:3#",
                   rf"{VRd} = \dfrac{{#b:0# \cdot 10 \cdot #z:2# \cdot 10 \cdot #nu1:3# \cdot #fcd:2#}}{{#cot:2# + #tanT:3#}} \cdot 10^{{-3}} = #VRd:1#{kN}"],
     "werte": [{"id": "d", "expr": "h-d1", "d": 1},
               {"id": "z", "expr": "0.9*d", "d": 2},
               {"id": "nu1", "expr": "0.75*nu2", "d": 3},
               {"id": "tanT", "expr": "1/cot", "d": 3},
               {"id": "VRd", "expr": "b*10*z*10*nu1*fcd/(cot+tanT)/1e3", "d": 1},
               {"id": "etaV", "expr": "V/VRd", "d": 3}]},

    {"titel": "Interaktion Torsion und Querkraft", "wenn": "V>0",
     "formel": [{"wenn": "quer=='voll'", "t": rf"\left(\dfrac{{{TEd}}}{{{TRd}}}\right)^2 + \left(\dfrac{{{VEd}}}{{{VRd}}}\right)^2 \le 1 \quad\text{{(Vollquerschnitt, DE NA)}}"},
                {"wenn": "quer=='kasten'", "t": rf"\dfrac{{{TEd}}}{{{TRd}}} + \dfrac{{{VEd}}}{{{VRd}}} \le 1 \quad\text{{(Kasten)}}"}],
     "einsetzen": [{"wenn": "quer=='voll'", "t": r"\left(\dfrac{#T:1#}{#TRd:1#}\right)^2 + \left(\dfrac{#V:1#}{#VRd:1#}\right)^2 = #inter:3# \;#interOk#"},
                   {"wenn": "quer=='kasten'", "t": r"\dfrac{#T:1#}{#TRd:1#} + \dfrac{#V:1#}{#VRd:1#} = #inter:3# \;#interOk#"}],
     "werte": [{"id": "inter", "expr": "quer=='kasten' ? etaT+etaV : etaT**2+etaV**2", "d": 3},
               {"id": "interOk", "expr": wahl("inter<=1", r"\le 1" + OK, "> 1" + NICHT)},
               {"id": "interArt", "expr": wahl("quer=='kasten'", "linear", "quadratisch")}]},

    {"titel": "Verzicht auf rechnerischen Torsionsnachweis", "wenn": "V>0",
     "text": "Rechteckvollquerschnitt nach DE NA, 6.3.2(5): Sind beide Bedingungen erfüllt, genügt die Mindestbewehrung.",
     "formel": [rf"{TEd} \le \dfrac{{{VEd}\,{bw}}}{{4{{,}}5}} \qquad\text{{und}}\qquad {VEd}\left(1 + \dfrac{{4{{,}}5\,{TEd}}}{{{VEd}\,{bw}}}\right) \le {VRdc}",
                rf"{VRdc} = \max\!\left[0{{,}}10\,k\,(100\,\rho_{{\mathrm{{l}}}}\,{fck})^{{1/3}};\; \dfrac{{0{{,}}0525}}{{\gamma_{{\mathrm{{c}}}}}}\,k^{{3/2}}\,{fck}^{{1/2}}\right] {bw}\,d"],
     "einsetzen": [r"k = 1 + \sqrt{\dfrac{200}{#d:1# \cdot 10}} = #k0:3# \;\Rightarrow\; k = #k:3#, \qquad \rho_{\mathrm{l}} = #rhol:4#",
                   rf"v_{{\mathrm{{Rd,c}}}} = \max\!\left[0{{,}}10 \cdot #k:3# \cdot (100 \cdot #rhol:4# \cdot #fck:0#)^{{1/3}};\; \dfrac{{0{{,}}0525}}{{1{{,}}5}} \cdot #k:3#^{{3/2}} \cdot #fck:0#^{{1/2}}\right] = \max(#v1:3#;\,#vmin:3#) = #vrd:3#{Nmm2}",
                   rf"{VRdc} = #vrd:3# \cdot #b:0# \cdot 10 \cdot #d:1# \cdot 10 \cdot 10^{{-3}} = #VRdc:1#{kN}",
                   rf"\dfrac{{{VEd}\,{bw}}}{{4{{,}}5}} = \dfrac{{#V:1# \cdot #bm:2#}}{{4{{,}}5}} = #g1:2#{kNm} \;#c1Txt#",
                   rf"{VEd}\left(1 + \dfrac{{4{{,}}5\,{TEd}}}{{{VEd}\,{bw}}}\right) = #V:1#\left(1 + \dfrac{{4{{,}}5 \cdot #T:1#}}{{#V:1# \cdot #bm:2#}}\right) = #g2:1#{kN} \;#c2Txt#",
                   r"\Rightarrow\; #verzichtTxt#"],
     "werte": [{"id": "k0", "expr": "1+sqrt(200/(d*10))", "d": 3},
               {"id": "k", "expr": "min(k0, 2)", "d": 3},
               {"id": "rhol", "expr": "min(rho/100, 0.02)", "d": 4},
               {"id": "v1", "expr": "0.1*k*cbrt(100*rhol*fck)", "d": 3},
               {"id": "vmin", "expr": "0.0525/1.5*pow(k,1.5)*sqrt(fck)", "d": 3},
               {"id": "vrd", "expr": "max(v1, vmin)", "d": 3},
               {"id": "VRdc", "expr": "vrd*b*10*d*10/1e3", "d": 1},
               {"id": "bm", "expr": "b/100", "d": 2},
               {"id": "g1", "expr": "V*bm/4.5", "d": 2},
               {"id": "c1", "expr": "T<=g1"},
               {"id": "c1Txt", "expr": wahl("c1", rf"\ge {TEd} = #T:1#{kNm}" + OK, rf"< {TEd} = #T:1#{kNm}" + NICHT)},
               {"id": "g2", "expr": "V*(1+4.5*T/(V*bm))", "d": 1},
               {"id": "c2", "expr": "g2<=VRdc"},
               {"id": "c2Txt", "expr": wahl("c2", rf"\le {VRdc} = #VRdc:1#{kN}" + OK, rf"> {VRdc} = #VRdc:1#{kN}" + NICHT)},
               {"id": "verzicht", "expr": "c1 && c2"},
               {"id": "verzichtTxt", "expr": wahl("verzicht", r"\text{Verzicht möglich, Mindestbewehrung genügt}", r"\text{rechnerischer Torsionsnachweis erforderlich}")},
               {"id": "verzichtWort", "expr": wahl("verzicht", "nein", "ja")},
               {"id": "verzichtSub", "expr": wahl("verzicht", "Mindestbewehrung genügt", "Bemessung erforderlich")}]},

    {"titel": "Ergebnis",
     "einsetzen": [r"\text{Bügel: } a_{\mathrm{sw}} = #asw:2#\,\mathrm{cm^2/m} \text{ je Schenkel}, \qquad s \le #smax:1#\,\mathrm{cm}",
                   rf"\text{{Längsbewehrung: }} \sum {Asl} = #asl:2#{cm2} \text{{ über den Umfang verteilt}}",
                   rf"\text{{Druckstrebe: }} {TEd}/{TRd} = #etaT:3# \;#etaTOk#",
                   {"wenn": "V>0", "t": r"\text{Interaktion: } #inter:3# \;#interOk#"}]},
]

ERGEBNISSE = [
    {"titel": "Druckstrebe", "wert": "etaT*100", "d": 0, "einheit": "%", "sub": f"${TRd} = #TRd:1#{kNm}$", "eta": "etaT"},
    {"titel": "Bügel je Schenkel", "wert": "asw", "d": 2, "einheit": "cm²/m", "sub": r"$s_{\max} = #smax:1#\,\mathrm{cm}$"},
    {"titel": "Längsbewehrung", "wert": "asl", "d": 2, "einheit": "cm²", "sub": f"$\\sum {Asl}$ über den Umfang"},
    {"titel": "Interaktion $T + V$", "wenn": "V>0", "wert": "inter", "d": 2, "einheit": "≤ 1", "sub": "#interArt#", "eta": "inter"},
    {"titel": "Nachweis nötig?", "wenn": "V>0", "wert": "verzichtWort", "einheit": "", "sub": "#verzichtSub#"},
]

PRUEFUNG = [{"wenn": "2*d1 >= min(b,h)", "text": "Bitte gültige Abmessungen eingeben: $2\\,d_1$ muss kleiner als $b$ und $h$ sein."}]

RECHNER = {"typ": "torsion", "titel": "Torsionsbemessung Rechteckquerschnitt", "skizze": "rechteck_hohlkasten",
           "eingaben": EINGABEN, "schritte": SCHRITTE, "ergebnisse": ERGEBNISSE, "pruefung": PRUEFUNG}

if __name__ == "__main__":
    ziel = Path(__file__).resolve().parent.parent / "content" / "01_torsion.json"
    daten = json.loads(ziel.read_text(encoding="utf-8"))
    daten["rechner"] = RECHNER
    ziel.write_text(json.dumps(daten, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Rechner geschrieben: {len(SCHRITTE)} Schritte, {len(EINGABEN)} Eingaben")
