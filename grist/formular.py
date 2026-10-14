#!/usr/bin/env python3
"""Setzt das Layout des Formular-Widgets auf 'Reisen'.

Erzeugt das Formular so, wie es im Grist-Editor aufgebaut wurde: fünf
Abschnitte (1, 2, 3, 4a, 5) mit den dort geschriebenen Beschreibungstexten,
Eingabefelder paarweise nebeneinander, „---“ als Trennlinie zwischen den
Paaren. Die Texte stehen als BESCHR_* am Kopf der Datei.

Aufruf (Zugangsdaten wie bei setup.py aus grist/.env):
    python3 grist/formular.py            # Layout schreiben
    python3 grist/formular.py --zeigen   # nur anzeigen, nichts ändern

Das Layout wird jedes Mal vollständig neu erzeugt — mehrfaches Ausführen ist
gefahrlos, ersetzt aber jede Anpassung, die seither im Editor gemacht wurde.
Ändert sich ZWISCHENZIELE in setup.py, erst setup.py laufen lassen (legt die
Spalten an), dann dieses Skript.

Ein Unterschied zum Google-Formular bleibt und ist nicht behebbar: Grist kennt
keine bedingten Fragen (grist-core#955). Die Detailfelder zu Tagegeld und
Nebenkosten stehen deshalb immer sichtbar in ihrem Abschnitt, statt erst nach
einem 'Ja' aufzuklappen. Der Abschnittstext sagt das dem Ausfüllenden.
"""
import json, sys, urllib.parse, uuid

from setup import api, ORT_SLOTS, ORT_LABEL

ZEIGEN = "--zeigen" in sys.argv


def sql(frage):
    return [z["fields"] for z in
            api("GET", "/sql?q=" + urllib.parse.quote(frage))["records"]]


# ---------------------------------------------------------- Abschnittstexte
# Wortlaut aus dem Formular-Editor. Anpassungen hier vornehmen, dann Skript
# laufen lassen.

BESCHR_1 = ("Datum, Uhrzeiten und Kilometerstände der Fahrt. Das Enddatum nur "
            "bei Reisen über mehrere Tage.")

BESCHR_2 = ("Alle Orte in der Reihenfolge der Fahrt. Bekannte Orte aus der Liste "
            "wählen. Fehlt ein Ort in der Liste, im Feld darunter in dieser Form "
            "eintragen: **Bezeichnung, Straße Hausnummer, PLZ Ort**, z. B. "
            "*Café Mokka, Bahnhofstr. 7, 12345 Musterstadt*. Ohne vollständige "
            "Anschrift lässt sich die Strecke nicht abrechnen. Nicht gebrauchte "
            "Orte leer lassen.")

BESCHR_3 = ("Ankreuzen, wenn Tagegeld beantragt wird. Die Höhe ergibt sich aus "
            "der Dauer der Reise und wird automatisch berechnet. Abgezogen wird die Zeit in der "
            "Dienststätte, am Dienstort und für private Unterbrechungen, "
            "jeweils in Minuten.")

BESCHR_4 = "Nur ausfüllen, wenn etwas angefallen ist."

BESCHR_5 = ("Ein Vermerk nur bei Besonderheiten, z. B. Umleitung wegen einer "
            "Straßensperrung oder Fahrt mit einem anderen Auto. Belege und "
            "Tachofotos hier hochladen.")


# Feldeinstellungen fürs Formular (Pflicht, Darstellung, abweichender Titel).
# Grist speichert sie an der Spalte, nicht im Layout -- sie gelten also auch,
# wenn das Layout neu geschrieben wird. Hier stehen sie, damit ein neu
# aufgebautes Dokument dieselben bekommt. Aus dem Editor übernommen.
FELD_OPTIONEN = {
    "Datum":      {"formRequired": True},
    "Datum_Ende": {"question": "Enddatum"},
    "Beginn":     {"formRequired": True, "formTextFormat": "singleline"},
    "Ende":       {"formRequired": True},
    "KM_Beginn":  {"formRequired": True, "formNumberFormat": "text"},
    "KM_Ende":    {"formRequired": True},
    "Vermerk":    {"formTextFormat": "multiline", "formTextLineCount": 5},
    # Platz für Bezeichnung und Anschrift
    **{f"{s}_Text": {"formTextFormat": "multiline", "formTextLineCount": 2}
       for s in ORT_SLOTS},
}


# ------------------------------------------------------------ Layout-Bausteine
# Format aus dem bestehenden Formular-Widget ausgelesen: ein Baum aus
# Layout > Section > Field, dazu Paragraph für Text, Columns für nebeneinander
# und Submit als Abschluss. 'leaf' verweist auf _grist_Views_section_field.

def knoten(typ, **rest):
    return {"id": str(uuid.uuid4()), "type": typ, "children": [], **rest}


def absatz(text, ausrichtung="left"):
    return knoten("Paragraph", text=text, alignment=ausrichtung)


def trenner():
    return absatz("---")


def feld(col_id):
    if col_id not in FELD:
        sys.exit(f"Spalte {col_id} hat kein Feld im Formular-Widget — "
                 f"erst setup.py laufen lassen.")
    return knoten("Field", leaf=FELD[col_id])


def reihe(*spalten):
    """Eine Columns-Zeile. None ergibt einen Platzhalter."""
    kinder = [knoten("Placeholder") if s is None else feld(s) for s in spalten]
    return knoten("Columns", children=kinder, leaf=None)


def mit_trennern(zeilen):
    """[a, b, c] -> [a, ---, b, ---, c]; eine Liste als Zeile zählt als ein
    Block aus mehreren Knoten."""
    aus = []
    for i, z in enumerate(zeilen):
        if i:
            aus.append(trenner())
        aus.extend(z if isinstance(z, list) else [z])
    return aus


def abschnitt(ueberschrift, beschreibung, *inhalt):
    kinder = [absatz(ueberschrift)]
    if beschreibung:
        kinder.append(absatz(beschreibung))
    return knoten("Section", children=kinder + list(inhalt), leaf=None)


def bauen():
    """Das Formular aus dem Grist-Editor: fünf Abschnitte, Felder paarweise."""
    return knoten(
        "Layout", submitText="Senden.", anotherResponse=True, successURL=None,
        children=[
            absatz("# **Dienstreise**", "center"),
            absatz("Bitte jede Dienstreise einzeln und möglichst direkt nach "
                   "der Fahrt eintragen.", "center"),

            abschnitt(
                "### **Abschnitt 1: Allgemeine Angaben zur Dienstreise**", BESCHR_1,
                *mit_trennern([
                    reihe("Datum", "Datum_Ende"),
                    reihe("Beginn", "Ende"),
                    reihe("KM_Beginn", "KM_Ende"),
                    reihe("Umweg_privat", None),
                ])),

            abschnitt(
                "### **Abschnitt 2: Angefahrene Orte**", BESCHR_2,
                # Auswahl halbe Breite, Freitext (zweizeilig) volle Breite
                # darunter -- so im Editor gesetzt, Platz für die Anschrift.
                *mit_trennern([[reihe(s, None), feld(f"{s}_Text")] for s in ORT_SLOTS])),

            abschnitt(
                "### **Abschnitt 3: Tagegeld** (Optional)", BESCHR_3,
                feld("Tagegeld_beantragt"),
                trenner(),
                reihe("Min_Dienststaette", "Min_Dienstort", "Min_privat_Abzug")),

            abschnitt(
                "### **Abschnitt 4: Weitere Fahrt- und Nebenkosten** (Optional)",
                BESCHR_4,
                *mit_trennern([
                    reihe("OePNV", "Nebenkosten"),
                    reihe("Uebernachtung", "Verpflegung"),
                    reihe("Mitnahme_Personen", None),
                ])),

            abschnitt(
                "### **Abschnitt 5: Sonstiges und Nachweise**", BESCHR_5,
                feld("Vermerk"),
                trenner(),
                reihe("Belege", "Tacho_Fotos")),

            knoten("Submit"),
        ])


def platzierte(baum):
    """Alle im Layout verbauten Spalten — für die Vollständigkeitsprüfung."""
    if baum.get("type") == "Field":
        yield NACH_COL[baum["leaf"]]
    for kind in baum.get("children") or []:
        yield from platzierte(kind)


def gliederung(baum, tiefe=0):
    for kind in baum.get("children") or []:
        if kind["type"] == "Paragraph":
            print("   " * tiefe + kind["text"].replace("**", ""))
        elif kind["type"] == "Field":
            print("   " * tiefe + f"· {NACH_COL[kind['leaf']]}")
        elif kind["type"] == "Columns":
            paar = [NACH_COL[k["leaf"]] if k["type"] == "Field" else "—"
                    for k in kind["children"]]
            print("   " * tiefe + "· " + "  |  ".join(paar))
        else:
            gliederung(kind, tiefe + 1)


# ---------------------------------------------------------------- Ausführung

sektionen = sql("select id from _grist_Views_section where parentKey = 'form'")
if len(sektionen) != 1:
    sys.exit(f"Erwarte genau ein Formular-Widget, gefunden: {len(sektionen)}. "
             f"Formular-Widget auf 'Reisen' anlegen bzw. überzählige entfernen.")
SEKTION = sektionen[0]["id"]

felder = sql("select f.id, c.colId from _grist_Views_section_field f "
             "join _grist_Tables_column c on c.id = f.colRef "
             f"where f.parentId = {SEKTION}")
FELD = {f["colId"]: f["id"] for f in felder}
NACH_COL = {f["id"]: f["colId"] for f in felder}

layout = bauen()

# Prüfung: jede Eingabespalte muss im Formular vorkommen. Schlägt an, sobald
# setup.py eine Spalte bekommt, die hier vergessen wurde. Trigger-Formeln
# (isFormula=0, aber formula gesetzt, z. B. Erstellt_am = NOW()) sind keine
# Eingabe und bleiben außen vor.
eingabe = {c["colId"] for c in sql(
    "select c.colId from _grist_Tables_column c "
    "join _grist_Tables t on t.id = c.parentId "
    "where t.tableId = 'Reisen' and c.isFormula = 0 and c.formula = '' "
    "and c.colId not like 'gristHelper%' and c.colId != 'manualSort'")}
fehlt = sorted(eingabe - set(platzierte(layout)))
if fehlt:
    sys.exit(f"Diese Eingabespalten fehlen im Formular-Layout: {fehlt}")

print(f"Formular-Widget: Section {SEKTION}, {len(list(platzierte(layout)))} Felder\n")
gliederung(layout)

if ZEIGEN:
    print("\n--zeigen: nichts geändert.")
    sys.exit(0)

api("POST", "/apply", [["UpdateRecord", "_grist_Views_section", SEKTION,
                        {"layoutSpec": json.dumps(layout)}]])

optionen = []
for c in sql("select c.id, c.colId, c.widgetOptions from _grist_Tables_column c "
             "join _grist_Tables t on t.id = c.parentId where t.tableId = 'Reisen'"):
    soll = FELD_OPTIONEN.get(c["colId"])
    alt = json.loads(c["widgetOptions"] or "{}")
    if soll and any(alt.get(k) != v for k, v in soll.items()):
        optionen.append(["UpdateRecord", "_grist_Tables_column", c["id"],
                         {"widgetOptions": json.dumps({**alt, **soll})}])
if optionen:
    api("POST", "/apply", optionen)
print(f"\nLayout geschrieben, Feldeinstellungen: {len(optionen)} angepasst. "
      f"Im Formular-Editor prüfen.")
