"""Einheiten in allen Rechenwegen (Bemessungstool, Übungsaufgaben, Buchbeispiele) – letzter Schritt nach den anderen Skripten.

1. Jede Größe bekommt ihre Einheit ("einheiten": {id: Einheit}); der Rechenkern (templates/engine.js, fill) schreibt sie
   beim Einsetzen hinter jede Zahl, klammert vor Potenzen und lässt sie bei empirischen Formeln (√f_ck, f_ck^(1/3)) weg.
2. Die bisherigen Umrechnungsfaktoren (· 10^6, · 10 …) entfallen: gerechnet wird mit den Einheiten selbst,
   das Ergebnis steht in der Zieleinheit.
3. Feste Zahlenwerte bekommen ihre Einheit (435 N/mm², 0,30 m …).

Jede Ersetzung muss mindestens einmal greifen – sonst bricht das Skript ab (Quelle geändert → hier anpassen).
Aufruf: python tools/einheiten_torsion.py  (läuft automatisch in tools/alle.py)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from buch_wendehorst import EINHEITEN as BALKEN_EINHEITEN  # noqa: E402

N2, MN2, CM2, CM2M = "N/mm^2", "MN/m^2", "cm^2", "cm^2/m"
PROMILLE = r"\text{‰}"

RECHNER = {
    "b": "cm", "h": "cm", "d1": "cm", "T": "kNm", "V": "kN", "tw": "cm", "fck": N2, "fcd": N2, "fyd": N2,
    "tef0": "cm", "tvorh": "cm", "tef": "cm", "Ak": CM2, "uk": "cm", "v": "N/mm", "z1": "cm", "VT1": "kN", "VT2": "kN",
    "VTV": "kN", "bwV": "cm", "VRdcc": "kN", "Fc": "kN", "Fs": "kN", "TRd": "kNm", "asw": CM2M, "asl": CM2, "NT": "kN",
    "bmin": "cm", "smax": "cm", "d": "cm", "z": "cm", "VRd": "kN", "vV": "N/mm", "vmax": "N/mm", "vmin": "N/mm",
    "aswV": CM2M, "aswtot": CM2M, "aswS": CM2M, "VRdc": "kN", "bm": "m", "g1": "kNm", "g2": "kN",
}
RECHNER_ERSATZ = [
    (r"f_{\mathrm{yd}} = \dfrac{500}{1{,}15}", r"f_{\mathrm{yd}} = \dfrac{500\,\mathrm{N/mm^2}}{1{,}15}"),
    (r"\nu_2 = 1{,}1 - \dfrac{#fck:0#}{500}", r"\nu_2 = 1{,}1 - \dfrac{#fck:0#}{500\,\mathrm{N/mm^2}}"),
    (r"\dfrac{#T:1# \cdot 10^6}{2 \cdot #Ak:0# \cdot 10^2} \cdot \dfrac{1}{#fyd:1#} \cdot #tanT:3# \cdot 10", r"\dfrac{#T:1#}{2 \cdot #Ak:0# \cdot #fyd:1#} \cdot #tanT:3#"),
    (r"\dfrac{#T:1# \cdot 10^6 \cdot #uk:1# \cdot 10}{2 \cdot #Ak:0# \cdot 10^2} \cdot \dfrac{1}{#fyd:1#} \cdot #cot:2# \cdot 10^{-2}", r"\dfrac{#T:1# \cdot #uk:1#}{2 \cdot #Ak:0# \cdot #fyd:1#} \cdot #cot:2#"),
    (r"\dfrac{#T:1# \cdot 10^6}{2 \cdot #Ak:0# \cdot 10^2}", r"\dfrac{#T:1#}{2 \cdot #Ak:0#}"),
    (r"#v:1# \cdot #z1:1# \cdot 10 \cdot 10^{-3}", r"#v:1# \cdot #z1:1#"),
    (r"0{,}24 \cdot #fck:0#^{1/3} \cdot #tef:1# \cdot 10 \cdot #z1:1# \cdot 10 \cdot 10^{-3}", r"0{,}24 \cdot #fck:0:o#^{1/3} \cdot #tef:1# \cdot #z1:1#"),
    (r"\dfrac{#nu:3# \cdot #fcd:2# \cdot 2 \cdot #Ak:0# \cdot 10^2 \cdot #tef:1# \cdot 10}{#ct:3#} \cdot 10^{-6}", r"\dfrac{#nu:3# \cdot #fcd:2# \cdot 2 \cdot #Ak:0# \cdot #tef:1#}{#ct:3#}"),
    (r"#v:1#^2 \cdot \dfrac{#uk:1# \cdot 10}{#asw:2# \cdot 10^{-1} \cdot #fyd:1#} \cdot 10^{-3}", r"#v:1#^2 \cdot \dfrac{#uk:1#}{#asw:2# \cdot #fyd:1#}"),
    (r"\dfrac{#bwV:0# \cdot 10 \cdot #z:2# \cdot 10 \cdot #nu1:3# \cdot #fcd:2#}{#ct:3#} \cdot 10^{-3}", r"\dfrac{#bwV:0# \cdot #z:2# \cdot #nu1:3# \cdot #fcd:2#}{#ct:3#}"),
    (r"\dfrac{#V:1# \cdot 10^3}{2 \cdot #z:2# \cdot 10}", r"\dfrac{#V:1#}{2 \cdot #z:2#}"),
    (r"\dfrac{#V:1# \cdot 10^3}{#z:2# \cdot 10 \cdot #fyd:1# \cdot #cot:2#} \cdot 10", r"\dfrac{#V:1#}{#z:2# \cdot #fyd:1# \cdot #cot:2#}"),
    (r"\sqrt{\dfrac{200}{#d:1# \cdot 10}}", r"\sqrt{\dfrac{200\,\mathrm{mm}}{#d:1#}}"),
    (r"(100 \cdot #rhol:4# \cdot #fck:0#)^{1/3}", r"(100 \cdot #rhol:4# \cdot #fck:0:o#)^{1/3}"),
    (r"\right] #b:0# \cdot 10 \cdot #d:1# \cdot 10 \cdot 10^{-3} = #VRdc:1#", r"\right] \cdot #b:0# \cdot #d:1# = #VRdc:1#"),
]

AUFG_BASIS = {
    "F": "kN", "e": "m", "T": "kNm", "R": "cm", "IT": "cm^4", "tmax": N2, "r2": "cm", "th2": N2, "G": N2, "Ec": N2,
    "p": "kN/m", "l": "m", "b": "cm", "h": "cm", "t": "cm", "Ak": CM2, "rds": CM2, "tau": N2, "q": "N/mm",
    "GIT": "kNm^2", "GI1": "kNm^2", "GI2": "kNm^2", "bm": "cm", "hm": "cm", "Am": CM2, "Um": "cm",
    "fck": N2, "fcd": N2, "fyd": N2, "d1": "cm", "a": "cm", "tef": "cm", "uk": "cm", "v": "N/mm", "zi": "cm", "z1": "cm",
    "VT": "kN", "V1": "kN", "Fc": "kN", "TRd": "kNm", "asw": CM2M, "asl": CM2, "Asl": CM2, "TRsl": "kNm", "TRsw": "kNm",
    "TR": "kNm", "V": "kN", "d": "cm", "z": "cm", "VRd": "kN", "vV": "N/mm", "vT": "N/mm", "vmax": "N/mm", "vmin": "N/mm",
    "aswV": CM2M, "aswT": CM2M, "aswtot": CM2M, "aswS": CM2M, "bmin": "cm", "smax": "cm", "serf": "cm", "s": "cm",
    "As1": CM2, "VRdc": "kN", "g1": "kNm", "g2": "kN",
}
AUFG_EXTRA = {"Torsionssteifigkeit Hohlkasten": {"bm": "cm"},
              "Entfall rechnerischer Bewehrung": {"v1": N2, "vmin": N2, "bm": "m"}}
AUFG_ERSATZ = [
    (r"\dfrac{#T:2# \cdot 10^6}{#IT:0# \cdot 10^4} \cdot #R:0# \cdot 10", r"\dfrac{#T:2#}{#IT:0#} \cdot #R:0#"),
    (r"\dfrac{#T:2# \cdot 10^6}{#IT:0# \cdot 10^4} \cdot #r2:1# \cdot 10", r"\dfrac{#T:2#}{#IT:0#} \cdot #r2:1#"),
    (r"\dfrac{#T:2# \cdot 10^6}{#G:0# \cdot #IT:0# \cdot 10^4} \cdot 10^3", r"\dfrac{#T:2#}{#G:0# \cdot #IT:0#}"),
    (r"\dfrac{#T:2# \cdot 10^6}{#t:0# \cdot 10 \cdot 2 \cdot #Ak:0# \cdot 10^2}", r"\dfrac{#T:2#}{#t:0# \cdot 2 \cdot #Ak:0#}"),
    (r"#tau:2# \cdot #t:0# \cdot 10 = #q:1#", r"#tau:2# \cdot #t:0# = #q:1#"),
    (r"#G:0# \cdot #IT:0# \cdot 10^4 \cdot 10^{-9}", r"#G:0# \cdot #IT:0#"),
    (r"\dfrac{#T:0# \cdot 10^6}{2 \cdot #Ak:0# \cdot 10^2 \cdot #fyd:1# \cdot 1{,}0} \cdot 10", r"\dfrac{#T:0#}{2 \cdot #Ak:0# \cdot #fyd:1# \cdot 1{,}0}"),
    (r"\dfrac{#T:0# \cdot 10^6 \cdot #uk:1# \cdot 10}{2 \cdot #Ak:0# \cdot 10^2 \cdot #fyd:1# \cdot 1{,}0} \cdot 10^{-2}", r"\dfrac{#T:0# \cdot #uk:1#}{2 \cdot #Ak:0# \cdot #fyd:1# \cdot 1{,}0}"),
    (r"\dfrac{#T:0# \cdot 10^6}{2 \cdot #Ak:0# \cdot 10^2} \cdot \dfrac{1}{#fyd:1#} \cdot 1{,}0 \cdot 10", r"\dfrac{#T:0#}{2 \cdot #Ak:0# \cdot #fyd:1#} \cdot 1{,}0"),
    (r"\dfrac{#T:0# \cdot 10^6 \cdot #uk:1# \cdot 10}{2 \cdot #Ak:0# \cdot 10^2} \cdot \dfrac{1}{#fyd:1#} \cdot 1{,}0 \cdot 10^{-2}", r"\dfrac{#T:0# \cdot #uk:1#}{2 \cdot #Ak:0# \cdot #fyd:1#} \cdot 1{,}0"),
    (r"\dfrac{#T:0# \cdot 10^6}{2 \cdot #Ak:0# \cdot 10^2}", r"\dfrac{#T:0#}{2 \cdot #Ak:0#}"),
    (r"#v:1# \cdot #zi:1# \cdot 10 \cdot 10^{-3}", r"#v:1# \cdot #zi:1#"),
    (r"#v:1# \cdot #z1:1# \cdot 10 \cdot 10^{-3}", r"#v:1# \cdot #z1:1#"),
    (r"\dfrac{0{,}525 \cdot #fcd:2# \cdot 2 \cdot #Ak:0# \cdot 10^2 \cdot #tef:1# \cdot 10}{2} \cdot 10^{-6}", r"\dfrac{0{,}525 \cdot #fcd:2# \cdot 2 \cdot #Ak:0# \cdot #tef:1#}{2}"),
    (r"\dfrac{#nu:3# \cdot #fcd:2# \cdot 2 \cdot #Ak:0# \cdot 10^2 \cdot #tef:1# \cdot 10}{2} \cdot 10^{-6}", r"\dfrac{#nu:3# \cdot #fcd:2# \cdot 2 \cdot #Ak:0# \cdot #tef:1#}{2}"),
    (r"2 \cdot #Ak:0# \cdot 10^2 \cdot \dfrac{#Asl:2# \cdot 10^2}{#uk:1# \cdot 10} \cdot #fyd:1# \cdot 1{,}0 \cdot 10^{-6}", r"2 \cdot #Ak:0# \cdot \dfrac{#Asl:2#}{#uk:1#} \cdot #fyd:1# \cdot 1{,}0"),
    (r"2 \cdot #Ak:0# \cdot 10^2 \cdot \dfrac{#asw:2#}{10} \cdot #fyd:1# \cdot 1{,}0 \cdot 10^{-6}", r"2 \cdot #Ak:0# \cdot #asw:2# \cdot #fyd:1# \cdot 1{,}0"),
    (r"\dfrac{#b:0# \cdot 10 \cdot #z:2# \cdot 10 \cdot 0{,}75 \cdot #fcd:2#}{2} \cdot 10^{-3}", r"\dfrac{#b:0# \cdot #z:2# \cdot 0{,}75 \cdot #fcd:2#}{2}"),
    (r"\dfrac{#V:0# \cdot 10^3}{2 \cdot #z:2# \cdot 10}", r"\dfrac{#V:0#}{2 \cdot #z:2#}"),
    (r"\dfrac{#V:0# \cdot 10^3}{#z:2# \cdot 10 \cdot #fyd:1# \cdot 1{,}0} \cdot 10", r"\dfrac{#V:0#}{#z:2# \cdot #fyd:1# \cdot 1{,}0}"),
    (r"\dfrac{0{,}785}{#asw:2#} \cdot 100", r"\dfrac{0{,}785\,\mathrm{cm^2}}{#asw:2#}"),
    (r"\dfrac{#uk:1#}{70}", r"\dfrac{#uk:1#}{70\,\mathrm{cm}}"),
    (r"\max(#v1:3#;\; #vmin:3#) \cdot #b:0# \cdot 10 \cdot #d:1# \cdot 10 \cdot 10^{-3}", r"\max(#v1:3#;\; #vmin:3#) \cdot #b:0# \cdot #d:1#"),
]

BUCH = {
    "einfach": {"F": "kN", "p": "kN/m", "l": "m", "e": "m", "b": "m", "h": "m", "A": "kN", "M": "kNm", "T": "kNm",
                "cdur": "mm", "dc": "mm", "cmin": "mm", "d1": "m", "d": "m", "fck": N2, "fcd": N2, "Mmn": "MNm", "sig": N2,
                "As1": CM2, "V1": "kN", "V1mn": "MN", "tau1": MN2, "sig2": MN2, "nfcd": MN2, "V2": "kN", "V2mn": "MN",
                "tau2": MN2, "aswV": CM2M, "tRd": MN2, "teff": "m", "Ak": "m^2", "uk": "m", "Tmn": "MNm", "tt": MN2,
                "ttRd": MN2, "aswT": CM2M, "Asl": CM2, "aslu": CM2M, "Aob": CM2, "Aobv": CM2, "Ase": CM2, "Asev": CM2,
                "fehl": CM2, "Aun": CM2, "Aunv": CM2, "aswTot": CM2M, "sBm": "m", "aswv": CM2M, "fctm": N2, "Mcr": "MNm",
                "Asu": CM2, "aswmin": CM2M, "sTmax": "m", "dB": "cm"},
    "komplex": {"F": "kN", "H": "kN", "Tg": "kNm", "hs": "m", "a": "m", "t": "m", "V": "kN", "N": "kN", "M": "kNm",
                "T": "kNm", "cdur": "mm", "dc": "mm", "cnom": "mm", "d1": "m", "zs1": "m", "MEds": "kNm", "x": "m",
                "aa": "m", "z": "m", "Fcd": "kN", "Fsd": "kN", "eA": PROMILLE, "eI": PROMILLE, "As1": CM2, "fck": N2,
                "fcd": MN2, "FRd": "MN", "FcdMN": "MN", "Vmn": "MN", "tauEd": MN2, "a6": "m", "teff": "m", "Ak": "m^2",
                "Tmn": "MNm", "tt": MN2, "tR2": MN2, "tRK": MN2, "aswV": CM2M, "aswT": CM2M, "zi": "m", "uk": "m",
                "Asl": CM2, "aslu": CM2M, "AsD": CM2, "AsZ": CM2, "Asv": CM2, "aswTot": CM2M, "jeSteg": CM2M, "sBm": "m",
                "aswv": CM2M, "aswv2": CM2M, "Wc": "m^3", "fctm": N2, "Mcr": "MNm", "Asu": CM2, "aswmin": CM2M,
                "sTmax": "m", "sl": "m", "dB": "cm"},
}
BUCH["balken"] = BALKEN_EINHEITEN
BUCH_ERSATZ = [
    (r"\frac{0{,}30}{2}", r"\frac{0{,}30\,\mathrm{m}}{2}"),
    (r"{435\cdot", r"{435\,\mathrm{N/mm^2}\cdot"),
    (r"{435}", r"{435\,\mathrm{N/mm^2}}"),
    (r"\cdot 500}", r"\cdot 500\,\mathrm{N/mm^2}}"),
    (r"\max\left\{#cdur:0#;\ 12\right\}", r"\max\left\{#cdur:0#;\ 12\,\mathrm{mm}\right\}"),
    (r"+ 12 + \frac{28}{2}", r"+ 12\,\mathrm{mm} + \frac{28\,\mathrm{mm}}{2}"),
    (r"\ 14\right\}", r"\ 14\,\mathrm{mm}\right\}"),
    (r"- 0{,}04}", r"- 0{,}04\,\mathrm{m}}"),
    (r"+ 0{,}04}", r"+ 0{,}04\,\mathrm{m}}"),
    (r"3{,}5\cdot\frac", r"3{,}5\,\text{‰}\cdot\frac"),
    (r"} - 3{,}5 =", r"} - 3{,}5\,\text{‰} ="),
    (r"{43{,}5}", r"{43{,}5\,\mathrm{kN/cm^2}}"),
    (r"\ 0{,}30\right\}", r"\ 0{,}30\,\mathrm{m}\right\}"),
]


def zeilen(schritte):
    """alle Einsetz-Zeilen als (Liste, Index) zum Ersetzen"""
    for st in schritte:
        for i, l in enumerate(st.get("einsetzen", [])):
            yield st["einsetzen"], i


def ersetze(schritt_listen, ersatz, name):
    for alt, neu in ersatz:
        treffer = 0
        for schritte in schritt_listen:
            for liste, i in zeilen(schritte):
                l = liste[i]
                t = l if isinstance(l, str) else l["t"]
                if alt in t:
                    treffer += t.count(alt)
                    t = t.replace(alt, neu)
                    if isinstance(l, str):
                        liste[i] = t
                    else:
                        l["t"] = t
        schon = any(neu in (l if isinstance(l, str) else l["t"]) for schritte in schritt_listen for liste, i in zeilen(schritte) for l in [liste[i]])
        if not treffer and not schon:
            raise SystemExit(f"Einheiten ({name}): Zeile nicht gefunden – {alt}")


def main():
    ziel = Path(__file__).resolve().parent.parent / "content" / "01_torsion.json"
    d = json.loads(ziel.read_text(encoding="utf-8"))
    d["rechner"]["einheiten"] = RECHNER
    ersetze([d["rechner"]["schritte"]], RECHNER_ERSATZ, "Bemessungstool")
    for a in d["aufgaben"]:
        a["einheiten"] = {**AUFG_BASIS, **AUFG_EXTRA.get(a["titel"], {})}
    ersetze([a["schritte"] for a in d["aufgaben"]], AUFG_ERSATZ, "Übungsaufgaben")
    for b in d["buchbeispiele"]["beispiele"]:
        b["einheiten"] = BUCH[b["id"]]
    ersetze([b["schritte"] for b in d["buchbeispiele"]["beispiele"]], BUCH_ERSATZ, "Buchbeispiele")
    ziel.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Einheiten ergänzt: Bemessungstool, %d Übungsaufgaben, %d Buchbeispiele" % (len(d["aufgaben"]), len(d["buchbeispiele"]["beispiele"])))


if __name__ == "__main__":
    main()
