"""Buchbeispiel Flachdecken: Schnittgrößen mit Ersatzrahmen- und Gurtstreifenverfahren (Thema 2).

Quelle: Finckh, Stahlbetonkonstruktion (Springer Vieweg 2023), Kap. Flachdecken, Beispiel S. 274–286,
wie im Vorlesungsskript Betonbau IV, Flachdecken Teil 2 (Folien 3–31). Texte eigene Formulierungen.
Momentenbeiwerte für Drei- bzw. Vierfeldträger mit gleichen Stützweiten, Verteilungsfaktoren nach DAfStb-Heft 631.
Biegebemessung mit der mb-Bemessungstafel (μ_Eds auf die nächste Zeile gerundet, keine Interpolation).

Aufruf: python tools/buch_flachdecke.py  (schreibt "buchbeispiele" in content/02_flachdecken.json)
"""
import json
from pathlib import Path

ZIEL = Path(__file__).resolve().parent.parent / "content" / "02_flachdecken.json"
OK, NICHT = r"\quad\checkmark", r"\quad\text{nicht erfüllt}"


def chk(bed, ja=OK, nein=NICHT):
    return [{"wenn": bed, "t": ja}, {"wenn": f"!({bed})", "t": nein}]


A0 = "2.1 Eingangswerte"
R1 = "2.2 Erste Tragrichtung: Dreifeldträger in l_y"
R2 = "2.3 Zweite Tragrichtung: Vierfeldträger in l_x"
ST = "2.4 Stützenkräfte und Mindestmomente"
SK = "Skript Flachdecken Teil 2"
kN2 = r"\,\mathrm{kN/m^2}"


def biege(pre, m, d, titel, seite, folie, text=""):
    """Biegebemessung je Meter mit der mb-Tafel (Zeile ab 0,005 aufgerundet)"""
    return {"abschnitt": None, "seite": seite, "titel": titel, "skript": f"{SK}, Folie {folie}",
            "frage": f"Bemesse den Plattenstreifen $b = 1{{,}}0\\,\\mathrm{{m}}$ für $|m_{{Ed}}| = #{m}:1#\\,\\mathrm{{kNm/m}}$.",
            "text": text + " μ_Eds wird auf die nächste Zeile der mb-Tafel gerundet (ab 0,005 auf).",
            "formel": [r"\mu_{Eds} = \dfrac{|m_{Ed}|}{f_{cd}\,b\,d^2}, \qquad a_s = \dfrac{\omega\,b\,d\,f_{cd}}{f_{yd}}"],
            "einsetzen": [rf"\mu_{{Eds}} = \dfrac{{#{pre}mn:4#\,\mathrm{{MNm/m}}}}{{#fcd:1#\,\mathrm{{MN/m^2}} \cdot 1{{,}}0\,\mathrm{{m}} \cdot (#{d}:3#\,\mathrm{{m}})^2}} = #{pre}mu:4# \;\rightarrow\; \text{{Zeile }} #{pre}Z:2#:\ \omega = #{pre}om:4#",
                          rf"a_s = \dfrac{{#{pre}om:4# \cdot 100\,\mathrm{{cm}} \cdot #{d}cm:1#\,\mathrm{{cm}} \cdot #fcd:1#\,\mathrm{{MN/m^2}}}}{{435\,\mathrm{{MN/m^2}}}} = #{pre}as:2#\,\mathrm{{cm^2/m}}"],
            "pruefen": [{"id": f"{pre}as", "label": "a_s", "einheit": "cm²/m"}],
            "werte": [{"id": f"{pre}mn", "expr": f"Math.abs({m})/1000", "d": 4}, {"id": f"{pre}mu", "expr": f"{pre}mn/(fcd*1.0*{d}*{d})", "d": 4},
                      {"id": f"{pre}Z", "expr": f"Math.min(Math.round({pre}mu*100 + 1e-9)/100, 0.37)", "d": 2},
                      {"id": f"{pre}om", "expr": f"tafelZeile({pre}Z).w", "d": 4},
                      {"id": f"{pre}as", "expr": f"{pre}om*100*{d}cm*fcd/435", "d": 2}]}


SCHRITTE = [
    {"abschnitt": A0, "seite": 4, "titel": "Anwendungsbedingung", "skript": f"{SK}, Folie 4; Teil 1, Folie 16",
     "frage": "Darf die Gurtstreifenmethode für dieses Stützenraster angewendet werden?",
     "formel": [r"0{,}8 \le \dfrac{l_x}{l_y} \le 1{,}25"],
     "einsetzen": [r"\dfrac{l_x}{l_y} = \dfrac{#lx:2#\,\mathrm{m}}{#ly:2#\,\mathrm{m}} = #v:3#", *chk("v >= 0.8 - 1e-9 && v <= 1.25 + 1e-9", r"\quad\checkmark\ \text{Gurtstreifenmethode anwendbar}", r"\quad\text{nicht anwendbar – genauer rechnen (FEM)}")],
     "pruefen": [{"id": "v", "label": "l_x/l_y", "einheit": ""}],
     "werte": [{"id": "fck", "expr": "FCK(beton)", "d": 0}, {"id": "v", "expr": "lx/ly", "d": 3}]},
    {"abschnitt": A0, "seite": 5, "titel": "Flächenlasten", "skript": f"{SK}, Folie 5–6",
     "frage": "Bestimme die Eigenlast der Platte und die Bemessungswerte $g_d$ und $q_d$.",
     "text": "Wie im Skript wird $g_d$ auf eine Nachkommastelle gerundet weiterverwendet.",
     "formel": [r"g_{k,1} = 25\,\mathrm{kN/m^3} \cdot h", r"g_d = 1{,}35\,(g_{k,1} + g_{k,2}), \qquad q_d = 1{,}5\,q_k"],
     "einsetzen": [rf"g_{{k,1}} = 25\,\mathrm{{kN/m^3}} \cdot #h:2#\,\mathrm{{m}} = #gk1:2#{kN2}",
                   rf"g_d = 1{{,}}35 \cdot (#gk1:2# + #gk2:2#){kN2} = #gd0:2#{kN2} \approx #gd:1#{kN2}",
                   rf"q_d = 1{{,}}5 \cdot #qk:2#{kN2} = #qd:2#{kN2}, \qquad g_d + q_d = #p:2#{kN2}"],
     "pruefen": [{"id": "gd", "label": "g_d", "einheit": "kN/m²"}, {"id": "qd", "label": "q_d", "einheit": "kN/m²"}],
     "werte": [{"id": "gk1", "expr": "25*h", "d": 2}, {"id": "gd0", "expr": "1.35*(gk1 + gk2)", "d": 2}, {"id": "gd", "expr": "Math.round(gd0*10)/10", "d": 1},
               {"id": "qd", "expr": "1.5*qk", "d": 2}, {"id": "p", "expr": "gd + qd", "d": 2}]},
    {"abschnitt": A0, "seite": 7, "titel": "Statische Nutzhöhen", "skript": f"{SK}, Folie 7",
     "frage": "Bestimme die Nutzhöhen der beiden Bewehrungslagen (Stäbe Ø14, #xk#).",
     "formel": [r"d_x = h - c_{\min} - \Delta c_{dev} - \dfrac{\phi}{2}, \qquad d_y = d_x - \phi"],
     "einsetzen": [r"d_x = #hmm:0# - #cmin:0# - #dc:0# - \dfrac{14\,\mathrm{mm}}{2} = #dxmm:0#\,\mathrm{mm}",
                   r"d_y = #dxmm:0# - 14\,\mathrm{mm} = #dymm:0#\,\mathrm{mm}"],
     "pruefen": [{"id": "dxmm", "label": "d_x", "einheit": "mm"}, {"id": "dymm", "label": "d_y", "einheit": "mm"}],
     "werte": [{"id": "hmm", "expr": "h*1000", "d": 0}, {"id": "cmin", "expr": "Math.max(expo(xk).cdur, 14)", "d": 0}, {"id": "dc", "expr": "expo(xk).dc", "d": 0},
               {"id": "minC", "expr": "expo(xk).minC"},
               {"id": "dxmm", "expr": "hmm - cmin - dc - 7", "d": 0}, {"id": "dymm", "expr": "dxmm - 14", "d": 0},
               {"id": "dx", "expr": "dxmm/1000", "d": 3}, {"id": "dy", "expr": "dymm/1000", "d": 3},
               {"id": "dxcm", "expr": "dxmm/10", "d": 1}, {"id": "dycm", "expr": "dymm/10", "d": 1}]},

    # ---------------- erste Richtung
    {"abschnitt": R1, "seite": 9, "titel": "Feldmomente des Dreifeldträgers", "skript": f"{SK}, Folie 8–9",
     "frage": "Berechne die Feldmomente des Ersatzstreifens (Breite $l_x$) in den Feldern 1/3 und 2.",
     "text": "Ersatzsystem in Richtung $l_y$: Dreifeldträger mit gleichen Stützweiten; die $q$-Beiwerte erfassen die ungünstigen Laststellungen.",
     "formel": [r"M_{1} = M_{3} = (0{,}080\,g_d + 0{,}101\,q_d)\,l_x\,l_y^2", r"M_{2} = (0{,}025\,g_d + 0{,}075\,q_d)\,l_x\,l_y^2"],
     "einsetzen": [rf"M_1 = (0{{,}}080 \cdot #gd:1# + 0{{,}}101 \cdot #qd:2#){kN2} \cdot #lx:2#\,\mathrm{{m}} \cdot (#ly:2#\,\mathrm{{m}})^2 = #M1a:1#\,\mathrm{{kNm}}",
                   rf"M_2 = (0{{,}}025 \cdot #gd:1# + 0{{,}}075 \cdot #qd:2#){kN2} \cdot #lx:2#\,\mathrm{{m}} \cdot (#ly:2#\,\mathrm{{m}})^2 = #M2a:1#\,\mathrm{{kNm}}"],
     "pruefen": [{"id": "M1a", "label": "M_1", "einheit": "kNm"}, {"id": "M2a", "label": "M_2", "einheit": "kNm"}],
     "werte": [{"id": "M1a", "expr": "(0.08*gd + 0.101*qd)*lx*ly*ly", "d": 1}, {"id": "M2a", "expr": "(0.025*gd + 0.075*qd)*lx*ly*ly", "d": 1}]},
    {"abschnitt": R1, "seite": 10, "titel": "Innenstützmomente des Dreifeldträgers", "skript": f"{SK}, Folie 10",
     "frage": "Berechne das Moment über den Innenstützen B und C.",
     "formel": [r"M_B = M_C = -(0{,}100\,g_d + 0{,}117\,q_d)\,l_x\,l_y^2"],
     "einsetzen": [rf"M_B = -(0{{,}}100 \cdot #gd:1# + 0{{,}}117 \cdot #qd:2#){kN2} \cdot #lx:2#\,\mathrm{{m}} \cdot (#ly:2#\,\mathrm{{m}})^2 = #MBa:1#\,\mathrm{{kNm}}"],
     "pruefen": [{"id": "MBa", "label": "M_B", "einheit": "kNm"}],
     "werte": [{"id": "MBa", "expr": "-(0.10*gd + 0.117*qd)*lx*ly*ly", "d": 1}]},
    {"abschnitt": R1, "seite": 11, "titel": "Randmoment: Beiwerte und Volleinspannmoment", "skript": f"{SK}, Folie 11–12",
     "frage": "Bestimme $\\alpha$, $\\beta$ und das Volleinspannmoment am Deckenrand (Stützenabstand quer $l_2 = l_x$).",
     "formel": [r"\alpha = 0{,}5 + 3\,\dfrac{d_s}{l_2}, \qquad \beta = 0{,}2 + 4\,\dfrac{d_s}{l_2}", r"M^{(0)}_{Rd} = -\alpha\,(g_d + q_d)\,l_x\,\dfrac{l_y^2}{12}"],
     "einsetzen": [r"\alpha = 0{,}5 + 3 \cdot \dfrac{#ds:2#\,\mathrm{m}}{#lx:2#\,\mathrm{m}} = #al1:3#, \qquad \beta = 0{,}2 + 4 \cdot \dfrac{#ds:2#\,\mathrm{m}}{#lx:2#\,\mathrm{m}} = #be1:3#",
                   rf"M^{{(0)}}_{{Rd}} = -#al1:3# \cdot #p:2#{kN2} \cdot #lx:2#\,\mathrm{{m}} \cdot \dfrac{{(#ly:2#\,\mathrm{{m}})^2}}{{12}} = #M01:1#\,\mathrm{{kNm}}"],
     "pruefen": [{"id": "al1", "label": "\\alpha", "einheit": ""}, {"id": "M01", "label": "M^{(0)}_{Rd}", "einheit": "kNm"}],
     "werte": [{"id": "al1", "expr": "0.5 + 3*ds/lx", "d": 3}, {"id": "be1", "expr": "0.2 + 4*ds/lx", "d": 3}, {"id": "M01", "expr": "-al1*p*lx*ly*ly/12", "d": 1}]},
    {"abschnitt": R1, "seite": 12, "titel": "Randmoment über die Steifigkeiten", "skript": f"{SK}, Folie 12–13",
     "frage": "Berechne die Steifigkeiten von Stütze und mitwirkendem Plattenstreifen und das Randmoment.",
     "text": "Stütze oben und unten gleich lang ($h_S$); Stütze quadratisch $d_s/d_s$.",
     "formel": [r"I_S = \dfrac{d_s^4}{12}, \qquad b_m = \beta\,l_x, \qquad I_R = \dfrac{b_m\,h^3}{12}",
                r"c_o = c_u = \dfrac{l_y\,I_S}{h_S\,I_R}, \qquad M_{R,d} = \dfrac{c_o + c_u}{1 + c_o + c_u}\,M^{(0)}_{Rd}"],
     "einsetzen": [r"I_S = \dfrac{(#ds:2#\,\mathrm{m})^4}{12} = #ISe:2# \cdot 10^{-4}\,\mathrm{m^4}, \qquad b_m = #be1:3# \cdot #lx:2#\,\mathrm{m} = #bm1:2#\,\mathrm{m}",
                   r"I_R = \dfrac{#bm1:2#\,\mathrm{m} \cdot (#h:2#\,\mathrm{m})^3}{12} = #IR1e:1# \cdot 10^{-4}\,\mathrm{m^4}",
                   r"c = \dfrac{#ly:2#\,\mathrm{m} \cdot #ISe:2#}{#hs:2#\,\mathrm{m} \cdot #IR1e:1#} = #c1:3#",
                   r"M_{R,d} = \dfrac{2 \cdot #c1:3#}{1 + 2 \cdot #c1:3#} \cdot (#M01:1#\,\mathrm{kNm}) = #MR1:1#\,\mathrm{kNm}"],
     "pruefen": [{"id": "c1", "label": "c", "einheit": ""}, {"id": "MR1", "label": "M_{R,d}", "einheit": "kNm"}],
     "werte": [{"id": "ISe", "expr": "Math.pow(ds, 4)/12*1e4", "d": 2}, {"id": "bm1", "expr": "be1*lx", "d": 2},
               {"id": "IR1e", "expr": "bm1*h*h*h/12*1e4", "d": 1}, {"id": "c1", "expr": "ly*ISe/(hs*IR1e)", "d": 3},
               {"id": "MR1", "expr": "2*c1/(1 + 2*c1)*M01", "d": 1}]},
    {"abschnitt": R1, "seite": 14, "titel": "Momente je Meter auf Feld- und Gurtstreifen", "skript": f"{SK}, Folie 14; Teil 1, Folie 18–19",
     "frage": "Verteile Feld- und Stützmomente mit den Verteilungsfaktoren auf die Streifen (je Meter).",
     "text": "Moment je Meter = Faktor · Streifenmoment / Streifenbreite $l_x$. Feld: Gurt 1,25, Feld 0,84; Stütze: innerer Gurt 2,10, benachbarter Gurt 1,40, Feld 0,40.",
     "formel": [r"m = k \cdot \dfrac{M}{l_x}"],
     "einsetzen": [r"m_{F,Gurt} = 1{,}25 \cdot \dfrac{#M1a:1#\,\mathrm{kNm}}{#lx:2#\,\mathrm{m}} = #mFG1:1#\,\mathrm{kNm/m}, \qquad m_{F,Feld} = 0{,}84 \cdot \dfrac{#M1a:1#\,\mathrm{kNm}}{#lx:2#\,\mathrm{m}} = #mFF1:1#\,\mathrm{kNm/m}",
                   r"m_{S,Gurt} = 2{,}10 \cdot \dfrac{#MBa:1#\,\mathrm{kNm}}{#lx:2#\,\mathrm{m}} = #mSG1:1#\,\mathrm{kNm/m}, \qquad m_{S,Nachbar} = 1{,}40 \cdot \dfrac{#MBa:1#\,\mathrm{kNm}}{#lx:2#\,\mathrm{m}} = #mSN1:1#\,\mathrm{kNm/m}",
                   r"m_{S,Feld} = 0{,}40 \cdot \dfrac{#MBa:1#\,\mathrm{kNm}}{#lx:2#\,\mathrm{m}} = #mSF1:1#\,\mathrm{kNm/m}"],
     "pruefen": [{"id": "mFG1", "label": "m_{F,Gurt}", "einheit": "kNm/m"}, {"id": "mSG1", "label": "m_{S,Gurt}", "einheit": "kNm/m"}],
     "werte": [{"id": "mFG1", "expr": "1.25*M1a/lx", "d": 1}, {"id": "mFF1", "expr": "0.84*M1a/lx", "d": 1},
               {"id": "mSG1", "expr": "2.10*MBa/lx", "d": 1}, {"id": "mSN1", "expr": "1.40*MBa/lx", "d": 1}, {"id": "mSF1", "expr": "0.40*MBa/lx", "d": 1}]},
    {"abschnitt": R1, "seite": 15, "titel": "Bemessungswerte der Baustoffe", "skript": f"{SK}, Folie 15",
     "frage": "Bestimme $f_{cd}$ für #beton#.", "text": "Wie im Skript auf 0,1 MN/m² gerundet.",
     "formel": [r"f_{cd} = 0{,}85 \cdot \dfrac{f_{ck}}{1{,}5}, \qquad f_{yd} = \sigma_{sd} = 435\,\mathrm{MN/m^2}"],
     "einsetzen": [r"f_{cd} = 0{,}85 \cdot \dfrac{#fck:0#}{1{,}5} = #fcd:1#\,\mathrm{MN/m^2}"],
     "pruefen": [{"id": "fcd", "label": "f_{cd}", "einheit": "MN/m²"}],
     "werte": [{"id": "fcd", "expr": "Math.round(0.85*fck/1.5*10)/10", "d": 1}]},
    biege("b1", "mFG1", "dx", "Bewehrung im Feld, Gurtstreifen (unten)", 16, "16", "Positives Feldmoment → untere Bewehrung, Nutzhöhe $d_x$."),
    biege("b2", "mSG1", "dx", "Bewehrung an der Stütze, Gurtstreifen (oben)", 17, "17", "Negatives Stützmoment → obere Bewehrung entlang der Stützenachse, Nutzhöhe $d_x$."),

    # ---------------- zweite Richtung
    {"abschnitt": R2, "seite": 20, "titel": "Feldmomente des Vierfeldträgers", "skript": f"{SK}, Folie 19–20",
     "frage": "Berechne die Feldmomente des Ersatzstreifens (Breite $l_y$) in den Feldern 1/4 und 2/3.",
     "formel": [r"M_{1} = M_{4} = (0{,}077\,g_d + 0{,}100\,q_d)\,l_y\,l_x^2", r"M_{2} = M_{3} = (0{,}036\,g_d + 0{,}080\,q_d)\,l_y\,l_x^2"],
     "einsetzen": [rf"M_1 = (0{{,}}077 \cdot #gd:1# + 0{{,}}100 \cdot #qd:2#){kN2} \cdot #ly:2#\,\mathrm{{m}} \cdot (#lx:2#\,\mathrm{{m}})^2 = #M1b:1#\,\mathrm{{kNm}}",
                   rf"M_2 = (0{{,}}036 \cdot #gd:1# + 0{{,}}080 \cdot #qd:2#){kN2} \cdot #ly:2#\,\mathrm{{m}} \cdot (#lx:2#\,\mathrm{{m}})^2 = #M2b:1#\,\mathrm{{kNm}}"],
     "pruefen": [{"id": "M1b", "label": "M_1", "einheit": "kNm"}],
     "werte": [{"id": "M1b", "expr": "(0.077*gd + 0.100*qd)*ly*lx*lx", "d": 1}, {"id": "M2b", "expr": "(0.036*gd + 0.080*qd)*ly*lx*lx", "d": 1}]},
    {"abschnitt": R2, "seite": 21, "titel": "Innenstützmomente des Vierfeldträgers", "skript": f"{SK}, Folie 21",
     "frage": "Berechne die Momente über den Stützen B/D und über der Mittelstütze C.",
     "formel": [r"M_B = M_D = -(0{,}107\,g_d + 0{,}121\,q_d)\,l_y\,l_x^2", r"M_C = -(0{,}071\,g_d + 0{,}107\,q_d)\,l_y\,l_x^2"],
     "einsetzen": [rf"M_B = -(0{{,}}107 \cdot #gd:1# + 0{{,}}121 \cdot #qd:2#){kN2} \cdot #ly:2#\,\mathrm{{m}} \cdot (#lx:2#\,\mathrm{{m}})^2 = #MBb:1#\,\mathrm{{kNm}}",
                   rf"M_C = -(0{{,}}071 \cdot #gd:1# + 0{{,}}107 \cdot #qd:2#){kN2} \cdot #ly:2#\,\mathrm{{m}} \cdot (#lx:2#\,\mathrm{{m}})^2 = #MCb:1#\,\mathrm{{kNm}}"],
     "pruefen": [{"id": "MBb", "label": "M_B", "einheit": "kNm"}],
     "werte": [{"id": "MBb", "expr": "-(0.107*gd + 0.121*qd)*ly*lx*lx", "d": 1}, {"id": "MCb", "expr": "-(0.071*gd + 0.107*qd)*ly*lx*lx", "d": 1}]},
    {"abschnitt": R2, "seite": 22, "titel": "Randmoment des Vierfeldträgers", "skript": f"{SK}, Folie 22",
     "frage": "Bestimme das Randmoment in der zweiten Richtung (Stützenabstand quer $l_2 = l_y$, Spannweite $l_x$).",
     "formel": [r"\alpha = 0{,}5 + 3\,\dfrac{d_s}{l_y}, \quad \beta = 0{,}2 + 4\,\dfrac{d_s}{l_y}, \quad M^{(0)}_{Rd} = -\alpha\,(g_d + q_d)\,l_y\,\dfrac{l_x^2}{12}",
                r"I_R = \dfrac{\beta\,l_y\,h^3}{12}, \quad c = \dfrac{l_x\,I_S}{h_S\,I_R}, \quad M_{R,d} = \dfrac{2c}{1 + 2c}\,M^{(0)}_{Rd}"],
     "einsetzen": [r"\alpha = 0{,}5 + 3 \cdot \dfrac{#ds:2#}{#ly:2#} = #al2:3#, \qquad \beta = 0{,}2 + 4 \cdot \dfrac{#ds:2#}{#ly:2#} = #be2:3#",
                   rf"M^{{(0)}}_{{Rd}} = -#al2:3# \cdot #p:2#{kN2} \cdot #ly:2#\,\mathrm{{m}} \cdot \dfrac{{(#lx:2#\,\mathrm{{m}})^2}}{{12}} = #M02:1#\,\mathrm{{kNm}}",
                   r"I_R = \dfrac{#be2:3# \cdot #ly:2#\,\mathrm{m} \cdot (#h:2#\,\mathrm{m})^3}{12} = #IR2e:1# \cdot 10^{-4}\,\mathrm{m^4}, \qquad c = \dfrac{#lx:2#\,\mathrm{m} \cdot #ISe:2#}{#hs:2#\,\mathrm{m} \cdot #IR2e:1#} = #c2:3#",
                   r"M_{R,d} = \dfrac{2 \cdot #c2:3#}{1 + 2 \cdot #c2:3#} \cdot (#M02:1#\,\mathrm{kNm}) = #MR2:1#\,\mathrm{kNm}"],
     "notiz": "Im Skript steht c ≈ 0,23 und M_R,d ≈ −28 kNm; dort wurde mit l = 5 m statt der Spannweite l_x = 4 m gerechnet. Mit l_x ergibt sich c ≈ 0,18 und M_R,d ≈ −24 kNm.",
     "pruefen": [{"id": "c2", "label": "c", "einheit": ""}, {"id": "MR2", "label": "M_{R,d}", "einheit": "kNm"}],
     "werte": [{"id": "al2", "expr": "0.5 + 3*ds/ly", "d": 3}, {"id": "be2", "expr": "0.2 + 4*ds/ly", "d": 3}, {"id": "M02", "expr": "-al2*p*ly*lx*lx/12", "d": 1},
               {"id": "IR2e", "expr": "be2*ly*h*h*h/12*1e4", "d": 1}, {"id": "c2", "expr": "lx*ISe/(hs*IR2e)", "d": 3}, {"id": "MR2", "expr": "2*c2/(1 + 2*c2)*M02", "d": 1}]},
    {"abschnitt": R2, "seite": 23, "titel": "Momente je Meter in der zweiten Richtung", "skript": f"{SK}, Folie 23",
     "frage": "Verteile Feld- und Stützmomente (Stütze B) auf die Streifen der Breite $l_y$.",
     "formel": [r"m = k \cdot \dfrac{M}{l_y}"],
     "einsetzen": [r"m_{F,Gurt} = 1{,}25 \cdot \dfrac{#M1b:1#\,\mathrm{kNm}}{#ly:2#\,\mathrm{m}} = #mFG2:1#\,\mathrm{kNm/m}, \qquad m_{F,Feld} = 0{,}84 \cdot \dfrac{#M1b:1#\,\mathrm{kNm}}{#ly:2#\,\mathrm{m}} = #mFF2:1#\,\mathrm{kNm/m}",
                   r"m_{S,Gurt} = 2{,}10 \cdot \dfrac{#MBb:1#\,\mathrm{kNm}}{#ly:2#\,\mathrm{m}} = #mSG2:1#\,\mathrm{kNm/m}, \qquad m_{S,Nachbar} = 1{,}40 \cdot \dfrac{#MBb:1#\,\mathrm{kNm}}{#ly:2#\,\mathrm{m}} = #mSN2:1#\,\mathrm{kNm/m}",
                   r"m_{S,Feld} = 0{,}40 \cdot \dfrac{#MBb:1#\,\mathrm{kNm}}{#ly:2#\,\mathrm{m}} = #mSF2:1#\,\mathrm{kNm/m}"],
     "pruefen": [{"id": "mFG2", "label": "m_{F,Gurt}", "einheit": "kNm/m"}, {"id": "mSG2", "label": "m_{S,Gurt}", "einheit": "kNm/m"}],
     "werte": [{"id": "mFG2", "expr": "1.25*M1b/ly", "d": 1}, {"id": "mFF2", "expr": "0.84*M1b/ly", "d": 1},
               {"id": "mSG2", "expr": "2.10*MBb/ly", "d": 1}, {"id": "mSN2", "expr": "1.40*MBb/ly", "d": 1}, {"id": "mSF2", "expr": "0.40*MBb/ly", "d": 1}]},
    {"abschnitt": R2, "seite": 24, "titel": "Bewehrung in der zweiten Richtung", "skript": f"{SK}, Folie 24",
     "frage": "Bestimme die Bewehrung je Meter für alle fünf Bereiche mit $d_y$.",
     "text": "Feldmomente → unten, Stützmomente → oben. μ_Eds jeweils auf die nächste Zeile der mb-Tafel gerundet.",
     "formel": [r"\mu_{Eds} = \dfrac{|m_{Ed}|}{f_{cd}\,b\,d_y^2} \;\rightarrow\; \omega, \qquad a_s = \dfrac{\omega\,b\,d_y\,f_{cd}}{f_{yd}}"],
     "einsetzen": [r"\text{Feld, Gurtstreifen: } #mFG2:1# \to \mu = #t1mu:3# \to #t1Z:2#,\ \omega = #t1om:4# \;\Rightarrow\; a_s = #t1as:2#\,\mathrm{cm^2/m}",
                   r"\text{Feld, Feldstreifen: } #mFF2:1# \to \mu = #t2mu:3# \to #t2Z:2#,\ \omega = #t2om:4# \;\Rightarrow\; a_s = #t2as:2#\,\mathrm{cm^2/m}",
                   r"\text{Stütze, Gurtstreifen: } #mSG2:1# \to \mu = #t3mu:3# \to #t3Z:2#,\ \omega = #t3om:4# \;\Rightarrow\; a_s = #t3as:2#\,\mathrm{cm^2/m}",
                   r"\text{Stütze, Nachbarstreifen: } #mSN2:1# \to \mu = #t4mu:3# \to #t4Z:2#,\ \omega = #t4om:4# \;\Rightarrow\; a_s = #t4as:2#\,\mathrm{cm^2/m}",
                   r"\text{Stütze, Feldstreifen: } #mSF2:1# \to \mu = #t5mu:3# \to #t5Z:2#,\ \omega = #t5om:4# \;\Rightarrow\; a_s = #t5as:2#\,\mathrm{cm^2/m}"],
     "notiz": "Das Skript liest ω feiner ab (z. B. 3,2 / 2,2 / 7,2 / 4,8 / 1,3 cm²/m). Mit dem 0,01-Raster der mb-Tafel weichen kleine Momente etwas ab.",
     "pruefen": [{"id": "t3as", "label": "a_{s,Stütze,Gurt}", "einheit": "cm²/m"}],
     "werte": [w for i, m in enumerate(["mFG2", "mFF2", "mSG2", "mSN2", "mSF2"], 1) for w in (
         {"id": f"t{i}mu", "expr": f"Math.abs({m})/1000/(fcd*dy*dy)", "d": 3},
         {"id": f"t{i}Z", "expr": f"Math.max(0.01, Math.min(Math.round(t{i}mu*100 + 1e-9)/100, 0.37))", "d": 2},
         {"id": f"t{i}om", "expr": f"tafelZeile(t{i}Z).w", "d": 4},
         {"id": f"t{i}as", "expr": f"t{i}om*100*dycm*fcd/435", "d": 2})]},

    # ---------------- Stützen
    {"abschnitt": ST, "seite": 27, "titel": "Lasteinzugsflächen", "skript": f"{SK}, Folie 26–28",
     "frage": "Bestimme die Einzugsflächen von Innenstütze S-B-2, Randstütze S-B-1 und Eckstütze S-A-1.",
     "text": "Lastscheiden an den Querkraft-Nulldurchgängen unter Volllast: Vierfeldträger ($l_x$) bei $0{,}393\\,l$ / $0{,}607\\,l$ / $0{,}536\\,l$, Dreifeldträger ($l_y$) bei $0{,}4\\,l$ / $0{,}6\\,l$ / $0{,}5\\,l$. Am Rand kommt der Plattenüberstand $d_s/2$ hinzu.",
     "formel": [r"A_{B2} = (0{,}607 + 0{,}536)\,l_x \cdot (0{,}6 + 0{,}5)\,l_y",
                r"A_{B1} = (0{,}393\,l_x + \tfrac{d_s}{2}) \cdot 1{,}1\,l_y, \qquad A_{A1} = (0{,}393\,l_x + \tfrac{d_s}{2}) \cdot (0{,}4\,l_y + \tfrac{d_s}{2})"],
     "einsetzen": [r"A_{B2} = #axI:2#\,\mathrm{m} \cdot #ayI:2#\,\mathrm{m} = #AI:1#\,\mathrm{m^2}",
                   r"A_{B1} = #axR:2#\,\mathrm{m} \cdot #ayI:2#\,\mathrm{m} = #AR:1#\,\mathrm{m^2}",
                   r"A_{A1} = #axR:2#\,\mathrm{m} \cdot #ayR:2#\,\mathrm{m} = #AE:1#\,\mathrm{m^2}"],
     "pruefen": [{"id": "AI", "label": "A_{B2}", "einheit": "m²"}, {"id": "AR", "label": "A_{B1}", "einheit": "m²"}, {"id": "AE", "label": "A_{A1}", "einheit": "m²"}],
     "werte": [{"id": "axI", "expr": "1.143*lx", "d": 2}, {"id": "ayI", "expr": "1.1*ly", "d": 2}, {"id": "axR", "expr": "0.393*lx + ds/2", "d": 2},
               {"id": "ayR", "expr": "0.4*ly + ds/2", "d": 2}, {"id": "AI", "expr": "axI*ayI", "d": 1}, {"id": "AR", "expr": "axR*ayI", "d": 1}, {"id": "AE", "expr": "axR*ayR", "d": 1}]},
    {"abschnitt": ST, "seite": 28, "titel": "Stützenkräfte", "skript": f"{SK}, Folie 26–28",
     "frage": "Berechne die Stützenkräfte aus den Einzugsflächen.",
     "formel": [r"V_{Ed} = A_{Einzug}\,(g_d + q_d)"],
     "einsetzen": [rf"V_{{Ed,B2}} = #AI:1#\,\mathrm{{m^2}} \cdot #p:2#{kN2} = #VI:1#\,\mathrm{{kN}}",
                   rf"V_{{Ed,B1}} = #AR:1#\,\mathrm{{m^2}} \cdot #p:2#{kN2} = #VR:1#\,\mathrm{{kN}}",
                   rf"V_{{Ed,A1}} = #AE:1#\,\mathrm{{m^2}} \cdot #p:2#{kN2} = #VE:1#\,\mathrm{{kN}}"],
     "pruefen": [{"id": "VI", "label": "V_{Ed,B2}", "einheit": "kN"}],
     "werte": [{"id": "VI", "expr": "AI*p", "d": 1}, {"id": "VR", "expr": "AR*p", "d": 1}, {"id": "VE", "expr": "AE*p", "d": 1}]},
    {"abschnitt": ST, "seite": 30, "titel": "Mindestmomente an den Stützen", "skript": f"{SK}, Folie 29–31",
     "frage": "Bestimme die Mindestmomente und vergleiche an der Innenstütze mit den Momenten aus dem Ersatzrahmen.",
     "text": "Verglichen wird mit dem Moment im benachbarten Gurtstreifen der jeweiligen Richtung.",
     "formel": [r"m_{Ed,\min} = \eta\,V_{Ed} \qquad (\text{Innen } 0{,}125;\ \text{Rand } 0{,}25 / 0{,}125;\ \text{Ecke } 0{,}50)"],
     "einsetzen": [r"\text{Innenstütze: } |m_{Ed,\min}| = 0{,}125 \cdot #VI:1#\,\mathrm{kN} = #mmI:1#\,\mathrm{kNm/m}",
                   r"\text{1. Richtung: } |m_{S,Nachbar}| = #mSN1a:1#\,\mathrm{kNm/m}",
                   {"wenn": "mSN1a >= mmI", "t": r"\quad\Rightarrow\ \text{Mindestmoment nicht maßgebend}"},
                   {"wenn": "mSN1a < mmI", "t": r"\quad\Rightarrow\ \text{Mindestmoment maßgebend – Bewehrung erhöhen}"},
                   r"\text{2. Richtung: } |m_{S,Nachbar}| = #mSN2a:1#\,\mathrm{kNm/m}",
                   {"wenn": "mSN2a >= mmI", "t": r"\quad\Rightarrow\ \text{Mindestmoment nicht maßgebend}"},
                   {"wenn": "mSN2a < mmI", "t": r"\quad\Rightarrow\ \text{Mindestmoment maßgebend – Bewehrung erhöhen}"},
                   r"\text{Randstütze: } 0{,}25 \cdot #VR:1#\,\mathrm{kN} = #mmR1:1#\,\mathrm{kNm/m}, \quad 0{,}125 \cdot #VR:1#\,\mathrm{kN} = #mmR2:1#\,\mathrm{kNm/m}",
                   r"\text{Eckstütze: } 0{,}50 \cdot #VE:1#\,\mathrm{kN} = #mmE:1#\,\mathrm{kNm/m}"],
     "notiz": "Das Skript nennt als Vergleichswerte etwa 74 kNm/m (1. Richtung) und etwa 59 kNm/m (2. Richtung); hier wird jeweils der benachbarte Gurtstreifen der Richtung verwendet.",
     "pruefen": [{"id": "mmI", "label": "|m_{Ed,\\min}|", "einheit": "kNm/m"}],
     "werte": [{"id": "mmI", "expr": "0.125*VI", "d": 1}, {"id": "mSN1a", "expr": "Math.abs(mSN1)", "d": 1}, {"id": "mSN2a", "expr": "Math.abs(mSN2)", "d": 1},
               {"id": "mmR1", "expr": "0.25*VR", "d": 1}, {"id": "mmR2", "expr": "0.125*VR", "d": 1}, {"id": "mmE", "expr": "0.5*VE", "d": 1}]},
]
for st in SCHRITTE:
    if st["abschnitt"] is None:
        st["abschnitt"] = R1

BEISPIEL = {
    "id": "flachdecke",
    "titel": "Flachdecke im Stützenraster",
    "untertitel": "Ersatzrahmen und Gurtstreifen: Momente, Bewehrung, Stützenkräfte",
    "quelle": "Finckh: Stahlbetonkonstruktion",
    "auflage": "Springer Vieweg 2023, Kap. Flachdecken",
    "abschnitt": "Beispiel S. 274–286",
    "kap": "2",
    "system": "flachdecke",
    "abb2": "Momente je Meter auf Feld- und Gurtstreifen",
    "aufgabe": ("Zwischengeschossdecke als Flachdecke auf einem regelmäßigen Stützenraster mit vier Feldern in $x$- und drei Feldern in $y$-Richtung. "
                "Mit dem Ersatzrahmen- und Gurtstreifenverfahren werden für beide Tragrichtungen Feld-, Stütz- und Randmomente bestimmt, "
                "auf Feld- und Gurtstreifen verteilt und bemessen. Abschließend werden die Stützenkräfte aus Lasteinzugsflächen und die Mindestmomente an den Stützen ermittelt."),
    "fest": [["Beton", "C30/37, XC3"], ["Raster", "4 Felder in x, 3 Felder in y"], ["Bewehrung", "B500, Ø14 in zwei Lagen"],
             ["Stützen", "quadratisch, oben und unten gleich lang"]],
    "eingaben": [
        {"id": "beton", "label": "Betonfestigkeitsklasse", "typ": "auswahl", "wert": "C30/37", "werte": ["C20/25", "C25/30", "C30/37", "C35/45", "C40/50"]},
        {"id": "xk", "label": "Expositionsklasse", "typ": "auswahl", "wert": "XC3", "werte": ["XC1", "XC2", "XC3", "XC4"]},
        {"id": "lx", "label": "Stützweite $l_x$", "einheit": "m", "wert": 4.0, "step": 0.05, "d": 2},
        {"id": "ly", "label": "Stützweite $l_y$", "einheit": "m", "wert": 5.0, "step": 0.05, "d": 2},
        {"id": "h", "label": "Plattendicke $h$", "einheit": "m", "wert": 0.30, "step": 0.01, "d": 2},
        {"id": "gk2", "label": "Ausbaulast $g_{k,2}$", "einheit": "kN/m²", "wert": 1.5, "step": 0.05, "d": 2},
        {"id": "qk", "label": "Nutzlast $q_k$", "einheit": "kN/m²", "wert": 5.0, "step": 0.1, "d": 2},
        {"id": "ds", "label": "Stützenbreite $d_s$", "einheit": "m", "wert": 0.30, "step": 0.01, "d": 2},
        {"id": "hs", "label": "Stützenlänge $h_S$", "einheit": "m", "wert": 3.0, "step": 0.05, "d": 2},
    ],
    "konstanten": {},
    "ergebnisse": [
        {"titel": "Stützmoment 1. Richtung", "wert": "MBa", "d": 0, "einheit": "kNm", "sub": "Gurtstreifen $#mSG1:1#\\,\\mathrm{kNm/m}$"},
        {"titel": "Bewehrung Stütze oben", "wert": "b2as", "d": 1, "einheit": "cm²/m", "sub": "Gurtstreifen, 1. Richtung"},
        {"titel": "Stützmoment 2. Richtung", "wert": "MBb", "d": 0, "einheit": "kNm", "sub": "Gurtstreifen $#mSG2:1#\\,\\mathrm{kNm/m}$"},
        {"titel": "Innenstütze S-B-2", "wert": "VI", "d": 0, "einheit": "kN", "sub": "$A = #AI:1#\\,\\mathrm{m^2}$"},
        {"titel": "Mindestmoment innen", "wert": "mmI", "d": 1, "einheit": "kNm/m", "sub": "$\\eta = 0{,}125$"},
    ],
    "schritte": SCHRITTE,
    "einheiten": {},
}


def main():
    d = json.loads(ZIEL.read_text(encoding="utf-8"))
    d["buchbeispiele"] = {"quelle": BEISPIEL["quelle"], "auflage": BEISPIEL["auflage"], "beispiele": [BEISPIEL]}
    ZIEL.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Buchbeispiel Flachdecke: {len(SCHRITTE)} Schritte")


if __name__ == "__main__":
    main()
