#!/usr/bin/env python3
"""Setzt das Layout des Formular-Widgets auf 'Reisen'.

Bildet die Gliederung des bisherigen Google-Formulars nach: fünf Abschnitte,
Reihenfolge und Gruppierung wie in sheets/manual.md beschrieben.

Aufruf (Zugangsdaten wie bei setup.py aus grist/.env):
    python3 grist/formular.py            # Layout schreiben
    python3 grist/formular.py --zeigen   # nur anzeigen, nichts ändern

Das Layout wird jedes Mal vollständig neu erzeugt — mehrfaches Ausführen ist
gefahrlos. Ändert sich ZWISCHENZIELE in setup.py, erst setup.py laufen lassen
(legt die Spalten an), dann dieses Skript.

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


# ------------------------------------------------------------ Layout-Bausteine
# Format aus einem bestehenden Formular-Widget ausgelesen: ein Baum aus
# Layout > Section > Field, dazu Paragraph für Text, Columns für nebeneinander
# und Submit als Abschluss. 'leaf' verweist auf _grist_Views_section_field.

def knoten(typ, **rest):
    return {"id": str(uuid.uuid4()), "type": typ, "children": [], **rest}


def absatz(text, ausrichtung="left"):
    return knoten("Paragraph", text=text, alignment=ausrichtung)


def feld(col_id):
    if col_id not in FELD:
        sys.exit(f"Spalte {col_id} hat kein Feld im Formular-Widget — "
                 f"erst setup.py laufen lassen.")
    return knoten("Field", leaf=FELD[col_id])


def nebeneinander(links, rechts):
    return knoten("Columns", children=[feld(links), feld(rechts)], leaf=None)


def abschnitt(titel, hinweis, *inhalt):
    kinder = [absatz(f"## **{titel}**")]
    if hinweis:
        kinder.append(absatz(hinweis))
    return knoten("Section", children=kinder + list(inhalt))


def bauen():
    """Die fünf Abschnitte des bisherigen Google-Formulars."""
    return knoten("Layout", children=[
        absatz("# **Dienstreise**", "center"),
        absatz("Eine Reise je Eintrag, am besten direkt im Anschluss ausfüllen.",
               "center"),

        abschnitt("1 · Allgemeine Angaben zur Dienstreise", "",
                  feld("Datum"),
                  feld("Datum_Ende"),
                  nebeneinander("Beginn", "KM_Beginn"),
                  nebeneinander("Ende", "KM_Ende"),
                  feld("Umweg_privat")),

        abschnitt("2 · Angefahrene Orte",
                  "Links aus der Liste wählen. Ist der Ort nicht dabei — "
                  "einmalige Ziele wie ein Café oder ein Ausweichgebäude — "
                  "rechts frei eintragen. Nicht benötigte Zwischenorte leer lassen.",
                  *[nebeneinander(s, f"{s}_Text") for s in ORT_SLOTS]),

        abschnitt("3 · Tagegeld",
                  "Die drei Zeitangaben nur ausfüllen, wenn oben „Ja“ steht.",
                  feld("Tagegeld_beantragt"),
                  feld("Min_Dienststaette"),
                  feld("Min_Dienstort"),
                  feld("Min_privat_Abzug")),

        abschnitt("4 · Weitere Fahrt- und Nebenkosten",
                  "Nur ausfüllen, was tatsächlich angefallen ist.",
                  feld("OePNV"),
                  feld("Uebernachtung"),
                  feld("Nebenkosten"),
                  feld("Mitnahme_Personen")),

        abschnitt("5 · Sonstiges und Nachweise", "",
                  feld("Verpflegung"),
                  feld("Vermerk"),
                  feld("Belege")),

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
            paar = [NACH_COL[k["leaf"]] for k in kind["children"] if k["type"] == "Field"]
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
# setup.py eine Spalte bekommt, die hier vergessen wurde.
eingabe = {c["colId"] for c in sql(
    "select c.colId from _grist_Tables_column c "
    "join _grist_Tables t on t.id = c.parentId "
    "where t.tableId = 'Reisen' and c.isFormula = 0 "
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
print("\nLayout geschrieben. Im Formular-Editor prüfen und veröffentlichen.")
