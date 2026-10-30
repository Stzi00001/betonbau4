"""Tabellenkalkulationen (Excel mit echten Formeln) zu den Bemessungstools."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

GELB = PatternFill("solid", fgColor="FCE8A6")
GRAU = PatternFill("solid", fgColor="E8EAE9")
DUNKEL = PatternFill("solid", fgColor="172025")
DUENN = Border(bottom=Side(style="thin", color="C9CECC"))


def torsion(pfad):
    """Rechenweg wie im Bemessungstool: Skript Teil 3 (Gl. 14–25) und Teil 4 (Gl. 26–30).
    Zeilen werden über Namen adressiert, damit Formeln lesbar bleiben."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Torsion"
    for col, w in zip("ABCD", (34, 14, 9, 58)):
        ws.column_dimensions[col].width = w
    ws["A1"] = "Torsionsbemessung Rechteckquerschnitt – nach Vorlesungsskript Betonbau IV, Teil 3 und 4"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = ("Gelbe Zellen eingeben. Baustoffe und Querkraft nach Betonbau 3; konstruktive Regeln und Verzicht "
                "auf den Nachweis vorläufig nach DIN EN 1992-1-1 + NA.")
    ws["A2"].font = Font(italic=True, color="56625F")

    zeilen = {}
    r = [3]

    def kopf(text):
        r[0] += 1
        ws.cell(r[0], 1, text).font = Font(bold=True, color="FFFFFF")
        for c in range(1, 5):
            ws.cell(r[0], c).fill = DUNKEL

    def zeile(key, name, wert, einheit="", info="", eingabe=False, fmt="0.00"):
        r[0] += 1
        zeilen[key] = r[0]
        if isinstance(wert, str) and wert.startswith("="):
            wert = "=" + __import__("re").sub(r"\{(\w+)\}", lambda m: f"B{zeilen[m.group(1)]}", wert[1:])
        ws.cell(r[0], 1, name)
        z = ws.cell(r[0], 2, wert)
        z.number_format = fmt
        z.alignment = Alignment(horizontal="right")
        if eingabe:
            z.fill = GELB
        ws.cell(r[0], 3, einheit)
        ws.cell(r[0], 4, info).font = Font(color="56625F")
        for c in range(1, 5):
            ws.cell(r[0], c).border = DUENN

    kopf("Eingabe")
    zeile("b", "Breite b", 40, "cm", eingabe=True, fmt="0.0")
    zeile("h", "Höhe h", 60, "cm", eingabe=True, fmt="0.0")
    zeile("d1", "d₁ (Achse Längsbewehrung)", 5, "cm", eingabe=True, fmt="0.0")
    zeile("beton", "Betonfestigkeitsklasse", "C30/37", "", "Auswahl", eingabe=True, fmt="@")
    zeile("T", "T_Ed", 40, "kNm", eingabe=True, fmt="0.0")
    zeile("V", "V_Ed", 150, "kN", "0 = reine Torsion", eingabe=True, fmt="0.0")
    zeile("cot", "cot θ", 1.0, "–", "1,0 = 45°, empfohlen bei überwiegender Torsion (Teil 3, Folie 18)", eingabe=True)
    zeile("quer", "Querschnitt", "voll", "", "voll / kasten (echter Hohlkasten)", eingabe=True, fmt="@")
    zeile("rho", "ρ_l", 1.0, "%", "nur für V_Rd,c (Verzicht, vorläufig)", eingabe=True)
    dv = DataValidation(type="list", formula1='"C20/25,C25/30,C30/37,C35/45,C40/50,C45/55,C50/60"')
    dv2 = DataValidation(type="list", formula1='"voll,kasten"')
    ws.add_data_validation(dv); ws.add_data_validation(dv2)
    dv.add(f"B{zeilen['beton']}"); dv2.add(f"B{zeilen['quer']}")

    kopf("Baustoffe (Betonbau 3)")
    zeile("fck", "f_ck", '=VALUE(MID({beton},2,FIND("/",{beton})-2))', "N/mm²", fmt="0")
    zeile("fcd", "f_cd", "=0.85*{fck}/1.5", "N/mm²", "α_cc·f_ck/γ_c")
    zeile("fyd", "f_yd", "=500/1.15", "N/mm²", "f_yk/γ_s", fmt="0.0")

    kopf("Ersatzhohlkasten (Teil 3, Folie 3)")
    zeile("tef", "t_ef", "=MIN(2*{d1},MIN({b},{h})/2)", "cm", "doppelter Abstand Schwerlinie Längsbewehrung – Außenkante", fmt="0.0")
    zeile("Ak", "A_k", "=({b}-{tef})*({h}-{tef})", "cm²", "Fläche innerhalb der Wandmittellinie", fmt="0")
    zeile("uk", "u_k", "=2*(({b}-{tef})+({h}-{tef}))", "cm", "Umfang der Wandmittellinie", fmt="0.0")
    zeile("th", "θ", "=DEGREES(ATAN(1/{cot}))", "°", fmt="0.0")
    zeile("ct", "cot θ + tan θ", "={cot}+1/{cot}", "–", "Teil 3, Folie 17", fmt="0.000")

    kopf("Kräfte im räumlichen Fachwerk (Teil 3)")
    zeile("v", "v_Ed,T", "={T}*1000000/(2*{Ak}*100)", "N/mm", "Gl. (14): T_Ed/(2·A_k)", fmt="0.0")
    zeile("VT1", "V_Ed,T Seitenwand", "={v}*({h}-{tef})*10/1000", "kN", "Gl. (15): v_Ed,T·z₁, z₁ = h − t_ef", fmt="0.0")
    zeile("VT2", "V_Ed,T Gurt", "={v}*({b}-{tef})*10/1000", "kN", "Gl. (15): v_Ed,T·z₂, z₂ = b − t_ef", fmt="0.0")
    zeile("Fc", "|F_cd| Seitenwand", "={VT1}/SIN(ATAN(1/{cot}))", "kN", "Gl. (16): V_Ed,T/sin θ", fmt="0.0")
    zeile("Fs", "F_sld Seitenwand", "={VT1}*{cot}", "kN", "Gl. (17): V_Ed,T·cot θ", fmt="0.0")
    zeile("Fw", "F_swd Seitenwand", "={VT1}", "kN", "Gl. (18): = V_Ed,T", fmt="0.0")

    kopf("Nachweise und Bewehrung (Teil 3)")
    zeile("nu", "ν", '=IF({quer}="kasten",0.75,0.525)', "–", "Folie 16: 0,525 allgemein, 0,75 echter Hohlkasten", fmt="0.000")
    zeile("scd", "|σ_cd|", "={T}*1000000/(2*{Ak}*100*{tef}*10)*{ct}", "N/mm²", "Gl. (20)")
    zeile("TRd", "T_Rd,max", "={nu}*{fcd}*2*{Ak}*100*{tef}*10/{ct}/1000000", "kNm", "Gl. (23): ν·f_cd·2·A_k·t_ef/(cot θ + tan θ)", fmt="0.0")
    zeile("etaT", "Ausnutzung T_Ed / T_Rd,max", "={T}/{TRd}", "–", fmt="0.0%")
    zeile("asw", "A_sw/s_w je Schenkel", "={T}*1000000/(2*{Ak}*100*{fyd}*{cot})*10", "cm²/m", "aus Gl. (25): T_Ed/(2·A_k·f_yd·cot θ)")
    zeile("asl", "A_sl", "={T}*1000000*{uk}*10*{cot}/(2*{Ak}*100*{fyd})/100", "cm²", "aus Gl. (24): T_Ed·u_k·cot θ/(2·A_k·f_yd)")
    zeile("NT", "N_T", "={v}^2*{uk}*10/({asw}/10*{fyd})/1000", "kN", "Gl. (26) mit erf. Bügeln (= A_sl·f_yd)", fmt="0.0")
    zeile("smax", "s_w,max (vorläufig)", "=MIN(2*({b}+{h})/8,MIN({b},{h}))", "cm", "min(u/8; min(b,h)) – DIN EN 1992-1-1, 9.2.3", fmt="0.0")

    kopf("Torsion mit Querkraft (Teil 4)")
    zeile("d", "d", "={h}-{d1}", "cm", fmt="0.0")
    zeile("z", "z", "=0.9*{d}", "cm", "0,9·d", fmt="0.0")
    zeile("VRd", "V_Rd,max", "={b}*10*{z}*10*0.75*{fcd}/{ct}/1000", "kN", "b_w·z·ν₁·f_cd/(cot θ + tan θ), ν₁ = 0,75 (Betonbau 3)", fmt="0.0")
    zeile("inter", "Interaktion", '=IF({quer}="kasten",{T}/{TRd}+{V}/{VRd},({T}/{TRd})^2+({V}/{VRd})^2)', "≤ 1",
          "Gl. (29) Vollquerschnitt quadratisch / Gl. (30) echter Hohlkasten linear", fmt="0.000")
    zeile("ok", "Druckstreben erfüllt?", '=IF(AND({etaT}<=1,{inter}<=1),"ja","nein")', fmt="@")
    zeile("vV", "V_Ed/(2z)", "={V}*1000/(2*{z}*10)", "N/mm", "Gl. (27), Anteil Querkraft", fmt="0.0")
    zeile("vmax", "v_Ed,max", "={vV}+{v}", "N/mm", "Gl. (27): Steg mit gleichgerichteten Schubflüssen", fmt="0.0")
    zeile("vmin", "v_Ed,min", "={vV}-{v}", "N/mm", "Gl. (27): Steg mit entgegengesetzten Schubflüssen", fmt="0.0")
    zeile("aswV", "A_sw,V/s_w (beide Schenkel)", "={V}*1000/({z}*10*{fyd}*{cot})*10", "cm²/m", "V_Ed/(z·f_yd·cot θ) (Betonbau 3)")
    zeile("aswtot", "A_sw,tot/s_w", "={aswV}+2*{asw}", "cm²/m", "Gl. (28): A_sw,V/s_w + 2·A_sw,T/s_w")
    zeile("aswS", "je Schenkel", "={aswtot}/2", "cm²/m")

    kopf("Verzicht auf rechnerischen Nachweis (vorläufig, DE NA 6.3.2(5))")
    zeile("k", "k", "=MIN(1+SQRT(200/({d}*10)),2)", "–", fmt="0.000")
    zeile("VRdc", "V_Rd,c", "=MAX(0.1*{k}*(100*MIN({rho}/100,0.02)*{fck})^(1/3),0.0525/1.5*{k}^1.5*SQRT({fck}))*{b}*10*{d}*10/1000",
          "kN", "ohne Querkraftbewehrung", fmt="0.0")
    zeile("c1", "Bedingung 1: T ≤ V·b_w/4,5", '=IF({V}>0,IF({T}<={V}*{b}/100/4.5,"ja","nein"),"–")', fmt="@")
    zeile("c2", "Bedingung 2: V·(1+4,5·T/(V·b_w)) ≤ V_Rd,c", '=IF({V}>0,IF({V}*(1+4.5*{T}/({V}*{b}/100))<={VRdc},"ja","nein"),"–")', fmt="@")

    for key in ("ok", "c1", "c2"):
        ws.cell(zeilen[key], 2).font = Font(bold=True)
    ws.freeze_panes = "A4"
    wb.save(pfad)
    return zeilen


TABELLEN = {"torsion": torsion}
