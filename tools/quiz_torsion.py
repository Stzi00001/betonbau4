"""Quizfragen Torsion – Quelle für content/01_torsion.json (Feld "quiz").

Aufbau je Frage:
  d      Schwierigkeit der Frage (1 = Stufe 1–5, 2 = Stufe 6–10, 3 = Stufe 11–15)
  f      Fragetext
  r      richtige Antwort
  falsch Falschantworten nach Stufe:
           leicht  = offensichtlich falsch
           mittel  = plausibel, aber erkennbar falsch
           schwer  = typische Fehler, der richtigen Antwort sehr ähnlich
  tipp   Hinweis für den Telefonjoker
  erkl   Erklärung nach dem Auflösen

Aufruf: python tools/quiz_torsion.py  -> schreibt das Feld "quiz" in die Inhaltsdatei.
"""
import json
from pathlib import Path

# Kurzschreibweisen für die Formeln
TEd, TRd = r"T_{\mathrm{Ed}}", r"T_{\mathrm{Rd,max}}"
VEd, VRd = r"V_{\mathrm{Ed}}", r"V_{\mathrm{Rd,max}}"
Ak, uk, tef = r"A_{\mathrm{k}}", r"u_{\mathrm{k}}", r"t_{\mathrm{ef}}"
fyd, fcd = r"f_{\mathrm{yd}}", r"f_{\mathrm{cd}}"
Asw, Asl, bw = r"A_{\mathrm{sw}}", r"A_{\mathrm{sl}}", r"b_{\mathrm{w}}"
tau = r"\tau_{\mathrm{t}}"


def m(s):
    return f"${s}$"


def frac(a, b):
    return rf"\dfrac{{{a}}}{{{b}}}"


QUIZ = [
    # ---------------- Schwierigkeit 1 ----------------
    {"d": 1, "f": "Welche Schnittgröße verdreht einen Balken um seine Längsachse?",
     "r": "Torsionsmoment $T$",
     "falsch": {"leicht": ["Normalkraft $N_{\\mathrm{Ed}}$", "Auflagerkraft $A_{\\mathrm{v}}$", "Eigengewicht $g_{\\mathrm{k}}$"],
                "mittel": ["Biegemoment $M_{\\mathrm{y}}$", "Querkraft $V_{\\mathrm{z}}$"]},
     "tipp": "Das Wort steckt im Namen des Themas.",
     "erkl": "Das Torsionsmoment wirkt um die Stabachse und verdreht den Querschnitt. Biegemoment und Querkraft verkrümmen bzw. verschieben ihn."},

    {"d": 1, "f": "Wie heißt Torsion, ohne die das System nicht im Gleichgewicht wäre?",
     "r": "Gleichgewichtstorsion",
     "falsch": {"leicht": ["Kriech- und Schwindtorsion", "Temperaturtorsion", "Lastumlagerungstorsion"],
                "mittel": ["Verträglichkeitstorsion", "Zwängungstorsion"]},
     "tipp": "Der Name sagt, wofür sie gebraucht wird.",
     "erkl": "Gleichgewichtstorsion ist für die Lastabtragung zwingend erforderlich und muss voll nachgewiesen werden. Verträglichkeitstorsion entsteht nur aus Verformungskompatibilität."},

    {"d": 1, "f": "Wie verlaufen die Risse an einem Stahlbetonbalken unter reiner Torsion?",
     "r": "Wendelförmig unter etwa $45^\\circ$",
     "falsch": {"leicht": ["Senkrecht zur Balkenachse, nur unten", "Parallel zur Balkenachse im Steg", "Strahlenförmig vom Auflager aus"],
                "mittel": ["Wendelförmig unter etwa $15^\\circ$", "Schräg, aber nur in den Seitenflächen"]},
     "tipp": "Denk an die Hauptzugspannungen bei reinem Schub, und zwar auf allen vier Seiten.",
     "erkl": "Reiner Schub erzeugt Hauptzugspannungen unter $45^\\circ$. Die Hauptspannungen verlaufen wendelförmig um den Stab; Risse entstehen, wenn sie die Betonzugfestigkeit überschreiten."},

    {"d": 1, "f": "Welche Bügel braucht man zur Aufnahme von Torsion?",
     "r": "Geschlossene Bügel",
     "falsch": {"leicht": ["Keine, Längsstäbe genügen", "Nur Schrägaufbiegungen", "Lose Montagebügel"],
                "mittel": ["Offene U-Bügel mit Haken", "Steckbügel ohne Übergreifung"]},
     "tipp": "Der Schubfluss läuft einmal komplett um den Querschnitt herum.",
     "erkl": "Die Bügel sind die Zugstreben des räumlichen Fachwerks auf allen vier Seiten. Sie müssen daher umlaufend geschlossen und mit $135^\\circ$-Haken oder Übergreifung verankert sein."},

    {"d": 1, "f": "Mit welchem Modell beschreibt man das Torsionstragverhalten im gerissenen Zustand?",
     "r": "Räumliches Fachwerk",
     "falsch": {"leicht": ["Bogen-Zugband-Modell", "Plattentheorie nach Kirchhoff", "Seileck-Verfahren"],
                "mittel": ["Ebenes Fachwerk nach Mörsch", "Wölbkrafttorsion nach Wlassow"]},
     "tipp": "Der Kern trägt kaum mit – übrig bleibt eine dünne Wand.",
     "erkl": "Im Zustand II wird der Querschnitt als dünnwandiger Hohlkasten idealisiert. In jeder Wand wirkt ein Fachwerk aus Betondruckstreben, Bügeln und Längsstäben."},

    {"d": 1, "f": "Wo muss Torsionslängsbewehrung mindestens liegen?",
     "r": "In jeder Querschnittsecke",
     "falsch": {"leicht": ["Nur unten in Balkenmitte", "Nur im Auflagerbereich", "Nirgends, die Bügel genügen"],
                "mittel": ["Nur in der Biegezugzone", "Nur in den Stegmitten beidseitig"]},
     "tipp": "Im räumlichen Fachwerk braucht jede Kante einen Gurt.",
     "erkl": "Die Längsstäbe bilden die Gurte des räumlichen Fachwerks. Die Kräfte laufen in den Ecken zusammen, deshalb gehört in jede Ecke mindestens ein Stab."},

    {"d": 1, "teil": "1", "f": "Wodurch wird das Torsionsmoment bei St.-Venantscher Torsion übertragen?",
     "r": "Ausschließlich durch Schubspannungen",
     "falsch": {"leicht": ["Ausschließlich durch Druckspannungen", "Nur durch Biegezugspannungen", "Durch Auflagerpressungen"],
                "mittel": ["Durch Schub- und Wölbnormalspannungen", "Durch Längsspannungen aus Verwölbung"]},
     "tipp": "Primäre Torsion – nur eine Spannungsart ist beteiligt.",
     "erkl": "St.-Venantsche (primäre) Torsion überträgt das Moment ausschließlich durch Schubspannungen $\\tau$. Längsspannungen entstehen erst, wenn die Verwölbung behindert wird."},

    {"d": 1, "f": f"Was bezeichnet ${tef}$?",
     "r": "Wanddicke des Ersatzhohlkastens",
     "falsch": {"leicht": ["Stabdurchmesser der Torsionsbügel", "Bügelabstand in Längsrichtung", "Betondeckung der Längsbewehrung"],
                "mittel": ["Höhe der Biegedruckzone im Zustand II", "Abstand der Längsstäbe untereinander"]},
     "tipp": "„ef“ steht für effektiv.",
     "erkl": "$t_{\\mathrm{ef}}$ ist die rechnerische Wanddicke des Ersatzhohlkastens, in der der Schubfluss angesetzt wird."},

    # ---------------- Schwierigkeit 2 ----------------
    {"d": 2, "f": "Welches Bauteil ist ein typisches Beispiel für Gleichgewichtstorsion?",
     "r": "Randträger mit angehängter Kragplatte",
     "falsch": {"leicht": ["Einfeldträger unter mittiger Gleichlast"],
                "mittel": ["Randunterzug einer durchlaufenden Deckenplatte", "Mittelstütze einer punktgestützten Flachdecke", "Innenunterzug einer Decke"],
                "schwer": ["Randträger mit eingespannter Deckenplatte"]},
     "tipp": "Die Last kann nur über die Verdrehung des Trägers abgetragen werden.",
     "erkl": "Die Kragplatte hat keinen anderen Lastweg: Ihr Einspannmoment muss als Torsion durch den Randträger. Beim Randunterzug einer Durchlaufdecke entsteht Torsion nur aus Verträglichkeit."},

    {"d": 2, "f": "Wie groß ist der Schubfluss im Ersatzhohlkasten (Bredtsche Formel)?",
     "r": m("q = " + frac(TEd, "2\\," + Ak)),
     "falsch": {"leicht": [m(f"q = {TEd} \\cdot {Ak}")],
                "mittel": [m("q = " + frac(TEd, Ak)), m("q = " + frac("2\\," + TEd, Ak)), m("q = " + frac(TEd, f"{uk}\\,{tef}"))],
                "schwer": [m("q = " + frac(TEd, f"2\\,{Ak}\\,{tef}"))]},
     "tipp": "Im Nenner steht die doppelte Kernfläche – und sonst nichts.",
     "erkl": "Schubfluss $q = \\tau_{\\mathrm{t}}\\,t_{\\mathrm{ef}} = T_{\\mathrm{Ed}}/(2\\,A_{\\mathrm{k}})$. Teilt man zusätzlich durch $t_{\\mathrm{ef}}$, erhält man die Schubspannung $\\tau_{\\mathrm{t}}$, nicht den Schubfluss."},

    {"d": 2, "f": f"Was ist die Fläche ${Ak}$?",
     "r": "Fläche innerhalb der Wandmittellinie",
     "falsch": {"leicht": ["Querschnittsfläche der Längsbewehrung"],
                "mittel": ["Betonfläche aller Wände des Hohlkastens", "Fläche innerhalb der Querschnittsaußenkante", "Fläche innerhalb der Bügelachsen"],
                "schwer": ["Fläche innerhalb der Wandinnenkante"]},
     "tipp": "Es geht um die Mitte der Ersatzwand – und der Hohlraum zählt mit.",
     "erkl": "$A_{\\mathrm{k}}$ ist die von der Mittellinie der Wände eingeschlossene Fläche, einschließlich des Hohlraums. Beim Rechteck: $(b - t_{\\mathrm{ef}})(h - t_{\\mathrm{ef}})$."},

    {"d": 2, "f": "Wie wird Verträglichkeitstorsion im Grenzzustand der Tragfähigkeit in der Regel behandelt?",
     "r": "Vernachlässigt, aber Mindestbewehrung",
     "falsch": {"leicht": ["Das Moment wird zur Sicherheit verdoppelt"],
                "mittel": ["Voller Nachweis wie Gleichgewichtstorsion", "Nur Nachweis der Betondruckstreben", "Nur bei Spannbetonbauteilen nachzuweisen"],
                "schwer": ["Vernachlässigt, ganz ohne Bewehrung"]},
     "tipp": "Mit den Rissen baut sich das Moment ab – ganz ignorieren darf man es trotzdem nicht.",
     "erkl": "Durch Rissbildung sinkt die Torsionssteifigkeit stark, das Zwangsmoment baut sich ab. Zur Begrenzung der Rissbreiten ist aber eine konstruktive Mindestbewehrung nötig."},

    {"d": 2, "f": "Wie verändert sich die Torsionssteifigkeit beim Übergang in Zustand II?",
     "r": "Sie fällt durch Rissbildung stark ab",
     "falsch": {"leicht": ["Sie verdoppelt sich durch die Bewehrung"],
                "mittel": ["Sie bleibt trotz Rissbildung nahezu gleich", "Sie steigt durch die Bewehrung an", "Sie fällt durch Rissbildung nur leicht ab"],
                "schwer": ["Sie fällt, aber weniger als die Biegesteifigkeit"]},
     "tipp": "Risse treffen die Schubsteifigkeit besonders hart.",
     "erkl": "Nach dem Reißen trägt nur noch das Fachwerk; die Torsionssteifigkeit fällt deutlich stärker ab als die Biegesteifigkeit. Deshalb baut sich Verträglichkeitstorsion ab."},

    {"d": 2, "f": f"Worauf bezieht sich ${Asw}$ in ${frac(Asw, 's')} = {frac(TEd, f'2\\,{Ak}\\,{fyd}\\cot\\theta')}$?",
     "r": "Auf einen Bügelschenkel",
     "falsch": {"leicht": ["Auf die gesamte Längsbewehrung"],
                "mittel": ["Auf beide Bügelschenkel", "Auf alle Bügel je Meter", "Auf die Bügel einer Ecke"],
                "schwer": ["Auf zwei Schenkel wie bei Querkraft"]},
     "tipp": "Der Schubfluss wirkt in jeder Wand einzeln.",
     "erkl": "Jede Wand des Hohlkastens nimmt den Schubfluss selbst auf, also wird $A_{\\mathrm{sw}}$ je Schenkel bestimmt. Bei der Querkraft wird dagegen meist mit beiden Schenkeln gerechnet – ein klassischer Fehler."},

    {"d": 2, "f": "Welche Druckstrebenneigung darf bei reiner Torsion vereinfacht angesetzt werden?",
     "r": "$\\theta = 45^\\circ$",
     "falsch": {"leicht": ["$\\theta = 90^\\circ$"],
                "mittel": ["$\\theta = 30^\\circ$", "$\\theta = 60^\\circ$", "$\\theta = 21{,}8^\\circ$"],
                "schwer": ["$\\cot\\theta = 2{,}5$"]},
     "tipp": "Der Winkel, unter dem auch die Risse verlaufen.",
     "erkl": "Vereinfachend gilt $\\theta = 45^\\circ$, also $\\cot\\theta = 1{,}0$. Flachere Druckstreben sind nur mit genauerem Nachweis bzw. in Kombination mit dem Querkraftnachweis möglich."},

    {"d": 2, "f": "Wie groß ist die Querkraft in einer Wand $i$ des Hohlkastens?",
     "r": m(f"V_{{\\mathrm{{Ed}},i}} = {tau}\\,{tef}\\,z_i"),
     "falsch": {"leicht": [m(f"V_{{\\mathrm{{Ed}},i}} = {TEd}\\,z_i\\,{tef}")],
                "mittel": [m(f"V_{{\\mathrm{{Ed}},i}} = {tau}\\,z_i"), m(f"V_{{\\mathrm{{Ed}},i}} = " + frac(TEd, "z_i")),
                           m(f"V_{{\\mathrm{{Ed}},i}} = {tau}\\,{tef}\\,{uk}")],
                "schwer": [m(f"V_{{\\mathrm{{Ed}},i}} = " + frac(f"{TEd}\\,z_i", Ak))]},
     "tipp": "Schubfluss mal Wandlänge.",
     "erkl": "Wandquerkraft = Schubfluss · Länge der Wand. Mit $q = T_{\\mathrm{Ed}}/(2\\,A_{\\mathrm{k}})$ ergibt sich $V_{\\mathrm{Ed},i} = T_{\\mathrm{Ed}}\\,z_i/(2\\,A_{\\mathrm{k}})$ – ohne die 2 wäre der Wert doppelt so groß."},

    # ---------------- Schwierigkeit 3 ----------------
    {"d": 3, "f": "Wie groß ist die erforderliche Torsionslängsbewehrung?",
     "r": m(f"\\sum {Asl} = " + frac(f"{TEd}\\,{uk}\\cot\\theta", f"2\\,{Ak}\\,{fyd}")),
     "falsch": {"mittel": [m(f"\\sum {Asl} = " + frac(TEd, f"2\\,{Ak}\\,{fyd}\\cot\\theta")),
                           m(f"\\sum {Asl} = " + frac(f"{TEd}\\,{Ak}", f"{uk}\\,{fyd}"))],
                "schwer": [m(f"\\sum {Asl} = " + frac(f"{TEd}\\,{uk}\\tan\\theta", f"2\\,{Ak}\\,{fyd}")),
                           m(f"\\sum {Asl} = " + frac(f"{TEd}\\,{uk}\\cot\\theta", f"{Ak}\\,{fyd}")),
                           m(f"\\sum {Asl} = " + frac(f"{TEd}\\,{uk}", f"2\\,{Ak}\\,{fyd}\\cot\\theta"))]},
     "tipp": "Der Umfang und $\\cot\\theta$ stehen beide im Zähler.",
     "erkl": "Aus dem Gleichgewicht am Fachwerk: $\\sum A_{\\mathrm{sl}}\\,f_{\\mathrm{yd}} = q\\,u_{\\mathrm{k}}\\cot\\theta$ mit $q = T_{\\mathrm{Ed}}/(2\\,A_{\\mathrm{k}})$. Bei den Bügeln steht $\\cot\\theta$ dagegen im Nenner."},

    {"d": 3, "f": "Wie groß darf der Längsabstand der Torsionsbügel höchstens sein (EC2, 9.2.3)?",
     "r": "$u/8$",
     "falsch": {"mittel": ["$h/2$", "$300\\,\\mathrm{mm}$"],
                "schwer": ["$u/4$", "$u/10$", "$u/6$"]},
     "tipp": "Ein Bruchteil des Außenumfangs – der Nenner ist eine Zweierpotenz.",
     "erkl": "$s \\le u/8$ mit $u$ als Außenumfang. Zusätzlich gelten die Grenzen aus der Querkraftbemessung und die kleinste Querschnittsabmessung."},

    {"d": 3, "f": "Welchen Größtabstand dürfen die Torsionslängsstäbe haben (EC2, 9.2.3)?",
     "r": "$350\\,\\mathrm{mm}$",
     "falsch": {"mittel": ["$150\\,\\mathrm{mm}$", "$500\\,\\mathrm{mm}$"],
                "schwer": ["$300\\,\\mathrm{mm}$", "$250\\,\\mathrm{mm}$", "$400\\,\\mathrm{mm}$"]},
     "tipp": "Etwas mehr als ein Drittel Meter.",
     "erkl": "Die Längsstäbe sind gleichmäßig über den Umfang zu verteilen, mit höchstens $350\\,\\mathrm{mm}$ Abstand und mindestens einem Stab je Ecke."},

    {"d": 3, "f": "Wie lautet der Interaktionsnachweis Torsion + Querkraft für Vollquerschnitte nach DE NA?",
     "r": m(f"\\left({frac(TEd, TRd)}\\right)^2 + \\left({frac(VEd, VRd)}\\right)^2 \\le 1"),
     "falsch": {"mittel": ["Getrennte Nachweise, keine Interaktion", "Interaktion nur über die Längsbewehrung"],
                "schwer": [m(f"{frac(TEd, TRd)} + {frac(VEd, VRd)} \\le 1"),
                           m(f"{frac(TEd, TRd)} + \\left({frac(VEd, VRd)}\\right)^2 \\le 1"),
                           m(f"\\left({frac(TEd, TRd)}\\right)^2 + {frac(VEd, VRd)} \\le 1")]},
     "tipp": "Bei Vollquerschnitten ist der NA großzügiger als bei Kästen.",
     "erkl": "Für Vollquerschnitte erlaubt der DE NA die quadratische Interaktion. Die lineare Summe gilt für Kastenquerschnitte."},

    {"d": 3, "f": "Welchen Beiwert $\\nu$ setzt der DE NA für die Torsions-Druckstrebe in Vollquerschnitten an (bis C50/60)?",
     "r": "$\\nu = 0{,}525$",
     "falsch": {"mittel": ["$\\nu = 1{,}000$", "$\\nu = 0{,}500$"],
                "schwer": ["$\\nu = 0{,}750$", "$\\nu = 0{,}600$", "$\\nu = 0{,}675$"]},
     "tipp": "70 % des Querkraftwerts $0{,}75$.",
     "erkl": "Nach DE NA: $\\nu = 0{,}525$ für Vollquerschnitte und $0{,}75$ für Kastenquerschnitte mit beidseitig bewehrten Wänden; ab C55/67 jeweils mal $\\nu_2$."},

    {"d": 3, "f": "Welche Bedingung gehört nach DE NA zum Verzicht auf einen rechnerischen Torsionsnachweis bei Rechteckvollquerschnitten?",
     "r": m(f"{TEd} \\le " + frac(f"{VEd}\\,{bw}", "4{,}5")),
     "falsch": {"mittel": [m(f"{TEd} \\le 0{{,}}10\\,{VEd}\\,h"), m(f"{TEd} \\le {VEd}\\,{bw}\\,h")],
                "schwer": [m(f"{TEd} \\le " + frac(f"{VEd}\\,{bw}", "2{,}5")),
                           m(f"{TEd} \\le " + frac(f"{VEd}\\,h", "4{,}5")),
                           m(f"{VEd} \\le " + frac(f"{TEd}\\,{bw}", "4{,}5"))]},
     "tipp": "Querkraft mal Stegbreite, geteilt durch eine Zahl zwischen 4 und 5.",
     "erkl": "Zusätzlich muss $V_{\\mathrm{Ed}}\\left(1 + \\frac{4{,}5\\,T_{\\mathrm{Ed}}}{V_{\\mathrm{Ed}}\\,b_{\\mathrm{w}}}\\right) \\le V_{\\mathrm{Rd,c}}$ erfüllt sein. Dann genügt die Mindestbewehrung."},

    {"d": 3, "f": "Wie groß ist die Druckstrebentragfähigkeit bei Torsion?",
     "r": m(f"{TRd} = 2\\,\\nu\\,{fcd}\\,{Ak}\\,{tef}\\sin\\theta\\cos\\theta"),
     "falsch": {"mittel": [m(f"{TRd} = \\nu\\,{fcd}\\,{Ak}\\,{tef}\\,\\tan\\theta"), m(f"{TRd} = 2\\,{fcd}\\,{uk}\\,{tef}\\cot\\theta")],
                "schwer": [m(f"{TRd} = \\nu\\,{fcd}\\,{Ak}\\,{tef}\\sin\\theta\\cos\\theta"),
                           m(f"{TRd} = 2\\,\\nu\\,{fcd}\\,{Ak}\\,{tef}\\cot\\theta"),
                           m(f"{TRd} = 2\\,\\nu\\,{fcd}\\,{uk}\\,{tef}\\sin\\theta\\cos\\theta")]},
     "tipp": "Wie bei Bredt taucht die doppelte Kernfläche auf.",
     "erkl": "Aus der Druckstrebenkraft in der Wand und $q = T_{\\mathrm{Ed}}/(2\\,A_{\\mathrm{k}})$ folgt $T_{\\mathrm{Rd,max}} = 2\\,\\nu\\,\\alpha_{\\mathrm{cw}}\\,f_{\\mathrm{cd}}\\,A_{\\mathrm{k}}\\,t_{\\mathrm{ef}}\\sin\\theta\\cos\\theta$."},

    {"d": 3, "f": f"Wie darf ${tef}$ nach DE NA bei Vollquerschnitten angesetzt werden?",
     "r": "Doppelter Abstand Rand bis Längsstabachse",
     "falsch": {"mittel": ["Gleich der Betondeckung der Längsstäbe", "Ein Viertel der kleineren Querschnittsseite"],
                "schwer": ["Einfacher Abstand Rand bis Längsstabachse",
                           "Doppelter Abstand Rand bis Bügelachse",
                           "$A/u$, ohne den Mindestwert aus EC2"]},
     "tipp": "Die Längsbewehrung soll in der Mitte der Ersatzwand liegen.",
     "erkl": "Mit $t_{\\mathrm{ef}} = 2\\,d_1$ liegt die Achse der Längsbewehrung genau auf der Wandmittellinie – passend zum Fachwerkmodell."},

    {"d": 3, "f": f"Rechteck $b/h = 40/60\\,\\mathrm{{cm}}$, ${tef} = 10\\,\\mathrm{{cm}}$. Wie groß ist ${Ak}$?",
     "r": "$1500\\,\\mathrm{cm^2}$",
     "falsch": {"mittel": ["$2400\\,\\mathrm{cm^2}$", "$1000\\,\\mathrm{cm^2}$"],
                "schwer": ["$1925\\,\\mathrm{cm^2}$", "$800\\,\\mathrm{cm^2}$", "$1600\\,\\mathrm{cm^2}$"]},
     "tipp": "Von jeder Seite eine halbe Wanddicke abziehen.",
     "erkl": "$A_{\\mathrm{k}} = (40 - 10)(60 - 10) = 30 \\cdot 50 = 1500\\,\\mathrm{cm^2}$. Wer $2\\,t_{\\mathrm{ef}}$ abzieht, erhält $800\\,\\mathrm{cm^2}$, wer nur $t_{\\mathrm{ef}}/2$ abzieht, $1925\\,\\mathrm{cm^2}$."},

    # ---------------- Skript Teil 1: Mechanische Grundlagen ----------------
    {"d": 1, "teil": "1", "f": "Wie verlaufen die Hauptspannungen um einen tordierten Stab?",
     "r": "Wendelförmig um den Stab",
     "falsch": {"leicht": ["Parallel zur Stabachse", "Senkrecht zur Stabachse", "Nur im Querschnittskern"],
                "mittel": ["Radial vom Mittelpunkt nach außen", "Ringförmig um die Stabachse"]},
     "tipp": "Denk an das Rissbild – es läuft einmal um den Stab herum.",
     "erkl": "Die schiefen Hauptspannungen unter $45^\\circ$ und $135^\\circ$ verlaufen wendelförmig um den Stab. Deshalb entsteht auch ein wendelförmiges Rissbild."},

    {"d": 1, "teil": "1", "f": "Wo sind die Hauptspannungen infolge Torsion am größten?",
     "r": "An der Außenfläche",
     "falsch": {"leicht": ["Genau in der Stabachse", "Im Querschnittsschwerpunkt", "Am Lastangriffspunkt"],
                "mittel": ["Auf halbem Radius", "Überall gleich groß"]},
     "tipp": "Die Schubspannung wächst mit dem Abstand von der Achse.",
     "erkl": "Die Schubspannung wächst linear mit dem Radius, Gl. (4). Entsprechend sind auch die Hauptspannungen an der Außenfläche am größten – dort entstehen die ersten Risse."},

    {"d": 1, "teil": "1", "f": "Ein abgewinkelter Kragträger trägt am Ende des Querarms die Einzellast $F$ mit dem Hebelarm $e$. Wie groß ist das Torsionsmoment im Hauptträger?",
     "r": "$T = F \\cdot e$",
     "falsch": {"leicht": ["$T = F + e$", "$T = F / e$", "$T = e / F$"],
                "mittel": ["$T = F \\cdot e^2$", "$T = F \\cdot e / 2$"]},
     "tipp": "Kraft mal Hebelarm – sonst nichts.",
     "erkl": "Die Last wirkt mit dem Hebelarm $e$ um die Längsachse des Hauptträgers: $T = F \\cdot e$. Im Querarm entsteht dagegen ein Biegemoment."},

    {"d": 1, "teil": "1", "f": "Auf welchen Punkt ist das Torsionsmoment bezogen?",
     "r": "Auf den Schubmittelpunkt",
     "falsch": {"leicht": ["Auf den Auflagerpunkt", "Auf den Lastangriffspunkt", "Auf die Querschnittsecke"],
                "mittel": ["Auf den Schwerpunkt", "Auf den Flächenmittelpunkt"]},
     "tipp": "Der Punkt, der sich bei Torsion nicht verschiebt.",
     "erkl": "Bezugspunkt ist der Schubmittelpunkt (Drehmittelpunkt). Er erfährt bei Torsion keine Verschiebung und stimmt nur bei zweifach symmetrischen Querschnitten mit dem Schwerpunkt überein."},

    {"d": 1, "teil": "1", "f": "Unter welchen Winkeln verlaufen die Hauptspannungen infolge Torsion?",
     "r": "$45^\\circ$ und $135^\\circ$",
     "falsch": {"leicht": ["$0^\\circ$ und $90^\\circ$", "$90^\\circ$ und $180^\\circ$", "$10^\\circ$ und $100^\\circ$"],
                "mittel": ["$30^\\circ$ und $120^\\circ$", "$60^\\circ$ und $150^\\circ$"]},
     "tipp": "Reiner Schub – die Hauptrichtungen liegen genau dazwischen.",
     "erkl": "Schubspannungen erzeugen schiefe Hauptspannungen unter $45^\\circ$ und $135^\\circ$: Zug in Drehrichtung, Druck in Gegenrichtung."},

    {"d": 2, "teil": "1", "f": "Wo ist die Schubspannung im Kreisquerschnitt unter Torsion am größten?",
     "r": "Am Außenradius $R$",
     "falsch": {"leicht": ["Im Querschnittsmittelpunkt"],
                "mittel": ["Bei halbem Radius $R/2$", "Überall gleich groß", "Bei $r = 2R/3$"],
                "schwer": ["Bei $r = R/\\sqrt{2}$"]},
     "tipp": "Gl. (4): $\\tau$ wächst linear mit $r$.",
     "erkl": "Nach Gl. (4) gilt $\\tau(r) = \\dfrac{T}{I_T} \\cdot r$, die Schubspannung wächst linear mit dem Radius. Das Maximum liegt am Außenradius, Gl. (5)."},

    {"d": 2, "teil": "1", "f": "Wann fallen Schubmittelpunkt und Schwerpunkt zusammen?",
     "r": "Bei zweifach symmetrischen Querschnitten",
     "falsch": {"leicht": ["Bei allen Stahlbetonquerschnitten"],
                "mittel": ["Bei allen geschlossenen Querschnitten", "Bei allen dünnwandigen Querschnitten", "Bei allen Querschnitten mit Bewehrung"],
                "schwer": ["Bei einfach symmetrischen Querschnitten"]},
     "tipp": "Eine Symmetrieachse reicht nicht – denk an das U-Profil.",
     "erkl": "Nur bei zweifach symmetrischen Querschnitten stimmen Schubmittelpunkt und Schwerpunkt überein. Beim U-Profil liegt der Schubmittelpunkt trotz Symmetrieachse außerhalb des Stegs."},

    {"d": 2, "teil": "1", "f": "Warum wird im Stahlbetonbau üblicherweise Torsion ohne Wölbbehinderung betrachtet?",
     "r": "Verwölbung gering, Risse bauen Wölbbehinderung ab",
     "falsch": {"leicht": ["Beton kann keine Schubspannungen aufnehmen"],
                "mittel": ["Die Bewehrung verhindert jede Verwölbung", "Es kommen nur offene Querschnitte vor", "Die Norm verbietet Verwölbung grundsätzlich"],
                "schwer": ["Rissbildung erhöht die Wölbbehinderung deutlich"]},
     "tipp": "Zwei Gründe: Querschnittsform und Rissbildung im Grenzzustand der Tragfähigkeit.",
     "erkl": "Übliche Hohl- und Vollquerschnitte verwölben sich nur gering, und im Grenzzustand der Tragfähigkeit reduziert die Rissbildung die Wölbbehinderung deutlich. Daher genügt die St.-Venantsche Torsion."},

    {"d": 2, "teil": "1", "f": "Wie verhält sich ein längs aufgeschnittenes Rohr bei Verdrehung im Vergleich zum geschlossenen Rohr?",
     "r": "Es verwölbt sich zusätzlich",
     "falsch": {"leicht": ["Es verdreht sich überhaupt nicht"],
                "mittel": ["Es verhält sich genau gleich", "Es ist deutlich torsionssteifer", "Es verformt sich nur durch Biegung"],
                "schwer": ["Es verwölbt sich weniger stark"]},
     "tipp": "Der Schlitz erlaubt eine Verschiebung in Längsrichtung.",
     "erkl": "Beim geschlossenen Rohr entsteht keine zusätzliche Längsverwölbung. Das aufgeschnittene Rohr verwölbt sich bei Verdrehung zusätzlich – die Ränder am Schlitz verschieben sich in Längsrichtung gegeneinander."},

    {"d": 2, "teil": "1", "f": "Was entsteht, wenn die Verwölbung eines tordierten Trägers behindert wird?",
     "r": "Spannungen in Trägerlängsrichtung",
     "falsch": {"leicht": ["Keinerlei zusätzliche Spannungen"],
                "mittel": ["Zusätzliche Auflagerkräfte quer", "Druckspannungen nur im Kern", "Eine größere Verdrillung"],
                "schwer": ["Spannungen nur in Querschnittsebene"]},
     "tipp": "Die Verwölbung ist eine Verschiebung in Längsrichtung.",
     "erkl": "Wird die Verwölbung behindert, entstehen Spannungen in Trägerlängsrichtung. Bei St.-Venantscher Torsion bleiben diese unberücksichtigt."},

    {"d": 3, "teil": "1", "f": "Wie lautet die erste Bredtsche Formel, Gl. (8)?",
     "r": "$\\tau = \\dfrac{T}{t \\cdot 2 \\cdot A_{\\mathrm{k}}}$",
     "falsch": {"mittel": ["$\\tau = \\dfrac{T}{t \\cdot A_{\\mathrm{k}}^2}$", "$\\tau = \\dfrac{T \\cdot 2}{t \\cdot u_{\\mathrm{k}}}$"],
                "schwer": ["$\\tau = \\dfrac{T}{t \\cdot A_{\\mathrm{k}}}$", "$\\tau = \\dfrac{T \\cdot t}{2 \\cdot A_{\\mathrm{k}}}$", "$\\tau = \\dfrac{2 \\cdot T}{t \\cdot A_{\\mathrm{k}}}$"]},
     "tipp": "Gl. (7): Das Konturintegral liefert die doppelte Kernfläche.",
     "erkl": "Aus Gl. (6) $T = \\tau \\cdot t \\oint r \\cdot ds$ und Gl. (7) $\\oint r \\cdot ds = 2 \\cdot A_{\\mathrm{k}}$ folgt $\\tau = \\dfrac{T}{t \\cdot 2 \\cdot A_{\\mathrm{k}}}$."},

    {"d": 3, "teil": "1", "f": "Wie groß ist $I_T$ eines Kreisquerschnitts mit Radius $R$?",
     "r": "$I_T = \\dfrac{\\pi R^4}{2}$",
     "falsch": {"mittel": ["$I_T = \\pi R^2$", "$I_T = \\dfrac{\\pi R^3}{2}$"],
                "schwer": ["$I_T = \\dfrac{\\pi R^4}{4}$", "$I_T = \\dfrac{\\pi D^4}{2}$", "$I_T = \\dfrac{\\pi R^4}{8}$"]},
     "tipp": "Aus Gl. (3) – Integration von $2\\pi r^3$ über den Radius.",
     "erkl": "Gl. (3): $T = G \\cdot \\vartheta \\cdot \\pi \\dfrac{R^4}{2}$, also $I_T = \\pi R^4/2$. $\\pi R^4/4$ ist das Flächenträgheitsmoment für Biegung – ein häufiger Verwechsler."},

    {"d": 3, "teil": "1", "f": "Welcher Zusammenhang gilt nach Gl. (2) am Außenrand des Kreisquerschnitts?",
     "r": "$\\tau = G \\cdot \\vartheta \\cdot R$",
     "falsch": {"mittel": ["$\\tau = E \\cdot \\gamma$", "$\\tau = G / \\gamma$"],
                "schwer": ["$\\tau = G \\cdot \\varphi \\cdot R$", "$\\tau = G \\cdot \\vartheta / R$", "$\\tau = E \\cdot \\vartheta \\cdot R$"]},
     "tipp": "Schubmodul mal Gleitung – und die Gleitung ist Verdrillung mal Radius.",
     "erkl": "Gl. (2): $\\tau = G \\cdot \\gamma$ mit der Gleitung $\\gamma = \\vartheta \\cdot R$ aus Gl. (1). Maßgebend ist die Verdrillung pro Länge $\\vartheta = d\\varphi/dx$, nicht der Verdrehwinkel $\\varphi$."},

    {"d": 3, "teil": "1", "f": "Welchem Ausdruck entspricht das Konturintegral $\\oint r \\cdot ds$ entlang der Wandmittellinie, Gl. (7)?",
     "r": "$2 \\cdot A_{\\mathrm{k}}$",
     "falsch": {"mittel": ["$u_{\\mathrm{k}}$", "$\\pi \\cdot A_{\\mathrm{k}}$"],
                "schwer": ["$A_{\\mathrm{k}}$", "$A_{\\mathrm{k}} / 2$", "$4 \\cdot A_{\\mathrm{k}}$"]},
     "tipp": "Jeder Beitrag $r \\cdot ds$ ist doppelt so groß wie das Dreieck $dA_{\\mathrm{k}}$.",
     "erkl": "Gl. (7): $dA_{\\mathrm{k}} = \\tfrac{1}{2}\\,r \\cdot ds$ – das schmale Dreieck zum Drehmittelpunkt. Über den Umlauf summiert: $\\oint r \\cdot ds = 2 \\cdot A_{\\mathrm{k}}$."},

    {"d": 3, "teil": "1", "f": "Ein Kragträger der Länge $l$ trägt die Streckenlast $p$ mit der Exzentrizität $e$ zum Schubmittelpunkt. Wie groß ist das Torsionsmoment an der Einspannung?",
     "r": "$T = p \\cdot e \\cdot l$",
     "falsch": {"mittel": ["$T = p \\cdot l^2 / 2$", "$T = p \\cdot e$"],
                "schwer": ["$T = p \\cdot e \\cdot l / 2$", "$T = p \\cdot e \\cdot l^2 / 2$", "$T = p \\cdot e^2 \\cdot l$"]},
     "tipp": "Das Streckentorsionsmoment $p \\cdot e$ ist konstant und summiert sich linear auf.",
     "erkl": "Die Last erzeugt das konstante Streckentorsionsmoment $p \\cdot e$. Integriert über die Länge ergibt sich an der Einspannung $T = p \\cdot e \\cdot l$ (linearer Verlauf). $p\\,l^2/2$ wäre das Biegemoment."},
]


if __name__ == "__main__":
    ziel = Path(__file__).resolve().parent.parent / "content" / "01_torsion.json"
    daten = json.loads(ziel.read_text(encoding="utf-8"))
    # Folien im Skript Teil 1 (Zuordnung über den Fragebeginn); zwei frühere Bemessungsfragen gehören inhaltlich zu Teil 1
    FOLIEN = {"Wodurch wird das Torsionsmoment bei St.-Venantscher": "7", "Wie verlaufen die Hauptspannungen um": "12",
              "Wo sind die Hauptspannungen": "12", "Ein abgewinkelter Kragträger trägt": "3", "Auf welchen Punkt ist": "4",
              "Unter welchen Winkeln verlaufen": "12", "Wo ist die Schubspannung im Kreisquerschnitt": "11",
              "Wann fallen Schubmittelpunkt": "4", "Warum wird im Stahlbetonbau": "7", "Wie verhält sich ein längs aufgeschnittenes": "6",
              "Was entsteht, wenn die Verwölbung": "6", "Wie lautet die erste Bredtsche Formel": "15", "Wie groß ist $I_T$": "10–11",
              "Welcher Zusammenhang gilt nach Gl. (2)": "9", "Welchem Ausdruck entspricht das Konturintegral": "14",
              "Ein Kragträger der Länge": "4", "Wie verlaufen die Risse an einem Stahlbetonbalken": "12", "Was ist die Fläche $A_": "14"}
    for q in QUIZ:
        for anfang, folie in FOLIEN.items():
            if q["f"].startswith(anfang):
                q["folie"] = folie
                q["teil"] = "1"
    fehlt = [q["f"][:50] for q in QUIZ if q.get("teil") == "1" and "folie" not in q]
    assert not fehlt, f"Teil-1-Fragen ohne Folie: {fehlt}"
    for q in QUIZ:
        q.setdefault("teil", "B")
    QUIZ.sort(key=lambda q: q["teil"] != "1")
    daten["quiz"] = QUIZ
    ziel.write_text(json.dumps(daten, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(QUIZ)} Fragen geschrieben:",
          {d: sum(q['d'] == d for q in QUIZ) for d in (1, 2, 3)})
