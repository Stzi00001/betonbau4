"""Flachdecken, Skript Teil 2 „Schnittgrößenermittlung mit dem Ersatzrahmen- und Gurtstreifenverfahren“ –
ergänzt Quiz, Karteikarten, Formeln, Paare, Mindmap und Übungsaufgaben in content/02_flachdecken.json.

Quelle: Vorlesungsskript Betonbau IV, Flachdecken Teil 2 (nach Finckh, Stahlbetonkonstruktion, Beispiel S. 274–286;
DAfStb-Heft 631). Folien wie im Skript; Texte sind eigene Formulierungen, Abbildungen werden nicht übernommen.
Läuft nach flachdecken_teil1.py (hängt Teil-2-Inhalte an).
"""
import json
from pathlib import Path

ZIEL = Path(__file__).resolve().parent.parent / "content" / "02_flachdecken.json"
T = "2"
TEIL = {"id": "2", "titel": "Teil 2 · Ersatzrahmen und Gurtstreifen am Beispiel", "quelle": "Skript Flachdecken Teil 2"}

KARTEN = [
    ("4–5", "Beispiel: Geometrie und Lasten",
     "Zwischengeschossdecke $h = 30\\,\\mathrm{cm}$, C30/37, XC3, Raster $l_x = 4{,}00\\,\\mathrm{m}$, $l_y = 5{,}00\\,\\mathrm{m}$, Stützen $30/30\\,\\mathrm{cm}$, Stützenlänge $3{,}00\\,\\mathrm{m}$. $g_{k,1} = 7{,}50$, $g_{k,2} = 1{,}50$, $q_k = 5{,}00\\,\\mathrm{kN/m^2}$."),
    ("6", "Bemessungswerte der Flächenlasten",
     "$g_d = 1{,}35 \\cdot (7{,}50 + 1{,}50) = 12{,}15 \\approx 12{,}2\\,\\mathrm{kN/m^2}$ und $q_d = 1{,}5 \\cdot 5{,}00 = 7{,}50\\,\\mathrm{kN/m^2}$ – getrennt angesetzt, damit die ungünstigen Laststellungen erfasst werden."),
    ("7", "Zwei statische Nutzhöhen",
     "Die Bewehrungslagen liegen übereinander: $d_x = h - c_{\\min} - \\Delta c_{dev} - \\phi/2 = 258\\,\\mathrm{mm}$, die zweite Lage $d_y = d_x - \\phi = 244\\,\\mathrm{mm}$."),
    ("8", "Ersatzsystem erste Tragrichtung",
     "In Richtung $l_y = 5\\,\\mathrm{m}$ ein Dreifeldträger mit der Streifenbreite $l_x = 4\\,\\mathrm{m}$. Momente mit Tabellenbeiwerten: $M_{Ed} = (\\alpha_g\\,g_d + \\alpha_q\\,q_d)\\,l_x\\,l_y^2$."),
    ("9–10", "Beiwerte des Dreifeldträgers",
     "Feld 1/3: $0{,}080\\,g_d + 0{,}101\\,q_d$; Feld 2: $0{,}025\\,g_d + 0{,}075\\,q_d$; Innenstützen: $-(0{,}100\\,g_d + 0{,}117\\,q_d)$ – jeweils mal $l_x\\,l_y^2$. Die $q$-Beiwerte enthalten die ungünstige Laststellung."),
    ("11", "Randmoment: Beiwerte α und β",
     "Am Deckenrand wird ein Rahmen aus Platte und Randstütze betrachtet: $\\alpha = 0{,}5 + 3\\,d_s/l_2$ (Anteil des Volleinspannmoments), $\\beta = 0{,}2 + 4\\,d_s/l_2$ (mitwirkende Plattenbreite $b_m = \\beta\\,l_2$); $d_s$ Stützenbreite, $l_2$ Stützenabstand quer."),
    ("12–13", "Randmoment über die Steifigkeiten",
     "Volleinspannmoment $M^{(0)}_{Rd} = -\\alpha\\,(g_d + q_d)\\,l_2\\,l^2/12$. Mit $c = l\\,I_S/(h\\,I_R)$ für Stütze oben und unten: $M_{R,d} = \\dfrac{c_o + c_u}{1 + c_o + c_u}\\,M^{(0)}_{Rd}$."),
    ("14", "Verteilung auf die Streifen",
     "Moment je Meter = Faktor · Streifenmoment / Streifenbreite. Feldmoment: Gurtstreifen 1,25, Feldstreifen 0,84. Stützmoment: innerer Gurtstreifen 2,10, benachbarter Gurtstreifen 1,40, Feldstreifen 0,50 (Abb. 7.6 bei Finckh; zusammen ergibt das wieder 1,0)."),
    ("15–17", "Biegebewehrung je Meter",
     "$\\mu_{Eds} = |m_{Ed}|/(f_{cd}\\,b\\,d^2)$ mit $b = 1{,}0\\,\\mathrm{m}$, $\\omega$ aus der Tafel, $a_s = \\omega\\,b\\,d\\,f_{cd}/\\sigma_{sd}$. Positive Feldmomente → untere Bewehrung, negative Stützmomente → obere Bewehrung."),
    ("19–21", "Ersatzsystem zweite Tragrichtung",
     "In Richtung $l_x = 4\\,\\mathrm{m}$ ein Vierfeldträger, Streifenbreite $l_y = 5\\,\\mathrm{m}$, Nutzhöhe $d_y$. Feld 1/4: $0{,}077\\,g_d + 0{,}100\\,q_d$; Feld 2/3: $0{,}036\\,g_d + 0{,}080\\,q_d$; Stütze B/D: $-(0{,}107\\,g_d + 0{,}121\\,q_d)$; Stütze C: $-(0{,}071\\,g_d + 0{,}107\\,q_d)$."),
    ("26–27", "Lasteinzugsflächen aus Nulldurchgängen",
     "Die Grenzen der Einzugsflächen liegen bei den Nulldurchgängen der Querkraftlinien unter Volllast. Je Stütze: $V_{Ed} = A_{Einzug}\\,(g_d + q_d)$."),
    ("28", "Stützenkräfte im Beispiel",
     "Mit $g_d + q_d = 19{,}7\\,\\mathrm{kN/m^2}$: Innenstütze S-B-2 $A \\approx 25{,}1\\,\\mathrm{m^2}$, $V_{Ed} \\approx 495\\,\\mathrm{kN}$; Randstütze S-B-1 $9{,}5\\,\\mathrm{m^2}$, $186\\,\\mathrm{kN}$; Eckstütze S-A-1 $3{,}7\\,\\mathrm{m^2}$, $73\\,\\mathrm{kN}$."),
    ("29–31", "Mindestmomente im Stützenbereich",
     "$m_{Ed,\\min} = \\eta\\,V_{Ed}$ mit lageabhängigem Beiwert, z. B. Innenstütze $\\eta = 0{,}125$, Randstütze $0{,}25$ bzw. $0{,}125$, Eckstütze $0{,}50$. Ist es größer als das Moment aus dem Ersatzrahmen, wird die Bewehrung erhöht."),
]

FORMELN = [
    {"name": "Moment am Ersatzträger", "f": "M_{Ed} = (\\alpha_g\\,g_d + \\alpha_q\\,q_d)\\,l_{\\perp}\\,l^2", "e": "$l$ Stützweite in Tragrichtung, $l_\\perp$ Streifenbreite quer", "folie": "8"},
    {"name": "Statische Nutzhöhen", "f": "d_x = h - c_{\\min} - \\Delta c_{dev} - \\tfrac{\\phi}{2}, \\qquad d_y = d_x - \\phi", "e": "obere bzw. untere Bewehrungslage", "folie": "7"},
    {"name": "Randmoment: Beiwerte", "f": "\\alpha = 0{,}5 + 3\\,\\dfrac{d_s}{l_2}, \\qquad \\beta = 0{,}2 + 4\\,\\dfrac{d_s}{l_2}", "e": "$d_s$ Stützenbreite, $l_2$ Stützenabstand quer", "folie": "11"},
    {"name": "Volleinspannmoment am Rand", "f": "M^{(0)}_{Rd} = -\\alpha\\,(g_d + q_d)\\,l_2\\,\\dfrac{l^2}{12}", "e": "Rahmen Platte–Randstütze", "folie": "12"},
    {"name": "Steifigkeiten", "f": "I_S = \\dfrac{b_s\\,d_s^3}{12}, \\qquad I_R = \\dfrac{\\beta\\,l_2\\,h^3}{12}", "e": "Stütze bzw. mitwirkender Plattenstreifen", "folie": "12"},
    {"name": "Randmoment", "f": "c = \\dfrac{l\\,I_S}{h_S\\,I_R}, \\qquad M_{R,d} = \\dfrac{c_o + c_u}{1 + c_o + c_u}\\,M^{(0)}_{Rd}", "e": "$h_S$ Stützenlänge, Stütze oben und unten", "folie": "13"},
    {"name": "Moment je Meter im Streifen", "f": "m = k \\cdot \\dfrac{M}{l_\\perp}", "e": "Feld: $k = 1{,}25$ (Gurt) / $0{,}84$ (Feld); Stütze: $2{,}10$ / $1{,}40$ / $0{,}50$", "folie": "14"},
    {"name": "Bewehrung je Meter", "f": "a_s = \\dfrac{\\omega\\,b\\,d\\,f_{cd}}{\\sigma_{sd}}", "e": "$\\omega$ aus $\\mu_{Eds} = |m_{Ed}|/(f_{cd}\\,b\\,d^2)$", "folie": "15"},
    {"name": "Stützenkraft aus Einzugsfläche", "f": "V_{Ed} = A_{Einzug}\\,(g_d + q_d)", "e": "Grenzen an den Querkraft-Nulldurchgängen unter Volllast", "folie": "26"},
    {"name": "Mindestmoment an der Stütze", "f": "m_{Ed,\\min} = \\eta\\,V_{Ed}", "e": "Innen $0{,}125$, Rand $0{,}25$/$0{,}125$, Ecke $0{,}50$", "folie": "29–31"},
]

PAARE = [
    ("Dreifeldträger", "Ersatzsystem in Richtung $l_y$", "8"),
    ("Vierfeldträger", "Ersatzsystem in Richtung $l_x$", "19"),
    ("$\\alpha = 0{,}5 + 3\\,d_s/l_2$", "Anteil des Volleinspannmoments am Rand", "11"),
    ("$\\beta\\,l_2$", "mitwirkende Plattenbreite am Randrahmen", "12"),
    ("$2{,}10$", "Faktor Stützmoment, innerer Gurtstreifen", "14"),
    ("$1{,}25$", "Faktor Feldmoment, Gurtstreifen", "14"),
    ("$d_y = d_x - \\phi$", "Nutzhöhe der zweiten Lage", "7"),
    ("$V_{Ed} = A\\,(g_d + q_d)$", "Stützenkraft aus Einzugsfläche", "26"),
    ("$m_{Ed,\\min} = \\eta\\,V_{Ed}$", "Mindestmoment an der Stütze", "29"),
    ("$\\eta = 0{,}125$", "Mindestmoment-Beiwert Innenstütze", "30"),
]

MINDMAP = {"t": "Teil 2 · Beispiel", "folie": "2–32", "c": [
    {"t": "Eingangswerte", "folie": "4–7", "c": [{"t": "$l_x/l_y = 0{,}8$ → Gurtstreifen zulässig"}, {"t": "$g_d = 12{,}2$, $q_d = 7{,}5\\,\\mathrm{kN/m^2}$"}, {"t": "$d_x = 258$, $d_y = 244\\,\\mathrm{mm}$"}]},
    {"t": "Erste Richtung", "folie": "8–18", "c": [{"t": "Dreifeldträger, Breite $l_x$"}, {"t": "Feld 173 / 87, Stütze −210 kNm"}, {"t": "Randmoment über $\\alpha$, $\\beta$, $c$"}]},
    {"t": "Zweite Richtung", "folie": "19–25", "c": [{"t": "Vierfeldträger, Breite $l_y$"}, {"t": "Feld 135 / 83, Stütze −177 / −133 kNm"}]},
    {"t": "Streifen und Bewehrung", "folie": "14–17, 23–24", "c": [{"t": "Feld: 1,25 / 0,84"}, {"t": "Stütze: 2,10 / 1,40 / 0,50"}, {"t": "$a_s = \\omega\\,b\\,d\\,f_{cd}/\\sigma_{sd}$"}]},
    {"t": "Stützen", "folie": "26–31", "c": [{"t": "Einzugsflächen aus Nulldurchgängen"}, {"t": "$V_{Ed} = A\\,(g_d + q_d)$"}, {"t": "Mindestmoment $\\eta\\,V_{Ed}$"}]},
]}


def q(d, folie, f, r, leicht, mittel, schwer, tipp, erkl):
    return {"d": d, "teil": T, "folie": folie, "f": f, "r": r,
            "falsch": {k: v for k, v in (("leicht", leicht), ("mittel", mittel), ("schwer", schwer)) if v}, "tipp": tipp, "erkl": erkl}


QUIZ = [
    q(1, "8", "Welches Ersatzsystem entsteht im Beispiel in Richtung $l_y$ (3 Felder)?", "Dreifeldträger",
      ["Kragträger", "Fachwerk"], ["Einfeldträger", "Vierfeldträger"], [], "Zähl die Felder in dieser Richtung.", "In Richtung $l_y = 5\\,\\mathrm{m}$ hat die Decke drei Felder – Ersatzsystem Dreifeldträger mit der Streifenbreite $l_x$."),
    q(1, "6", "Warum werden $g_d$ und $q_d$ getrennt angesetzt?", "Für ungünstige Laststellungen der Nutzlast",
      ["Weil es einfacher ist", "Wegen des Brandschutzes"], ["Weil $g_d$ kleiner ist", "Nur wegen der Teilsicherheitsbeiwerte"], [],
      "Die Nutzlast kann feldweise fehlen.", "Die veränderliche Last wird feldweise ungünstig gestellt; die Beiwerte $\\alpha_q$ enthalten diese Laststellungen."),
    q(1, "15", "Welche Breite hat der Bemessungsstreifen für die Biegebewehrung?", "$b = 1{,}0\\,\\mathrm{m}$",
      ["$b = 10\\,\\mathrm{m}$"], ["$b = l_x$", "$b = 0{,}30\\,\\mathrm{m}$ (Stütze)"], [], "Bemessen wird je laufendem Meter.", "Die Momente je Meter werden für einen Streifen $b = 1{,}0\\,\\mathrm{m}$ bemessen."),
    q(1, "26", "Wie wird die Stützenkraft aus der Lasteinzugsfläche berechnet?", "$V_{Ed} = A_{Einzug}\\,(g_d + q_d)$",
      ["$V_{Ed} = A_{Einzug}/(g_d + q_d)$"], ["$V_{Ed} = A_{Einzug}\\,g_d$", "$V_{Ed} = (g_d + q_d)\\,l_x$"], [], "Fläche mal Flächenlast.", "Die zugeordnete Fläche wird mit der Bemessungsflächenlast multipliziert."),
    q(1, "17", "Welche Bewehrung erfordert das negative Moment über der Stütze?", "Obere Bewehrung",
      ["Keine"], ["Untere Bewehrung", "Nur Querkraftbewehrung"], [], "Wo entsteht Zug?", "Negative Stützmomente erzeugen Zug oben – obere Bewehrung entlang der Stützenachse."),
    q(2, "7", "Warum ist $d_y$ kleiner als $d_x$?", "Die zweite Lage liegt um einen Stabdurchmesser weiter innen",
      ["Wegen der größeren Spannweite"], ["Wegen größerer Betondeckung in $y$", "Weil $l_y > l_x$"], ["Weil die Stützen in $y$-Richtung rechteckig ausgebildet sind", "Weil das Vorhaltemaß nur in $y$-Richtung angesetzt wird"],
      "Zwei Bewehrungslagen liegen übereinander.", "$d_y = d_x - \\phi$: Die zweite Lage liegt einen Stabdurchmesser tiefer bzw. höher."),
    q(2, "9", "Wie groß ist das Feldmoment im Endfeld des Dreifeldträgers im Beispiel?", "$\\approx 173\\,\\mathrm{kNm}$",
      ["$\\approx 17\\,\\mathrm{kNm}$"], ["$\\approx 87\\,\\mathrm{kNm}$", "$\\approx 210\\,\\mathrm{kNm}$"], ["$\\approx 135\\,\\mathrm{kNm}$", "$\\approx 155\\,\\mathrm{kNm}$"],
      "$(0{,}08 \\cdot 12{,}2 + 0{,}101 \\cdot 7{,}5) \\cdot 4 \\cdot 25$", "$M_1 = (0{,}08 \\cdot 12{,}2 + 0{,}101 \\cdot 7{,}5) \\cdot 4 \\cdot 5^2 \\approx 173\\,\\mathrm{kNm}$."),
    q(2, "11", "Was beschreibt $\\beta\\,l_2$ beim Randmoment?", "Die mitwirkende Plattenbreite am Randrahmen",
      ["Die Stützenhöhe"], ["Die Stützenbreite", "Die Feldstreifenbreite"], ["Den Anteil des Volleinspannmoments", "Die Gurtstreifenbreite $0{,}4\\,l_2$"],
      "Daraus wird $I_R$ berechnet.", "$b_m = \\beta\\,l_2$ ist die mitwirkende Breite der Platte im Randrahmen; $I_R = b_m\\,h^3/12$."),
    q(2, "14", "Mit welchem Faktor wird das Stützmoment auf den inneren Gurtstreifen verteilt?", "$2{,}10$",
      ["$10{,}0$"], ["$0{,}50$", "$0{,}84$"], ["$1{,}25$", "$1{,}40$"],
      "Über der Stütze konzentriert sich das Moment am stärksten.", "Stützmoment: innerer Gurtstreifen 2,10, benachbarter Gurtstreifen 1,40, Feldstreifen 0,50 (je mal $M/l_\\perp$)."),
    q(2, "14", "Welcher Faktor gilt für das Feldmoment im Feldstreifen?", "$0{,}84$",
      ["$4{,}0$"], ["$2{,}10$", "$0{,}50$"], ["$1{,}25$", "$1{,}00$"],
      "Etwas weniger als der Mittelwert 1,0.", "Feldmoment: Gurtstreifen 1,25, Feldstreifen 0,84."),
    q(2, "27", "Wo liegen die Grenzen der Lasteinzugsflächen?", "An den Nulldurchgängen der Querkraft unter Volllast",
      ["An den Plattenrändern"], ["Genau in Feldmitte", "An den Momentennullpunkten"], ["An den Nulldurchgängen unter feldweiser Last", "Im Abstand $d$ von der Stütze"],
      "Wo wechselt die Querkraft das Vorzeichen?", "Die Lastscheiden liegen bei den Nulldurchgängen der Querkraftlinien unter Volllast – deshalb ist die Innenstütze am ersten Innenfeld größer als $l_x\\,l_y$."),
    q(2, "30", "Wie groß ist das Mindestmoment an der Innenstütze im Beispiel ($V_{Ed} = 495\\,\\mathrm{kN}$)?", "$\\approx 62\\,\\mathrm{kNm/m}$",
      ["$\\approx 6\\,\\mathrm{kNm/m}$"], ["$\\approx 124\\,\\mathrm{kNm/m}$", "$\\approx 248\\,\\mathrm{kNm/m}$"], ["$\\approx 50\\,\\mathrm{kNm/m}$", "$\\approx 74\\,\\mathrm{kNm/m}$"],
      "$\\eta = 0{,}125$", "$|m_{Ed,\\min}| = 0{,}125 \\cdot 495{,}2 \\approx 62\\,\\mathrm{kNm/m}$."),
    q(3, "13", "Wie wird das Randmoment aus dem Volleinspannmoment ermittelt?", "$M_{R,d} = \\dfrac{c_o + c_u}{1 + c_o + c_u}\\,M^{(0)}_{Rd}$",
      [], ["$M_{R,d} = (c_o + c_u)\\,M^{(0)}_{Rd}$", "$M_{R,d} = M^{(0)}_{Rd}/2$"], ["$M_{R,d} = \\dfrac{1}{1 + c_o + c_u}\\,M^{(0)}_{Rd}$", "$M_{R,d} = \\dfrac{c_o}{1 + c_u}\\,M^{(0)}_{Rd}$"],
      "Je steifer die Stützen, desto näher am Volleinspannmoment.", "Mit $c = l\\,I_S/(h_S\\,I_R)$ ergibt sich $M_{R,d} = \\dfrac{c_o + c_u}{1 + c_o + c_u}\\,M^{(0)}_{Rd}$; im Beispiel $\\approx -40\\,\\mathrm{kNm}$."),
    q(3, "11", "Wie groß ist $\\alpha$ im Beispiel für $d_s = 0{,}30\\,\\mathrm{m}$ und $l_2 = 4{,}00\\,\\mathrm{m}$?", "$0{,}725$",
      [], ["$0{,}50$", "$1{,}00$"], ["$0{,}575$", "$0{,}80$"], "$0{,}5 + 3\\,d_s/l_2$", "$\\alpha = 0{,}5 + 3 \\cdot 0{,}30/4 = 0{,}725$; $\\beta = 0{,}2 + 4 \\cdot 0{,}30/4 = 0{,}50$."),
    q(3, "21", "Welches Innenstützmoment ist beim Vierfeldträger betragsmäßig am größten?", "An den Stützen B und D",
      [], ["An der Mittelstütze C", "An den Endauflagern"], ["Alle Innenstützen gleich", "Nur bei feldweiser Last an C"],
      "Neben dem Endfeld ist die Durchlaufwirkung am stärksten.", "B/D: $-(0{,}107\\,g_d + 0{,}121\\,q_d)\\,l_y\\,l_x^2 \\approx -177\\,\\mathrm{kNm}$; C: $\\approx -133\\,\\mathrm{kNm}$."),
    q(3, "28", "Warum ist die Einzugsfläche der Innenstütze S-B-2 größer als $l_x \\cdot l_y = 20\\,\\mathrm{m^2}$?", "Die Querkraft-Nulldurchgänge liegen im Endfeld weiter vom Rand weg",
      [], ["Weil die Stütze größer ist", "Wegen der Nutzlast"], ["Weil die Deckenränder als voll eingespannt gelten", "Weil die Randstützen fast keine Last abtragen"],
      "Erstes Innenauflager eines Durchlaufträgers bekommt mehr als die halben Felder.", "Am ersten Innenauflager eines Durchlaufträgers liegt der Nulldurchgang bei $0{,}6\\,l$ bzw. $0{,}607\\,l$ – daher $A \\approx 4{,}57 \\cdot 5{,}50 \\approx 25{,}1\\,\\mathrm{m^2}$."),
    q(3, "30", "Wann ist das Mindestmoment an der Stütze maßgebend?", "Wenn $\\eta\\,V_{Ed}$ größer als das Moment aus dem Ersatzrahmen ist",
      [], ["Immer", "Nie bei Innenstützen"], ["Nur an Eck- und Randstützen der Decke", "Wenn $V_{Ed}$ kleiner als $V_{Rd,c}$ der Platte ist"],
      "Es ist eine Untergrenze.", "Das Mindestmoment ist eine Untergrenze: Im Beispiel ist es in der zweiten Richtung maßgebend, in der ersten nicht."),
]

AUFGABEN = [
    {"titel": "Momente am Dreifeldträger", "teil": T,
     "text": "Flachdecke mit Raster $l_x = #lx:2#\\,\\mathrm{m}$ (Streifenbreite) und $l_y = #ly:2#\\,\\mathrm{m}$ (Spannweite, drei Felder), Bemessungslasten $g_d = #gd:1#\\,\\mathrm{kN/m^2}$ und $q_d = #qd:1#\\,\\mathrm{kN/m^2}$. Berechnen Sie die Feld- und Stützmomente des Ersatzstreifens und die Momente je Meter im Gurtstreifen.",
     "params": {"lx": {"min": 3.5, "max": 6.0, "step": 0.25}, "ly": {"min": 4.0, "max": 7.0, "step": 0.25}, "gd": {"min": 9.0, "max": 14.0, "step": 0.5}, "qd": {"min": 3.0, "max": 9.0, "step": 0.5}},
     "schritte": [
         {"titel": "Feldmoment Endfeld", "folie": "9", "formel": ["M_1 = (0{,}080\\,g_d + 0{,}101\\,q_d)\\,l_x\\,l_y^2"],
          "einsetzen": [r"M_1 = (0{,}080 \cdot #gd:1# + 0{,}101 \cdot #qd:1#)\,\mathrm{kN/m^2} \cdot #lx:2#\,\mathrm{m} \cdot (#ly:2#\,\mathrm{m})^2 = #M1:1#\,\mathrm{kNm}"],
          "werte": [{"id": "M1", "expr": "(0.08*gd + 0.101*qd)*lx*ly*ly", "d": 1, "frage": True, "label": "M_1", "einheit": "kNm"}]},
         {"titel": "Stützmoment Innenstütze", "folie": "10", "formel": ["M_B = -(0{,}100\\,g_d + 0{,}117\\,q_d)\\,l_x\\,l_y^2"],
          "einsetzen": [r"M_B = -(0{,}100 \cdot #gd:1# + 0{,}117 \cdot #qd:1#)\,\mathrm{kN/m^2} \cdot #lx:2#\,\mathrm{m} \cdot (#ly:2#\,\mathrm{m})^2 = #MB:1#\,\mathrm{kNm}"],
          "werte": [{"id": "MB", "expr": "-(0.10*gd + 0.117*qd)*lx*ly*ly", "d": 1, "frage": True, "label": "M_B", "einheit": "kNm"}]},
         {"titel": "Moment je Meter im Gurtstreifen", "folie": "14", "formel": ["m_{F,Gurt} = 1{,}25\\,\\dfrac{M_1}{l_x}, \\qquad m_{S,Gurt} = 2{,}10\\,\\dfrac{M_B}{l_x}"],
          "einsetzen": [r"m_{F,Gurt} = 1{,}25 \cdot \dfrac{#M1:1#\,\mathrm{kNm}}{#lx:2#\,\mathrm{m}} = #mF:1#\,\mathrm{kNm/m}",
                        r"m_{S,Gurt} = 2{,}10 \cdot \dfrac{#MB:1#\,\mathrm{kNm}}{#lx:2#\,\mathrm{m}} = #mS:1#\,\mathrm{kNm/m}"],
          "werte": [{"id": "mF", "expr": "1.25*M1/lx", "d": 1, "frage": True, "label": "m_{F,Gurt}", "einheit": "kNm/m"},
                    {"id": "mS", "expr": "2.10*MB/lx", "d": 1, "frage": True, "label": "m_{S,Gurt}", "einheit": "kNm/m"}]},
     ]},
    {"titel": "Randmoment am Deckenrand", "teil": T,
     "text": "Randfeld einer Flachdecke: Spannweite $l = #l:2#\\,\\mathrm{m}$, Stützenabstand quer $l_2 = #l2:2#\\,\\mathrm{m}$, quadratische Stützen $d_s = #ds:2#\\,\\mathrm{m}$, Stützenlänge oben und unten $h_S = #hs:2#\\,\\mathrm{m}$, Plattendicke $h = #h:2#\\,\\mathrm{m}$, $g_d + q_d = #p:1#\\,\\mathrm{kN/m^2}$. Bestimmen Sie das Randmoment.",
     "params": {"l": {"min": 4.0, "max": 7.0, "step": 0.25}, "l2": {"min": 4.0, "max": 7.0, "step": 0.25}, "ds": {"werte": [0.30, 0.35, 0.40, 0.45]},
                "hs": {"werte": [2.75, 3.0, 3.25, 3.5]}, "h": {"werte": [0.22, 0.25, 0.28, 0.30]}, "p": {"min": 14.0, "max": 24.0, "step": 0.5}},
     "schritte": [
         {"titel": "Beiwerte", "folie": "11", "formel": ["\\alpha = 0{,}5 + 3\\,\\dfrac{d_s}{l_2}, \\qquad \\beta = 0{,}2 + 4\\,\\dfrac{d_s}{l_2}"],
          "einsetzen": [r"\alpha = 0{,}5 + 3 \cdot \dfrac{#ds:2#}{#l2:2#} = #al:3#, \qquad \beta = 0{,}2 + 4 \cdot \dfrac{#ds:2#}{#l2:2#} = #be:3#"],
          "werte": [{"id": "al", "expr": "0.5 + 3*ds/l2", "d": 3, "frage": True, "label": "\\alpha", "einheit": "–"}, {"id": "be", "expr": "0.2 + 4*ds/l2", "d": 3}]},
         {"titel": "Volleinspannmoment", "folie": "12", "formel": ["M^{(0)}_{Rd} = -\\alpha\\,(g_d + q_d)\\,l_2\\,\\dfrac{l^2}{12}"],
          "einsetzen": [r"M^{(0)}_{Rd} = -#al:3# \cdot #p:1#\,\mathrm{kN/m^2} \cdot #l2:2#\,\mathrm{m} \cdot \dfrac{(#l:2#\,\mathrm{m})^2}{12} = #M0:1#\,\mathrm{kNm}"],
          "werte": [{"id": "M0", "expr": "-al*p*l2*l*l/12", "d": 1, "frage": True, "label": "M^{(0)}_{Rd}", "einheit": "kNm"}]},
         {"titel": "Steifigkeiten", "folie": "12–13", "formel": ["I_S = \\dfrac{d_s^4}{12}, \\quad I_R = \\dfrac{\\beta\\,l_2\\,h^3}{12}, \\quad c = \\dfrac{l\\,I_S}{h_S\\,I_R}"],
          "einsetzen": [r"I_S = \dfrac{(#ds:2#\,\mathrm{m})^4}{12} = #ISe:2# \cdot 10^{-4}\,\mathrm{m^4}, \qquad I_R = \dfrac{#be:3# \cdot #l2:2#\,\mathrm{m} \cdot (#h:2#\,\mathrm{m})^3}{12} = #IRe:2# \cdot 10^{-4}\,\mathrm{m^4}",
                        r"c = \dfrac{#l:2#\,\mathrm{m} \cdot #ISe:2#}{#hs:2#\,\mathrm{m} \cdot #IRe:2#} = #c:3#"],
          "werte": [{"id": "ISe", "expr": "ds**4/12*1e4", "d": 2}, {"id": "IRe", "expr": "be*l2*h**3/12*1e4", "d": 2},
                    {"id": "c", "expr": "l*ISe/(hs*IRe)", "d": 3, "frage": True, "label": "c", "einheit": "–"}]},
         {"titel": "Randmoment", "folie": "13", "formel": ["M_{R,d} = \\dfrac{c_o + c_u}{1 + c_o + c_u}\\,M^{(0)}_{Rd}"],
          "einsetzen": [r"M_{R,d} = \dfrac{2 \cdot #c:3#}{1 + 2 \cdot #c:3#} \cdot (#M0:1#\,\mathrm{kNm}) = #MR:1#\,\mathrm{kNm}"],
          "werte": [{"id": "MR", "expr": "2*c/(1 + 2*c)*M0", "d": 1, "frage": True, "label": "M_{R,d}", "einheit": "kNm"}]},
     ]},
    {"titel": "Stützenkraft und Mindestmoment", "teil": T,
     "text": "Gleichmäßiges Stützenraster mit $l_x = #lx:2#\\,\\mathrm{m}$ (vier Felder) und $l_y = #ly:2#\\,\\mathrm{m}$ (drei Felder), $g_d + q_d = #p:1#\\,\\mathrm{kN/m^2}$. Die Lastscheiden liegen bei den Querkraft-Nulldurchgängen unter Volllast (Vierfeldträger: $0{,}393\\,l$ / $0{,}607\\,l$ / $0{,}536\\,l$; Dreifeldträger: $0{,}4\\,l$ / $0{,}6\\,l$ / $0{,}5\\,l$). Bestimmen Sie für die Innenstütze am ersten Innenfeld in beiden Richtungen die Einzugsfläche, die Stützenkraft und das Mindestmoment.",
     "params": {"lx": {"min": 3.5, "max": 6.0, "step": 0.25}, "ly": {"min": 4.0, "max": 7.0, "step": 0.25}, "p": {"min": 14.0, "max": 24.0, "step": 0.5}},
     "schritte": [
         {"titel": "Einzugsbreiten", "folie": "27", "text": "Erstes Innenauflager: links der Nulldurchgang im Endfeld, rechts im ersten Innenfeld.",
          "formel": ["a_x = (0{,}607 + 0{,}536)\\,l_x, \\qquad a_y = (0{,}6 + 0{,}5)\\,l_y"],
          "einsetzen": [r"a_x = 1{,}143 \cdot #lx:2#\,\mathrm{m} = #ax:2#\,\mathrm{m}, \qquad a_y = 1{,}1 \cdot #ly:2#\,\mathrm{m} = #ay:2#\,\mathrm{m}"],
          "werte": [{"id": "ax", "expr": "1.143*lx", "d": 2, "frage": True, "label": "a_x", "einheit": "m"}, {"id": "ay", "expr": "1.1*ly", "d": 2}]},
         {"titel": "Einzugsfläche und Stützenkraft", "folie": "26–28", "formel": ["A = a_x\\,a_y, \\qquad V_{Ed} = A\\,(g_d + q_d)"],
          "einsetzen": [r"A = #ax:2#\,\mathrm{m} \cdot #ay:2#\,\mathrm{m} = #A:1#\,\mathrm{m^2}", r"V_{Ed} = #A:1#\,\mathrm{m^2} \cdot #p:1#\,\mathrm{kN/m^2} = #V:1#\,\mathrm{kN}"],
          "werte": [{"id": "A", "expr": "ax*ay", "d": 1, "frage": True, "label": "A", "einheit": "m²"},
                    {"id": "V", "expr": "A*p", "d": 1, "frage": True, "label": "V_{Ed}", "einheit": "kN"}]},
         {"titel": "Mindestmoment", "folie": "30", "formel": ["|m_{Ed,\\min}| = 0{,}125\\,V_{Ed}"],
          "einsetzen": [r"|m_{Ed,\min}| = 0{,}125 \cdot #V:1#\,\mathrm{kN} = #mmin:1#\,\mathrm{kNm/m}"],
          "werte": [{"id": "mmin", "expr": "0.125*V", "d": 1, "frage": True, "label": "|m_{Ed,\\min}|", "einheit": "kNm/m"}]},
     ]},
]


def main():
    d = json.loads(ZIEL.read_text(encoding="utf-8"))
    alt = lambda L: [x for x in L if x.get("teil") != T]
    d["teile"] = [x for x in d.get("teile", []) if x["id"] != T] + [TEIL]
    d["karten"] = alt(d.get("karten", [])) + [{"v": v, "r": r, "folie": f, "teil": T} for f, v, r in KARTEN]
    d["formeln"] = alt(d.get("formeln", [])) + [{**x, "teil": T} for x in FORMELN]
    d["paare"] = alt(d.get("paare", [])) + [{"a": a, "b": b, "folie": f, "teil": T} for a, b, f in PAARE]
    d["quiz"] = alt(d.get("quiz", [])) + QUIZ
    d["aufgaben"] = alt(d.get("aufgaben", [])) + AUFGABEN
    d["mindmap"]["c"] = [c for c in d["mindmap"]["c"] if not c["t"].startswith("Teil 2")] + [MINDMAP]
    d["statusText"] = "Skript Teil 1 und 2 sind eingearbeitet – Folien wie im Skript. Weitere Teile folgen."
    ZIEL.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Flachdecken Teil 2: {len(QUIZ)} Quizfragen, {len(KARTEN)} Karten, {len(FORMELN)} Formeln, {len(PAARE)} Paare, {len(AUFGABEN)} Aufgaben")


if __name__ == "__main__":
    main()
