#!/usr/bin/env python3
"""Testet die tragende Annahme hinter der geplanten Adressen-Tabelle: kann
eine Formelspalte per Table.lookupOrAddDerived() automatisch Zeilen in einer
ANDEREN, normal angelegten Tabelle anlegen (nicht nur in Summary-Tabellen)?

Legt zwei Wegwerf-Tabellen an (ZZ_Test_Quelle, ZZ_Test_Ziel) und prüft:
  1. Anlegen: ein Datensatz in Quelle erzeugt automatisch einen in Ziel.
  2. Kein Merge: ein zweiter Quelle-Datensatz mit demselben Text ergibt eine
     ZWEITE Ziel-Zeile (Schlüssel ist die Quelle-Zeilen-ID — wie im Vorhaben
     Reise-ID + Slot, dort ebenfalls immer eindeutig).
  3. Nachziehen: Text in Quelle nachträglich geändert -> Label in Ziel zieht
     nach. Die ursprüngliche Vermutung war das Gegenteil; der Lauf hat sie
     widerlegt, Grist leitet die Zeile bei jeder Neuberechnung neu ab.

Läuft gegen das echte Dokument aus grist/.env. Räumt am Ende automatisch auf.

Aufruf:
    python3 grist/test_lookuporadd.py             # testen, aufräumen
    python3 grist/test_lookuporadd.py --behalten  # Testtabellen stehen lassen
"""
import sys

from setup import api, spalte

BEHALTEN = "--behalten" in sys.argv
QUELLE, ZIEL = "ZZ_Test_Quelle", "ZZ_Test_Ziel"

FORMEL = f'''
if not $Text:
  return None
return {ZIEL}.lookupOrAddDerived(Schluessel=$id, Label=$Text)
'''.strip()


def aufraeumen():
    vorhanden = {t["id"] for t in api("GET", "/tables")["tables"]}
    weg = [t for t in (QUELLE, ZIEL) if t in vorhanden]
    if weg:
        api("POST", "/apply", [["RemoveTable", t] for t in weg])


def pruefen(bedingung, meldung):
    print(f"  [{'OK' if bedingung else 'FEHLER'}] {meldung}")
    return bedingung


print("Räume alte Testtabellen auf (falls vorhanden)...")
aufraeumen()

print("Lege Testtabellen an...")
api("POST", "/tables", {"tables": [
    {"id": QUELLE, "columns": [spalte("Text", "Text", "Text")]},
    {"id": ZIEL, "columns": [spalte("Schluessel", "Schlüssel", "Int"),
                              spalte("Label", "Label", "Text")]},
]})
api("POST", f"/tables/{QUELLE}/columns", {"columns": [
    spalte("Ziel_Ref", "Ziel", f"Ref:{ZIEL}", formel=FORMEL),
]})

print("\nTest 1 — legt die Formel automatisch eine Ziel-Zeile an?")
r1 = api("POST", f"/tables/{QUELLE}/records",
         {"records": [{"fields": {"Text": "Bürgerhaus Wirges"}}]})["records"][0]["id"]
ziel = api("GET", f"/tables/{ZIEL}/records")["records"]
ok = pruefen(len(ziel) == 1, f"genau eine Ziel-Zeile entstanden (gefunden: {len(ziel)})")
ok &= pruefen(bool(ziel) and ziel[0]["fields"]["Label"] == "Bürgerhaus Wirges",
              "Label korrekt übernommen")

print("\nTest 2 — legt ein zweiter Datensatz mit gleichem Text eine ZWEITE Zeile an (kein Merge)?")
api("POST", f"/tables/{QUELLE}/records",
    {"records": [{"fields": {"Text": "Bürgerhaus Wirges"}}]})
ziel = api("GET", f"/tables/{ZIEL}/records")["records"]
ok &= pruefen(len(ziel) == 2, f"zwei Ziel-Zeilen, kein Merge (gefunden: {len(ziel)})")

print("\nTest 3 — zieht eine spätere Korrektur des Texts ins Ziel nach?")
api("PATCH", f"/tables/{QUELLE}/records",
    {"records": [{"id": r1, "fields": {"Text": "korrigiert"}}]})
q1 = next(r for r in api("GET", f"/tables/{QUELLE}/records")["records"] if r["id"] == r1)
z1 = next(z for z in api("GET", f"/tables/{ZIEL}/records")["records"]
          if z["id"] == q1["fields"]["Ziel_Ref"])
ok &= pruefen(z1["fields"]["Label"] == "korrigiert",
              f"Korrektur im Ziel angekommen (gefunden: {z1['fields']['Label']!r})")

print(f"\n{'Kernannahme bestätigt' if ok else 'Kernannahme WIDERLEGT'} — lookupOrAddDerived "
      f"{'funktioniert' if ok else 'funktioniert NICHT'} gegen eine normale Tabelle.")

if BEHALTEN:
    print(f"\n--behalten: {QUELLE}/{ZIEL} bleiben im Dokument stehen, im Editor prüfbar.")
else:
    aufraeumen()
    print("\nTesttabellen aufgeräumt.")
