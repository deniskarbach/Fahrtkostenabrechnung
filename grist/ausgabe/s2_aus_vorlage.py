#!/usr/bin/env python3
"""Erzeugt den S2-Tabellenblock von ausdruck.html aus dem XLSX-Blatt "S2".

S2 ist ein amtliches Formular -- Ränder, Füllungen, Schriftgrößen,
Zeilenhöhen und Zellverbünde werden deshalb Zelle für Zelle aus der Vorlage
übernommen statt nachgebaut. Ändert sich die Vorlage, dieses Skript erneut
laufen lassen und die Ausgabe in ausdruck.html zwischen <table class="s2">
und </table> einsetzen -- nicht von Hand nachziehen.

    python3 grist/ausgabe/s2_aus_vorlage.py > /tmp/s2.html

Braucht ReisekostenabrechnungFINAL.xlsx im Repo-Wurzelverzeichnis. Die Datei
ist per .gitignore ausgeschlossen (öffentliches Repo), behördenspezifische
Zellen werden beim Erzeugen geschwärzt -- siehe SCHWAERZEN.

    python3 grist/ausgabe/s2_aus_vorlage.py --fingerabdruecke   # nach Vorlagenwechsel
"""
import hashlib
import os
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import openpyxl
from openpyxl.cell.rich_text import CellRichText, TextBlock

# S2_VORLAGE überschreibt den Pfad — braucht test_schwaerzung.py, um die
# Wächter gegen manipulierte Kopien der Vorlage laufen zu lassen.
VORLAGE = pathlib.Path(os.environ.get("S2_VORLAGE") or
                       pathlib.Path(__file__).resolve().parents[2]
                       / "ReisekostenabrechnungFINAL.xlsx")
# rich_text: Unterstreichung und Fettdruck gelten in der Vorlage oft nur für
# einen Teil der Zelle (die Leerstelle nach "KK anweisen," ist eine
# unterstrichene Leerzeichenkette). Ohne rich_text liefert openpyxl nur den
# blanken Text -- die Linien fehlten im Ausdruck bis 16.10.2026.
WB = openpyxl.load_workbook(VORLAGE, rich_text=True)
WS = WB["S2"]
SPALTEN = list("ABCDEFG")
DEF_W = 12.6328125
SATZ = 145.79   # gemessene Breite des Originaldrucks (PDF der Vorlage,
                # Skalierung 100%): 17,46mm .. 163,25mm ab Blattkante.
                # NICHT auf den Satzspiegel normiert -- sonst stimmen die
                # Zeilenumbrüche im Fließtext nicht mit dem Formular überein.
PT_MM = 25.4 / 72

# Behördenspezifisches bleibt Platzhalter — das Repo ist öffentlich. Adressiert
# wird über die Zelle, nicht über ihren Inhalt: so steht der zu schwärzende Wert
# nirgends in dieser Datei. Der Fingerabdruck (sha256, 12 Zeichen, über den
# rechts beschnittenen Zellwert) sichert die Adresse ab -- verschiebt sich die
# Vorlage um eine Zeile, bricht der Lauf ab, statt den echten Wert still in die
# öffentliche Ausgabe zu schreiben. Neue Vorlage: mit --fingerabdruecke die
# Werte der hier eingetragenen Zellen neu ausgeben lassen und prüfen.
#
# Der Ersatz bildet die Formatierung des Originals nach (fett, unterstrichen,
# Stück für Stück). Ein Stück mit id wird zum <span>, den das Widget aus
# Einstellungen füllt; bleibt das Feld dort leer, steht die Linie zum
# Ausfüllen von Hand da. Nach der Migration ins interne Netz entfällt die
# Schwärzung: Regel löschen, dann kommt der Originalwert aus der Vorlage.
def T(text, art="", id=None):
    """Ein Stück Ersatztext. art: "b" fett, "u" unterstrichen."""
    return (text, "b" in art, "u" in art, id)


SCHWAERZEN = {
    (34, 1): ("81e3e161d025", [T("Abteilung: ", "bu"), T("__________", "bu", "s2-abteilung")]),
    (34, 4): ("3df650914e3b", [T("_______________", "", "s2-behoerde-ort"), T(", "),
                               T("_______________", "u")]),
    (37, 1): ("719b8d22e6d7", [T("1.", "b"), T(" KK anweisen,"), T(" " * 25, "u"),
                               T("\u20ac bei: "), T("_____________________", "", "s2-buchungsstelle")]),
    (45, 3): ("ed6bb6080fdc", [T("_____________________________", "", "s2-behoerde")]),
}

GESCHWAERZT = {}   # (Zeile, Spalte) -> Originalwert, für die Schlusskontrolle


def schwaerzen(r, c, wert):
    """Ersetzt den Inhalt einer als behördenspezifisch markierten Zelle. Bricht
    ab, sobald die Zelle nicht mehr den erwarteten Inhalt hat -- der stille
    Fehlschlag ist hier das eigentliche Risiko, nicht der laute."""
    erwartet, ersatz = SCHWAERZEN[(r, c)]
    ist = hashlib.sha256(wert.encode()).hexdigest()[:12]
    if ist != erwartet:
        sys.exit(f"Zelle {WS.cell(r, c).coordinate}: Inhalt weicht von der "
                 f"hinterlegten Schwärzungsregel ab (erwartet {erwartet}, ist {ist}).\n"
                 f"Vorlage geändert? Regel in SCHWAERZEN prüfen und den "
                 f"Fingerabdruck mit --fingerabdruecke neu bestimmen. "
                 f"Abbruch, damit nichts Behördenspezifisches in die "
                 f"öffentliche Ausgabe gerät.")
    GESCHWAERZT[(r, c)] = wert
    return ersatz


if "--fingerabdruecke" in sys.argv:
    # Gibt Adresse, Fingerabdruck und Inhalt der in SCHWAERZEN eingetragenen
    # Zellen aus -- nur lokal, die Vorlage liegt ja ohnehin nur lokal.
    for (zr, zc) in sorted(SCHWAERZEN):
        w = str(WS.cell(zr, zc).value or "").rstrip()
        print(f"({zr:3d}, {zc}): {hashlib.sha256(w.encode()).hexdigest()[:12]}   {w!r}")
    sys.exit(0)

STAERKE = {"thin": "var(--rahmen)", "medium": "var(--rahmen-breit)"}

# Das Widget füllt im S2-Block nur die <span> aus SCHWAERZEN (Abteilung,
# Buchungsstelle, Ort und Name der Behörde). Die Kontoverbindung wird nicht erfasst, IBAN-
# und BIC-Kasten bleiben als Vordruck stehen.


def stuecke(zelle):
    """Die Zelle als Liste von (Text, fett, unterstrichen, id) -- Rich Text
    Stück für Stück, sonst die ganze Zelle mit ihrer Schrift."""
    f = zelle.font
    if isinstance(zelle.value, CellRichText):
        return [(t.text, bool(t.font.b), bool(t.font.u), None) if isinstance(t, TextBlock)
                else (t, bool(f.bold), bool(f.u), None) for t in zelle.value]
    return [(str(zelle.value), bool(f.bold), bool(f.u), None)]


def html_stueck(text, fett, unter, id, ganz_fett, ganz_unter):
    """Ein Stück als HTML. Leerzeichen in unterstrichenen Stücken werden alle
    zu &nbsp; -- sonst fasst der Browser die Linie zusammen."""
    t = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = t.replace(" ", "&nbsp;") if unter else t.replace("  ", "&nbsp;&nbsp;")
    if id:
        t = f'<span id="{id}">{t}</span>'
    if unter and not ganz_unter:
        t = f"<u>{t}</u>"
    if fett and not ganz_fett:
        t = f"<b>{t}</b>"
    return t


def breite(sp):
    d = WS.column_dimensions.get(sp)
    return d.width if d and d.width else DEF_W


def hoehe(r):
    d = WS.row_dimensions.get(r)
    return d.height if d and d.height else 12.75


# ---------------------------------------------------------------- Merges
ANKER = {}      # (row, col_index) -> (rowspan, colspan)
BELEGT = set()  # von einem Merge überdeckte Zellen
for m in WS.merged_cells.ranges:
    ANKER[(m.min_row, m.min_col)] = (m.max_row - m.min_row + 1,
                                     m.max_col - m.min_col + 1)
    for r in range(m.min_row, m.max_row + 1):
        for c in range(m.min_col, m.max_col + 1):
            if (r, c) != (m.min_row, m.min_col):
                BELEGT.add((r, c))


def rahmen(r, c, rs, cs):
    """Rahmen einer (ggf. verbundenen) Zelle: je Seite aus den Randzellen des
    verbundenen Bereichs, nicht nur aus der Ankerzelle."""
    seiten = {}
    for spalte in range(c, c + cs):                      # oben / unten
        for seite, zeile in (("top", r), ("bottom", r + rs - 1)):
            stil = getattr(WS.cell(zeile, spalte).border, seite).style
            if stil:
                seiten[seite] = stil
    for zeile in range(r, r + rs):                       # links / rechts
        for seite, spalte in (("left", c), ("right", c + cs - 1)):
            stil = getattr(WS.cell(zeile, spalte).border, seite).style
            if stil:
                seiten[seite] = stil
    return seiten


# ---------------------------------------------------------------- Linien
# Die Unterschriftslinien über "(Datum)" und "(Unterschrift,
# Dienstbezeichnung)" sind in der Vorlage gezeichnete Formen, keine
# Zellrahmen -- openpyxl liest sie nicht ein, sie fehlten bis 16.10.2026.
# Hier direkt aus dem Zeichnungsteil der XLSX: jede waagrechte Linie wird ein
# absolut positioniertes <div> in der Zelle, an der sie beginnt. Versatz in
# echten mm (EMU / 36000); die Spalten skaliert dieses Skript auf SATZ, die
# Abweichung liegt unter 0,1 mm.
EMU_MM = 36000
NS = {"xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def zeichnung():
    """Wurzel der Zeichnung zum Blatt S2, oder None ohne Zeichnung. Ziele
    über ihren Dateinamen: openpyxl schreibt sie beim Speichern absolut."""
    z = zipfile.ZipFile(VORLAGE)

    def ziel(rels, pruefen):
        if rels not in z.namelist():
            return None
        t = next((r.get("Target") for r in ET.fromstring(z.read(rels)) if pruefen(r)), None)
        return t and t.rsplit("/", 1)[-1]

    rid = next(b.get(f"{{{NS['r']}}}id") for b in ET.fromstring(z.read("xl/workbook.xml")).iter()
               if b.tag.endswith("}sheet") and b.get("name") == "S2")
    blatt = ziel("xl/_rels/workbook.xml.rels", lambda r: r.get("Id") == rid)
    bild = ziel(f"xl/worksheets/_rels/{blatt}.rels", lambda r: r.get("Type", "").endswith("/drawing"))
    return ET.fromstring(z.read(f"xl/drawings/{bild}")) if bild else None


LINIEN = {}   # (Zeile, Spalte) der Startzelle -> [<div>, …]


def linien_lesen():
    mm = [breite(s) / sum(breite(x) for x in SPALTEN) * SATZ for s in SPALTEN]
    wurzel = zeichnung()
    for anker in ([] if wurzel is None else wurzel.findall("xdr:twoCellAnchor", NS)):
        if anker.find(".//a:prstGeom[@prst='straightConnector1']", NS) is None:
            sys.exit("Die Zeichnung auf S2 enthält eine Form, die keine Linie ist -- "
                     "nicht unterstützt. Abbruch, sonst fehlt sie still im Ausdruck.")
        (c1, o1, r1, ro1), (c2, o2, r2, ro2) = [
            [int(anker.find(f"xdr:{p}/xdr:{k}", NS).text)
             for k in ("col", "colOff", "row", "rowOff")] for p in ("from", "to")]
        if (r1, ro1) != (r2, ro2):
            sys.exit(f"Linie ab Zeile {r1 + 1} ist nicht waagrecht -- nicht unterstützt. Abbruch.")
        if (r1 + 1, c1 + 1) in BELEGT:
            sys.exit(f"Linie beginnt in einer verbundenen Zelle (Zeile {r1 + 1}) -- "
                     f"nicht unterstützt. Abbruch.")
        staerke = int(anker.find(".//a:ln", NS).get("w", 9525)) / 12700
        breite_mm = sum(mm[:c2]) + o2 / EMU_MM - sum(mm[:c1]) - o1 / EMU_MM
        LINIEN.setdefault((r1 + 1, c1 + 1), []).append(
            f'<div style="position:absolute;left:{o1 / EMU_MM:.2f}mm;top:{ro1 / EMU_MM:.2f}mm;'
            f'width:{breite_mm:.2f}mm;border-top:{staerke:g}pt solid #000"></div>')


# ---------------------------------------------------------------- Ausgabe
linien_lesen()
aus = []
gesamt = sum(breite(s) for s in SPALTEN)
aus.append('  <table class="s2">')
aus.append("    <colgroup>")
for s in SPALTEN:
    aus.append(f'      <col style="width:{breite(s) / gesamt * SATZ:.2f}mm">')
aus.append("    </colgroup>")

for r in range(1, WS.max_row + 1):
    aus.append(f'    <tr style="height:{hoehe(r) * PT_MM:.2f}mm">')
    for ci, sp in enumerate(SPALTEN, start=1):
        if (r, ci) in BELEGT:
            continue
        rs, cs = ANKER.get((r, ci), (1, 1))
        zelle = WS.cell(r, ci)
        stil, attr = [], []
        if rs > 1:
            attr.append(f'rowspan="{rs}"')
        if cs > 1:
            attr.append(f'colspan="{cs}"')

        for seite, art in rahmen(r, ci, rs, cs).items():
            stil.append(f"border-{seite}:{STAERKE.get(art, 'var(--rahmen)')}")

        fuell = zelle.fill
        if fuell and fuell.patternType and fuell.fgColor and fuell.fgColor.rgb:
            stil.append(f"background:#{str(fuell.fgColor.rgb)[2:]}")

        wert = zelle.value
        # rstrip: die Vorlage hat in mehreren Zellen lange Leerzeichenketten am
        # Ende. Als &nbsp; ausgegeben schieben sie den Text weit über den
        # Seitenrand -- der Browser skaliert dann das GANZE Dokument klein.
        wert = "" if wert is None else str(wert).rstrip()
        if wert.startswith("="):        # Formeln der Vorlage: leer lassen
            wert = ""
        teile = stuecke(zelle) if wert else []
        if (r, ci) in SCHWAERZEN:
            teile = schwaerzen(r, ci, wert)
        while teile and not teile[-1][0].rstrip():     # dasselbe rstrip je Stück
            teile.pop()
        if teile:
            teile[-1] = (teile[-1][0].rstrip(),) + teile[-1][1:]
        ganz_fett = bool(teile) and all(t[1] for t in teile)
        ganz_unter = bool(teile) and all(t[2] for t in teile)

        if teile:
            f, a = zelle.font, zelle.alignment
            stil.append(f"font-size:{f.size:g}pt")
            if ganz_fett:
                stil.append("font-weight:bold")
            if ganz_unter:
                stil.append("text-decoration:underline")
            if a.horizontal in ("center", "right", "left"):
                stil.append(f"text-align:{a.horizontal}")
            if a.vertical in ("top", "center", "bottom"):
                stil.append("vertical-align:" +
                            {"center": "middle"}.get(a.vertical, a.vertical))
            if a.wrapText:
                stil.append("white-space:normal")
            else:
                # Excel laesst Text in leere Nachbarzellen ueberlaufen und kappt
                # ihn erst an der naechsten belegten Zelle -- genau das hier.
                nachbar = ci + cs
                if nachbar <= len(SPALTEN) and WS.cell(r, nachbar).value not in (None, ""):
                    stil.append("overflow:hidden")

        inhalt = "".join(html_stueck(*t, ganz_fett, ganz_unter) for t in teile)
        if (r, ci) in LINIEN:
            stil.append("position:relative")
            inhalt += "".join(LINIEN[(r, ci)])
        offen = "<td" + ("".join(" " + x for x in attr))
        if stil:
            offen += ' style="' + ";".join(stil) + '"'
        aus.append(f"      {offen}>{inhalt}</td>")
    aus.append("    </tr>")
aus.append("  </table>")

# ------------------------------------------------- Kontrolle vor der Ausgabe
# Zwei Dinge müssen stimmen, sonst wird nichts gedruckt: jede Regel muss eine
# Zelle erwischt haben (eine von einem Merge überdeckte Zelle besucht die
# Schleife nie), und kein geschwärzter Originalwert darf anderswo im Blatt
# stehen geblieben sein.
# 297mm Blatt minus 10mm oberer Rand (.dok-s2 .blatt, unten kein Rand).
SEITE_MM = 287
gesamt_mm = sum(hoehe(r) for r in range(1, WS.max_row + 1)) * PT_MM
if gesamt_mm > SEITE_MM:
    sys.exit(f"S2-Block wäre {gesamt_mm:.1f}mm hoch, auf ein A4-Blatt passen "
             f"{SEITE_MM}mm ({WS.max_row} Zeilen in der Vorlage). Die Zeilenzahl "
             f"kommt aus der Vorlage -- stehen am Blattende formatierte "
             f"Leerzeilen? Abbruch, sonst läuft S2 still auf Seite 2 über.")

fehlend = sorted(SCHWAERZEN.keys() - GESCHWAERZT.keys())
if fehlend:
    sys.exit(f"Schwärzungsregeln liefen ins Leere für Zellen {fehlend} — "
             f"Zeilenbereich oder Zellverbünde der Vorlage geändert? Abbruch.")

fertig = "\n".join(aus)
uebrig = sorted({WS.cell(r, c).coordinate for (r, c), wert in GESCHWAERZT.items()
                 if wert in fertig})
if uebrig:
    sys.exit(f"Ein geschwärzter Wert steht noch an anderer Stelle im Blatt "
             f"(Ursprung: {uebrig}). Betroffene Zelle in SCHWAERZEN ergänzen. Abbruch.")

print(fertig)
