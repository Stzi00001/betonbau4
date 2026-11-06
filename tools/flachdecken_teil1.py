"""Flachdecken, Skript Teil 1 „Grundlagen und Schnittgrößenermittlung“ – Quiz, Karteikarten, Formeln, Paare,
Mindmap und Übungsaufgaben für content/02_flachdecken.json.

Quelle: Vorlesungsskript Betonbau IV, Flachdecken Teil 1 (nach Finckh, Stahlbetonkonstruktion, Kap. Flachdecken,
S. 268–273; DAfStb-Heft 631). Folienangaben wie im Skript; Texte sind eigene Formulierungen, Abbildungen werden
nicht übernommen.

Aufruf: python tools/flachdecken_teil1.py   (mehrfach ausführbar, ersetzt jeweils die Teil-1-Inhalte)
"""
import json
from pathlib import Path

ZIEL = Path(__file__).resolve().parent.parent / "content" / "02_flachdecken.json"
T = "1"

TEILE = [{"id": "1", "titel": "Teil 1 · Grundlagen und Schnittgrößenermittlung", "quelle": "Skript Flachdecken Teil 1"}]

lxly = r"\dfrac{l_x}{l_y}"

# ---------------------------------------------------------------- Karteikarten (v = Vorderseite, r = Rückseite)
KARTEN = [
    ("3", "Platten als flächenhafte Tragwerke",
     "Platten werden senkrecht zu ihrer Mittelebene belastet; es entstehen Biegemomente und Querkräfte. Das Tragverhalten hängt vor allem von Art und Anordnung der Lagerung ab."),
    ("3–4", "Einteilung nach dem Tragverhalten",
     "Einachsig gespannte Platten (Lastabtrag in eine Richtung), mehrachsig gespannte Platten (Lastabtrag in zwei Richtungen, z. B. vierseitig gelagert) und punktgestützte Platten (Lagerung auf Stützen)."),
    ("5", "Mindestdicken von Ortbetonplatten",
     "Ohne rechnerisch erforderliche Querkraftbewehrung $h \\ge 70\\,\\mathrm{mm}$. Mit Querkraftbewehrung $h \\ge 200\\,\\mathrm{mm}$; wird sie nur durch aufgebogene Stäbe abgedeckt, genügen $h \\ge 160\\,\\mathrm{mm}$."),
    ("5", "Wann darf als Platte gerechnet werden?",
     "Kleinste Stützweite und Bauteilbreite müssen jeweils mindestens das Fünffache der Plattendicke betragen: $l_{\\min} \\ge 5\\,h$ und $b \\ge 5\\,h$."),
    ("6", "Querrichtung einachsig gespannter Platten",
     "Durch die behinderte Querdehnung entstehen auch Momente quer zur Hauptspannrichtung. Sie werden mit einer Querbewehrung von mindestens 20 % der Längsbewehrung aufgenommen: $a_{s,q} \\ge 0{,}2\\,a_{s,l}$."),
    ("7", "Arten punktgestützter Platten",
     "Unterzugdecke (Platte auf Unterzügen zwischen den Stützen), Pilzdecke (Stützenkopf pilzförmig verstärkt) und Flachdecke (Platte liegt direkt auf den Stützen)."),
    ("8", "Was kennzeichnet eine Flachdecke?",
     "Die Platte wird unmittelbar durch Stützen gelagert – ohne Unterzüge und ohne Stützenkopfverstärkung. Die Last geht über die Platte direkt in die Stützen; dort konzentrieren sich Biegemomente und Querkräfte."),
    ("9", "Vorteile von Flachdecken",
     "Geringe Konstruktionshöhe, geringer Schalungsaufwand, glatte Deckenuntersicht und einfache Führung der Haustechnik unter der Decke. Dem steht oft ein höherer Betonstahlbedarf gegenüber."),
    ("10", "Nachteile von Flachdecken",
     "Höherer Bewehrungs- und Betonbedarf und größeres Eigengewicht, komplexes räumliches Tragverhalten, große Momente und Querkräfte im Stützenbereich und tendenziell größere Durchbiegungen."),
    ("10", "Was bestimmt die Deckendicke einer Flachdecke?",
     "Die Begrenzung der Durchbiegungen im Gebrauchszustand und eine ausreichende Tragfähigkeit gegen Durchstanzen."),
    ("11–12", "Hauptmomente einer Flachdecke",
     "Im Feld überwiegend positive Momente in $x$- und $y$-Richtung. Über den Stützen sind die Hauptmomente negativ und radial bzw. tangential gerichtet – sie erzeugen Zug an der Plattenoberseite."),
    ("12", "Bewehrungsrichtung in Flachdecken",
     "Obwohl die Hauptmomente an der Stütze radial und tangential verlaufen, wird praktisch meist eine orthogonale Bewehrung in beiden Richtungen eingelegt."),
    ("13", "Besonderheiten der punktförmigen Lagerung",
     "Der Lastabtrag unterscheidet sich deutlich von liniengelagerten Platten: Nahe der Stützen ändern sich die Momentenrichtungen räumlich, und die größten Momente können in Richtung der längeren Stützweite auftreten."),
    ("15", "Schnittgrößen in der Praxis",
     "Flachdecken sind hochgradig statisch unbestimmt; in der Praxis rechnet man meist mit der Finite-Elemente-Methode. Näherungsverfahren (Ersatzrahmen, Gurtstreifen, Lasteinzugsflächen) dienen der Vorbemessung und der Plausibilitätskontrolle."),
    ("16", "Gurtstreifenmethode – Voraussetzungen",
     "Näherungsverfahren für mehrfeldrige Flachdecken mit rechteckigem Stützenraster. Anwendbar, wenn das Stützweitenverhältnis $0{,}8 \\le l_x/l_y \\le 1{,}25$ eingehalten ist."),
    ("16–17", "Ersatzrahmen",
     "Die Platte wird in sich kreuzende Streifenscharen zerlegt, die als Durchlaufträger bzw. Rahmen mit den Stützen berechnet werden. Die Streifenbreite entspricht dem Stützenachsabstand quer zur jeweiligen Tragrichtung."),
    ("18–19", "Feld- und Gurtstreifen",
     "Jedes Feld wird für beide Tragrichtungen geteilt: ein Feldstreifen der Breite $0{,}6\\,l_y$ in der Mitte und zwei halbe Gurtstreifen von je $0{,}2\\,l_y$ über den Stützenachsen. Feld- und Stützmomente werden unterschiedlich auf die Streifen verteilt."),
    ("19", "Womit wird bemessen?",
     "Mit Momenten je laufendem Meter Plattenbreite: das auf einen Streifen entfallende Moment geteilt durch die Streifenbreite."),
    ("20", "Lastansatz am Ersatzrahmen",
     "Die Schnittgrößen werden für jede der beiden Haupttragrichtungen getrennt ermittelt – jeweils mit der gesamten Last, feldweise in ungünstigster Stellung. Danach werden die Momente auf Feld- und Gurtstreifen verteilt."),
    ("21", "Auflagerkräfte der Stützen",
     "Das Ersatzrahmenverfahren eignet sich dafür nur eingeschränkt. Zur Abschätzung werden die Lasten über Lasteinzugsflächen bzw. Sektoren den Stützen zugeordnet."),
    ("21–22", "Lasteinzugsflächen und Sektoren",
     "Innenstützen haben näherungsweise kreisförmige Einzugsbereiche, Rand- und Eckstützen entsprechende Teilbereiche. Die Aufteilung in Sektoren erlaubt zusätzlich eine differenzierte Betrachtung der Querkraftverteilung um die Stütze."),
]

FORMELN = [
    {"name": "Querbewehrung einachsig gespannter Platten", "f": "a_{s,q} \\ge 0{,}2 \\cdot a_{s,l}",
     "e": "$a_{s,l}$ Längsbewehrung, $a_{s,q}$ Querbewehrung", "folie": "6"},
    {"name": "Mindestdicke ohne Querkraftbewehrung", "f": "h \\ge 70\\,\\mathrm{mm}", "e": "Ortbetonplatte", "folie": "5"},
    {"name": "Mindestdicke mit Querkraftbewehrung", "f": "h \\ge 200\\,\\mathrm{mm} \\quad (160\\,\\mathrm{mm} \\text{ bei nur aufgebogenen Stäben})",
     "e": "rechnerisch erforderliche Querkraftbewehrung", "folie": "5"},
    {"name": "Plattenberechnung zulässig", "f": "l_{\\min} \\ge 5\\,h, \\qquad b \\ge 5\\,h", "e": "kleinste Stützweite und Bauteilbreite", "folie": "5"},
    {"name": "Anwendungsgrenze Gurtstreifenmethode", "f": "0{,}8 \\le " + lxly + " \\le 1{,}25", "e": "rechteckiges Stützenraster", "folie": "16"},
    {"name": "Breite des Feldstreifens", "f": "b_{F} = 0{,}6 \\cdot l_y", "e": "Feldmitte, je Tragrichtung", "folie": "19"},
    {"name": "Breite eines halben Gurtstreifens", "f": "b_{G/2} = 0{,}2 \\cdot l_y", "e": "beidseits der Stützenachse, zusammen $0{,}4\\,l_y$", "folie": "19"},
    {"name": "Moment je Meter Plattenbreite", "f": "m = \\dfrac{M_{\\text{Streifen}}}{b_{\\text{Streifen}}}", "e": "Bemessungsgröße für die Biegebewehrung", "folie": "19"},
]

PAARE = [
    ("Flachdecke", "Platte direkt auf Stützen, ohne Unterzüge", "8"),
    ("Pilzdecke", "Stützenkopf pilzförmig verstärkt", "7"),
    ("Unterzugdecke", "Platte auf Unterzügen zwischen den Stützen", "7"),
    ("$0{,}8 \\le l_x/l_y \\le 1{,}25$", "Grenze der Gurtstreifenmethode", "16"),
    ("$0{,}6\\,l_y$", "Breite des Feldstreifens", "19"),
    ("$0{,}2\\,l_y$", "Breite eines halben Gurtstreifens", "19"),
    ("$a_{s,q} \\ge 0{,}2\\,a_{s,l}$", "Querbewehrung einachsig gespannter Platten", "6"),
    ("$h \\ge 200\\,\\mathrm{mm}$", "Mindestdicke mit Querkraftbewehrung", "5"),
    ("negative Stützmomente", "Zug an der Plattenoberseite", "12"),
    ("Lasteinzugsfläche", "Abschätzung der Stützenkräfte", "21"),
    ("FEM", "übliche Schnittgrößenermittlung in der Praxis", "15"),
    ("Durchstanzen", "maßgebend für die Deckendicke", "10"),
]

MINDMAP = {"t": "Flachdecken", "c": [
    {"t": "Teil 1 · Grundlagen", "folie": "3–23", "c": [
        {"t": "Platten", "folie": "3–6", "c": [{"t": "einachsig / mehrachsig / punktgestützt"}, {"t": "$h \\ge 70$ bzw. $200\\,\\mathrm{mm}$"},
                                                {"t": "$l_{\\min}, b \\ge 5\\,h$"}, {"t": "Querbewehrung $\\ge 0{,}2\\,a_{s,l}$"}]},
        {"t": "Flachdecke", "folie": "7–10", "c": [{"t": "direkt auf Stützen"}, {"t": "Vorteile: flach, wenig Schalung"},
                                                   {"t": "Nachteile: Stützbereich, Durchbiegung"}, {"t": "Dicke: Durchbiegung, Durchstanzen"}]},
        {"t": "Hauptmomente", "folie": "11–13", "c": [{"t": "Feld: positiv in $x$ und $y$"}, {"t": "Stütze: negativ, radial/tangential"},
                                                      {"t": "Bewehrung meist orthogonal"}]},
        {"t": "Schnittgrößen", "folie": "14–20", "c": [{"t": "Praxis: FEM"}, {"t": "Ersatzrahmen je Richtung, volle Last"},
                                                       {"t": "Gurtstreifen: $0{,}8 \\le l_x/l_y \\le 1{,}25$"},
                                                       {"t": "Feldstreifen $0{,}6\\,l_y$, Gurtstreifen $2 \\times 0{,}2\\,l_y$"}]},
        {"t": "Auflagerkräfte", "folie": "21–22", "c": [{"t": "Lasteinzugsflächen"}, {"t": "Sektoren je Stütze"}]},
    ]}]}

# ---------------------------------------------------------------- Quiz
def q(d, folie, f, r, leicht, mittel, schwer, tipp, erkl):
    return {"d": d, "teil": T, "folie": folie, "f": f, "r": r,
            "falsch": {k: v for k, v in (("leicht", leicht), ("mittel", mittel), ("schwer", schwer)) if v}, "tipp": tipp, "erkl": erkl}


QUIZ = [
    q(1, "8", "Worauf liegt eine Flachdecke auf?", "Direkt auf Stützen",
      ["Auf Seilen", "Auf dem Erdreich"], ["Auf Unterzügen", "Auf durchgehenden Wänden"], [],
      "Der Name verrät es: unten ist sie flach.", "Bei einer Flachdecke wird die Platte unmittelbar durch Stützen gelagert, ohne Unterzüge und ohne Stützenkopfverstärkung."),
    q(1, "3", "Wie werden Platten belastet?", "Senkrecht zu ihrer Mittelebene",
      ["Nur durch Wind", "Nur durch Temperatur"], ["Nur durch Normalkraft"], ["Parallel zu ihrer Mittelebene", "Schräg zu ihrer Mittelebene"],
      "Denk an eine Decke mit Möbeln darauf.", "Platten tragen Lasten senkrecht zur Mittelebene ab; dabei entstehen Biegemomente und Querkräfte."),
    q(1, "9", "Welcher ist ein Vorteil von Flachdecken?", "Glatte Deckenuntersicht",
      ["Kein Beton nötig", "Keine Bewehrung nötig"], ["Kleinere Durchbiegungen", "Weniger Bewehrung"], [],
      "Schau von unten an die Decke.", "Flachdecken haben eine glatte Untersicht, geringe Konstruktionshöhe und wenig Schalungsaufwand; Haustechnik lässt sich einfach führen."),
    q(1, "10", "Wo treten bei einer Flachdecke besonders große Querkräfte auf?", "Im Bereich der Stützen",
      ["An der Fassade", "Im Dach"], ["In Feldmitte", "Am freien Plattenrand"], [],
      "Wo wird die ganze Last abgegeben?", "Die Last fließt über die Platte zu den Stützen; dort konzentrieren sich Momente und Querkräfte."),
    q(1, "15", "Womit werden Schnittgrößen von Flachdecken in der Praxis meist ermittelt?", "Finite-Elemente-Methode",
      ["Handskizze", "Schätzung nach Erfahrung"], ["Nur Ersatzrahmenverfahren", "Nur Lasteinzugsflächen"], [],
      "Hochgradig statisch unbestimmt – da hilft der Rechner.", "Flachdecken sind hochgradig statisch unbestimmt; Standard ist FEM. Näherungsverfahren dienen der Vorbemessung und Kontrolle."),
    q(1, "7", "Wodurch unterscheidet sich eine Pilzdecke von einer Flachdecke?", "Verstärkten Stützenkopf",
      ["Andere Betonfarbe", "Keine Stützen"], ["Unterzüge zwischen den Stützen", "Geringere Plattendicke"], [],
      "Denk an die Form eines Pilzes.", "Bei der Pilzdecke ist der Stützenkopf pilzförmig verstärkt; die Flachdecke hat keine Verstärkung."),
    q(1, "12", "Welche Plattenseite wird über einer Innenstütze auf Zug beansprucht?", "Die Oberseite",
      ["Keine Seite", "Die Stütze selbst"], ["Die Unterseite", "Beide Seiten gleich"], [],
      "Über der Stütze ist das Moment negativ.", "Die negativen Stützmomente erzeugen Zug an der Plattenoberseite – dort liegt die Stützbewehrung."),
    q(1, "19", "Womit wird die Biegebewehrung von Platten bemessen?", "Momenten je laufendem Meter",
      ["Momenten je Stütze", "Momenten je Geschoss"], ["Gesamtmoment des Feldes", "Moment je Quadratmeter"], [],
      "Platten bemisst man für einen Streifen von 1 m.", "Bemessen wird mit dem Moment je Meter Plattenbreite: Streifenmoment geteilt durch Streifenbreite."),
    q(2, "5", "Welche Mindestdicke braucht eine Ortbetonplatte mit rechnerisch erforderlicher Querkraftbewehrung?", "$h \\ge 200\\,\\mathrm{mm}$",
      ["$h \\ge 20\\,\\mathrm{mm}$"], ["$h \\ge 70\\,\\mathrm{mm}$", "$h \\ge 400\\,\\mathrm{mm}$"], ["$h \\ge 160\\,\\mathrm{mm}$", "$h \\ge 180\\,\\mathrm{mm}$"],
      "160 mm gelten nur bei aufgebogenen Stäben.", "Ohne Querkraftbewehrung 70 mm, mit Querkraftbewehrung 200 mm; nur aufgebogene Stäbe: 160 mm."),
    q(2, "5", "Ab welcher Bauteilgröße darf mit Plattenansätzen gerechnet werden?", "Kleinste Stützweite und Breite $\\ge 5\\,h$",
      ["Immer, unabhängig von der Größe"], ["Stützweite $\\ge 2\\,h$", "Breite $\\ge h$"], ["Kleinste Stützweite und Breite $\\ge 3\\,h$", "Größte Stützweite und Breite $\\ge 5\\,h$"],
      "Das Fünffache der Dicke.", "Kleinste Stützweite und Bauteilbreite müssen jeweils mindestens das Fünffache der Dicke betragen."),
    q(2, "6", "Wie groß muss die Querbewehrung einachsig gespannter Platten mindestens sein?", "$a_{s,q} \\ge 0{,}2\\,a_{s,l}$",
      ["Keine Querbewehrung nötig"], ["$a_{s,q} \\ge a_{s,l}$", "$a_{s,q} \\ge 2\\,a_{s,l}$"], ["$a_{s,q} \\ge 0{,}1\\,a_{s,l}$", "$a_{s,q} \\ge 0{,}5\\,a_{s,l}$"],
      "Ein Fünftel der Längsbewehrung.", "Wegen der behinderten Querdehnung entstehen Quermomente; die Querbewehrung beträgt mindestens 20 % der Längsbewehrung."),
    q(2, "10", "Was ist für die Deckendicke einer Flachdecke maßgebend?", "Durchbiegung und Durchstanzen",
      ["Brandschutz der Fassade"], ["Nur das Eigengewicht", "Nur die Feldmomente"], ["Durchbiegung und Rissbreite", "Durchstanzen und Feldbiegung"],
      "Zwei Nachweise – einer im Gebrauch, einer an der Stütze.", "Maßgebend sind die Begrenzung der Durchbiegung im Gebrauchszustand und die Tragfähigkeit gegen Durchstanzen."),
    q(2, "11–12", "Wie sind die Hauptmomente einer Flachdecke über der Stütze gerichtet?", "Radial und tangential",
      ["Gar nicht – dort ist $m = 0$"], ["Nur in $x$-Richtung", "Nur parallel zum Plattenrand"], ["Diagonal unter 45° zum Raster", "Nur in Richtung der kürzeren Spannweite"],
      "Denk an Speichen und Ringe um die Stütze.", "Im Stützenbereich sind die Hauptmomente negativ und radial bzw. tangential gerichtet; bewehrt wird trotzdem meist orthogonal."),
    q(2, "16", "In welchem Bereich muss das Stützweitenverhältnis für die Gurtstreifenmethode liegen?", "$0{,}8 \\le l_x/l_y \\le 1{,}25$",
      ["Beliebig"], ["$0{,}5 \\le l_x/l_y \\le 2{,}0$", "$l_x/l_y = 1{,}0$ genau"], ["$0{,}75 \\le l_x/l_y \\le 1{,}33$", "$0{,}8 \\le l_x/l_y \\le 1{,}5$"],
      "Die Grenzen sind Kehrwerte voneinander.", "Die Gurtstreifenmethode setzt ein rechteckiges Raster mit $0{,}8 \\le l_x/l_y \\le 1{,}25$ voraus ($1{,}25 = 1/0{,}8$)."),
    q(2, "19", "Wie breit ist der Feldstreifen eines Feldes?", "$0{,}6\\,l_y$",
      ["$l_y$"], ["$0{,}2\\,l_y$", "$0{,}4\\,l_y$"], ["$0{,}5\\,l_y$", "$0{,}8\\,l_y$"],
      "Zusammen mit zwei halben Gurtstreifen ergibt sich die ganze Feldbreite.", "Feldstreifen $0{,}6\\,l_y$ plus zwei halbe Gurtstreifen $2 \\cdot 0{,}2\\,l_y$ ergeben $l_y$."),
    q(2, "20", "Welche Last wird je Tragrichtung am Ersatzrahmen angesetzt?", "Die gesamte Last, feldweise ungünstig",
      ["Keine Verkehrslast"], ["Die halbe Last je Richtung", "Nur das Eigengewicht"], ["Die Last nach Steifigkeiten aufgeteilt", "Die gesamte Last, immer in allen Feldern"],
      "Jede Richtung muss die ganze Last tragen können.", "In jeder Richtung wird die gesamte Last angesetzt – feldweise in ungünstigster Stellung – und danach auf Feld- und Gurtstreifen verteilt."),
    q(2, "13", "Wo können bei punktgestützten Platten die größten Biegemomente auftreten?", "In Richtung der längeren Stützweite",
      ["Immer am Plattenrand"], ["Nur in Feldmitte quer", "Unter 45° zum Raster"], ["In Richtung der kürzeren Stützweite", "Quer zur längeren Stützweite"],
      "Anders als bei vierseitig gelagerten Platten!", "Bei punktgestützten Platten können die größten Momente in Richtung der längeren Stützweite liegen – ein Unterschied zu liniengelagerten Platten."),
    q(3, "21", "Wofür ist das Ersatzrahmenverfahren nur eingeschränkt geeignet?", "Ermittlung der Stützenkräfte",
      [], ["Ermittlung der Feldmomente", "Ermittlung der Stützmomente"], ["Verteilung auf Feld- und Gurtstreifen", "Biegebewehrung in beiden Richtungen"],
      "Dafür nimmt man Lasteinzugsflächen.", "Für die Auflagerkräfte der Stützen ist das Ersatzrahmenverfahren nur eingeschränkt geeignet; abgeschätzt wird über Lasteinzugsflächen bzw. Sektoren."),
    q(3, "21–22", "Welche Form hat der Lasteinzugsbereich einer Innenstütze näherungsweise?", "Kreisförmig",
      ["Dreieckig"], ["Streifenförmig in einer Richtung", "Nur ein Viertel des Feldes"], ["Quadratisch über ein ganzes Feld", "Rautenförmig"],
      "Die Stütze sammelt die Last von allen Seiten.", "Innenstützen besitzen näherungsweise kreisförmige Einzugsbereiche; am Rand und an Ecken entstehen entsprechende Teilbereiche."),
    q(3, "18–19", "Wie werden Feld- und Stützmomente auf Feld- und Gurtstreifen verteilt?", "Unterschiedlich – Stützmomente stärker in den Gurtstreifen",
      [], ["Gleichmäßig über die ganze Breite", "Nur auf den Feldstreifen"], ["Für Feld- und Stützmomente gleich", "Stützmomente vor allem in den Feldstreifen"],
      "Über der Stütze konzentrieren sich die Momente.", "Die Verteilung ist für positive Feld- und negative Stützmomente unterschiedlich; die Stützmomente konzentrieren sich im Gurtstreifen über der Stützenachse."),
    q(3, "16–17", "Wie werden Flachdecken beim Ersatzrahmenverfahren zerlegt?", "Kreuzende Streifen als Ersatzrahmen",
      [], ["In einzelne Felder als Einfeldplatten", "In Kragplatten um jede Stütze"], ["Streifen nur in einer Richtung", "Radiale Sektoren um die Stützen"],
      "Zwei Richtungen, jede mit Streifen über die Stützenreihen.", "Die Platte wird in sich kreuzende Streifenscharen aufgeteilt; jede wird als Durchlaufträger bzw. Ersatzrahmen mit den Stützen berechnet."),
    q(3, "16", "Wie breit ist ein Streifen des Ersatzrahmens?", "Stützenachsabstand quer zur Tragrichtung",
      [], ["Eine Plattendicke", "1 m"], ["Stützenachsabstand in Tragrichtung", "Halber Stützenachsabstand"],
      "Der Rahmen nimmt alles zwischen zwei Feldmitten auf.", "Die Streifenbreite entspricht dem Stützenachsabstand quer zur jeweiligen Tragrichtung."),
    q(3, "9–10", "Was steht dem geringeren Schalungsaufwand einer Flachdecke meist gegenüber?", "Höherer Betonstahlbedarf",
      [], ["Höhere Schalungskosten", "Mehr Unterzüge"], ["Geringere Deckendicke", "Weniger Eigengewicht"],
      "Was braucht die Platte an den Stützen mehr?", "Flachdecken sparen Schalung, brauchen aber mehr Bewehrung, Beton und haben mehr Eigengewicht."),
    q(3, "5", "Welche Mindestdicke gilt, wenn die erforderliche Querkraftbewehrung nur aus aufgebogenen Stäben besteht?", "$h \\ge 160\\,\\mathrm{mm}$",
      [], ["$h \\ge 70\\,\\mathrm{mm}$", "$h \\ge 300\\,\\mathrm{mm}$"], ["$h \\ge 200\\,\\mathrm{mm}$", "$h \\ge 180\\,\\mathrm{mm}$"],
      "Weniger als bei Bügeln.", "Mit Querkraftbewehrung gelten 200 mm; nur aufgebogene Stäbe erlauben 160 mm."),
]

# ---------------------------------------------------------------- Übungsaufgaben (Zufallswerte)
m_, mm_ = r"\,\mathrm{m}", r"\,\mathrm{mm}"
AUFGABEN = [
    {"titel": "Gurtstreifenmethode anwendbar?", "teil": T,
     "text": "Eine Flachdecke hat ein rechteckiges Stützenraster mit $l_x = #lx:2#\\,\\mathrm{m}$ und $l_y = #ly:2#\\,\\mathrm{m}$. Prüfen Sie, ob die Gurtstreifenmethode angewendet werden darf, und geben Sie für die $x$-Richtung die Breiten von Feld- und Gurtstreifen an.",
     "params": {"lx": {"min": 5.0, "max": 8.0, "step": 0.25}, "ly": {"min": 5.0, "max": 8.0, "step": 0.25}},
     "schritte": [
         {"titel": "Stützweitenverhältnis", "folie": "16", "text": "Die Gurtstreifenmethode setzt ein annähernd quadratisches Raster voraus.",
          "formel": ["0{,}8 \\le " + lxly + " \\le 1{,}25"],
          "einsetzen": [r"\dfrac{l_x}{l_y} = \dfrac{#lx:2#\,\mathrm{m}}{#ly:2#\,\mathrm{m}} = #v:3#",
                        {"wenn": "v >= 0.8 && v <= 1.25", "t": r"\quad\checkmark\ \text{Gurtstreifenmethode anwendbar}"},
                        {"wenn": "!(v >= 0.8 && v <= 1.25)", "t": r"\quad\text{nicht anwendbar – Ersatzrahmen bzw. FEM}"}],
          "werte": [{"id": "v", "expr": "lx/ly", "d": 3, "frage": True, "label": "l_x/l_y", "einheit": "–"}]},
         {"titel": "Feldstreifen", "folie": "19", "text": "Die Streifen der $x$-Richtung liegen nebeneinander quer zur Tragrichtung, also über die Breite $l_y$.",
          "formel": ["b_F = 0{,}6 \\cdot l_y"], "einsetzen": [r"b_F = 0{,}6 \cdot #ly:2#\,\mathrm{m} = #bF:2#\,\mathrm{m}"],
          "werte": [{"id": "bF", "expr": "0.6*ly", "d": 2, "frage": True, "label": "b_F", "einheit": "m"}]},
         {"titel": "Gurtstreifen", "folie": "19", "text": "Beidseits der Stützenachse liegt je ein halber Gurtstreifen.",
          "formel": ["b_{G/2} = 0{,}2 \\cdot l_y, \\qquad b_G = 2 \\cdot b_{G/2}"],
          "einsetzen": [r"b_{G/2} = 0{,}2 \cdot #ly:2#\,\mathrm{m} = #bG2:2#\,\mathrm{m}, \qquad b_G = 2 \cdot #bG2:2#\,\mathrm{m} = #bG:2#\,\mathrm{m}"],
          "werte": [{"id": "bG2", "expr": "0.2*ly", "d": 2, "frage": True, "label": "b_{G/2}", "einheit": "m"}, {"id": "bG", "expr": "2*bG2", "d": 2}]},
     ]},
    {"titel": "Moment je Meter im Streifen", "teil": T,
     "text": "Aus dem Ersatzrahmen in $x$-Richtung entfällt auf den Gurtstreifen über einer Innenstütze das Stützmoment $M_G = #MG:0#\\,\\mathrm{kNm}$, auf den Feldstreifen $M_F = #MF:0#\\,\\mathrm{kNm}$. Die Stützweite quer dazu beträgt $l_y = #ly:2#\\,\\mathrm{m}$. Bestimmen Sie die Bemessungsmomente je Meter Plattenbreite.",
     "params": {"MG": {"min": 120, "max": 300, "step": 10}, "MF": {"min": 30, "max": 90, "step": 5}, "ly": {"min": 5.0, "max": 8.0, "step": 0.25}},
     "schritte": [
         {"titel": "Streifenbreiten", "folie": "19", "formel": ["b_G = 2 \\cdot 0{,}2 \\cdot l_y = 0{,}4 \\cdot l_y, \\qquad b_F = 0{,}6 \\cdot l_y"],
          "einsetzen": [r"b_G = 0{,}4 \cdot #ly:2#\,\mathrm{m} = #bG:2#\,\mathrm{m}, \qquad b_F = 0{,}6 \cdot #ly:2#\,\mathrm{m} = #bF:2#\,\mathrm{m}"],
          "werte": [{"id": "bG", "expr": "0.4*ly", "d": 2, "frage": True, "label": "b_G", "einheit": "m"}, {"id": "bF", "expr": "0.6*ly", "d": 2}]},
         {"titel": "Moment je Meter im Gurtstreifen", "folie": "19", "text": "Das Streifenmoment wird gleichmäßig über die Streifenbreite verteilt.",
          "formel": ["m_G = \\dfrac{M_G}{b_G}"], "einsetzen": [r"m_G = \dfrac{#MG:0#\,\mathrm{kNm}}{#bG:2#\,\mathrm{m}} = #mG:1#\,\mathrm{kNm/m}"],
          "werte": [{"id": "mG", "expr": "MG/bG", "d": 1, "frage": True, "label": "m_G", "einheit": "kNm/m"}]},
         {"titel": "Moment je Meter im Feldstreifen", "folie": "19",
          "formel": ["m_F = \\dfrac{M_F}{b_F}"], "einsetzen": [r"m_F = \dfrac{#MF:0#\,\mathrm{kNm}}{#bF:2#\,\mathrm{m}} = #mF:1#\,\mathrm{kNm/m}"],
          "werte": [{"id": "mF", "expr": "MF/bF", "d": 1, "frage": True, "label": "m_F", "einheit": "kNm/m"}]},
         {"titel": "Vergleich", "folie": "12", "text": "Über der Stütze konzentrieren sich die negativen Momente – der Gurtstreifen braucht deutlich mehr obere Bewehrung je Meter.",
          "formel": ["\\dfrac{m_G}{m_F}"], "einsetzen": [r"\dfrac{m_G}{m_F} = \dfrac{#mG:1#}{#mF:1#} = #r:2#"],
          "werte": [{"id": "r", "expr": "mG/mF", "d": 2}]},
     ]},
    {"titel": "Mindestdicke und Querbewehrung", "teil": T,
     "text": "Eine einachsig gespannte Ortbetonplatte hat die Dicke $h = #h:0#\\,\\mathrm{mm}$, die kleinste Stützweite $l = #l:2#\\,\\mathrm{m}$ und eine erforderliche Längsbewehrung $a_{s,l} = #asl:2#\\,\\mathrm{cm^2/m}$. Querkraftbewehrung ist rechnerisch #qtxt#. Prüfen Sie die Mindestdicke und die Anwendbarkeit der Plattentheorie und bestimmen Sie die Querbewehrung.",
     "params": {"h": {"werte": [160, 180, 200, 220, 240]}, "l": {"min": 3.5, "max": 6.5, "step": 0.25}, "asl": {"min": 3.0, "max": 8.0, "step": 0.25},
                "qb": {"werte": [0, 1]}},
     "schritte": [
         {"titel": "Mindestdicke", "folie": "5", "text": "Mit rechnerisch erforderlicher Querkraftbewehrung (Bügel) mindestens 200 mm, sonst 70 mm.",
          "formel": ["h \\ge h_{\\min} = \\begin{cases} 70\\,\\mathrm{mm} & \\text{ohne Querkraftbewehrung} \\\\ 200\\,\\mathrm{mm} & \\text{mit Querkraftbewehrung} \\end{cases}"],
          "einsetzen": [r"h = #h:0#\,\mathrm{mm} \ge h_{\min} = #hmin:0#\,\mathrm{mm}",
                        {"wenn": "h >= hmin", "t": r"\quad\checkmark"}, {"wenn": "h < hmin", "t": r"\quad\text{nicht erfüllt – Platte dicker ausführen}"}],
          "werte": [{"id": "qtxt", "expr": "qb ? 'erforderlich (Bügel)' : 'nicht erforderlich'"}, {"id": "hmin", "expr": "qb ? 200 : 70", "d": 0}]},
         {"titel": "Plattentheorie anwendbar?", "folie": "5", "formel": ["l_{\\min} \\ge 5 \\cdot h"],
          "einsetzen": [r"5 \cdot #hm:3#\,\mathrm{m} = #l5:2#\,\mathrm{m} \le l = #l:2#\,\mathrm{m}",
                        {"wenn": "l >= l5", "t": r"\quad\checkmark"}, {"wenn": "l < l5", "t": r"\quad\text{nicht erfüllt – als Balken bzw. Scheibe rechnen}"}],
          "werte": [{"id": "hm", "expr": "h/1000", "d": 3}, {"id": "l5", "expr": "5*hm", "d": 2, "frage": True, "label": "5\\,h", "einheit": "m"}]},
         {"titel": "Querbewehrung", "folie": "6", "formel": ["a_{s,q} \\ge 0{,}2 \\cdot a_{s,l}"],
          "einsetzen": [r"a_{s,q} = 0{,}2 \cdot #asl:2#\,\mathrm{cm^2/m} = #asq:2#\,\mathrm{cm^2/m}"],
          "werte": [{"id": "asq", "expr": "0.2*asl", "d": 2, "frage": True, "label": "a_{s,q}", "einheit": "cm²/m"}]},
     ]},
]


def main():
    d = json.loads(ZIEL.read_text(encoding="utf-8"))
    d["status"] = "teilweise"
    d["statusText"] = "Skript Teil 1 (Grundlagen und Schnittgrößenermittlung) ist eingearbeitet – Folien wie im Skript. Weitere Teile folgen."
    d["teile"] = TEILE
    d["karten"] = [{"v": v, "r": r, "folie": f, "teil": T} for f, v, r in KARTEN]
    d["formeln"] = [{**x, "teil": T} for x in FORMELN]
    d["paare"] = [{"a": a, "b": b, "folie": f, "teil": T} for a, b, f in PAARE]
    d["mindmap"] = MINDMAP
    d["quiz"] = QUIZ
    d["aufgaben"] = AUFGABEN
    ZIEL.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Flachdecken Teil 1: {len(QUIZ)} Quizfragen, {len(KARTEN)} Karten, {len(FORMELN)} Formeln, {len(PAARE)} Paare, {len(AUFGABEN)} Aufgaben")


if __name__ == "__main__":
    main()
