#!/usr/bin/env python3
"""Prüft, dass in den Ausgabe-Widgets kein Zeilen-Template ohne Escaping steht.

Die Zeilen werden aus Formulareingaben zusammengesetzt (Vermerk, Freitext-Orte,
Adressen) und landen per insertAdjacentHTML/innerHTML im Dokument. Ohne das
Präfix html`…` würde eingeschleustes Markup ausgeführt -- im Widget, das mit
requiredAccess "full" Name, Wohnadresse und Belege lesen kann.

Der Test fängt den wahrscheinlichen Rückfall: jemand ergänzt eine Zeile und
vergisst das Präfix.

Was er NICHT fängt (nachgemessen, nicht vermutet):
  * ein Zeilen-Template, das in einem anderen Template steckt
    (html`<table>${rs.map(r => `<tr>…`)}</table>`) -- die Regex paart die
    Backticks falsch und überspringt das innere,
  * Zeilen aus Stringkonkatenation ("<tr><td>" + x + "</td></tr>"),
  * alles hinter einem Backtick, der in einem gewöhnlichen String steht --
    ab da ist die Paarung verschoben.
Ein JS-Parser würde das schließen und wäre länger als die zwei Dateien, die
er prüft. Wer eine der drei Formen einführt, prüft das Escaping von Hand.

    python3 grist/ausgabe/test_escaping.py
"""
import pathlib, re, sys

HIER = pathlib.Path(__file__).resolve().parent

# Template-Literale mit ${...}, die HTML-Tags enthalten -- also gerenderte Zellen.
# Ausgenommen: Literale ohne Interpolation und solche, die nur fertiges HTML
# aus anderen Funktionen einsetzen (dort escapt das innere Template bereits).
TEMPLATE = re.compile(r"`(?:[^`\\]|\\.)*`", re.S)

fehler = []
for datei in ["ausdruck.html", "fahrtenbuch-schnitt.html", "routenlinks.html"]:
    text = (HIER / datei).read_text(encoding="utf-8")
    js = "\n".join(re.findall(r"<script>(.*?)</script>", text, re.S))

    if "const html = " not in js or "const esc = " not in js:
        fehler.append(f"{datei}: esc/html fehlen")
        continue

    for m in TEMPLATE.finditer(js):
        roh = m.group(0)
        if "${" not in roh:
            continue                                  # statisches Gerüst
        if "<td" not in roh and "<tr" not in roh:
            continue                                  # keine Datenzelle
        if js[max(0, m.start() - 4):m.start()].endswith("html"):
            continue                                  # escapt
        zeile = js[:m.start()].count("\n") + 1
        fehler.append(f"{datei}: Zeilen-Template ohne html`` (Skriptzeile {zeile})")

if fehler:
    sys.exit("FEHLER\n" + "\n".join("  " + f for f in fehler))
print("OK: alle Zeilen-Templates escapen ihre Werte.")
