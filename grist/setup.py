#!/usr/bin/env python3
"""Legt das Datenmodell der Fahrtkostenabrechnung in einem leeren Grist-Dokument an.

Aufruf:
    cp grist/.env.beispiel grist/.env   # dort die drei Werte eintragen
    python3 grist/setup.py

Alternativ ohne Datei, direkt in der Shell:
    export GRIST_URL="https://grist.example.intern"
    export GRIST_API_KEY="..."
    export GRIST_DOC_ID="..."

Laeuft vollstaendig lokal, nur Standardbibliothek. Bestehende Spalten werden
uebersprungen, das Skript kann also gefahrlos erneut laufen.
"""
import json, os, sys, urllib.request, urllib.error, pathlib

# Zugangsdaten kommen NIE in diese Datei. Entweder aus der Umgebung oder aus
# grist/.env — beides liegt ausserhalb der Versionierung (siehe .gitignore).
_env = pathlib.Path(__file__).with_name(".env")
if _env.exists():
    for zeile in _env.read_text(encoding="utf-8").splitlines():
        zeile = zeile.strip()
        if zeile and not zeile.startswith("#") and "=" in zeile:
            schluessel, wert = zeile.split("=", 1)
            os.environ.setdefault(schluessel.strip(), wert.strip().strip('"\''))

URL = os.environ.get("GRIST_URL", "").rstrip("/")
KEY = os.environ.get("GRIST_API_KEY", "")
DOC = os.environ.get("GRIST_DOC_ID", "")
SELBSTTEST = "--selbsttest" in sys.argv          # prüft die Formeln ohne Grist
if not (URL and KEY and DOC) and not SELBSTTEST:
    sys.exit("Bitte GRIST_URL, GRIST_API_KEY und GRIST_DOC_ID setzen "
             "(grist/.env anlegen oder exportieren).")


def api(method, pfad, daten=None):
    req = urllib.request.Request(
        f"{URL}/api/docs/{DOC}{pfad}", method=method,
        data=json.dumps(daten).encode() if daten is not None else None,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"\nFehler {e.code} bei {method} {pfad}\n{e.read().decode()[:400]}")
    except urllib.error.URLError as e:
        sys.exit(f"\nKeine Verbindung zu {URL} — {e.reason}")


def spalte(sid, label, typ="Any", formel=None, optionen=None):
    f = {"label": label, "type": typ, "isFormula": formel is not None,
         "formula": formel or ""}
    if optionen:
        f["widgetOptions"] = json.dumps(optionen)
    return {"id": sid, "fields": f}


# ----------------------------------------------------------- Konfiguration

# Zahl der Zwischenziele je Reise. Spalten und Formeln richten sich danach.
# Aendern und setup.py erneut laufen lassen ergaenzt die fehlenden Spalten.
ZWISCHENZIELE = 5

ORT_SLOTS = ["Ort_Beginn"] + [f"Ort_{i}" for i in range(1, ZWISCHENZIELE + 1)] + ["Ort_Ende"]
ORT_LABEL = {"Ort_Beginn": "Ort Reisebeginn", "Ort_Ende": "Ort Reiseende",
             **{f"Ort_{i}": f"Zwischenort {i}" for i in range(1, ZWISCHENZIELE + 1)}}

# Jeder Stopp ist ein Paar: Auswahl aus 'Orte' fuer die Stammorte, Freitext
# fuer die Einmalziele. Ist die Auswahl gesetzt, gewinnt sie — stillschweigend.
PAARE = "[" + ", ".join(f"(${s}, ${s}_Text)" for s in ORT_SLOTS) + "]"


# ---------------------------------------------------------------- Formeln

ABWESENHEIT = '''
def minuten(s):
  try:
    h, m = str(s).split(":")
    return int(h) * 60 + int(m)
  except Exception:
    return None
a, b = minuten($Beginn), minuten($Ende)
if a is None or b is None or not $Datum:
  return 0
tage = ($Datum_bis - $Datum).days if $Datum_bis else 0
return tage * 1440 + b - a
'''.strip()

STUFE = '''
if not $Tagegeld_beantragt:
  return ""
if $Abwesenheit_min - $Min_privat_Abzug < 481:   # Anspruch dem Grunde nach
  return ""
r = $Rest_min
if r < 481:  return "anteilig"
if r < 840:  return ">8h"
if r < 1440: return ">=14h"
return "24h"
'''.strip()

LFD_NR = '''
if not $Datum:
  return None
alle = [r for r in Reisen.all if r.Datum and r.Datum.year == $Datum.year]
alle.sort(key=lambda r: (r.Datum, r.id))
return [r.id for r in alle].index($id) + 1
'''.strip()

REISEWEG = f'''
paare = {PAARE}
teile = [(o.Kuerzel if o else "") or t for o, t in paare]
return " > ".join(x for x in teile if x)
'''.strip()

MAPS = f'''
import urllib.parse as u
paare = {PAARE}
adr = [x for x in [(o.Adresse if o else "") or t for o, t in paare] if x]
if len(adr) < 2:
  return ""
link = ("https://www.google.com/maps/dir/?api=1&origin=" + u.quote(adr[0])
        + "&destination=" + u.quote(adr[-1]))
if len(adr) > 2:
  link += "&waypoints=" + u.quote("|".join(adr[1:-1]))
return link
'''.strip()

VERMERK_LABEL = '''
if not $Vermerk or not $Datum:
  return ""
mit = [r for r in Reisen.all if r.Vermerk and r.Datum and r.Datum.year == $Datum.year]
mit.sort(key=lambda r: (r.Datum, r.id))
n = [r.id for r in mit].index($id) + 1
return "V%s-%02d" % ($Datum.strftime("%y"), n)
'''.strip()

JA_NEIN = {"choices": ["Ja", "Nein"]}

# ---------------------------------------------------------------- Tabellen

ORTE = [
    spalte("Kuerzel",  "Kürzel", "Text"),
    spalte("Name",     "Name der Einrichtung", "Text"),
    spalte("Strasse",  "Straße und Hausnummer", "Text"),
    spalte("PLZ",      "PLZ", "Text"),
    spalte("Ort",      "Ort", "Text"),
    spalte("Adresse",  "Vollständige Adresse", "Text",
           formel='", ".join(x for x in [$Strasse, ($PLZ + " " + $Ort).strip()] if x)'),
]

EINSTELLUNGEN = [
    spalte("Vorname", "Vorname", "Text"),
    spalte("Name", "Name", "Text"),
    spalte("Organisationseinheit", "Organisationseinheit", "Text"),
    spalte("Wohnort_Strasse", "Wohnort – Straße und Nr.", "Text"),
    spalte("Wohnort_PLZ", "Wohnort – PLZ", "Text"),
    spalte("Wohnort_Ort", "Wohnort – Ort", "Text"),
    spalte("Dienstort_Strasse", "Dienstort – Straße und Nr.", "Text"),
    spalte("Dienstort_PLZ", "Dienstort – PLZ", "Text"),
    spalte("Dienstort_Ort", "Dienstort – Ort", "Text"),
    spalte("IBAN", "IBAN", "Text"),
    spalte("BIC", "BIC", "Text"),
    spalte("Zeitraum_von", "Abrechnungszeitraum von", "Date"),
    spalte("Zeitraum_bis", "Abrechnungszeitraum bis", "Date"),
]

def ort_spalten():
    """Je Stopp zwei Felder: Auswahlliste und Freitext, im Formular nebeneinander."""
    for sid in ORT_SLOTS:
        yield spalte(sid, ORT_LABEL[sid], "Ref:Orte")
        yield spalte(f"{sid}_Text", f"{ORT_LABEL[sid]} – oder frei eintragen", "Text")


REISEN = [
    # --- Eingabe über das Formular ---
    spalte("Datum",             "Reisedatum", "Date"),
    spalte("Datum_Ende",        "Enddatum (nur mehrtägig)", "Date"),
    spalte("Beginn",            "Reisebeginn (HH:MM)", "Text"),
    spalte("Ende",              "Reiseende (HH:MM)", "Text"),
    spalte("KM_Beginn",         "Kilometerstand Beginn", "Int"),
    spalte("KM_Ende",           "Kilometerstand Ende", "Int"),
    spalte("Umweg_privat",      "Privater Umweg (km)", "Int"),
    *ort_spalten(),
    spalte("Tagegeld_beantragt","Tagegeld beantragen?", "Bool"),
    spalte("Min_Dienststaette", "Aufenthalt Dienststätte (Minuten)", "Int"),
    spalte("Min_Dienstort",     "Aufenthalt Dienstort (Minuten)", "Int"),
    spalte("Min_privat_Abzug",  "Privater Zeitabzug (Minuten)", "Int"),
    spalte("Verpflegung",       "Unentgeltliche Verpflegung", "Choice", optionen=JA_NEIN),
    spalte("OePNV",             "Fahrtkosten ÖPNV (EUR)", "Numeric"),
    spalte("Mitnahme_Personen", "Mitnahme von Personen (Anzahl)", "Int"),
    spalte("Uebernachtung",     "Übernachtungskosten (EUR)", "Numeric"),
    spalte("Nebenkosten",       "Nebenkosten (EUR)", "Numeric"),
    spalte("Vermerk",           "Sonstige Informationen", "Text"),
    spalte("Belege",            "Belege", "Attachments"),
    # --- berechnet ---
    spalte("Datum_bis",       "Reisedatum bis", "Date",  formel="$Datum_Ende or $Datum"),
    spalte("Lfd_Nr",          "Laufende Nummer", "Int",  formel=LFD_NR),
    spalte("KM_gesamt",       "Kilometer gesamt", "Int", formel="($KM_Ende or 0) - ($KM_Beginn or 0)"),
    spalte("KM_dienstlich",   "Kilometer dienstlich", "Int",
           formel="$KM_gesamt - ($Umweg_privat or 0)"),
    spalte("Abwesenheit_min", "Abwesenheit (Minuten)", "Int", formel=ABWESENHEIT),
    spalte("Rest_min",        "Rest-Zeit (Minuten)", "Int",
           formel="$Abwesenheit_min - ($Min_privat_Abzug or 0) "
                  "- ($Min_Dienststaette or 0) - ($Min_Dienstort or 0)"),
    spalte("Tagegeld_Stufe",  "Tagegeld-Stufe", "Text", formel=STUFE),
    spalte("Reiseweg",        "Reiseweg", "Text", formel=REISEWEG),
    spalte("Maps_Link",       "Routenlink", "Text", formel=MAPS),
    spalte("Vermerk_Label",   "Vermerk-Kennung", "Text", formel=VERMERK_LABEL),
]

# ---------------------------------------------------------------- Ausführung

def anlegen(tabelle, spalten):
    vorhanden = {t["id"] for t in api("GET", "/tables")["tables"]}
    if tabelle not in vorhanden:
        api("POST", "/tables", {"tables": [{"id": tabelle, "columns": spalten}]})
        print(f"  Tabelle {tabelle} angelegt ({len(spalten)} Spalten)")
        return
    da = {c["id"] for c in api("GET", f"/tables/{tabelle}/columns")["columns"]}
    fehlend = [s for s in spalten if s["id"] not in da]
    if fehlend:
        api("POST", f"/tables/{tabelle}/columns", {"columns": fehlend})
    print(f"  Tabelle {tabelle}: {len(fehlend)} Spalten ergänzt, {len(spalten)-len(fehlend)} vorhanden")


def selbsttest():
    """Führt REISEWEG und MAPS ohne Grist aus: Auswahl gewinnt, sonst Freitext."""
    class Ort:
        def __init__(self, k="", a=""):
            self.Kuerzel, self.Adresse = k, a
        def __bool__(self):
            return bool(self.Kuerzel or self.Adresse)

    rec = type("Rec", (), {})()
    for s in ORT_SLOTS:                       # alles leer als Ausgangslage
        setattr(rec, s, Ort())
        setattr(rec, f"{s}_Text", "")
    rec.Ort_Beginn = Ort("BÜR", "Hauptstr. 1, Musterstadt")
    rec.Ort_1_Text = "Café Mokka, Bahnhofstr. 7, Musterstadt"   # Einmalziel
    rec.Ort_2 = Ort("KITA", "Lindenweg 3, Musterstadt")
    rec.Ort_2_Text = "darf nicht gewinnen"                      # beides gefüllt
    rec.Ort_Ende = Ort("BÜR", "Hauptstr. 1, Musterstadt")

    def lauf(formel):
        rumpf = "\n".join("  " + z for z in formel.replace("$", "rec.").splitlines())
        raum = {}
        exec("def f(rec):\n" + rumpf, raum)
        return raum["f"](rec)

    weg = lauf(REISEWEG)
    assert weg == "BÜR > Café Mokka, Bahnhofstr. 7, Musterstadt > KITA > BÜR", weg
    link = lauf(MAPS)
    assert "Bahnhofstr" in link and "Lindenweg" in link, link
    assert "darf%20nicht" not in link, link
    print(f"Selbsttest ok ({ZWISCHENZIELE} Zwischenziele)\n  Reiseweg: {weg}")


# Beim Import (formular.py holt sich api(), ORT_SLOTS und ORT_LABEL von hier)
# passiert nichts am Dokument.
if __name__ == "__main__" and SELBSTTEST:
    selbsttest()
    sys.exit(0)

if __name__ == "__main__":
    print(f"Dokument {DOC} auf {URL}")
    for name, spalten in (("Orte", ORTE), ("Einstellungen", EINSTELLUNGEN), ("Reisen", REISEN)):
        anlegen(name, spalten)      # Orte zuerst — Reisen verweist darauf

    if not api("GET", "/tables/Einstellungen/records")["records"]:
        api("POST", "/tables/Einstellungen/records", {"records": [{"fields": {}}]})
        print("  Einstellungen: leere Zeile angelegt")

    print(f"""
Fertig. Rest in der Oberfläche:
  1. Bei den {len(ORT_SLOTS)} Ort-Referenzspalten unter SHOW COLUMN 'Kuerzel' wählen
     (ponytail: einmalige Klickarbeit — der API-Weg kostet mehr Code als er spart)
  2. Formular-Widget auf 'Reisen' anlegen — das Layout setzt formular.py
  3. Custom-Widget-Seite mit der URL der s1.html hinzufügen
  4. Formular veröffentlichen, dann 'Duplicate Document' — das ist die Vorlage
""")
