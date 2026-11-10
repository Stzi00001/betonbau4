"""Buchbeispiel Flachdecken: Schnittgrößenermittlung einer Flachdecke (Thema 2).

Quelle: Finckh, Stahlbetonkonstruktion (Springer Vieweg 2023), Abschn. 7.3 „Beispiel Schnittgrößenermittlung“,
S. 274–286; dasselbe Beispiel steht im Vorlesungsskript Betonbau IV, Flachdecken Teil 2 (Folien 3–31).
Aufbau und Bezeichnungen wie im Buch (ψ, λ, m_xx/m_yy, Gurt- und Feldstreifen), Texte in eigenen Worten.
Biegebemessung mit der mb-Bemessungstafel (μ_Eds auf die nächste Zeile gerundet, ab 0,005 auf, keine Interpolation).

Aufruf: python tools/buch_flachdecke.py  (schreibt "buchbeispiele" in content/02_flachdecken.json)
"""
import json
from pathlib import Path

ZIEL = Path(__file__).resolve().parent.parent / "content" / "02_flachdecken.json"
SK = "Skript Flachdecken Teil 2"
kN2 = r"\,\mathrm{kN/m^2}"
KNM = r"\,\mathrm{kNm}"
KNMM = r"\,\mathrm{kNm/m}"

A_SYS = "7.3.1 System"
A_ALL = "7.3.2.1 Gurtstreifenverfahren: Allgemeines"
A_Y = "7.3.2.2 Bewehrung in Y-Richtung (m_xx)"
A_X = "7.3.2.3 Bewehrung in X-Richtung (m_yy)"
A_Q = "7.3.3 Querkräfte"
A_M = "7.3.4 Mindestmomente"

# Verteilungsfaktoren nach Abb. 7.6 (DAfStb-Heft 631): Stütze innen / neben der Stütze / Feldstreifen; Feld Gurt / Feld
K_S = {"G": 2.10, "N": 1.40, "F": 0.50}
K_F = {"G": 1.25, "N": 1.25, "F": 0.84}


def zeile_tafel(mu):
    return f"Math.max(0.01, Math.min(Math.round(({mu})*100 + 1e-9)/100, 0.37))"


def streifen(ab, mid, k, M, l2, d, titel, seite, folie, mlabel, wo, notiz=None):
    """Moment je Meter im Streifen und Biegebemessung mit der mb-Tafel (ein Schritt wie im Buch)"""
    p = "a" + mid
    lage = "obere" if mid[1] == "S" else "untere"
    fk = f"{k:.2f}".rstrip("0").replace(".", "{,}")
    st = {"abschnitt": ab, "seite": seite, "titel": titel, "skript": f"{SK}, Folie {folie}",
          "frage": f"Bestimme das Moment je Meter {wo} und die erforderliche {lage} Bewehrung ($b = 1{{,}}0\\,\\mathrm{{m}}$, $d = #{d}cm:1#\\,\\mathrm{{cm}}$).",
          "text": "Moment je Meter = Verteilungsfaktor nach Abb. 7.6 · Moment des Ersatzträgers / Streifenbreite. μ_Eds wird auf die nächste Zeile der mb-Tafel gerundet.",
          "formel": [rf"{mlabel} = {fk} \cdot \dfrac{{M}}{{l_2}}",
                     r"\mu_{Eds} = \dfrac{|m_{Ed}|}{f_{cd}\,b\,d^2} \;\rightarrow\; \omega, \qquad a_s = \dfrac{1}{\sigma_{sd}}\,\omega\,b\,d\,f_{cd}"],
          "einsetzen": [rf"{mlabel} = {fk} \cdot \dfrac{{#{M}:1#{KNM}}}{{#{l2}:2#\,\mathrm{{m}}}} = #{mid}:1#{KNMM}",
                        rf"\mu_{{Eds}} = \dfrac{{#{p}mn:4#\,\mathrm{{MNm/m}}}}{{#fcd:1#\,\mathrm{{MN/m^2}} \cdot 1{{,}}0\,\mathrm{{m}} \cdot (#{d}:3#\,\mathrm{{m}})^2}} = #{p}mu:3# \;\rightarrow\; \text{{Zeile }} #{p}Z:2#:\ \omega = #{p}om:4#",
                        rf"a_s = \dfrac{{1}}{{435\,\mathrm{{MN/m^2}}}} \cdot #{p}om:4# \cdot 100\,\mathrm{{cm}} \cdot #{d}cm:1#\,\mathrm{{cm}} \cdot #fcd:1#\,\mathrm{{MN/m^2}} = #{p}as:2#\,\mathrm{{cm^2/m}}"],
          "pruefen": [{"id": mid, "label": mlabel, "einheit": "kNm/m"}, {"id": p + "as", "label": "a_s", "einheit": "cm²/m"}],
          "werte": [{"id": mid, "expr": f"{k}*{M}/{l2}", "d": 1}, {"id": p + "mn", "expr": f"Math.abs({mid})/1000", "d": 4},
                    {"id": p + "mu", "expr": f"{p}mn/(fcd*1.0*{d}*{d})", "d": 3}, {"id": p + "Z", "expr": zeile_tafel(p + "mu"), "d": 2},
                    {"id": p + "om", "expr": f"tafelZeile({p}Z).w", "d": 4}, {"id": p + "as", "expr": f"{p}om*100*{d}cm*fcd/435", "d": 2}]}
    if notiz:
        st["notiz"] = notiz
    return st


def uebersicht(ab, r, spalten, l2, d, titel, seite, folie, tab, notiz):
    """Tabelle wie Tab. 7.1 / 7.2: Momente des Ersatzsystems, je Meter in drei Streifen und Bewehrung"""
    werte, kopf, mom = [], [], []
    zeilen = {"G": [], "N": [], "F": []}
    bew = {"G": [], "N": [], "F": []}
    for name, M, art in spalten:
        kopf.append(r"\text{" + name + "}")
        mom.append(f"#{M}:0#")
        for z in "GNF":
            k = (K_S if art == "S" else K_F)[z]
            i = f"T{r}{name.replace('-', '')}{z}"
            werte.append({"id": i, "expr": f"{k}*{M}/{l2}", "d": 1})
            werte.append({"id": i + "as", "expr": f"tafelZeile({zeile_tafel(f'Math.abs({i})/1000/(fcd*{d}*{d})')}).w*100*{d}cm*fcd/435", "d": 1})
            zeilen[z].append(f"#{i}:1#")
            bew[z].append(f"#{i}as:1#")
    n = len(spalten)
    name = {"G": r"\text{Stütze}", "N": r"\text{neben Stütze}", "F": r"\text{Feld}"}
    arr = (r"\begin{array}{l|" + "r" * n + r"}" + r" & " + " & ".join(kopf) + r"\\ \hline"
           + r"\text{Ersatzsystem [kNm]} & " + " & ".join(mom) + r"\\ \hline"
           + "".join(name[z] + r"\ [\mathrm{kNm/m}] & " + " & ".join(zeilen[z]) + r"\\" for z in "GNF") + r"\hline"
           + "".join(name[z] + r"\ [\mathrm{cm^2/m}] & " + " & ".join(bew[z]) + r"\\" for z in "GNF") + r"\end{array}")
    return {"abschnitt": ab, "seite": seite, "titel": titel, "skript": f"{SK}, Folie {folie}",
            "frage": f"Stelle alle Momente je Meter und die Bewehrung der Richtung zusammen (wie {tab}).",
            "text": "Gleiches Vorgehen für Randmoment und Feld 2: Stützmomente mit 2,1 / 1,4 / 0,5, Feldmomente mit 1,25 / 0,84.",
            "formel": [], "einsetzen": [arr], "notiz": notiz, "werte": werte}


SCHRITTE = [
    # ---------------- 7.3.1 System
    {"abschnitt": A_SYS, "seite": 274, "titel": "Lasten und Bemessungswerte", "skript": f"{SK}, Folie 5–6",
     "frage": "Bestimme die Eigenlast der #h:2#-m-Decke und die Bemessungswerte $g_d$ und $q_d$.",
     "text": "Wie im Buch wird $g_d$ auf eine Nachkommastelle gerundet weiterverwendet.",
     "formel": [r"g_{k1} = 25\,\mathrm{kN/m^3} \cdot h, \qquad g_d = 1{,}35\,(g_{k1} + g_{k2}), \qquad q_d = 1{,}5\,q_k"],
     "einsetzen": [rf"g_{{k1}} = 25 \cdot #h:2# = #gk1:2#{kN2}",
                   rf"g_d = 1{{,}}35 \cdot (#gk1:2# + #gk2:2#) = #gd0:2# \approx #gd:1#{kN2}",
                   rf"q_d = 1{{,}}5 \cdot #qk:2# = #qd:2#{kN2}, \qquad g_d + q_d = #p:2#{kN2}"],
     "pruefen": [{"id": "gd", "label": "g_d", "einheit": "kN/m²"}, {"id": "qd", "label": "q_d", "einheit": "kN/m²"}],
     "werte": [{"id": "fck", "expr": "FCK(beton)", "d": 0}, {"id": "gk1", "expr": "25*h", "d": 2}, {"id": "gd0", "expr": "1.35*(gk1 + gk2)", "d": 2},
               {"id": "gd", "expr": "Math.round(gd0*10)/10", "d": 1}, {"id": "qd", "expr": "1.5*qk", "d": 2}, {"id": "p", "expr": "gd + qd", "d": 2}]},
    {"abschnitt": A_SYS, "seite": 275, "titel": "Statische Nutzhöhen", "skript": f"{SK}, Folie 7",
     "frage": "Bestimme die Nutzhöhen der beiden Bewehrungslagen ($\\phi_l = 14\\,\\mathrm{mm}$, #xk#).",
     "text": "Die Lage in $x$ liegt außen, die Lage in $y$ einen Stabdurchmesser weiter innen.",
     "formel": [r"d_x = h - c_{\min} - \Delta c_{dev} - \dfrac{\phi_l}{2}, \qquad d_y = h - c_{\min} - \Delta c_{dev} - \phi_l - \dfrac{\phi_l}{2}"],
     "einsetzen": [r"d_x = #hmm:0# - #cmin:0# - #dc:0# - \dfrac{14}{2} = #dxmm:0#\,\mathrm{mm}",
                   r"d_y = #hmm:0# - #cmin:0# - #dc:0# - 14 - \dfrac{14}{2} = #dymm:0#\,\mathrm{mm}"],
     "pruefen": [{"id": "dxmm", "label": "d_x", "einheit": "mm"}, {"id": "dymm", "label": "d_y", "einheit": "mm"}],
     "werte": [{"id": "hmm", "expr": "h*1000", "d": 0}, {"id": "cmin", "expr": "Math.max(expo(xk).cdur, 14)", "d": 0}, {"id": "dc", "expr": "expo(xk).dc", "d": 0},
               {"id": "dxmm", "expr": "hmm - cmin - dc - 7", "d": 0}, {"id": "dymm", "expr": "dxmm - 14", "d": 0},
               {"id": "dx", "expr": "dxmm/1000", "d": 3}, {"id": "dy", "expr": "dymm/1000", "d": 3},
               {"id": "dxcm", "expr": "dxmm/10", "d": 1}, {"id": "dycm", "expr": "dymm/10", "d": 1}]},

    # ---------------- 7.3.2.1 Allgemeines
    {"abschnitt": A_ALL, "seite": 275, "titel": "Anwendungsgrenze", "skript": f"{SK}, Folie 4; Teil 1, Folie 16",
     "frage": "Darf das Gurtstreifenverfahren nach DAfStb-Heft 631 angewendet werden?",
     "formel": [r"0{,}8 \le \dfrac{l_x}{l_y} \le 1{,}25"],
     "einsetzen": [r"\dfrac{l_x}{l_y} = \dfrac{#lx:2#}{#ly:2#} = #v:3#",
                   {"wenn": "v >= 0.8 - 1e-9 && v <= 1.25 + 1e-9", "t": r"\quad\checkmark\ \text{Anwendungsgrenzen eingehalten}"},
                   {"wenn": "!(v >= 0.8 - 1e-9 && v <= 1.25 + 1e-9)", "t": r"\quad\text{nicht eingehalten – Schnittgrößen genauer ermitteln (z. B. FEM)}"}],
     "pruefen": [{"id": "v", "label": "l_x/l_y", "einheit": ""}],
     "werte": [{"id": "v", "expr": "lx/ly", "d": 3}]},
    {"abschnitt": A_ALL, "seite": 277, "titel": "Bemessungswert der Betondruckfestigkeit", "skript": f"{SK}, Folie 15",
     "frage": "Bestimme $f_{cd}$ für #beton#.", "text": "Wie im Buch auf 0,1 MN/m² gerundet; $\\sigma_{sd} = 435\\,\\mathrm{MN/m^2}$.",
     "formel": [r"f_{cd} = \alpha_{cc}\,\dfrac{f_{ck}}{\gamma_c} = 0{,}85 \cdot \dfrac{f_{ck}}{1{,}5}"],
     "einsetzen": [r"f_{cd} = 0{,}85 \cdot \dfrac{#fck:0#}{1{,}5} = #fcd:1#\,\mathrm{MN/m^2}"],
     "pruefen": [{"id": "fcd", "label": "f_{cd}", "einheit": "MN/m²"}],
     "werte": [{"id": "fcd", "expr": "Math.round(0.85*fck/1.5*10)/10", "d": 1}]},

    # ---------------- 7.3.2.2 Y-Richtung
    {"abschnitt": A_Y, "seite": 275, "titel": "Feldmomente des Dreifeldträgers", "skript": f"{SK}, Folie 8–9",
     "frage": "Berechne die Feldmomente des Ersatzträgers in $y$-Richtung (Breite $l_x$) für Feld 1/3 und Feld 2.",
     "text": "Tabellenbeiwerte für den Dreifeldträger mit gleichen Stützweiten; die $q$-Beiwerte enthalten die ungünstige feldweise Laststellung.",
     "formel": [r"M_{1Ed} = M_{3Ed} = (0{,}080\,g_d + 0{,}101\,q_d)\,l_x\,l_y^2", r"M_{2Ed} = (0{,}025\,g_d + 0{,}075\,q_d)\,l_x\,l_y^2"],
     "einsetzen": [rf"M_{{1Ed}} = (0{{,}}08 \cdot #gd:1# + 0{{,}}101 \cdot #qd:2#) \cdot #lx:2# \cdot #ly:2#^2 = #M1a:1#{KNM}",
                   rf"M_{{2Ed}} = (0{{,}}025 \cdot #gd:1# + 0{{,}}075 \cdot #qd:2#) \cdot #lx:2# \cdot #ly:2#^2 = #M2a:1#{KNM}"],
     "pruefen": [{"id": "M1a", "label": "M_{1Ed}", "einheit": "kNm"}, {"id": "M2a", "label": "M_{2Ed}", "einheit": "kNm"}],
     "werte": [{"id": "M1a", "expr": "(0.08*gd + 0.101*qd)*lx*ly*ly", "d": 1}, {"id": "M2a", "expr": "(0.025*gd + 0.075*qd)*lx*ly*ly", "d": 1}]},
    {"abschnitt": A_Y, "seite": 275, "titel": "Stützmoment über den Mittelstützen", "skript": f"{SK}, Folie 10",
     "frage": "Berechne das Stützmoment über den Stützen B und C.",
     "formel": [r"M_{BEd} = M_{CEd} = -(0{,}100\,g_d + 0{,}117\,q_d)\,l_x\,l_y^2"],
     "einsetzen": [rf"M_{{BEd}} = -(0{{,}}10 \cdot #gd:1# + 0{{,}}117 \cdot #qd:2#) \cdot #lx:2# \cdot #ly:2#^2 = #MBa:1#{KNM}"],
     "pruefen": [{"id": "MBa", "label": "M_{BEd}", "einheit": "kNm"}],
     "werte": [{"id": "MBa", "expr": "-(0.10*gd + 0.117*qd)*lx*ly*ly", "d": 1}]},
    {"abschnitt": A_Y, "seite": 276, "titel": "Randmoment: Beiwerte und Volleinspannmoment", "skript": f"{SK}, Folie 11–12",
     "frage": "Bestimme die Beiwerte $\\psi$ und $\\lambda$ (Stützweite quer $l_2 = l_x$) und das Volleinspannmoment am Deckenrand.",
     "text": "Das Randmoment des Ersatzrahmens wird mit dem $c_o$-$c_u$-Verfahren nach Heft 631 bestimmt.",
     "formel": [r"\psi = 0{,}5 + 3\,\dfrac{d_s}{l_2}, \qquad \lambda = 0{,}2 + 4\,\dfrac{d_s}{l_2}", r"M^{(0)}_{Rd} = -\psi\,(g + q)\,b_L\,\dfrac{l_1^2}{12}"],
     "einsetzen": [r"\psi = 0{,}5 + 3 \cdot \dfrac{#ds:2#}{#lx:2#} = #al1:3#, \qquad \lambda = 0{,}2 + 4 \cdot \dfrac{#ds:2#}{#lx:2#} = #be1:3#",
                   rf"M^{{(0)}}_{{Rd}} = -#al1:3# \cdot #p:2# \cdot #lx:2# \cdot \dfrac{{#ly:2#^2}}{{12}} = #M01:1#{KNM}"],
     "pruefen": [{"id": "al1", "label": "\\psi", "einheit": ""}, {"id": "M01", "label": "M^{(0)}_{Rd}", "einheit": "kNm"}],
     "werte": [{"id": "al1", "expr": "0.5 + 3*ds/lx", "d": 3}, {"id": "be1", "expr": "0.2 + 4*ds/lx", "d": 3}, {"id": "M01", "expr": "-al1*p*lx*ly*ly/12", "d": 1}]},
    {"abschnitt": A_Y, "seite": 276, "titel": "Randmoment über die Steifigkeiten", "skript": f"{SK}, Folie 12–13",
     "frage": "Berechne Stützen- und Riegelsteifigkeit, die Verteilungsbeiwerte $c_o = c_u$ und das Randmoment.",
     "text": "Stütze oben und unten gleich lang ($h_S$). Der Riegel wirkt mit der Breite $b_m = \\lambda\\,l_2$ mit.",
     "formel": [r"I_S = \dfrac{d_s^4}{12}, \qquad b_m = \lambda\,l_2, \qquad I_R = \dfrac{b_m\,h^3}{12}",
                r"c_o = c_u = \dfrac{l_1\,I_S}{h_S\,I_R}, \qquad M_{R,d} = \dfrac{c_o + c_u}{1 + c_o + c_u}\,M^{(0)}_{Rd}"],
     "einsetzen": [r"I_S = \dfrac{#ds:2#^4}{12} = #ISe:2# \cdot 10^{-4}\,\mathrm{m^4}, \qquad b_m = #be1:3# \cdot #lx:2# = #bm1:2#\,\mathrm{m}",
                   r"I_R = \dfrac{#bm1:2# \cdot #h:2#^3}{12} = #IR1e:1# \cdot 10^{-4}\,\mathrm{m^4}, \qquad c_o = c_u = \dfrac{#ly:2# \cdot #ISe:2#}{#hs:2# \cdot #IR1e:1#} = #c1:3#",
                   rf"M_{{R,d}} = \dfrac{{2 \cdot #c1:3#}}{{1 + 2 \cdot #c1:3#}} \cdot (#M01:1#) = #MR1:1#{KNM}"],
     "pruefen": [{"id": "c1", "label": "c_o", "einheit": ""}, {"id": "MR1", "label": "M_{R,d}", "einheit": "kNm"}],
     "werte": [{"id": "ISe", "expr": "Math.pow(ds, 4)/12*1e4", "d": 2}, {"id": "bm1", "expr": "be1*lx", "d": 2},
               {"id": "IR1e", "expr": "bm1*h*h*h/12*1e4", "d": 1}, {"id": "c1", "expr": "ly*ISe/(hs*IR1e)", "d": 3},
               {"id": "MR1", "expr": "2*c1/(1 + 2*c1)*M01", "d": 1}]},
    streifen(A_Y, "mFG1", 1.25, "M1a", "lx", "dx", "Feld 1, Gurtstreifen", 277, "14–16", "m_{1xx,SG}", "im Gurtstreifen von Feld 1"),
    streifen(A_Y, "mFF1", 0.84, "M1a", "lx", "dx", "Feld 1, Feldstreifen", 277, "14–16", "m_{1xx,FG}", "im Feldstreifen (Mittelstreifen) von Feld 1"),
    streifen(A_Y, "mSG1", 2.10, "MBa", "lx", "dx", "Stütze B, Gurtstreifen an der Stütze", 277, "14, 17", "m_{Bxx,SG}", "im inneren Gurtstreifen über Stütze B"),
    streifen(A_Y, "mSN1", 1.40, "MBa", "lx", "dx", "Stütze B, Gurtstreifen neben der Stütze", 277, "14, 17", "m_{Bxx,SG2}", "im Gurtstreifen neben Stütze B",
             "Im Buch steht in der Formel versehentlich der Faktor 2,1; gerechnet ist mit 1,4 (−74 kNm/m)."),
    streifen(A_Y, "mSF1", 0.50, "MBa", "lx", "dx", "Stütze B, Feldstreifen", 278, "14, 17", "m_{Bxx,FG}", "im Feldstreifen über Stütze B",
             "Faktor 0,5 nach Abb. 7.6; die drei Streifen ergeben zusammen 0,2·2,1 + 0,2·1,4 + 0,6·0,5 = 1,0."),
    uebersicht(A_Y, "Y", [("MS-A", "MR1", "S"), ("MF-1", "M1a", "F"), ("MS-B", "MBa", "S"), ("MF-2", "M2a", "F")], "lx", "dx",
               "Zusammenstellung Y-Richtung", 278, "14–18", "Tab. 7.1",
               "Das Buch liest ω feiner ab als im 0,01-Raster der mb-Tafel; die Bewehrung weicht deshalb leicht ab (z. B. 5,2 statt 5,0 cm²/m)."),

    # ---------------- 7.3.2.3 X-Richtung
    {"abschnitt": A_X, "seite": 279, "titel": "Feldmomente des Vierfeldträgers", "skript": f"{SK}, Folie 19–20",
     "frage": "Berechne die Feldmomente des Ersatzträgers in $x$-Richtung (Breite $l_y$) für Feld 1/4 und Feld 2/3.",
     "formel": [r"M_{1Ed} = M_{4Ed} = (0{,}077\,g_d + 0{,}100\,q_d)\,l_y\,l_x^2", r"M_{2Ed} = M_{3Ed} = (0{,}036\,g_d + 0{,}080\,q_d)\,l_y\,l_x^2"],
     "einsetzen": [rf"M_{{1Ed}} = (0{{,}}077 \cdot #gd:1# + 0{{,}}100 \cdot #qd:2#) \cdot #ly:2# \cdot #lx:2#^2 = #M1b:1#{KNM}",
                   rf"M_{{2Ed}} = (0{{,}}036 \cdot #gd:1# + 0{{,}}080 \cdot #qd:2#) \cdot #ly:2# \cdot #lx:2#^2 = #M2b:1#{KNM}"],
     "pruefen": [{"id": "M1b", "label": "M_{1Ed}", "einheit": "kNm"}, {"id": "M2b", "label": "M_{2Ed}", "einheit": "kNm"}],
     "werte": [{"id": "M1b", "expr": "(0.077*gd + 0.100*qd)*ly*lx*lx", "d": 1}, {"id": "M2b", "expr": "(0.036*gd + 0.080*qd)*ly*lx*lx", "d": 1}]},
    {"abschnitt": A_X, "seite": 280, "titel": "Stützmomente des Vierfeldträgers", "skript": f"{SK}, Folie 21",
     "frage": "Berechne die Stützmomente über der Mittelstütze C und über den Stützen B und D.",
     "formel": [r"M_{CEd} = -(0{,}071\,g_d + 0{,}107\,q_d)\,l_y\,l_x^2", r"M_{BEd} = M_{DEd} = -(0{,}107\,g_d + 0{,}121\,q_d)\,l_y\,l_x^2"],
     "einsetzen": [rf"M_{{CEd}} = -(0{{,}}071 \cdot #gd:1# + 0{{,}}107 \cdot #qd:2#) \cdot #ly:2# \cdot #lx:2#^2 = #MCb:1#{KNM}",
                   rf"M_{{BEd}} = -(0{{,}}107 \cdot #gd:1# + 0{{,}}121 \cdot #qd:2#) \cdot #ly:2# \cdot #lx:2#^2 = #MBb:1#{KNM}"],
     "pruefen": [{"id": "MCb", "label": "M_{CEd}", "einheit": "kNm"}, {"id": "MBb", "label": "M_{BEd}", "einheit": "kNm"}],
     "werte": [{"id": "MBb", "expr": "-(0.107*gd + 0.121*qd)*ly*lx*lx", "d": 1}, {"id": "MCb", "expr": "-(0.071*gd + 0.107*qd)*ly*lx*lx", "d": 1}]},
    {"abschnitt": A_X, "seite": 280, "titel": "Randmoment: Beiwerte und Volleinspannmoment", "skript": f"{SK}, Folie 22",
     "frage": "Bestimme $\\psi$, $\\lambda$ (Stützweite quer $l_2 = l_y$) und das Volleinspannmoment.",
     "formel": [r"\psi = 0{,}5 + 3\,\dfrac{d_s}{l_2}, \qquad \lambda = 0{,}2 + 4\,\dfrac{d_s}{l_2}, \qquad M^{(0)}_{Rd} = -\psi\,(g + q)\,b_L\,\dfrac{l_1^2}{12}"],
     "einsetzen": [r"\psi = 0{,}5 + 3 \cdot \dfrac{#ds:2#}{#ly:2#} = #al2:3#, \qquad \lambda = 0{,}2 + 4 \cdot \dfrac{#ds:2#}{#ly:2#} = #be2:3#",
                   rf"M^{{(0)}}_{{Rd}} = -#al2:3# \cdot #p:2# \cdot #ly:2# \cdot \dfrac{{#lx:2#^2}}{{12}} = #M02:1#{KNM}"],
     "pruefen": [{"id": "al2", "label": "\\psi", "einheit": ""}, {"id": "M02", "label": "M^{(0)}_{Rd}", "einheit": "kNm"}],
     "werte": [{"id": "al2", "expr": "0.5 + 3*ds/ly", "d": 3}, {"id": "be2", "expr": "0.2 + 4*ds/ly", "d": 3}, {"id": "M02", "expr": "-al2*p*ly*lx*lx/12", "d": 1}]},
    {"abschnitt": A_X, "seite": 281, "titel": "Randmoment über die Steifigkeiten", "skript": f"{SK}, Folie 22",
     "frage": "Berechne Riegelsteifigkeit, Verteilungsbeiwerte und Randmoment in $x$-Richtung.",
     "formel": [r"b_m = \lambda\,l_2, \quad I_R = \dfrac{b_m\,h^3}{12}, \quad c_o = c_u = \dfrac{l_1\,I_S}{h_S\,I_R}, \quad M_{R,d} = \dfrac{c_o + c_u}{1 + c_o + c_u}\,M^{(0)}_{Rd}"],
     "einsetzen": [r"b_m = #be2:3# \cdot #ly:2# = #bm2:2#\,\mathrm{m}, \qquad I_R = \dfrac{#bm2:2# \cdot #h:2#^3}{12} = #IR2e:1# \cdot 10^{-4}\,\mathrm{m^4}",
                   r"c_o = c_u = \dfrac{#lx:2# \cdot #ISe:2#}{#hs:2# \cdot #IR2e:1#} = #c2:3#",
                   rf"M_{{R,d}} = \dfrac{{2 \cdot #c2:3#}}{{1 + 2 \cdot #c2:3#}} \cdot (#M02:1#) = #MR2:1#{KNM}"],
     "notiz": "Im Buch (S. 281) wird für l_1 die Stützweite 5 m eingesetzt und c = 0,23 bzw. M_R,d = −28 kNm erhalten. Das betrachtete System spannt in x-Richtung, also gilt l_1 = l_x = 4 m: c ≈ 0,18 und M_R,d ≈ −24 kNm.",
     "pruefen": [{"id": "c2", "label": "c_o", "einheit": ""}, {"id": "MR2", "label": "M_{R,d}", "einheit": "kNm"}],
     "werte": [{"id": "bm2", "expr": "be2*ly", "d": 2}, {"id": "IR2e", "expr": "bm2*h*h*h/12*1e4", "d": 1},
               {"id": "c2", "expr": "lx*ISe/(hs*IR2e)", "d": 3}, {"id": "MR2", "expr": "2*c2/(1 + 2*c2)*M02", "d": 1}]},
    streifen(A_X, "mFG2", 1.25, "M1b", "ly", "dy", "Feld 1, Gurtstreifen", 281, "23–24", "m_{1yy,SG}", "im Gurtstreifen von Feld 1"),
    streifen(A_X, "mFF2", 0.84, "M1b", "ly", "dy", "Feld 1, Feldstreifen", 281, "23–24", "m_{1yy,FG}", "im Feldstreifen von Feld 1"),
    streifen(A_X, "mSG2", 2.10, "MBb", "ly", "dy", "Stütze B, Gurtstreifen an der Stütze", 281, "23–24", "m_{Byy,SG}", "im inneren Gurtstreifen über Stütze B"),
    streifen(A_X, "mSN2", 1.40, "MBb", "ly", "dy", "Stütze B, Gurtstreifen neben der Stütze", 282, "23–24", "m_{Byy,SG2}", "im Gurtstreifen neben Stütze B"),
    streifen(A_X, "mSF2", 0.50, "MBb", "ly", "dy", "Stütze B, Feldstreifen", 282, "23–24", "m_{Byy,FG}", "im Feldstreifen über Stütze B",
             "Buch S. 282 und Tab. 7.2 verwenden hier 0,4 (−14,2 kNm/m), in Y-Richtung und in Abb. 7.6 aber 0,5. Mit 0,5 ergibt sich −17,7 kNm/m; nur so summieren sich die Streifen zu 1,0."),
    uebersicht(A_X, "X", [("MS-1", "MR2", "S"), ("MF-1", "M1b", "F"), ("MS-2", "MBb", "S"), ("MF-2", "M2b", "F"), ("MS-3", "MCb", "S")], "ly", "dy",
               "Zusammenstellung X-Richtung", 282, "23–24", "Tab. 7.2",
               "Abweichungen zum Buch: Randmoment mit l_x (siehe oben), Feldstreifen an der Stütze mit 0,5 statt 0,4 und ω aus dem 0,01-Raster der mb-Tafel."),

    # ---------------- 7.3.3 Querkräfte
    {"abschnitt": A_Q, "seite": 284, "titel": "Lasteinzugsflächen", "skript": f"{SK}, Folie 26–28",
     "frage": "Bestimme aus den Querkraft-Nulldurchgängen unter Volllast die Einzugsflächen der Stützen S-B-2 (innen), S-B-1 (Rand) und S-A-1 (Ecke).",
     "text": "Nulldurchgänge (Abb. 7.11): Vierfeldträger bei $0{,}393\\,l_x$ bzw. $0{,}607\\,l_x$ und $0{,}536\\,l_x$, Dreifeldträger bei $0{,}4\\,l_y$ bzw. $0{,}6\\,l_y$ und $0{,}5\\,l_y$. Am Deckenrand kommt der Überstand $d_s/2$ hinzu.",
     "formel": [r"L_1 = (0{,}607 + 0{,}536)\,l_x \ \text{bzw.}\ 0{,}393\,l_x + \tfrac{d_s}{2}, \qquad L_2 = (0{,}6 + 0{,}5)\,l_y \ \text{bzw.}\ 0{,}4\,l_y + \tfrac{d_s}{2}"],
     "einsetzen": [r"\text{S-B-2: } A = #axI:2# \cdot #ayI:2# = #AI:1#\,\mathrm{m^2}",
                   r"\text{S-B-1: } A = #axR:2# \cdot #ayI:2# = #AR:1#\,\mathrm{m^2}",
                   r"\text{S-A-1: } A = #axR:2# \cdot #ayR:2# = #AE:1#\,\mathrm{m^2}"],
     "pruefen": [{"id": "AI", "label": "A_{B2}", "einheit": "m²"}, {"id": "AR", "label": "A_{B1}", "einheit": "m²"}, {"id": "AE", "label": "A_{A1}", "einheit": "m²"}],
     "werte": [{"id": "axI", "expr": "1.143*lx", "d": 2}, {"id": "ayI", "expr": "1.1*ly", "d": 2}, {"id": "axR", "expr": "0.393*lx + ds/2", "d": 2},
               {"id": "ayR", "expr": "0.4*ly + ds/2", "d": 2}, {"id": "AI", "expr": "axI*ayI", "d": 1}, {"id": "AR", "expr": "axR*ayI", "d": 1}, {"id": "AE", "expr": "axR*ayR", "d": 1}]},
    {"abschnitt": A_Q, "seite": 285, "titel": "Stützenkräfte", "skript": f"{SK}, Folie 26–28",
     "frage": "Berechne die Stützenkräfte aus Einzugsfläche und Flächenlast (Tab. 7.3).",
     "formel": [r"V_{Ed} = A \cdot (g_d + q_d)"],
     "einsetzen": [rf"V_{{Ed,B2}} = #AI:1# \cdot #p:2# = #VI:1#\,\mathrm{{kN}}",
                   rf"V_{{Ed,B1}} = #AR:1# \cdot #p:2# = #VR:1#\,\mathrm{{kN}}",
                   rf"V_{{Ed,A1}} = #AE:1# \cdot #p:2# = #VE:1#\,\mathrm{{kN}}"],
     "pruefen": [{"id": "VI", "label": "V_{Ed,B2}", "einheit": "kN"}, {"id": "VR", "label": "V_{Ed,B1}", "einheit": "kN"}],
     "werte": [{"id": "VI", "expr": "AI*p", "d": 1}, {"id": "VR", "expr": "AR*p", "d": 1}, {"id": "VE", "expr": "AE*p", "d": 1}]},

    # ---------------- 7.3.4 Mindestmomente
    {"abschnitt": A_M, "seite": 284, "titel": "Mindestmoment an der Innenstütze S-B-2", "skript": f"{SK}, Folie 29–30",
     "frage": "Bestimme das Mindestmoment an der Innenstütze und vergleiche es mit den Momenten aus dem Gurtstreifenverfahren.",
     "text": "Beiwerte nach DIN EN 1992-1-1, Tab. NA.6.1.1 (Tab. 7.4): Innenstütze $\\eta = 0{,}125$ (Zug oben). Verglichen wird mit dem Gurtstreifen neben der Stütze (bei etwa $0{,}15\\,l$).",
     "formel": [r"m_{Ed} = -\eta \cdot V_{Ed}"],
     "einsetzen": [rf"m_{{Ed}} = -0{{,}}125 \cdot #VI:1# = -#mmI:1#{KNMM}",
                   rf"\text{{Y-Richtung: }} |m_{{Bxx,SG2}}| = #mSN1a:1#{KNMM}",
                   {"wenn": "mSN1a >= mmI", "t": r"\quad\Rightarrow\ \text{Mindestmoment nicht maßgebend}"},
                   {"wenn": "mSN1a < mmI", "t": r"\quad\Rightarrow\ \text{Mindestmoment maßgebend}"},
                   rf"\text{{X-Richtung: }} |m_{{Byy,SG2}}| = #mSN2a:1#{KNMM}",
                   {"wenn": "mSN2a >= mmI", "t": r"\quad\Rightarrow\ \text{Mindestmoment nicht maßgebend}"},
                   {"wenn": "mSN2a < mmI", "t": r"\quad\Rightarrow\ \text{Mindestmoment maßgebend}"}],
     "notiz": "Das Buch nennt für die X-Richtung 59 kNm/m als Vergleichswert; der Gurtstreifen neben der Stütze hat dort 49,6 kNm/m. Das Ergebnis (Mindestmoment maßgebend) bleibt gleich.",
     "pruefen": [{"id": "mmI", "label": "|m_{Ed}|", "einheit": "kNm/m"}],
     "werte": [{"id": "mmI", "expr": "0.125*VI", "d": 1}, {"id": "mSN1a", "expr": "Math.abs(mSN1)", "d": 1}, {"id": "mSN2a", "expr": "Math.abs(mSN2)", "d": 1}]},
    {"abschnitt": A_M, "seite": 284, "titel": "Mindestmoment an der Randstütze S-B-1", "skript": f"{SK}, Folie 30",
     "frage": "Bestimme die Mindestmomente an der Randstütze in beiden Richtungen.",
     "text": "Senkrecht zum Rand $\\eta = 0{,}25$ (Zug oben), parallel zum Rand $\\eta = 0{,}125$ oben und unten.",
     "formel": [r"m_{Ed} = \eta \cdot V_{Ed}"],
     "einsetzen": [rf"\text{{senkrecht zum Rand: }} m_{{Ed}} = -0{{,}}25 \cdot #VR:1# = -#mmR1:1#{KNMM}",
                   rf"\text{{parallel zum Rand: }} m_{{Ed}} = \pm 0{{,}}125 \cdot #VR:1# = \pm #mmR2:1#{KNMM}"],
     "pruefen": [{"id": "mmR1", "label": "|m_{Ed}|", "einheit": "kNm/m"}],
     "werte": [{"id": "mmR1", "expr": "0.25*VR", "d": 1}, {"id": "mmR2", "expr": "0.125*VR", "d": 1}]},
    {"abschnitt": A_M, "seite": 286, "titel": "Mindestmoment an der Eckstütze S-A-1", "skript": f"{SK}, Folie 31",
     "frage": "Bestimme das Mindestmoment an der Eckstütze.",
     "text": "Eckstütze: $\\eta = 0{,}5$ in beiden Richtungen, oben und unten, je Meter.",
     "formel": [r"m_{Ed} = \pm 0{,}5 \cdot V_{Ed}"],
     "einsetzen": [rf"m_{{Ed}} = \pm 0{{,}}5 \cdot #VE:1# = \pm #mmE:1#{KNMM}"],
     "pruefen": [{"id": "mmE", "label": "|m_{Ed}|", "einheit": "kNm/m"}],
     "werte": [{"id": "mmE", "expr": "0.5*VE", "d": 1}]},
]

BEISPIEL = {
    "id": "flachdecke",
    "titel": "Flachdecke im Stützenraster",
    "untertitel": "Schnittgrößen mit dem Gurtstreifenverfahren: Momente, Bewehrung, Stützenkräfte",
    "quelle": "Finckh: Stahlbetonkonstruktion",
    "auflage": "Springer Vieweg 2023",
    "abschnitt": "Abschn. 7.3, S. 274–286",
    "kap": "7.3",
    "system": "flachdecke",
    "abb2": "Momente je Meter auf Gurt- und Feldstreifen (Stütze B und Feld 1)",
    "aufgabe": ("Zwischengeschossdecke als Flachdecke ($h = 30\\,\\mathrm{cm}$) auf Stützen 30/30 im Raster 4 × 4,00 m in $x$ und 3 × 5,00 m in $y$, Geschosshöhe 3,0 m. "
                "Mit Ersatzträgern und dem Gurtstreifenverfahren nach DAfStb-Heft 631 werden in beiden Richtungen Feld-, Stütz- und Randmomente bestimmt, "
                "auf Gurt- und Feldstreifen verteilt und bemessen. Danach folgen die Stützenkräfte aus Lasteinzugsflächen und die Mindestmomente an Innen-, Rand- und Eckstütze."),
    "fest": [["Beton", "C30/37, XC3"], ["Raster", "4 Felder in x, 3 Felder in y"], ["Bewehrung", "B500, φ_l = 14 mm in zwei Lagen"],
             ["Stützen", "quadratisch, oben und unten gleich lang"]],
    "eingaben": [
        {"id": "beton", "label": "Betonfestigkeitsklasse", "typ": "auswahl", "wert": "C30/37", "werte": ["C20/25", "C25/30", "C30/37", "C35/45", "C40/50"]},
        {"id": "xk", "label": "Expositionsklasse", "typ": "auswahl", "wert": "XC3", "werte": ["XC1", "XC2", "XC3", "XC4"]},
        {"id": "lx", "label": "Stützweite $l_x$", "einheit": "m", "wert": 4.0, "step": 0.05, "d": 2},
        {"id": "ly", "label": "Stützweite $l_y$", "einheit": "m", "wert": 5.0, "step": 0.05, "d": 2},
        {"id": "h", "label": "Deckendicke $h$", "einheit": "m", "wert": 0.30, "step": 0.01, "d": 2},
        {"id": "gk2", "label": "Ausbaulast $g_{k2}$", "einheit": "kN/m²", "wert": 1.5, "step": 0.05, "d": 2},
        {"id": "qk", "label": "Verkehrslast $q_k$", "einheit": "kN/m²", "wert": 5.0, "step": 0.1, "d": 2},
        {"id": "ds", "label": "Stützenbreite $d_s$", "einheit": "m", "wert": 0.30, "step": 0.01, "d": 2},
        {"id": "hs", "label": "Geschosshöhe $h_S$", "einheit": "m", "wert": 3.0, "step": 0.05, "d": 2},
    ],
    "konstanten": {},
    "ergebnisse": [
        {"titel": "Stützmoment Y-Richtung", "wert": "MBa", "d": 0, "einheit": "kNm", "sub": "Gurtstreifen $#mSG1:1#\\,\\mathrm{kNm/m}$"},
        {"titel": "Bewehrung Stütze B oben", "wert": "amSG1as", "d": 1, "einheit": "cm²/m", "sub": "Gurtstreifen, Y-Richtung"},
        {"titel": "Stützmoment X-Richtung", "wert": "MBb", "d": 0, "einheit": "kNm", "sub": "Gurtstreifen $#mSG2:1#\\,\\mathrm{kNm/m}$"},
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
