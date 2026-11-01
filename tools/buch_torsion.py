"""Buchbeispiele Torsion – Quelle für content/01_torsion.json (Feld "buchbeispiele").

Rechenwege nach Finckh, Stahlbetonkonstruktion 2 (2. Aufl. 2026), Kap. 2:
  Abschn. 2.6 Einfaches Beispiel (Fertigteil-Hauptträger mit Konsole, S. 26–33)
  Abschn. 2.7 Komplexes Beispiel (Aussteifungskern als Hohlkasten, S. 33–40)
Die Schritte folgen der Gliederung des Buchs; Texte sind eigene Formulierungen.
Die Ausgangswerte dürfen in der App um ±10 % verändert werden.

Jeder Schritt: abschnitt, seite, titel, text, formel, einsetzen, werte (wie beim Bemessungstool),
optional notiz (Hinweis zu einer Stelle im Buch).
Helfer in den Ausdrücken (templates/buch.js): ceil, floor, omegaTafel(mu), wahlUnten(A), cotStufe(summe, nfcd),
stabA(n, phi) [cm²], stabTxt(n, phi).

Aufruf: python tools/buch_torsion.py
"""
import json
from pathlib import Path

QUELLE = "Finckh: Stahlbetonkonstruktion 2"
kN, kNm, m, cm, mm = r"\,\mathrm{kN}", r"\,\mathrm{kNm}", r"\,\mathrm{m}", r"\,\mathrm{cm}", r"\,\mathrm{mm}"
m2, cm2, cm2m, MN2, MNm, MN = (r"\,\mathrm{m^2}", r"\,\mathrm{cm^2}", r"\,\mathrm{cm^2/m}", r"\,\mathrm{MN/m^2}",
                               r"\,\mathrm{MNm}", r"\,\mathrm{MN}")
OK, NICHT = r"\quad\checkmark", r"\quad\text{nicht erfüllt}"


def chk(bed, ja=OK, nein=NICHT):
    """zwei Zeilen: je nach Bedingung Haken oder 'nicht erfüllt' anhängen"""
    return [{"wenn": bed, "t": ja}, {"wenn": f"!({bed})", "t": nein}]


def zeile(t, wenn=None):
    return {"wenn": wenn, "t": t} if wenn else t


# ---------------------------------------------------------------- Einfaches Beispiel (Abschn. 2.6)
A_26 = "2.6.2 Ermittlung der Schnittgrößen"
B_26 = "2.6.3 Biegebemessung"
Q_26 = "2.6.4 Querkraftbemessung"
T_26 = "2.6.5 Torsionsbemessung"
I_26 = "2.6.6 Interaktionsnachweis"
K_26 = "2.6.7 Konstruktive Durchbildung"

EINFACH = {
    "id": "einfach",
    "titel": "Einfaches Beispiel",
    "untertitel": "Fertigteil-Hauptträger mit Konsole",
    "abschnitt": "Abschn. 2.6, S. 26–33",
    "system": "traeger",
    "aufgabe": ("Ein Fertigteil-Hauptträger einer offenen Halle liegt als Einfeldträger auf zwei Stützen. "
                "In Feldmitte trägt eine seitliche Konsole den Nebenträger. Dessen Auflagerkraft $F_{Ed}$ greift "
                "ausmittig mit dem Hebelarm $e$ an und erzeugt ein Torsionsmoment. Bemessen werden Biegung, "
                "Querkraft und Torsion einschließlich Interaktion und konstruktiver Durchbildung."),
    "fest": [["Beton", "C30/37, XC3"], ["Betonstahl", "B500 A"], ["Auflagertiefe", "t = 30 cm"],
             ["Bügel / Längsstäbe", "Ø12 / Ø28"]],
    "eingaben": [
        {"id": "F", "label": "Konsollast $F_{Ed}$", "einheit": "kN", "wert": 340, "step": 1, "d": 0},
        {"id": "p", "label": "Streckenlast $p_{Ed}$", "einheit": "kN/m", "wert": 40, "step": 0.5, "d": 1},
        {"id": "l", "label": "Spannweite $l$", "einheit": "m", "wert": 5.0, "step": 0.05, "d": 2},
        {"id": "e", "label": "Hebelarm $e$", "einheit": "m", "wert": 0.35, "step": 0.005, "d": 3},
        {"id": "b", "label": "Breite $b$", "einheit": "m", "wert": 0.30, "step": 0.01, "d": 2},
        {"id": "h", "label": "Höhe $h$", "einheit": "m", "wert": 0.80, "step": 0.01, "d": 2},
    ],
    "konstanten": {"tA": 0.30, "fck": 30, "fctm": 2.9, "fyd": 435, "fyk": 500},
    "ergebnisse": [
        {"titel": "Biegebewehrung unten", "wert": "Aunv", "d": 1, "einheit": "cm²", "sub": "gewählt: $#txtUn#$"},
        {"titel": "Torsionslängsbewehrung", "wert": "Asl", "d": 1, "einheit": "cm²", "sub": "$#aslu:1#\\,\\mathrm{cm^2/m}$ am Umfang"},
        {"titel": "Bügel gesamt", "wert": "aswTot", "d": 1, "einheit": "cm²/m", "sub": "gewählt: $#txtBu#$"},
        {"titel": "Interaktion V + T", "wert": "eta", "d": 2, "eta": "eta", "einheit": "", "sub": "Gl. (2.43)"},
    ],
    "schritte": [
        {"abschnitt": A_26, "seite": 27, "titel": "Auflagerkräfte",
         "text": "Einfeldträger unter Streckenlast und mittiger Einzellast aus der Konsole.",
         "formel": [r"A_{Ed} = B_{Ed} = \frac{F_{Ed}}{2} + p_{Ed}\cdot\frac{l}{2}"],
         "einsetzen": [r"A_{Ed} = \frac{#F:0#}{2} + #p:1#\cdot\frac{#l:2#}{2} = #A:1#" + kN],
         "werte": [{"id": "A", "expr": "F/2 + p*l/2", "d": 1}]},
        {"abschnitt": A_26, "seite": 27, "titel": "Biegemoment in Feldmitte",
         "formel": [r"M_{Ed} = \frac{F_{Ed}\cdot l}{4} + p_{Ed}\cdot\frac{l^2}{8}"],
         "einsetzen": [r"M_{Ed} = \frac{#F:0#\cdot #l:2#}{4} + #p:1#\cdot\frac{#l:2#^2}{8} = #M:1#" + kNm],
         "werte": [{"id": "M", "expr": "F*l/4 + p*l*l/8", "d": 1}]},
        {"abschnitt": A_26, "seite": 27, "titel": "Torsionsmoment",
         "text": "Das Moment aus der ausmittigen Konsollast teilt sich je zur Hälfte auf die beiden Trägerhälften auf.",
         "formel": [r"T_{Ed} = \frac{F_{Ed}\cdot e}{2}"],
         "einsetzen": [r"T_{Ed} = \frac{#F:0#\cdot #e:3#}{2} = #T:1#" + kNm],
         "werte": [{"id": "T", "expr": "F*e/2", "d": 1}]},

        {"abschnitt": B_26, "seite": 28, "titel": "Randabstand und Nutzhöhe",
         "text": "XC3 mit Bügeln Ø12 und Längsstäben Ø28; der Randabstand wird auf 6 cm gerundet.",
         "formel": [r"d_1 = c_{min} + \Delta c_{dev} + \phi_w + \frac{\phi_l}{2} = 20 + 15 + 12 + \frac{28}{2} = 61\,\mathrm{mm} \approx 6\,\mathrm{cm}",
                    r"d = h - d_1"],
         "einsetzen": [r"d = #h:2# - 0{,}06 = #d:2#" + m],
         "werte": [{"id": "d1", "expr": "0.06", "d": 2}, {"id": "d", "expr": "h - d1", "d": 2}]},
        {"abschnitt": B_26, "seite": 28, "titel": "Betondruckfestigkeit",
         "formel": [r"f_{cd} = \eta_{cc}\cdot k_{tc}\cdot\frac{f_{ck}}{\gamma_C}"],
         "einsetzen": [r"f_{cd} = 1\cdot 0{,}85\cdot\frac{30}{1{,}5} = #fcd:1#\,\mathrm{N/mm^2}"],
         "werte": [{"id": "fcd", "expr": "0.85*fck/1.5", "d": 1}]},
        {"abschnitt": B_26, "seite": 28, "titel": "Bezogenes Moment",
         "text": "Abgelesen wird in der Tafelzeile, die auf der sicheren Seite liegt (nächsthöherer Wert).",
         "formel": [r"\mu_{Eds} = \frac{M_{Eds}}{b\cdot d^2\cdot f_{cd}}"],
         "einsetzen": [r"\mu_{Eds} = \frac{#Mmn:4#}{#b:2#\cdot #d:2#^2\cdot #fcd:0#} = #mu:3# \;\rightarrow\; \text{Tafelzeile } #muT:2#"],
         "notiz": "Im Buch steht im Zähler 0,555 MNm; gemeint ist M_Ed = 0,550 MNm. Die Tafelzeile 0,20 bleibt gleich.",
         "werte": [{"id": "Mmn", "expr": "M/1000", "d": 4},
                   {"id": "mu", "expr": "Mmn/(b*d*d*fcd)", "d": 3},
                   {"id": "muT", "expr": "Math.ceil(mu*100 - 1e-9)/100", "d": 2}]},
        {"abschnitt": B_26, "seite": 28, "titel": "Tafelwerte ablesen",
         "text": "Bemessungstafel für Rechteckquerschnitte ohne Druckbewehrung (Parabel-Rechteck, B500 mit ansteigendem Ast).",
         "formel": [r"\mu_{Eds} = #muT:2# \;\Rightarrow\; \omega = #om:4#,\quad \sigma_{sd} = #sig:1#\,\mathrm{N/mm^2},\quad \xi = #xi:3#"],
         "einsetzen": [zeile(r"\xi = #xi:3# > 0{,}45:\ \text{hohe Ausnutzung, Druckbewehrung prüfen}", "xi > 0.45")],
         "werte": [{"id": "om", "expr": "omegaTafel(muT).w", "d": 4}, {"id": "sig", "expr": "omegaTafel(muT).s", "d": 1},
                   {"id": "xi", "expr": "omegaTafel(muT).xi", "d": 3}]},
        {"abschnitt": B_26, "seite": 28, "titel": "Erforderliche Biegebewehrung",
         "formel": [r"A_{s1} = \frac{1}{\sigma_{sd}}\cdot\omega\cdot b\cdot d\cdot f_{cd}"],
         "einsetzen": [r"A_{s1} = \frac{1}{#sig:1#}\cdot #om:4#\cdot #b:2#\cdot #d:2#\cdot #fcd:0# = #As1:2#" + cm2],
         "werte": [{"id": "As1", "expr": "om*b*d*fcd/sig*1e4", "d": 2}]},

        {"abschnitt": Q_26, "seite": 29, "titel": "Querkraft am Auflagerrand",
         "text": "Der Druckstrebennachweis darf am Auflagerrand geführt werden (Auflagertiefe $t$ = 30 cm).",
         "formel": [r"V_{Ed,1} = V_{Ed,A} - p_{Ed}\cdot\frac{t}{2}"],
         "einsetzen": [r"V_{Ed,1} = #A:1# - #p:1#\cdot\frac{0{,}30}{2} = #V1:1#" + kN],
         "werte": [{"id": "V1", "expr": "A - p*tA/2", "d": 1}]},
        {"abschnitt": Q_26, "seite": 29, "titel": "Schubspannung am Auflagerrand",
         "formel": [r"\tau_{Ed,1} = \frac{V_{Ed,1}}{b_w\cdot z} = \frac{V_{Ed,1}}{b_w\cdot 0{,}9\,d}"],
         "einsetzen": [r"\tau_{Ed,1} = \frac{#V1mn:4#}{#b:2#\cdot 0{,}9\cdot #d:2#} = #tau1:2#" + MN2],
         "werte": [{"id": "V1mn", "expr": "V1/1000", "d": 4}, {"id": "tau1", "expr": "V1mn/(b*0.9*d)", "d": 2}]},
        {"abschnitt": Q_26, "seite": 29, "titel": "Grenzen des Druckstrebenwinkels",
         "text": "Vereinfachter Nachweis: keine Normalkraft und Betonstahl der Duktilitätsklasse A, daher wird $\\cot\\theta_{min}$ um 20 % abgemindert.",
         "formel": [r"1{,}0 \le \cot\theta \le \cot\theta_{min} = 2{,}5\cdot 0{,}8 = 2{,}0"]},
        {"abschnitt": Q_26, "seite": 29, "titel": "Druckstrebe mit dem flachsten Winkel",
         "text": "Zuerst wird der flachste zulässige Winkel ($\\cot\\theta$ = 2,0) geprüft.",
         "formel": [r"\sigma_{cd} = \tau_{Ed,1}\cdot(\cot\theta + \tan\theta) \le \nu\cdot f_{cd}"],
         "einsetzen": [r"\sigma_{cd} = #tau1:2#\cdot(2{,}0 + 1/2) = #sig2:2#" + MN2 + r" \le 0{,}5\cdot #fcd:0# = #nfcd:2#" + MN2,
                       *chk("sig2 <= nfcd"),
                       zeile(r"\Rightarrow \text{steilerer Winkel: } \cot\theta = #cotV:2#", "sig2 > nfcd && okV"),
                       zeile(r"\Rightarrow \text{auch mit } \cot\theta = 1{,}0 \text{ nicht erfüllt – Querschnitt vergrößern}", "!okV")],
         "werte": [{"id": "sig2", "expr": "tau1*2.5", "d": 2}, {"id": "nfcd", "expr": "0.5*fcd", "d": 2},
                   {"id": "kV", "expr": "nfcd/tau1", "d": 3},
                   {"id": "okV", "expr": "kV >= 2"},
                   {"id": "cotV", "expr": "sig2 <= nfcd ? 2 : (okV ? Math.floor((kV + Math.sqrt(kV*kV - 4))/2*10)/10 : 1)", "d": 1}]},
        {"abschnitt": Q_26, "seite": 29, "titel": "Querkraft im Abstand d",
         "text": "Bei direkter Lagerung darf die Querkraftbewehrung für die Querkraft im Abstand $d$ vom Auflagerrand ermittelt werden.",
         "formel": [r"V_{Ed,2} = V_{Ed,A} - p_{Ed}\cdot\left(\frac{t}{2} + d\right)", r"\tau_{Ed,2} = \frac{V_{Ed,2}}{b_w\cdot z}"],
         "einsetzen": [r"V_{Ed,2} = #A:1# - #p:1#\cdot\left(\frac{0{,}30}{2} + #d:2#\right) = #V2:1#" + kN,
                       r"\tau_{Ed,2} = \frac{#V2mn:4#}{#b:2#\cdot 0{,}9\cdot #d:2#} = #tau2:2#" + MN2],
         "werte": [{"id": "V2", "expr": "A - p*(tA/2 + d)", "d": 1}, {"id": "V2mn", "expr": "V2/1000", "d": 4},
                   {"id": "tau2", "expr": "V2mn/(b*0.9*d)", "d": 2}]},
        {"abschnitt": Q_26, "seite": 29, "titel": "Querkraftbewehrung",
         "text": "Auf der sicheren Seite mit demselben Winkel wie beim Druckstrebennachweis.",
         "formel": [r"\rho_w = \frac{A_{sw}}{b_w\cdot s} = \frac{\tau_{Ed}}{f_{ywd}\cdot\cot\theta}", r"a_{sw,V} = \rho_w\cdot b_w"],
         "einsetzen": [r"\rho_w = \frac{#tau2:2#}{435\cdot #cotV:1#} = #rhoP:3#\cdot 10^{-3}",
                       r"a_{sw,V} = #rhoP:3#\cdot 10^{-3}\cdot #b:2# = #aswV:2#" + cm2m],
         "werte": [{"id": "rhow", "expr": "tau2/(fyd*cotV)", "d": 5}, {"id": "rhoP", "expr": "rhow*1000", "d": 3},
                   {"id": "aswV", "expr": "rhow*b*1e4", "d": 2}]},
        {"abschnitt": Q_26, "seite": 30, "titel": "Druckstrebentragfähigkeit für die Interaktion",
         "formel": [r"\tau_{Rd,max} = \frac{\nu\cdot f_{cd}}{\tan\theta + \cot\theta}"],
         "einsetzen": [r"\tau_{Rd,max} = \frac{0{,}5\cdot #fcd:0#}{1/#cotV:1# + #cotV:1#} = #tRd:2#" + MN2],
         "werte": [{"id": "tRd", "expr": "0.5*fcd/(1/cotV + cotV)", "d": 2}]},

        {"abschnitt": T_26, "seite": 30, "titel": "Bredtscher Kasten",
         "text": "Die Ersatzwanddicke ist der doppelte Abstand der Längsbewehrung vom Rand, Gl. (2.34).",
         "formel": [r"t_{eff} = 2\cdot a", r"A_k = \left(b - t_{eff}\right)\cdot\left(h - t_{eff}\right)",
                    r"u_k = 2\cdot\left(b - t_{eff}\right) + 2\cdot\left(h - t_{eff}\right)"],
         "einsetzen": [r"t_{eff} = 2\cdot 0{,}06 = #teff:2#" + m,
                       r"A_k = (#b:2# - #teff:2#)\cdot(#h:2# - #teff:2#) = #Ak:4#" + m2,
                       r"u_k = 2\cdot(#b:2# - #teff:2#) + 2\cdot(#h:2# - #teff:2#) = #uk:2#" + m],
         "werte": [{"id": "teff", "expr": "2*d1", "d": 2}, {"id": "Ak", "expr": "(b - teff)*(h - teff)", "d": 4},
                   {"id": "uk", "expr": "2*(b - teff) + 2*(h - teff)", "d": 2}]},
        {"abschnitt": T_26, "seite": 30, "titel": "Torsionsschubspannung",
         "formel": [r"\tau_{t,i} = \frac{T_{Ed}}{2\cdot A_k\cdot t_{eff}} \qquad \text{Gl. (2.35)}"],
         "einsetzen": [r"\tau_{t,i} = \frac{#Tmn:4#}{2\cdot #Ak:4#\cdot #teff:2#} = #tt:2#" + MN2],
         "werte": [{"id": "Tmn", "expr": "T/1000", "d": 4}, {"id": "tt", "expr": "Tmn/(2*Ak*teff)", "d": 2}]},
        {"abschnitt": T_26, "seite": 30, "titel": "Druckstrebe aus Torsion",
         "text": "Vereinfacht mit $\\theta$ = 45° ($\\cot\\theta$ = 1); dafür darf $\\nu$ = 0,6 angesetzt werden.",
         "formel": [r"\tau_{t,Rd,max} = \frac{\nu\cdot f_{cd}}{\cot\theta + \tan\theta} \qquad \text{Gl. (2.38)}"],
         "einsetzen": [r"\tau_{t,Rd,max} = \frac{0{,}6\cdot #fcd:0#}{1 + 1} = #ttRd:2#" + MN2,
                       r"\tau_{t,i} = #tt:2#" + MN2 + r" \le \tau_{t,Rd,max} = #ttRd:2#" + MN2, *chk("tt <= ttRd")],
         "werte": [{"id": "ttRd", "expr": "0.6*fcd/2", "d": 2}]},
        {"abschnitt": T_26, "seite": 30, "titel": "Torsionsbügel",
         "formel": [r"a_{sw,T} = \frac{A_{sw,erf}}{s} = \frac{\tau_{t,i}\cdot t_{eff}}{f_{ywd}\cdot\cot\theta} \qquad \text{Gl. (2.41)}"],
         "einsetzen": [r"a_{sw,T} = \frac{#tt:2#\cdot #teff:2#}{435\cdot 1} = #aswT:2#" + cm2m],
         "werte": [{"id": "aswT", "expr": "tt*teff/fyd*1e4", "d": 2}]},
        {"abschnitt": T_26, "seite": 31, "titel": "Torsionslängsbewehrung",
         "formel": [r"A_{sl,erf} = \frac{\tau_{t,i}\cdot t_{eff}\cdot u_k}{f_{yd}}\cdot\cot\theta \qquad \text{Gl. (2.42)}",
                    r"\frac{A_{sl}}{u_k}"],
         "einsetzen": [r"A_{sl,erf} = \frac{#tt:2#\cdot #teff:2#\cdot #uk:2#}{435}\cdot 1{,}0 = #Asl:2#" + cm2,
                       r"\frac{A_{sl}}{u_k} = \frac{#Asl:2#}{#uk:2#} = #aslu:2#" + cm2m],
         "werte": [{"id": "Asl", "expr": "tt*teff*uk/fyd*1e4", "d": 2}, {"id": "aslu", "expr": "Asl/uk", "d": 2}]},

        {"abschnitt": I_26, "seite": 31, "titel": "Längsbewehrung aus Biegung und Torsion addieren",
         "text": "Die Torsionslängsbewehrung wird je Seite über die Kastenlänge verteilt; unten kommt die Biegebewehrung hinzu.",
         "formel": [r"\text{oben: } A_s = \frac{A_{sl}}{u_k}\cdot(b - t_{eff})",
                    r"\text{seitlich: } A_s = \frac{A_{sl}}{u_k}\cdot(h - t_{eff})",
                    r"\text{unten: } A_s = \frac{A_{sl}}{u_k}\cdot(b - t_{eff}) + A_{s1}"],
         "einsetzen": [r"\text{oben: } #aslu:2#\cdot(#b:2# - #teff:2#) = #Aob:2#" + cm2 + r"\;\Rightarrow\; #txtOb# = #Aobv:2#" + cm2,
                       r"\text{seitlich: } #aslu:2#\cdot(#h:2# - #teff:2#) = #Ase:2#" + cm2 + r"\;\Rightarrow\; #txtSe# = #Asev:2#" + cm2,
                       zeile(r"\quad\text{Fehlbetrag } #fehl:2#\,\mathrm{cm^2}\text{ durch die höhere Wahl oben abgedeckt}", "Asev < Ase"),
                       r"\text{unten: } #aslu:2#\cdot(#b:2# - #teff:2#) + #As1:2# = #Aun:2#" + cm2 + r"\;\Rightarrow\; #txtUn# = #Aunv:2#" + cm2],
         "werte": [{"id": "Aob", "expr": "aslu*(b - teff)", "d": 2},
                   {"id": "nOb", "expr": "Math.max(2, Math.ceil(Aob/stabA(1,12) - 1e-9))", "d": 0},
                   {"id": "Aobv", "expr": "stabA(nOb,12)", "d": 2}, {"id": "txtOb", "expr": "stabTxt(nOb,12)"},
                   {"id": "Ase", "expr": "aslu*(h - teff)", "d": 2},
                   {"id": "nSe", "expr": "(() => { let n = 3; while (stabA(n,12) + (Aobv - Aob)/2 < Ase - 1e-9) n++; return n; })()", "d": 0},
                   {"id": "Asev", "expr": "stabA(nSe,12)", "d": 2}, {"id": "txtSe", "expr": "stabTxt(nSe,12)"},
                   {"id": "fehl", "expr": "Ase - Asev", "d": 2},
                   {"id": "Aun", "expr": "aslu*(b - teff) + As1", "d": 2},
                   {"id": "Aunv", "expr": "wahlUnten(Aun).A", "d": 2}, {"id": "txtUn", "expr": "wahlUnten(Aun).txt"}]},
        {"abschnitt": I_26, "seite": 31, "titel": "Bügelbewehrung addieren",
         "text": "Die Torsionsbügel beziehen sich auf einen Bügelschenkel, die Querkraftbügel auf beide. Gewählt werden zweischnittige Bügel Ø12 (Ø14/Ø16, falls der Abstand sonst unter 10 cm fiele).",
         "formel": [r"\frac{A_{sw,tot}}{s} = \frac{A_{sw,V}}{s} + 2\cdot\frac{A_{sw,T}}{s}"],
         "einsetzen": [r"\frac{A_{sw,tot}}{s} = #aswV:2# + 2\cdot #aswT:2# = #aswTot:2#" + cm2m,
                       r"\text{gewählt: } #txtBu# \;\Rightarrow\; a_{sw,vorh} = 2\cdot\frac{#dB#^2\,\pi}{4}\,/\,#sBm:2# = #aswv:2#" + cm2m],
         "werte": [{"id": "aswTot", "expr": "aswV + 2*aswT", "d": 2},
                   {"id": "bw", "expr": "buegelWahl(aswTot, [12, 14, 16], Math.min(Math.floor(100*Math.min(b, h, uk/8) + 1e-9), 30), 1)"},
                   {"id": "sB", "expr": "bw.s", "d": 0}, {"id": "dB", "expr": "bw.dcm"},
                   {"id": "sBm", "expr": "sB/100", "d": 2}, {"id": "aswv", "expr": "bw.a", "d": 2},
                   {"id": "txtBu", "expr": "bw.txt"}]},
        {"abschnitt": I_26, "seite": 31, "titel": "Interaktion Querkraft und Torsion",
         "formel": [r"\frac{\tau_{t,i}}{\tau_{t,Rd,max}} + \frac{\tau_{Ed}}{\tau_{Rd,max}} \le 1{,}0 \qquad \text{Gl. (2.43)}"],
         "einsetzen": [r"\frac{#tt:2#}{#ttRd:2#} + \frac{#tau1:2#}{#tRd:2#} = #eta:2# \le 1{,}0", *chk("eta <= 1")],
         "werte": [{"id": "eta", "expr": "tt/ttRd + tau1/tRd", "d": 2}]},

        {"abschnitt": K_26, "seite": 32, "titel": "Mindestbiegebewehrung",
         "formel": [r"M_{cr} = f_{ctm}\cdot W_{c,o} = f_{ctm}\cdot\frac{b\cdot h^2}{6}",
                    r"A_{s,u} = \frac{M_{cr}}{z_o^{II}\cdot f_{yk}} = \frac{M_{cr}}{0{,}9\cdot d\cdot f_{yk}}"],
         "einsetzen": [r"M_{cr} = 2{,}9\cdot\frac{#b:2#\cdot #h:2#^2}{6} = #Mcr:3#" + MNm,
                       r"A_{s,u} = \frac{#Mcr:3#}{0{,}9\cdot #d:2#\cdot 500} = #Asu:2#" + cm2 + r" \le A_{s,vorh} = #Aunv:1#" + cm2,
                       *chk("Asu <= Aunv")],
         "werte": [{"id": "Mcr", "expr": "fctm*b*h*h/6", "d": 3}, {"id": "Asu", "expr": "Mcr/(0.9*d*fyk)*1e4", "d": 2}]},
        {"abschnitt": K_26, "seite": 32, "titel": "Mindestbügelbewehrung",
         "formel": [r"\frac{A_{sw}}{s} \ge 0{,}08\cdot\frac{\sqrt{f_{ck}}}{f_{yk}}\cdot b_w\cdot\sin\alpha"],
         "einsetzen": [r"\frac{A_{sw}}{s} \ge 0{,}08\cdot\frac{\sqrt{30}}{500}\cdot #b:2#\cdot\sin 90^\circ = #aswmin:2#" + cm2m
                       + r" \le #aswv:1#" + cm2m, *chk("aswmin <= aswv")],
         "werte": [{"id": "aswmin", "expr": "0.08*Math.sqrt(fck)/fyk*b*1e4", "d": 2}]},
        {"abschnitt": K_26, "seite": 32, "titel": "Bügelabstand und Bügelform",
         "text": "Geschlossene Bügel nach Abb. 2.19. Aus der Querkraft gilt hier $s_{l,max}$ = 0,30 m; die Längsstäbe dürfen höchstens 30 cm auseinanderliegen.",
         "formel": [r"s_{T,max} = \min\left\{b;\ h;\ u_k/8\right\}"],
         "einsetzen": [r"s_{T,max} = \min\left\{#b:2#;\ #h:2#;\ #uk:2#/8\right\} = #sTmax:3#" + m,
                       r"s = #sBm:2#" + m + r" \le \min\left\{#sTmax:3#;\ 0{,}30\right\}", *chk("sBm <= Math.min(sTmax, 0.30) + 1e-9")],
         "werte": [{"id": "sTmax", "expr": "Math.min(b, h, uk/8)", "d": 3}]},
    ],
}

# ---------------------------------------------------------------- Komplexes Beispiel (Abschn. 2.7)
A_27 = "2.7.2 Ermittlung der Schnittgrößen"
B_27 = "2.7.3 Biegebemessung"
S_27 = "2.7.4 Einwirkende Schubspannungen"
D_27 = "2.7.5 Druckstrebentragfähigkeit"
Q_27 = "2.7.6 Querkraftbewehrung"
T_27 = "2.7.7 Torsionsbewehrung"
W_27 = "2.7.8 Bewehrungsaddition"
K_27 = "2.7.9 Konstruktive Durchbildung"

KOMPLEX = {
    "id": "komplex",
    "titel": "Komplexes Beispiel",
    "untertitel": "Aussteifungskern als Hohlkasten",
    "abschnitt": "Abschn. 2.7, S. 33–40",
    "system": "kern",
    "aufgabe": ("Der Aussteifungskern eines Bürogebäudes mit fünf Decken besteht aus vier zu einem Hohlkasten "
                "verbundenen Wänden. Er wird vereinfacht als eingespannter Kragarm betrachtet. Je Geschoss wirken "
                "die Vertikallast $F_{Ed}$, die Windlast $H_{Ed}$ und wegen der ausmittigen Lage des Kerns das "
                "Torsionsmoment $T_{Ed}$. Bemessen wird an der Einspannstelle."),
    "fest": [["Beton", "C35/45, XC1"], ["Betonstahl", "B500 A"], ["Geschosse", "5"], ["Bügel / Längsstäbe", "Ø14 / Ø25 + Ø20"]],
    "eingaben": [
        {"id": "F", "label": "Vertikallast $F_{Ed}$ je Geschoss", "einheit": "kN", "wert": 300, "step": 1, "d": 0},
        {"id": "H", "label": "Horizontallast $H_{Ed}$ je Geschoss", "einheit": "kN", "wert": 150, "step": 1, "d": 0},
        {"id": "Tg", "label": "Torsionsmoment $T_{Ed}$ je Geschoss", "einheit": "kNm", "wert": 1000, "step": 5, "d": 0},
        {"id": "hs", "label": "Geschosshöhe $h_{St}$", "einheit": "m", "wert": 2.5, "step": 0.01, "d": 2},
        {"id": "a", "label": "Außenmaß $b = h$", "einheit": "m", "wert": 2.0, "step": 0.01, "d": 2},
        {"id": "t", "label": "Wanddicke $t$", "einheit": "m", "wert": 0.24, "step": 0.005, "d": 3},
    ],
    "konstanten": {"fck": 35, "fctm": 3.2, "fyd": 435, "fyk": 500},
    "ergebnisse": [
        {"titel": "Bewehrung Zuggurt (Biegung)", "wert": "As1", "d": 1, "einheit": "cm²", "sub": "Zweipunktquerschnitt"},
        {"titel": "Druckstrebenwinkel", "wert": "cotK", "d": 1, "einheit": "cot θ", "sub": "Interaktion $#etaK:2#$"},
        {"titel": "Längsbewehrung je Wand", "wert": "Asv", "d": 0, "einheit": "cm²", "sub": "gewählt: $#txtL#$"},
        {"titel": "Bügel je Steg", "wert": "jeSteg", "d": 1, "einheit": "cm²/m", "sub": "gewählt: $#txtBu#$"},
        {"titel": "Interaktion V + T", "wert": "etaK", "d": 2, "eta": "etaK", "einheit": "", "sub": "Gl. (2.43)"},
    ],
    "schritte": [
        {"abschnitt": A_27, "seite": 33, "titel": "Schnittgrößen an der Einspannstelle",
         "text": "Kragarm mit fünf Geschossen; die Lasten jedes Geschosses greifen mit den Hebelarmen $1\\cdot h_{St}$ bis $5\\cdot h_{St}$ an.",
         "formel": [r"V_{Ed} = 5\cdot H_{Ed}", r"N_{Ed} = -5\cdot F_{Ed}",
                    r"M_{Ed} = H_{Ed}\cdot h_{St}\cdot(1 + 2 + 3 + 4 + 5)", r"T_{Ed} = 5\cdot T_{Ed,Geschoss}"],
         "einsetzen": [r"V_{Ed} = 5\cdot #H:0# = #V:0#" + kN, r"N_{Ed} = -5\cdot #F:0# = #N:0#" + kN,
                       r"M_{Ed} = #H:0#\cdot #hs:2#\cdot 15 = #M:0#" + kNm, r"T_{Ed} = 5\cdot #Tg:0# = #T:0#" + kNm],
         "werte": [{"id": "V", "expr": "5*H", "d": 0}, {"id": "N", "expr": "-5*F", "d": 0},
                   {"id": "M", "expr": "H*hs*15", "d": 0}, {"id": "T", "expr": "5*Tg", "d": 0}]},

        {"abschnitt": B_27, "seite": 34, "titel": "Zweipunktquerschnitt und Stabachse",
         "text": "Biegung wird vereinfacht am Zweipunktquerschnitt bemessen, die Stege werden vernachlässigt. Die Bewehrung liegt in Wandmitte.",
         "formel": [r"d_1 = \frac{t}{2}", r"M_{Eds} = M_{Ed} - N_{Ed}\cdot z_{s1}, \qquad z_{s1} = \frac{h}{2} - d_1"],
         "einsetzen": [r"d_1 = \frac{#t:3#}{2} = #d1:3#" + m,
                       r"M_{Eds} = #M:0# - (#N:0#)\cdot\left(\frac{#a:2#}{2} - #d1:3#\right) = #MEds:0#" + kNm],
         "werte": [{"id": "d1", "expr": "t/2", "d": 3}, {"id": "zs1", "expr": "a/2 - d1", "d": 3},
                   {"id": "MEds", "expr": "M - N*zs1", "d": 0}]},
        {"abschnitt": B_27, "seite": 35, "titel": "Druckzone und innerer Hebelarm",
         "text": "Die Druckzone entspricht der oberen Wand: $x = t$. Mit $\\varepsilon_c$ = 3,5 ‰ ist $k_a$ = 0,416.",
         "formel": [r"a = k_a\cdot x", r"z = h - d_1 - a"],
         "einsetzen": [r"a = 0{,}416\cdot #t:3# = #aa:3#" + m, r"z = #a:2# - #d1:3# - #aa:3# = #z:3#" + m],
         "werte": [{"id": "x", "expr": "t", "d": 3}, {"id": "aa", "expr": "0.416*x", "d": 3}, {"id": "z", "expr": "a - d1 - aa", "d": 3}]},
        {"abschnitt": B_27, "seite": 35, "titel": "Innere Druck- und Zugkraft",
         "formel": [r"F_{cd} = \frac{M_{Eds}}{z}", r"F_{sd} = F_{cd} + N_{Ed}"],
         "einsetzen": [r"F_{cd} = \frac{#MEds:0#}{#z:3#} = #Fcd:0#" + kN, r"F_{sd} = #Fcd:0# + (#N:0#) = #Fsd:0#" + kN],
         "werte": [{"id": "Fcd", "expr": "MEds/z", "d": 0}, {"id": "Fsd", "expr": "Fcd + N", "d": 0}]},
        {"abschnitt": B_27, "seite": 35, "titel": "Dehnung der Bewehrungslagen",
         "text": "Abstand der äußeren Längsbewehrung vom Bauteilrand: 4 cm.",
         "formel": [r"\varepsilon_{s} = \varepsilon_c\cdot\frac{d_i}{x} - \varepsilon_c"],
         "einsetzen": [r"\varepsilon_{s,\text{außen}} = 3{,}5\cdot\frac{#a:2# - 0{,}04}{#x:3#} - 3{,}5 = #eA:1#\,\text{‰}",
                       r"\varepsilon_{s,\text{innen}} = 3{,}5\cdot\frac{#a:2# - #t:3# + 0{,}04}{#x:3#} - 3{,}5 = #eI:1#\,\text{‰}",
                       r"\varepsilon_s > \varepsilon_{yd} = 2{,}175\,\text{‰}", *chk("eI > 2.175", r"\quad\text{Bewehrung fließt}")],
         "werte": [{"id": "eA", "expr": "3.5*(a - 0.04)/x - 3.5", "d": 1}, {"id": "eI", "expr": "3.5*(a - t + 0.04)/x - 3.5", "d": 1}]},
        {"abschnitt": B_27, "seite": 36, "titel": "Bewehrung im Zuggurt",
         "formel": [r"A_{s1} = \frac{F_{sd}}{f_{yd}}"],
         "einsetzen": [r"A_{s1} = \frac{#Fsd:0#}{43{,}5} = #As1:1#" + cm2],
         "werte": [{"id": "As1", "expr": "Fsd/43.5", "d": 1}]},
        {"abschnitt": B_27, "seite": 36, "titel": "Tragfähigkeit der Druckzone",
         "text": "Völligkeitsbeiwert $\\alpha_R$ = 0,81 für $\\varepsilon_c$ = 3,5 ‰.",
         "formel": [r"f_{cd} = \eta_{cc}\cdot k_{tc}\cdot\frac{f_{ck}}{\gamma_C}", r"F_{Rd} = \alpha_R\cdot x\cdot b\cdot f_{cd}"],
         "einsetzen": [r"f_{cd} = 1\cdot 0{,}85\cdot\frac{35}{1{,}5} = #fcd:1#" + MN2,
                       r"F_{Rd} = 0{,}81\cdot #x:3#\cdot #a:2#\cdot #fcd:1# = #FRd:1#" + MN + r" \ge F_{cd} = #FcdMN:1#" + MN,
                       *chk("FcdMN <= FRd", r"\quad\checkmark\ \text{Ausnutzung } #ausn:0#\,\%")],
         "notiz": "Im Buchtext steht F_Rd = 5,5 MN; nach der Rechnung darüber sind es 7,7 MN.",
         "werte": [{"id": "fcd", "expr": "0.85*fck/1.5", "d": 1}, {"id": "FRd", "expr": "0.81*x*a*fcd", "d": 1},
                   {"id": "FcdMN", "expr": "Fcd/1000", "d": 1}, {"id": "ausn", "expr": "FcdMN/FRd*100", "d": 0}]},

        {"abschnitt": S_27, "seite": 36, "titel": "Schubspannung aus Querkraft",
         "text": "Die Querkraft tragen die beiden Stege gemeinsam: $b_w = 2\\cdot t$.",
         "formel": [r"\tau_{Ed} = \frac{V_{Ed}}{b_w\cdot z}"],
         "einsetzen": [r"\tau_{Ed} = \frac{#Vmn:3#}{2\cdot #t:3#\cdot #z:3#} = #tauEd:2#" + MN2],
         "werte": [{"id": "Vmn", "expr": "V/1000", "d": 3}, {"id": "tauEd", "expr": "Vmn/(2*t*z)", "d": 2}]},
        {"abschnitt": S_27, "seite": 36, "titel": "Wanddicke des Bredtschen Kastens",
         "text": "Bei einem schlanken Hohlkasten mit beidseitiger Bewehrung darf die ganze Wanddicke angesetzt werden, Gl. (2.34).",
         "formel": [r"h_w \le \frac{h}{6} \;\Rightarrow\; t_{eff,i} = h_w"],
         "einsetzen": [r"h_w = #t:3#" + m + r" \le \frac{#a:2#}{6} = #a6:3#" + m,
                       *chk("t <= a6", r"\;\Rightarrow\;\text{schlanker Hohlkasten}", r"\;\Rightarrow\;\text{kein schlanker Hohlkasten}"),
                       r"t_{eff,i} = #teff:3#" + m],
         "werte": [{"id": "a6", "expr": "a/6", "d": 3}, {"id": "teff", "expr": "t", "d": 3}]},
        {"abschnitt": S_27, "seite": 36, "titel": "Kernquerschnitt und Torsionsschubspannung",
         "formel": [r"A_k = (h - h_w)\cdot(b - h_w)", r"\tau_t = \frac{T_{Ed}}{2\cdot A_k\cdot t_{eff,i}} \qquad \text{Gl. (2.35)}"],
         "einsetzen": [r"A_k = (#a:2# - #t:3#)^2 = #Ak:2#" + m2,
                       r"\tau_t = \frac{#Tmn:3#}{2\cdot #Ak:2#\cdot #teff:3#} = #tt:2#" + MN2],
         "werte": [{"id": "Ak", "expr": "(a - t)*(a - t)", "d": 2}, {"id": "Tmn", "expr": "T/1000", "d": 3},
                   {"id": "tt", "expr": "Tmn/(2*Ak*teff)", "d": 2}]},

        {"abschnitt": D_27, "seite": 37, "titel": "Grenzen des Druckstrebenwinkels",
         "text": "Keine Normalkraft angesetzt und Duktilitätsklasse A, daher Abminderung um 20 %. Kasten mit innerer und äußerer Bewehrung: $\\nu$ = 0,5.",
         "formel": [r"1{,}0 \le \cot\theta \le \cot\theta_{min} = 2{,}5\cdot 0{,}8 = 2{,}0"]},
        {"abschnitt": D_27, "seite": 37, "titel": "Nachweise mit cot θ = 2,0",
         "formel": [r"\tau_{Rd,max} = \tau_{t,Rd,max} = \frac{\nu\cdot f_{cd}}{\tan\theta + \cot\theta} \qquad \text{Gl. (2.38)}"],
         "einsetzen": [r"\tau_{Rd,max} = \frac{0{,}5\cdot #fcd:1#}{2{,}0 + 1/2{,}0} = #tR2:2#" + MN2,
                       r"\tau_{Ed} = #tauEd:2# \le #tR2:2#" + MN2 + r",\qquad \tau_t = #tt:2# \le #tR2:2#" + MN2,
                       *chk("tauEd <= tR2 && tt <= tR2"),
                       r"\text{Interaktion (linear, Hohlkasten): } \frac{#tt:2#}{#tR2:2#} + \frac{#tauEd:2#}{#tR2:2#} = #eta2:2# \le 1{,}0",
                       *chk("eta2 <= 1"),
                       zeile(r"\Rightarrow \cot\theta = 2{,}0 \text{ wird beibehalten}", "eta2 <= 1")],
         "werte": [{"id": "tR2", "expr": "0.5*fcd/2.5", "d": 2}, {"id": "eta2", "expr": "(tt + tauEd)/tR2", "d": 2},
                   {"id": "cotK", "expr": "eta2 <= 1 ? 2 : cotStufe(tt + tauEd, 0.5*fcd)", "d": 1},
                   {"id": "tRK", "expr": "0.5*fcd/(cotK + 1/cotK)", "d": 2},
                   {"id": "etaK", "expr": "(tt + tauEd)/tRK", "d": 2},
                   {"id": "cotGr", "expr": "(() => { const k = 0.5*fcd/(tt + tauEd); return k >= 2 ? (k + Math.sqrt(k*k - 4))/2 : 0; })()", "d": 2}]},
        {"abschnitt": D_27, "seite": 37, "titel": "Steilerer Druckstrebenwinkel", "wenn": "eta2 > 1",
         "text": "Die Interaktion ist nicht erfüllt. Gewählt wird ein steilerer Winkel (Stufen von 0,2 wie im Buch).",
         "formel": [r"\frac{\tau_{t}}{\tau_{t,Rd,max}} + \frac{\tau_{Ed}}{\tau_{Rd,max}} \le 1{,}0"],
         "einsetzen": [r"\cot\theta = #cotK:1#:\quad \tau_{Rd,max} = \frac{0{,}5\cdot #fcd:1#}{#cotK:1# + 1/#cotK:1#} = #tRK:2#" + MN2,
                       r"\frac{#tt:2#}{#tRK:2#} + \frac{#tauEd:2#}{#tRK:2#} = #etaK:2# \le 1{,}0", *chk("etaK <= 1"),
                       zeile(r"\text{Größter zulässiger Wert: } \cot\theta \le #cotGr:2#", "cotGr >= 1"),
                       zeile(r"\Rightarrow\text{ Auch mit } \cot\theta = 1{,}0 \text{ nicht erfüllt – Wanddicke vergrößern}", "etaK > 1")]},

        {"abschnitt": Q_27, "seite": 38, "titel": "Querkraftbewehrung",
         "formel": [r"\rho_w = \frac{\tau_{Ed}}{f_{ywd}\cdot\cot\theta}", r"a_{sw,V} = \rho_w\cdot b_w"],
         "einsetzen": [r"\rho_w = \frac{#tauEd:2#}{435\cdot #cotK:1#} = #rhoP:2#\cdot 10^{-3}",
                       r"a_{sw,V} = #rhoP:2#\cdot 10^{-3}\cdot 2\cdot #t:3# = #aswV:1#" + cm2m],
         "werte": [{"id": "rhow", "expr": "tauEd/(fyd*cotK)", "d": 5}, {"id": "rhoP", "expr": "rhow*1000", "d": 2},
                   {"id": "aswV", "expr": "rhow*2*t*1e4", "d": 1}]},

        {"abschnitt": T_27, "seite": 38, "titel": "Torsionsbügel",
         "formel": [r"a_{sw,T} = \frac{\tau_{t,i}\cdot t_{eff}}{f_{ywd}\cdot\cot\theta} \qquad \text{Gl. (2.41)}"],
         "einsetzen": [r"a_{sw,T} = \frac{#tt:2#\cdot #teff:3#}{435\cdot #cotK:1#} = #aswT:1#" + cm2m],
         "notiz": "Das Buch rundet a_sw,T auf 12 cm²/m und rechnet damit weiter.",
         "werte": [{"id": "aswT", "expr": "tt*teff/(fyd*cotK)*1e4", "d": 1}]},
        {"abschnitt": T_27, "seite": 38, "titel": "Umfang und Torsionslängsbewehrung",
         "formel": [r"u_k = 4\cdot z_i, \qquad z_i = h - h_w",
                    r"A_{sl,erf} = \frac{\tau_{t,i}\cdot t_{eff}\cdot u_k}{f_{yd}}\cdot\cot\theta \qquad \text{Gl. (2.42)}"],
         "einsetzen": [r"u_k = 4\cdot #zi:2# = #uk:2#" + m,
                       r"A_{sl,erf} = \frac{#tt:2#\cdot #teff:3#\cdot #uk:2#}{435}\cdot #cotK:1# = #Asl:0#" + cm2,
                       r"\frac{A_{sl}}{u_k} = \frac{#Asl:0#}{#uk:2#} = #aslu:1#" + cm2m],
         "werte": [{"id": "zi", "expr": "a - t", "d": 2}, {"id": "uk", "expr": "4*zi", "d": 2},
                   {"id": "Asl", "expr": "tt*teff*uk/fyd*cotK*1e4", "d": 0}, {"id": "aslu", "expr": "Asl/uk", "d": 1}]},

        {"abschnitt": W_27, "seite": 38, "titel": "Längsbewehrung addieren",
         "text": "Biegung und Torsion werden vereinfacht addiert. Da der Wind aus jeder Richtung kommen kann, erhalten alle Wände dieselbe Bewehrung.",
         "formel": [r"\text{Druckgurt und Steg: } A_s = \frac{A_{sl}}{u_k}\cdot z_i",
                    r"\text{Zuggurt: } A_s = \frac{A_{sl}}{u_k}\cdot z_i + A_{s1}"],
         "einsetzen": [r"\text{Druckgurt und Steg: } #aslu:1#\cdot #zi:2# = #AsD:0#" + cm2,
                       r"\text{Zuggurt: } #aslu:1#\cdot #zi:2# + #As1:1# = #AsZ:0#" + cm2,
                       r"\text{je Wand gewählt: } #txtL# \;\Rightarrow\; A_{s,vorh} = #Asv:0#" + cm2],
         "werte": [{"id": "AsD", "expr": "aslu*zi", "d": 0}, {"id": "AsZ", "expr": "aslu*zi + As1", "d": 0},
                   {"id": "n20", "expr": "Math.max(2, 2*Math.ceil((AsZ - stabA(4,25))/(2*stabA(1,20)) - 1e-9))", "d": 0},
                   {"id": "Asv", "expr": "stabA(4,25) + stabA(n20,20)", "d": 0},
                   {"id": "txtL", "expr": "stabTxt(4,25) + ' + ' + stabTxt(n20,20)"}]},
        {"abschnitt": W_27, "seite": 39, "titel": "Bügelbewehrung addieren",
         "text": "Torsionsbügel je Bügelschenkel, Querkraftbügel für beide Stege zusammen. Je Steg liegen zwei Schenkel (innen und außen).",
         "formel": [r"\frac{A_{sw,tot}}{s} = \frac{A_{sw,V}}{s} + 2\cdot\frac{A_{sw,T}}{s}"],
         "einsetzen": [r"\frac{A_{sw,tot}}{s} = #aswV:1# + 2\cdot #aswT:1# = #aswTot:1#" + cm2m + r",\qquad \text{je Steg } #jeSteg:1#" + cm2m,
                       r"\text{gewählt: } #txtBu# \;\Rightarrow\; a_{sw,vorh} = 2\cdot\frac{#dB#^2\,\pi}{4}\,/\,#sBm:2# = #aswv:1#" + cm2m],
         "notiz": "Das Buch wählt Bügel Ø14/15 (20,5 cm²/m); hier wird der größte ausreichende Abstand in 5-cm-Schritten gewählt (Ø16/Ø20, falls er sonst unter 10 cm fiele).",
         "werte": [{"id": "aswTot", "expr": "aswV + 2*aswT", "d": 1}, {"id": "jeSteg", "expr": "aswTot/2", "d": 1},
                   {"id": "bw", "expr": "buegelWahl(jeSteg, [14, 16, 20], Math.min(30, 5*Math.floor(100*Math.min(a, uk/8)/5 + 1e-9)), 5)"},
                   {"id": "sB", "expr": "bw.s", "d": 0}, {"id": "dB", "expr": "bw.dcm"},
                   {"id": "sBm", "expr": "sB/100", "d": 2}, {"id": "aswv", "expr": "bw.a", "d": 1},
                   {"id": "txtBu", "expr": "bw.txt"}]},

        {"abschnitt": K_27, "seite": 39, "titel": "Mindestbiegebewehrung",
         "formel": [r"W_c = \frac{b\cdot h^3 - (b - 2t)\cdot(h - 2t)^3}{6\cdot h}", r"M_{cr} = f_{ctm}\cdot W_c",
                    r"A_{s,u} = \frac{M_{cr}}{z_o^{II}\cdot f_{yk}}"],
         "einsetzen": [r"W_c = \frac{#a:2#^4 - (#a:2# - 2\cdot #t:3#)^4}{6\cdot #a:2#} = #Wc:4#\,\mathrm{m^3}",
                       r"M_{cr} = 3{,}2\cdot #Wc:4# = #Mcr:2#" + MNm,
                       r"A_{s,u} = \frac{#Mcr:2#}{#zi:2#\cdot 500} = #Asu:0#" + cm2 + r" \le A_{s,vorh} = #Asv:0#" + cm2, *chk("Asu <= Asv")],
         "werte": [{"id": "Wc", "expr": "(Math.pow(a,4) - Math.pow(a - 2*t, 4))/(6*a)", "d": 4},
                   {"id": "Mcr", "expr": "fctm*Wc", "d": 2}, {"id": "Asu", "expr": "Mcr/(zi*fyk)*1e4", "d": 0}]},
        {"abschnitt": K_27, "seite": 39, "titel": "Mindestbügelbewehrung",
         "formel": [r"\frac{A_{sw}}{s} \ge 0{,}08\cdot\frac{\sqrt{f_{ck}}}{f_{yk}}\cdot b_w\cdot\sin\alpha"],
         "einsetzen": [r"\frac{A_{sw}}{s} \ge 0{,}08\cdot\frac{\sqrt{35}}{500}\cdot 2\cdot #t:3#\cdot\sin 90^\circ = #aswmin:1#" + cm2m
                       + r" \le 2\cdot #aswv:1# = #aswv2:1#" + cm2m, *chk("aswmin <= aswv2")],
         "notiz": "Im Buch wird hier mit 2 · 32 = 64 cm²/m verglichen; gemeint sind die gewählten Bügel beider Stege.",
         "werte": [{"id": "aswmin", "expr": "0.08*Math.sqrt(fck)/fyk*2*t*1e4", "d": 1}, {"id": "aswv2", "expr": "2*aswv", "d": 1}]},
        {"abschnitt": K_27, "seite": 39, "titel": "Bügel- und Stababstände",
         "text": "Geschlossene Bügel nach Abb. 2.19. Aus der Querkraft gilt $s_{max}$ = 0,30 m, die Längsstäbe dürfen höchstens 35 cm auseinanderliegen.",
         "formel": [r"s_{T,max} = \min\left\{b;\ h;\ u_k/8\right\}"],
         "einsetzen": [r"s_{T,max} = \min\left\{#a:2#;\ #a:2#;\ #uk:2#/8\right\} = #sTmax:2#" + m,
                       r"s = #sBm:2#" + m + r" \le \min\left\{#sTmax:2#;\ 0{,}30\right\}", *chk("sBm <= Math.min(sTmax, 0.30) + 1e-9"),
                       r"\text{Längsstäbe je Lage: } \frac{#zi:2#}{#nLage:0# - 1} = #sl:2#" + m + r" \le 0{,}35" + m, *chk("sl <= 0.35")],
         "werte": [{"id": "sTmax", "expr": "Math.min(a, uk/8)", "d": 2},
                   {"id": "nLage", "expr": "n20/2 + 2", "d": 0}, {"id": "sl", "expr": "zi/(nLage - 1)", "d": 2}]},
    ],
}


def main():
    ziel = Path(__file__).resolve().parent.parent / "content" / "01_torsion.json"
    daten = json.loads(ziel.read_text(encoding="utf-8"))
    daten["buchbeispiele"] = {"quelle": QUELLE, "auflage": "2. Aufl. 2026, Kap. 2", "beispiele": [EINFACH, KOMPLEX]}
    ziel.write_text(json.dumps(daten, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(len(b["schritte"]) for b in (EINFACH, KOMPLEX))
    print(f"Buchbeispiele geschrieben: 2 Beispiele, {n} Schritte")


if __name__ == "__main__":
    main()
