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
import json, os, sys, urllib.request, urllib.error, urllib.parse, pathlib

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


def sql(frage):
    return [z["fields"] for z in
            api("GET", "/sql?q=" + urllib.parse.quote(frage))["records"]]


def ohne_icon(name):
    """Seitenname ohne vorangestelltes Emoji ('🖨️ Ausdruck' -> 'Ausdruck').
    Die Icons setzt die Vorlage im Editor; gesucht wird nach dem Namen."""
    kopf, _, rest = name.partition(" ")
    return rest if rest and not kopf[0].isalnum() else name


def seite_suchen(name):
    """Wie sql('select id from _grist_Views where name = ...'), aber mit
    oder ohne Icon vor dem Namen."""
    return [{"id": v["id"]} for v in sql("select id, name from _grist_Views")
            if ohne_icon(v["name"]) == name]


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
             **{f"Ort_{i}": f"Ort {i}" for i in range(1, ZWISCHENZIELE + 1)}}

# Jedes Ortsfeld ist ein Paar: Auswahl aus 'Stammziele' für die Stammziele,
# Freitext für die Einzelziele. Keine Rangfolge: was eingetragen ist, wird
# gedruckt. Sind beide gefüllt, sind es zwei Stopps -- erst die Auswahl, dann
# der Freitext. Ein Versehen steht so sichtbar im Reiseweg, statt still zu
# verschwinden; korrigiert wird durch Leeren des falschen Felds.
PAARE = "[" + ", ".join(f"(${s}, ${s}_Text)" for s in ORT_SLOTS) + "]"

# Freitext einzeilig: Zeilenumbrüche werden zu ", ", Leerzeilen fallen weg.
# Bleibt danach nichts übrig, gilt das Feld als leer.
EINZEILIG = '", ".join(x.strip() for x in (t or "").splitlines() if x.strip())'


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
if tage < 0:
  return 0
total = tage * 1440 + b - a
if total < 0:
  total += 1440
return total
'''.strip()

STUFE = '''
if not $Tagegeld_beantragt:
  return ""
if ($Abwesenheit_min or 0) - ($Min_privat_Abzug or 0) < 481:   # Anspruch dem Grunde nach
  return ""
r = $Rest_min
if r <= 0:   return ""     # Abwesenheit ging vollstaendig fuer Dienststaette/
                           # Dienstort/privaten Abzug drauf -- keine Stufe,
                           # nicht die kleinste
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

# Einzelziele der Reise, je Zeile "E26-07: Freitext". Gezählt wird wie bei
# VERMERK_LABEL: laufend über das Kalenderjahr, sortiert nach (Datum, Zeilen-Id)
# wie LFD_NR -- das Kürzel ist damit für sich allein eindeutig. Preis: eine
# nachträglich erfasste oder umdatierte Reise verschiebt die späteren Nummern
# des Jahres, wie bei Lfd_Nr und Vermerk_Label auch.
# Einzige Quelle der Nummern: REISEWEG und das Ortsverzeichnis lesen sie hier.
EINZELZIELE = f'''
def frei(r):
  return [{EINZEILIG} for t in [{", ".join(f"r.{s}_Text" for s in ORT_SLOTS)}]]
if not $Datum:
  return ""
vorher = [r for r in Reisen.all if r.Datum and r.Datum.year == $Datum.year
          and (r.Datum, r.id) < ($Datum, $id)]
n = sum(1 for r in vorher for t in frei(r) if t)
zeilen = []
for t in frei(rec):
  if t:
    n += 1
    zeilen.append("E%s-%02d: %s" % ($Datum.strftime("%y"), n, t))
return "\\n".join(zeilen)
'''.strip()

REISEWEG = f'''
e = iter(z.split(":")[0] for z in $Einzelziele.splitlines())
teile = []
for o, t in {PAARE}:
  if o:
    teile.append(o.Kuerzel)
  if (t or "").strip():
    teile.append(next(e, "?"))
return " > ".join(x for x in teile if x)
'''.strip()

MAPS = f'''
import urllib.parse as u
adr = []
for o, t in {PAARE}:
  if o and not o.Adresse:
    return ""                # Stammziel ohne Anschrift -> lieber kein Link
  if o:
    adr.append(o.Adresse)
  t = {EINZEILIG}
  if t:
    adr.append(t)            # leere Felder fallen still heraus
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

# Reiseziele mit vollständiger Adresse -- gepflegt wird ausschließlich hier,
# für jeden Ort gleich, auch für WO (Wohnung) und KV (Dienststelle). Keine
# Formel, kein Verweis auf 'Einstellungen': jeder Versuch, diese beiden Zeilen
# automatisch aus 'Einstellungen' zu befüllen, hat mehr Verwirrung erzeugt als
# die Dopplung, die er vermeiden sollte -- Ref-Spalten mit leerem Datenfeld,
# eine Formel, die Strasse/PLZ/Ort editierbar aussehen aber wirkungslos bleiben
# ließ. Bewusst zurückgebaut: bei einem Umzug ändert sich die Adresse an zwei
# Stellen (hier und in 'Einstellungen'); vergisst man eine, ist der Ausdruck
# einmal falsch -- ein Anruf bei der Abrechnungsstelle klärt das.
STAMMZIELE = [
    spalte("Kuerzel",  "Kürzel", "Text"),
    spalte("Name",     "Name der Einrichtung", "Text"),
    spalte("Strasse",  "Straße und Hausnummer", "Text"),
    spalte("PLZ",      "PLZ", "Text"),
    spalte("Ort",      "Ort", "Text"),
    spalte("Adresse",  "Vollständige Adresse", "Text",
           formel='", ".join(x for x in [$Strasse, ($PLZ + " " + $Ort).strip()] if x)'),
]

MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]
# Ohne Jahr gilt das laufende, ohne Monat das ganze Jahr -- die Liste bleibt
# auch bei hunderten Reisen kurz.
KORREKTUR_REISEN = f"""
jahr = $Korrektur_Jahr or TODAY().year
monat = {MONATE}.index($Korrektur_Monat) + 1 if $Korrektur_Monat else None
return [r for r in Reisen.all if r.Datum and r.Datum.year == jahr
        and (monat is None or r.Datum.month == monat)]
""".strip()

# Speist die Formulare (S1/S2-Kopf, Vermerke, Ortsverzeichnis) -- unabhängig von
# 'Stammziele' gepflegt, siehe Kommentar dort.
#
# IBAN/BIC werden bewusst nicht erfasst: die Kontoverbindung liegt bereits in
# der Bezügeabrechnung, im S2-Vordruck bleiben die Felder leer.
EINSTELLUNGEN = [
    spalte("Vorname", "Vorname", "Text"),
    spalte("Name", "Name", "Text"),
    spalte("Organisationseinheit", "Organisationseinheit", "Text"),
    spalte("Wohnort_Strasse", "Wohnort – Straße und Hausnummer", "Text"),
    spalte("Wohnort_PLZ", "Wohnort – PLZ", "Text"),
    spalte("Wohnort_Ort", "Wohnort – Ort", "Text"),
    spalte("Dienstort_Strasse", "Dienstort – Straße und Hausnummer", "Text"),
    spalte("Dienstort_PLZ", "Dienstort – PLZ", "Text"),
    spalte("Dienstort_Ort", "Dienstort – Ort", "Text"),
    # S2, Verfügungsteil. Hier statt im Code, solange das Repo öffentlich ist;
    # leer bleibt auf S2 die Linie zum Ausfüllen von Hand.
    spalte("Abteilung", "Abteilung (S2)", "Text"),
    spalte("Buchungsstelle", "Buchungsstelle (S2, nach „€ bei:“)", "Text"),
    spalte("Behoerde_Ort", "Behörde – Ort (S2, vor dem Datum)", "Text"),
    spalte("Behoerde", "Behörde – Name (S2, unter „3. z. d. A.“)", "Text"),
    spalte("Zeitraum_von", "Abrechnungszeitraum von", "Date"),
    spalte("Zeitraum_bis", "Abrechnungszeitraum bis", "Date"),
    # Seite Reisekorrektur: Jahr und Monat filtern nur die Liste darunter
    # (Grist-Verknüpfung über die RefList, kein eigenes Widget).
    spalte("Korrektur_Jahr", "Jahr", "Int"),
    spalte("Korrektur_Monat", "Monat", "Choice", optionen={"choices": MONATE}),
    spalte("Korrektur_Reisen", "Reisen in Jahr/Monat", "RefList:Reisen",
           formel=KORREKTUR_REISEN),
]

# Die beiden Pflichtzeilen, die setup.py in 'Stammziele' anlegt (nur Kürzel und
# Name) -- Reiseweg und Routenlink brauchen sie für fast jede Fahrt. Adresse
# trägt die Abrechnungsstelle direkt in 'Stammziele' ein, wie bei jedem anderen Ort.
FESTE_ORTE = [("WO", "Wohnung"), ("KV", "Dienststelle")]


def ort_spalten():
    """Je Stopp zwei Felder: Auswahlliste und Freitext, im Formular nebeneinander."""
    for sid in ORT_SLOTS:
        yield spalte(sid, ORT_LABEL[sid], "Ref:Stammziele")
        yield spalte(f"{sid}_Text", f"{ORT_LABEL[sid]} (Freitext)", "Text")


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
    spalte("KM_gesamt",       "Kilometer gesamt", "Int",
           formel="max(0, ($KM_Ende or 0) - ($KM_Beginn or 0))"),
    spalte("KM_dienstlich",   "Kilometer dienstlich", "Int",
           formel="max(0, $KM_gesamt - ($Umweg_privat or 0))"),
    spalte("Abwesenheit_min", "Abwesenheit (Minuten)", "Int", formel=ABWESENHEIT),
    spalte("Rest_min",        "Rest-Zeit (Minuten)", "Int",
           formel="$Abwesenheit_min - ($Min_privat_Abzug or 0) "
                  "- ($Min_Dienststaette or 0) - ($Min_Dienstort or 0)"),
    spalte("Tagegeld_Stufe",  "Tagegeld-Stufe", "Text", formel=STUFE),
    spalte("Einzelziele",     "Einzelziele (Ortsverzeichnis)", "Text", formel=EINZELZIELE),
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
    da = {c["id"]: (c.get("fields") or {})
          for c in api("GET", f"/tables/{tabelle}/columns")["columns"]}
    fehlend = [s for s in spalten if s["id"] not in da]
    if fehlend:
        api("POST", f"/tables/{tabelle}/columns", {"columns": fehlend})
    # Nur Labels bestehender Spalten nachziehen. colId unverändert mitschicken,
    # damit Grist den Formelbezug ($Ort_1_Text …) nicht aus dem neuen Label
    # ableitet. Formeln und Typ bleiben unangetastet — eine im Editor geänderte
    # Formel soll ein erneuter Lauf nicht stillschweigend zurücksetzen.
    umbenannt = [{"id": s["id"], "fields": {"colId": s["id"], "label": s["fields"]["label"]}}
                 for s in spalten
                 if da.get(s["id"], {}).get("label") not in (None, s["fields"]["label"])]
    if umbenannt:
        api("PATCH", f"/tables/{tabelle}/columns", {"columns": umbenannt})
    print(f"  Tabelle {tabelle}: {len(fehlend)} ergänzt, {len(umbenannt)} umbenannt, "
          f"{len(spalten) - len(fehlend)} vorhanden")


def reihenfolge_ordnen():
    """Setzt jede Ort-Freitext-Spalte direkt hinter ihre Auswahlspalte — in der
    Tabelle selbst, in der Rohdatenansicht, im Record-Card-Popup und in
    Tabellen-Widgets. Nötig nur, wenn die _Text-Spalten nachträglich angelegt
    wurden (sie landen dann am Ende). Formular-Sections bleiben unberührt,
    dort ordnet formular.py die Paare über Columns-Zeilen."""
    tid = sql('select id from _grist_Tables where tableId = "Reisen"')[0]["id"]
    aktionen = []

    spos = {c["colId"]: c["parentPos"] for c in
            sql(f"select colId, parentPos from _grist_Tables_column where parentId = {tid}")}
    sid = {c["colId"]: c["id"] for c in
           sql(f"select id, colId from _grist_Tables_column where parentId = {tid}")}
    aktionen += [["UpdateRecord", "_grist_Tables_column", sid[f"{s}_Text"],
                  {"parentPos": spos[s] + 0.5}]
                 for s in ORT_SLOTS
                 if f"{s}_Text" in sid and spos.get(f"{s}_Text") != spos[s] + 0.5]

    for sek in sql(f"select id from _grist_Views_section "
                   f"where tableRef = {tid} and parentKey <> 'form'"):
        felder = sql(f"select f.id, f.parentPos, c.colId from _grist_Views_section_field f "
                     f"join _grist_Tables_column c on c.id = f.colRef "
                     f"where f.parentId = {sek['id']}")
        pos = {x["colId"]: x["parentPos"] for x in felder}
        fid = {x["colId"]: x["id"] for x in felder}
        aktionen += [["UpdateRecord", "_grist_Views_section_field", fid[f"{s}_Text"],
                      {"parentPos": pos[s] + 0.5}]
                     for s in ORT_SLOTS
                     if f"{s}_Text" in fid and pos.get(f"{s}_Text") != pos[s] + 0.5]

    if aktionen:
        api("POST", "/apply", aktionen)
    print(f"  Reihenfolge: {len(aktionen)} Spalten/Felder einsortiert")


def ort_anzeige_setzen():
    """Lässt die Ort-Auswahlspalten das Kürzel zeigen statt der Zeilennummer.
    War bisher Punkt 1 der Handarbeit nach dem Lauf; aus dem eingerichteten
    Dokument abgelesen und hierher gezogen.

    Grist hängt dafür an jede Ref-Spalte eine Hilfsspalte
    (gristHelper_DisplayN, Formel `$Ort_X.Kuerzel`) und merkt sich in
    visibleCol, welche Spalte der Zieltabelle gemeint ist. SetDisplayFormula
    legt beides an -- von Hand zusammengesetzt bliebe die Hilfsspalte aus und
    die Zelle zeigte weiter die Zeilennummer. Idempotent: Spalten, die schon
    auf Kürzel zeigen, bleiben unangetastet."""
    ziel = sql("select c.id from _grist_Tables_column c join _grist_Tables t "
               "on t.id = c.parentId where t.tableId = 'Stammziele' and c.colId = 'Kuerzel'")
    if not ziel:
        print("  Ort-Anzeige: Spalte Stammziele.Kuerzel fehlt -- übersprungen")
        return
    ziel = ziel[0]["id"]

    aktionen = []
    for c in sql("select c.id, c.colId, c.visibleCol from _grist_Tables_column c "
                 "join _grist_Tables t on t.id = c.parentId "
                 "where t.tableId = 'Reisen' and c.type = 'Ref:Stammziele'"):
        if c["visibleCol"] == ziel:
            continue
        aktionen += [["SetDisplayFormula", "Reisen", None, c["id"],
                      f"${c['colId']}.Kuerzel"],
                     ["UpdateRecord", "_grist_Tables_column", c["id"],
                      {"visibleCol": ziel}]]
    if aktionen:
        api("POST", "/apply", aktionen)
    print(f"  Ort-Anzeige: {len(aktionen) // 2} Spalte(n) auf Kürzel gestellt")


# Reine Zwischenwerte oder Verknüpfungs-Spalten ohne eigenständigen
# Aussagewert für die Fachkraft -- bleiben im Datenmodell (Formeln greifen
# weiter darauf zu), verschwinden nur aus der Tabellenansicht.
HILFSSPALTEN = {
    "Reisen": ["Datum_bis", "KM_gesamt", "Abwesenheit_min", "Rest_min", "Einzelziele"],
    # Adresse ist wie in Stammziele nur die zusammengesetzte Formel aus
    # Strasse/PLZ/Ort -- die Fachkraft trägt in den Einzelfeldern ein.
    "Stammziele": ["Adresse"],
    # Zeitraum nur auf 'Ausdruck', Korrektur_* nur auf 'Reisekorrektur' --
    # für Einstellungen nimmt hilfsspalten_ausblenden() beide Seiten aus.
    "Einstellungen": ["Zeitraum_von", "Zeitraum_bis", "Korrektur_Jahr", "Korrektur_Monat",
                      "Korrektur_Reisen"],
}


def hilfsspalten_ausblenden():
    """Entfernt die HILFSSPALTEN aus allen Nicht-Formular-Ansichten der
    jeweiligen Tabelle (Formular bleibt unberührt, zeigte sie ohnehin nie).
    Die Spalte bleibt im Datenmodell -- im Editor über 'Hidden columns' am
    Ende der Tabellenansicht jederzeit wieder einblendbar. Idempotent: ein
    bereits entferntes Feld taucht in der Section nicht mehr auf."""
    aktionen = []
    for tabelle, versteckt in HILFSSPALTEN.items():
        treffer = sql(f'select id, rawViewSectionRef from _grist_Tables '
                      f'where tableId = "{tabelle}"')
        if not treffer:
            continue
        tid, raw = treffer[0]["id"], treffer[0]["rawViewSectionRef"]
        # Nur für Einstellungen: deren Karten dort zeigen genau diese Felder.
        # Reisen-Hilfsspalten müssen auch auf der Reisekorrektur weg -- Grist
        # hängt eine neu angelegte Spalte (zuletzt 'Einzelziele') an jedes
        # Widget der Tabelle, auch an die dort gestaltete Karte.
        frei = ",".join(str(v["id"]) for n in ("Ausdruck", KORREKTUR_SEITE)
                        for v in seite_suchen(n)) if tabelle == "Einstellungen" else ""
        frei = frei or "0"
        # rawViewSectionRef ist die interne "Raw Data"-Ansicht -- Grist
        # verweigert das Entfernen von Feldern dort (jede Spalte muss dort
        # vollständig bleiben); ausgeblendet wird nur in echten Grid-/
        # Card-Ansichten (Reisekorrektur, Record-Card-Popup).
        for sek in sql(f"select id from _grist_Views_section "
                       f"where tableRef = {tid} and parentKey <> 'form' and id <> {raw} "
                       f"and parentId not in ({frei})"):
            felder = sql(f"select f.id, c.colId from _grist_Views_section_field f "
                         f"join _grist_Tables_column c on c.id = f.colRef "
                         f"where f.parentId = {sek['id']}")
            aktionen += [["RemoveRecord", "_grist_Views_section_field", f["id"]]
                         for f in felder if f["colId"] in versteckt]
    if aktionen:
        api("POST", "/apply", aktionen)
    print(f"  Hilfsspalten ausgeblendet: {len(aktionen)} Feld(er)")


def formeln_angleichen(tabelle, spalten):
    """Bringt die reinen Rechenspalten (isFormula) auf den Stand hier im Code.
    Anders als Label und Formular-Layout werden diese Spalten nicht im Editor
    getunt — ein erneuter Lauf darf sie also gefahrlos zurücksetzen. Fängt u. a.
    ab, dass ein Snapshot-Restore Reiseweg/Maps_Link auf eine ältere Fassung
    zieht, die die (Freitext)-Felder ignoriert."""
    live = {c["id"]: (c.get("fields") or {})
            for c in api("GET", f"/tables/{tabelle}/columns")["columns"]}
    # isFormula wird mitgeschickt, nicht nur formula -- fängt auch den Fall
    # ab, dass eine Spalte (wie einst Stammziele!Adresse) von einer Eingabe- zu einer
    # Rechenspalte umgewidmet wird, nicht nur ihr Formeltext sich ändert.
    patch = [{"id": s["id"], "fields": {"isFormula": True, "formula": s["fields"]["formula"]}}
             for s in spalten
             if s["fields"]["isFormula"] and s["id"] in live
             and (not live[s["id"]].get("isFormula")
                  or live[s["id"]].get("formula", "").strip() != s["fields"]["formula"].strip())]
    if patch:
        api("PATCH", f"/tables/{tabelle}/columns", {"columns": patch})
    print(f"  Formeln {tabelle}: {len(patch)} angeglichen")


def blaetter(knoten):
    """Alle Section-Ids, die in einem Seitenlayout vorkommen -- auch die in
    verschachtelten Knoten (nebeneinander angeordnete Widgets)."""
    for k in knoten:
        if "leaf" in k:
            yield k["leaf"]
        yield from blaetter(k.get("children") or [])


def ohne_blaetter(knoten, weg):
    """Entfernt rekursiv alle Knoten, die auf eine der genannten Sections
    zeigen. Nötig, weil das Entfernen einer Section ihr Blatt in der
    layoutSpec stehen lässt -- ein solches Karteileichen-Blatt hat auf der
    Reisen-Seite dieses Dokuments dazu geführt, dass dort eine fremde
    Section referenziert wurde."""
    raus = []
    for k in knoten:
        if k.get("leaf") in weg:
            continue
        if k.get("children"):
            k = dict(k, children=ohne_blaetter(k["children"], weg))
            if not k["children"]:
                continue
        raus.append(k)
    return raus


def layouts_aufraeumen():
    """Nimmt aus jedem Seitenlayout die Blätter heraus, die auf eine Section
    zeigen, die es nicht (mehr) gibt oder die inzwischen zu einer anderen
    Seite gehört. Solche Karteileichen entstanden, solange das Entfernen eines
    Widgets sein Blatt stehen liess -- die Reisen-Seite verwies dadurch auf die
    Einstellungs-Karte. Idempotent: ohne Fund passiert nichts."""
    aktionen = []
    for v in sql("select id, name, layoutSpec from _grist_Views"):
        if not v["layoutSpec"]:
            continue
        eigen = {s["id"] for s in
                 sql(f"select id from _grist_Views_section where parentId = {v['id']}")}
        kinder = json.loads(v["layoutSpec"]).get("children") or []
        fremd = set(blaetter(kinder)) - eigen
        if fremd:
            aktionen.append(["UpdateRecord", "_grist_Views", v["id"], {"layoutSpec": json.dumps(
                {"children": ohne_blaetter(kinder, fremd), "collapsed": []})}])
            print(f"  Layout {v['name']}: Blatt/Blätter {sorted(fremd)} entfernt")
    if aktionen:
        api("POST", "/apply", aktionen)
    print(f"  Layouts aufgeräumt: {len(aktionen)} Seite(n)")


def seiten_kinder(vid, ohne=()):
    """Kind-Knoten des Seitenlayouts, ohne die Knoten der genannten Sections.
    Verschachtelte Knoten (nebeneinander angeordnete Widgets) tragen keinen
    eigenen 'leaf' und bleiben unangetastet stehen -- ein neues Widget wird
    davor gehaengt, nie an ihre Stelle gesetzt. Eine frisch angelegte Seite
    hat noch gar keine layoutSpec, daher das `or`.
    ponytail: ein Container, der nur entfernte Sections enthielt, bleibt als
    leerer Knoten stehen -- Grist blendet ihn aus; erst aufraeumen, wenn das
    im Editor jemals stoert."""
    roh = sql(f"select layoutSpec from _grist_Views where id = {vid}")[0]["layoutSpec"]
    return ohne_blaetter(json.loads(roh or "{}").get("children") or [], set(ohne))


def zeitraum_widget():
    """Karten-Widget 'Abrechnungszeitraum' auf der Ausdruck-Seite: nur die zwei
    Datumsfelder aus Einstellungen, über dem Druck-Widget. Die Fachkraft setzt
    den Zeitraum damit dort, wo gedruckt wird, statt in der Stammdaten-Zeile.
    Idempotent: ist das Widget da, passiert nichts."""
    et = sql("select id from _grist_Tables where tableId = 'Einstellungen'")
    if not et:
        print("  Zeitraum-Widget: Tabelle 'Einstellungen' fehlt — übersprungen")
        return
    et = et[0]["id"]
    seite = seite_suchen("Ausdruck")

    if seite:
        vid = seite[0]["id"]
        if sql(f"select id from _grist_Views_section "
               f"where parentId = {vid} and tableRef = {et} and parentKey <> 'custom'"):
            print("  Zeitraum-Widget: vorhanden")
            return
        sec = api("POST", "/apply", [["CreateViewSection", et, vid, "single", None, None]]
                  )["retValues"][0]["sectionRef"]
    else:
        # Ein frisch angelegtes Dokument hat die Seite noch nicht. Ohne sie
        # blieb die komplette Ausgabeseite ungebaut -- Zeitraum-Karte, beide
        # Druck-Widgets, Anordnung: alles übersprungen, kommentarlos. Beim
        # Lauf gegen ein leeres Testdokument aufgefallen, nicht im Betrieb,
        # weil dort immer ein Vorlagendokument kopiert wird.
        # parentId 0 legt Seite und Section zusammen an; die Seite trägt
        # danach den Tabellennamen und wird umbenannt.
        neu = api("POST", "/apply",
                  [["CreateViewSection", et, 0, "single", None, None]])["retValues"][0]
        vid, sec = neu["viewRef"], neu["sectionRef"]
        api("POST", "/apply", [["UpdateRecord", "_grist_Views", vid, {"name": "Ausdruck"}]])
        print(f"  Seite 'Ausdruck' angelegt (View {vid})")
    weg = [f["id"] for f in sql(
        f"select f.id from _grist_Views_section_field f "
        f"join _grist_Tables_column c on c.id = f.colRef "
        f"where f.parentId = {sec} and c.colId not in ('Zeitraum_von', 'Zeitraum_bis')")]
    layout = {"children": [{"leaf": sec}] + seiten_kinder(vid), "collapsed": []}
    api("POST", "/apply", [
        ["BulkRemoveRecord", "_grist_Views_section_field", weg],
        ["UpdateRecord", "_grist_Views_section", sec, {"title": "Abrechnungszeitraum"}],
        ["UpdateRecord", "_grist_Views", vid, {"layoutSpec": json.dumps(layout)}],
    ])
    print(f"  Zeitraum-Widget: angelegt (Section {sec})")


# Reihenfolge = Reihenfolge auf der Ausdruck-Seite. S1/S2, Vermerke und
# Ortsverzeichnis stecken zusammen in einer Datei (ausdruck.html) -- ein
# Widget statt drei, ein Grist-Fetch statt drei. Das Fahrtenbuch steht in
# fahrtenbuch-preview.html (Vorbereitung, noch kein Widget). Die Schnittversion
# bleibt eigenständig, sie ist kein Bestandteil der Standardausgabe.
# Routenlinks gibt es nur noch in der Prüfliste -- ein früheres Widget hier
# entfernt ausgabe_widgets() beim nächsten Lauf.
AUSGABE_WIDGETS = [
    ("Reisekostenabrechnung",        "ausdruck.html"),
    ("Fahrtenbuch",                  "fahrtenbuch.html"),
]

# Die Prüfliste liegt bewusst NICHT auf der Ausdruck-Seite, sondern auf einer
# eigenen: sie ist für die Zeiterfassungsstelle, und eine Grist-Freigabe geht
# über Seiten -- neben den Druck-Widgets bekäme die Stelle zwangsläufig alles
# andere mit zu sehen. (Seitenname, Datei)
PRUEFLISTE = ("Prüfliste", "pruefliste.html")
AUSGABE_BASIS_URL = "https://deniskarbach.github.io/Fahrtkostenabrechnung/grist/ausgabe/"


def widget_einrichten(vid, titel, url, sec=None):
    """Legt auf Seite `vid` ein Custom-Widget auf `url` an (oder konfiguriert
    eine bereits vorhandene Section `sec` dazu um) und gibt dessen Section-Id
    zurück. Die options-Struktur ist die, die Grist selbst schreibt --
    'access': 'full', weil die Widgets mehrere Tabellen lesen."""
    if sec is None:
        sec = api("POST", "/apply", [["CreateViewSection", et_id(), vid, "custom", None, None]]
                  )["retValues"][0]["sectionRef"]
    options = {"customView": json.dumps({
        "mode": "url", "url": url, "widgetDef": None, "access": "full",
        "pluginId": "", "sectionId": "", "renderAfterReady": False,
        "widgetId": None, "widgetOptions": None, "columnsMapping": None})}
    api("POST", "/apply", [["UpdateRecord", "_grist_Views_section", sec,
                            {"title": titel, "options": json.dumps(options)}]])
    return sec


def et_id():
    """Table-Ref von 'Einstellungen' -- die Custom-Widgets hängen alle daran
    (sie lesen zwar mehrere Tabellen, eine Section braucht aber genau eine)."""
    return sql("select id from _grist_Tables where tableId = 'Einstellungen'")[0]["id"]


def pruefliste_widget():
    """Die Prüfliste bekommt eine EIGENE Seite, nicht die Ausdruck-Seite: sie
    ist für die Zeiterfassungsstelle gedacht, und eine Grist-Freigabe geht über
    Seiten. Läge sie neben den Druck-Widgets, sähe die Stelle bei einer
    Freigabe zwangsläufig auch alles andere.

    Idempotent: ist die Seite mit dem Widget da, passiert nichts."""
    url = AUSGABE_BASIS_URL + PRUEFLISTE[1]
    seite = seite_suchen(PRUEFLISTE[0])

    if seite:
        vid = seite[0]["id"]
        for row in sql(f"select id, options from _grist_Views_section "
                       f"where parentId = {vid} and parentKey = 'custom'"):
            try:
                cv = json.loads(json.loads(row["options"] or "{}").get("customView") or "{}")
            except (ValueError, TypeError):
                continue
            if cv.get("url") == url:
                print(f"  Prüflisten-Seite: vorhanden")
                return
        sec = widget_einrichten(vid, PRUEFLISTE[0], url)
    else:
        # parentId 0 legt Seite und Section zusammen an (wie in
        # zeitraum_widget); die entstandene Section wird gleich das Widget.
        neu = api("POST", "/apply",
                  [["CreateViewSection", et_id(), 0, "custom", None, None]])["retValues"][0]
        vid = neu["viewRef"]
        api("POST", "/apply",
            [["UpdateRecord", "_grist_Views", vid, {"name": PRUEFLISTE[0]}]])
        sec = widget_einrichten(vid, PRUEFLISTE[0], url, sec=neu["sectionRef"])
        print(f"  Seite '{PRUEFLISTE[0]}' angelegt (View {vid})")

    api("POST", "/apply", [["UpdateRecord", "_grist_Views", vid, {"layoutSpec": json.dumps(
        {"children": [{"leaf": sec}] + seiten_kinder(vid), "collapsed": []})}]])
    print(f"  Prüflisten-Widget: angelegt (Section {sec})")


def ausgabe_widgets():
    """Gleicht die Custom-Widgets auf der Ausdruck-Seite mit AUSGABE_WIDGETS ab:
    fehlende URLs werden angelegt, vorhandene Widgets mit einer URL, die nicht
    mehr in AUSGABE_WIDGETS steht (z. B. nach einem Zusammenlegen wie hier),
    werden entfernt. Abgleich anhand der URL, nicht des Titels -- ein im
    Editor umbenanntes Widget bleibt unangetastet, solange die URL passt."""
    seite = seite_suchen("Ausdruck")
    et = sql("select id from _grist_Tables where tableId = 'Einstellungen'")
    if not (seite and et):
        print("  Ausgabe-Widgets: Seite 'Ausdruck' oder Tabelle fehlt — übersprungen")
        return
    vid, et = seite[0]["id"], et[0]["id"]
    ziel_urls = {AUSGABE_BASIS_URL + datei for _, datei in AUSGABE_WIDGETS}

    vorhanden = {}   # url -> section id
    for row in sql(f"select id, options from _grist_Views_section "
                   f"where parentId = {vid} and parentKey = 'custom'"):
        try:
            cv = json.loads(json.loads(row["options"] or "{}").get("customView") or "{}")
            if cv.get("url"):
                vorhanden[cv["url"]] = row["id"]
        except (ValueError, TypeError):
            pass

    veraltet = [sec for url, sec in vorhanden.items() if url not in ziel_urls]
    if veraltet:
        # Blätter mitnehmen: eine entfernte Section liess ihren Knoten sonst in
        # der layoutSpec stehen, und die Seite verwies auf eine Section, die es
        # nicht mehr gibt (oder inzwischen zu einer anderen Seite gehoert).
        api("POST", "/apply",
            [["RemoveRecord", "_grist_Views_section", sec] for sec in veraltet]
            + [["UpdateRecord", "_grist_Views", vid,
                {"layoutSpec": json.dumps({"children": seiten_kinder(vid, veraltet),
                                           "collapsed": []})}]])

    angelegt = 0
    for titel, datei in AUSGABE_WIDGETS:
        url = AUSGABE_BASIS_URL + datei
        if url in vorhanden:
            continue
        widget_einrichten(vid, titel, url)
        angelegt += 1
    print(f"  Ausgabe-Widgets: {angelegt} angelegt, {len(veraltet)} entfernt, "
          f"{len(AUSGABE_WIDGETS) - angelegt} vorhanden")


def ausdruck_layout():
    """Bringt die Ausdruck-Seite in die Anordnung des eingerichteten Dokuments:
    der Abrechnungszeitraum als schmale Zeile oben, darunter die Widgets aus
    AUSGABE_WIDGETS nebeneinander. Die Groessen sind die dort abgelesenen
    Verhaeltniswerte -- Grist rechnet sie relativ, die absolute Zahl ist egal.

    Fasst eine Seite nicht an, auf der bereits alle Widgets im Layout stehen:
    wer sie von Hand umsortiert hat, behaelt seine Anordnung. Greift also
    im Normalfall genau einmal, beim Einrichten eines frischen Dokuments --
    ein neu ergaenztes AUSGABE_WIDGETS-Widget zieht aber automatisch nach,
    weil dann noch nicht 'alle' im Layout stehen."""
    seite = seite_suchen("Ausdruck")
    if not seite:
        print("  Ausdruck-Layout: Seite fehlt -- übersprungen")
        return
    vid = seite[0]["id"]

    zeitraum = sql(f"select s.id from _grist_Views_section s "
                   f"join _grist_Tables t on t.id = s.tableRef "
                   f"where s.parentId = {vid} and t.tableId = 'Einstellungen' "
                   f"and s.parentKey = 'single'")
    druck = []
    for _, datei in AUSGABE_WIDGETS:
        url = AUSGABE_BASIS_URL + datei
        for row in sql(f"select id, options from _grist_Views_section "
                       f"where parentId = {vid} and parentKey = 'custom'"):
            try:
                cv = json.loads(json.loads(row["options"] or "{}").get("customView") or "{}")
            except (ValueError, TypeError):
                continue
            if cv.get("url") == url:
                druck.append(row["id"])

    if not (zeitraum and druck):
        print("  Ausdruck-Layout: Widgets unvollständig -- übersprungen")
        return
    zeitraum = zeitraum[0]["id"]

    da = set(blaetter(json.loads(
        sql(f"select layoutSpec from _grist_Views where id = {vid}")[0]["layoutSpec"] or "{}"
    ).get("children") or []))
    if {zeitraum, *druck} <= da:
        print("  Ausdruck-Layout: vorhanden")
        return

    layout = {"children": [{"size": 16, "leaf": zeitraum},
                           {"size": 118, "children": [{"leaf": d} for d in druck]}],
              "collapsed": []}
    api("POST", "/apply", [["UpdateRecord", "_grist_Views", vid,
                            {"layoutSpec": json.dumps(layout)}]])
    print(f"  Ausdruck-Layout: gesetzt (Zeitraum oben, {len(druck)} Druck-Widgets darunter)")


def feste_orte_anlegen():
    """Stellt sicher, dass 'Stammziele' die Pflichtzeilen WO und KV enthält --
    Reiseweg und Routenlink brauchen sie für fast jede Fahrt. Setzt nur
    Kürzel und Name; Adresse trägt die Abrechnungsstelle wie bei jedem
    anderen Ort direkt ein. Idempotent: ein vorhandenes Kürzel bleibt
    unangetastet -- eine vorhandene Adresse wird nie überschrieben."""
    zeilen = api("GET", "/tables/Stammziele/records")["records"]
    da = {r["fields"].get("Kuerzel") for r in zeilen}
    fehlend = [(k, n) for k, n in FESTE_ORTE if k not in da]
    if fehlend:
        api("POST", "/tables/Stammziele/records",
            {"records": [{"fields": {"Kuerzel": k, "Name": n}} for k, n in fehlend]})
        print(f"  Stammziele: {len(fehlend)} Pflichtzeile(n) angelegt "
              f"({', '.join(k for k, _ in fehlend)}) -- Adresse dort nachtragen")

    # Ein Ort ohne Anschrift laesst 'Maps_Link' jeder Reise leer, die ihn
    # anfaehrt -- das war lange nur am fehlenden Routenlink zu merken.
    ohne = sorted(r["fields"].get("Kuerzel") or f"Zeile {r['id']}" for r in zeilen
                  if not (r["fields"].get("Adresse") or "").strip())
    if ohne:
        print(f"  Stammziele: OHNE ADRESSE ({', '.join(ohne)}) -- Reisen ueber diese "
              f"Orte bekommen keinen Routenlink, Strasse/PLZ/Ort nachtragen")


def formelfehler_melden():
    """Nennt jede Formelspalte, deren Zellen einen Fehler tragen.

    Noetig, weil der Fehler sonst niemandem auffaellt: der REST-Endpunkt
    /tables/X/records liefert fuer eine Fehlerzelle schlicht null, und die
    Ausgabe-Widgets zeigen dann eine leere Spalte. So blieben die sieben
    Sync-Spalten lange kaputt. /tables/X/data reicht den Rohwert
    ["E", "SyntaxError"] durch -- daher dieser Endpunkt."""
    fehler = []
    for name in ("Stammziele", "Einstellungen", "Reisen"):
        for spalte_id, werte in api("GET", f"/tables/{name}/data").items():
            art = {w[1] for w in werte if isinstance(w, list) and w and w[0] == "E"}
            if art:
                fehler.append(f"{name}.{spalte_id}: {', '.join(sorted(art))}")
    if fehler:
        print(f"  FORMELFEHLER in {len(fehler)} Spalte(n):")
        for z in fehler:
            print(f"    {z}")
    else:
        print("  Formeln: keine Fehlerzellen")


# Seite zum Korrigieren einer erfassten Reise: oben die Karte mit
# Einstellungen!Korrektur_Jahr/_Monat (wie der Abrechnungszeitraum auf
# 'Ausdruck'), darunter links die Reisen dieses Zeitraums (nur Datum),
# rechts die gewählte Reise als eine Karte -- Felder und Paare wie im
# Formular, ohne Rechenspalten.
# Verworfen: eigenes Auswahl-Widget (zu aufwendig), vier Einzelkarten
# (unübersichtlich), Grist-Kalender (bot trotz Lesezugriff Verschieben an).
KORREKTUR_SEITE = "Reisekorrektur"
# Breiten von Auswahlliste und Karte nebeneinander, im Editor an der
# Reisekorrektur eingestellt und für alle Seiten dieser Art übernommen.
BREITE_LISTE, BREITE_KARTE = 0.6, 2.4
KORREKTUR_KARTE = [
    ("Datum", "Datum_Ende"), ("Beginn", "Ende"), ("KM_Beginn", "KM_Ende"),
    ("Umweg_privat",),
    *[(s, f"{s}_Text") for s in ORT_SLOTS],
    ("Tagegeld_beantragt",), ("Min_Dienststaette", "Min_Dienstort", "Min_privat_Abzug"),
    ("OePNV", "Nebenkosten"), ("Uebernachtung", "Verpflegung"), ("Mitnahme_Personen",),
    ("Vermerk",), ("Belege",),
]


def spalten_ids(tabelle):
    tid = sql(f"select id from _grist_Tables where tableId = '{tabelle}'")[0]["id"]
    return tid, {c["colId"]: c["id"] for c in
                 sql(f"select id, colId from _grist_Tables_column where parentId = {tid}")}


def reisekorrektur_seite():
    """Legt die Seite KORREKTUR_SEITE an: oben die Datumskarte, darunter links
    (1/5) die Liste der Reisen bis zu diesem Datum, neueste oben, rechts (4/5)
    die Karte der in der Liste gewählten Reise. Eine ältere Fassung ohne Liste
    wird ergänzt, die vorhandene Reisen-Karte bleibt. Sonst idempotent:
    eine im Editor angepasste Seite bleibt, wie sie ist."""
    et, ecol = spalten_ids("Einstellungen")
    rt, rcol = spalten_ids("Reisen")
    seite = seite_suchen(KORREKTUR_SEITE)
    if seite:
        vid = seite[0]["id"]
        da = {(r["tableRef"], r["parentKey"]): r["id"] for r in sql(
            f"select id, tableRef, parentKey from _grist_Views_section where parentId = {vid}")}
        if (rt, "record") in da:
            print(f"  Seite '{KORREKTUR_SEITE}': vorhanden")
            return
        datum, karte = da.get((et, "single")), da.get((rt, "single"))
    else:
        neu = api("POST", "/apply", [["CreateViewSection", et, 0, "single", None, None]]
                  )["retValues"][0]
        vid, datum, karte = neu["viewRef"], neu["sectionRef"], None
    datum = datum or api("POST", "/apply", [["CreateViewSection", et, vid, "single", None, None]]
                         )["retValues"][0]["sectionRef"]
    liste = liste_anlegen(vid, "Reisen", ["Datum"], ["-Datum", "-Beginn"])
    karte = karte or karte_anlegen(vid, "Reisen", KORREKTUR_KARTE)

    filter_karte(datum, ecol)
    api("POST", "/apply", [
        ["UpdateRecord", "_grist_Views", vid, {"name": KORREKTUR_SEITE, "layoutSpec": json.dumps(
            {"children": [{"leaf": datum, "size": 16},
                          {"size": 118, "children": [{"leaf": liste, "size": BREITE_LISTE},
                                                     {"leaf": karte, "size": BREITE_KARTE}]}],
             "collapsed": []})}],
        ["UpdateRecord", "_grist_Views_section", datum, {"title": "Filter"}],
        ["UpdateRecord", "_grist_Views_section", liste,
         {"title": "Reisen", "linkSrcSectionRef": datum,
          "linkSrcColRef": ecol["Korrektur_Reisen"], "linkTargetColRef": 0}],
        ["UpdateRecord", "_grist_Views_section", karte,
         {"title": "Reise bearbeiten", "linkSrcSectionRef": liste,
          "linkSrcColRef": 0, "linkTargetColRef": 0}],
    ])
    print(f"  Seite '{KORREKTUR_SEITE}': eingerichtet (View {vid})")


def filter_karte(sec, ecol):
    """Jahr und Monat nebeneinander in Karte `sec`. Felder ersetzen statt
    filtern: Grist übernimmt nicht zuverlässig alle Spalten in eine neue
    Karte (ein neues Feld fehlte im Test)."""
    weg = [f["id"] for f in sql(f"select id from _grist_Views_section_field "
                                f"where parentId = {sec}")]
    ids = api("POST", "/apply", [
        ["BulkRemoveRecord", "_grist_Views_section_field", weg],
        ["BulkAddRecord", "_grist_Views_section_field", [None, None],
         {"parentId": [sec, sec], "parentPos": [1, 2],
          "colRef": [ecol["Korrektur_Jahr"], ecol["Korrektur_Monat"]]}],
    ])["retValues"][1]
    api("POST", "/apply", [["UpdateRecord", "_grist_Views_section", sec, {"layoutSpec": json.dumps(
        {"children": [{"children": [{"leaf": i} for i in ids]}]})}]])


def liste_anlegen(vid, tabelle, spalten, sortierung):
    """Schmale Tabelle auf Seite `vid` zum Auswählen, rechts daneben steht die
    Karte zum Bearbeiten. Möglichst nur Datenspalten -- eine Rechenspalte lädt
    in einer Tabelle zum Bearbeiten der Formel ein. `sortierung`: Spalten-Ids, ein
    '-' davor sortiert absteigend."""
    tid, col = spalten_ids(tabelle)
    liste = api("POST", "/apply", [["CreateViewSection", tid, vid, "record", None, None]]
                )["retValues"][0]["sectionRef"]
    weg = [f["id"] for f in sql(f"select id from _grist_Views_section_field "
                                f"where parentId = {liste}")]
    sort = [-col[c[1:]] if c.startswith("-") else col[c] for c in sortierung]
    api("POST", "/apply", [
        ["BulkRemoveRecord", "_grist_Views_section_field", weg],
        ["BulkAddRecord", "_grist_Views_section_field", [None] * len(spalten),
         {"parentId": [liste] * len(spalten), "colRef": [col[c] for c in spalten],
          "parentPos": list(range(1, len(spalten) + 1))}],
        ["UpdateRecord", "_grist_Views_section", liste, {"sortColRefs": json.dumps(sort)}],
    ])
    return liste


def karte_anlegen(vid, tabelle, reihen):
    """Karte auf Seite `vid`; jede Reihe in `reihen` ist eine Zeile der Karte,
    mehrere Spalten darin stehen nebeneinander."""
    tid, col = spalten_ids(tabelle)
    karte = api("POST", "/apply", [["CreateViewSection", tid, vid, "single", None, None]]
                )["retValues"][0]["sectionRef"]
    # Grist legt in der Karte alle sichtbaren Spalten an -- ersetzen.
    # Position: Freitext genau hinter seine Auswahl (+0.5), wie es
    # reihenfolge_ordnen() ohnehin erzwingen würde.
    alt = [f["id"] for f in sql(f"select id from _grist_Views_section_field "
                                f"where parentId = {karte}")]
    spalten = [c for reihe in reihen for c in reihe]
    pos, i = [], 0
    for c in spalten:
        if c.endswith("_Text"):
            pos.append(pos[-1] + 0.5)
        else:
            i += 1
            pos.append(i)
    ids = api("POST", "/apply", [
        ["BulkRemoveRecord", "_grist_Views_section_field", alt],
        ["BulkAddRecord", "_grist_Views_section_field", [None] * len(spalten),
         {"parentId": [karte] * len(spalten), "colRef": [col[c] for c in spalten],
          "parentPos": pos}],
    ])["retValues"][1]
    fid = iter(ids)
    layout = {"children": [{"leaf": next(fid)} if len(r) == 1 else
                           {"children": [{"leaf": next(fid)} for _ in r]}
                           for r in reihen]}
    api("POST", "/apply", [["UpdateRecord", "_grist_Views_section", karte,
                            {"layoutSpec": json.dumps(layout)}]])
    return karte


# Seiten nach dem Muster der Reisekorrektur: links (1/5) eine schmale Liste
# zum Auswählen, rechts (4/5) die Karte zum Bearbeiten. Eine Bearbeitungs-
# ansicht je Seite statt Liste und Karte, die beide alles ändern können.
# (Seite, Tabelle, Listenspalten, Sortierung, Kartenreihen, Titel Liste, Titel Karte)
AUSWAHL_SEITEN = [
    ("Stammziele", "Stammziele", ["Kuerzel"], ["Kuerzel"],
     [("Kuerzel", "Name"), ("Strasse",), ("PLZ", "Ort")],
     "Stammziele", "Ziel bearbeiten"),
]


def auswahl_seiten():
    """Baut die AUSWAHL_SEITEN um. Idempotent: hat die Seite schon eine mit
    der Liste verknüpfte Karte, bleibt sie, wie sie ist."""
    for name, tabelle, spalten, sortierung, reihen, t_liste, t_karte in AUSWAHL_SEITEN:
        treffer = seite_suchen(name)
        if not treffer:
            print(f"  Seite '{name}': fehlt -- übersprungen")
            continue
        vid = treffer[0]["id"]
        da = sql(f"select id, parentKey, linkSrcSectionRef from _grist_Views_section "
                 f"where parentId = {vid}")
        listen = {s["id"] for s in da if s["parentKey"] == "record"}
        if any(s["parentKey"] == "single" and s["linkSrcSectionRef"] in listen for s in da):
            print(f"  Seite '{name}': vorhanden")
            continue
        liste = liste_anlegen(vid, tabelle, spalten, sortierung)
        karte = karte_anlegen(vid, tabelle, reihen)
        api("POST", "/apply", [
            *[["RemoveRecord", "_grist_Views_section", s["id"]] for s in da],
            ["UpdateRecord", "_grist_Views", vid, {"layoutSpec": json.dumps(
                {"children": [{"children": [{"leaf": liste, "size": BREITE_LISTE},
                                            {"leaf": karte, "size": BREITE_KARTE}]}],
                 "collapsed": []})}],
            ["UpdateRecord", "_grist_Views_section", liste, {"title": t_liste}],
            ["UpdateRecord", "_grist_Views_section", karte,
             {"title": t_karte, "linkSrcSectionRef": liste,
              "linkSrcColRef": 0, "linkTargetColRef": 0}],
        ])
        print(f"  Seite '{name}': Liste + Karte eingerichtet")


# Titel und Text hinter dem Info-Symbol je Widget. Schlüssel: (Seite, Tabelle,
# Widget-Art) -- bei Custom-Widgets der Dateiname statt der Art, weil alle
# an 'Einstellungen' hängen. Wird bei jedem Lauf gesetzt; eine Änderung im
# Editor gehört deshalb hierher.
WIDGET_TEXTE = {
    ("Ausdruck", "Einstellungen", "single"): ("Abrechnungszeitraum",
        "Von und bis der Abrechnung. Es zählen die Reisen, die in diesem "
        "Zeitraum beginnen."),
    ("Ausdruck", "Einstellungen", "ausdruck.html"): ("Reisekostenabrechnung",
        "S1, S2, Vermerke und Ortsverzeichnis für den Zeitraum oben. Nach "
        "neuen oder geänderten Reisen zuerst Aktualisieren, dann Drucken."),
    ("Ausdruck", "Einstellungen", "fahrtenbuch.html"): ("Fahrtenbuch",
        "Das Fahrtenbuch zum Ausschneiden und Einkleben. Vor dem Drucken "
        "Aktualisieren."),
    ("Stammziele", "Stammziele", "record"): ("Stammziele",
        "Ziele, die regelmäßig angefahren werden. Das Kürzel steht im Formular "
        "zur Auswahl. Neues Ziel: in der leeren Zeile ganz unten das Kürzel "
        "eintragen, dann rechts Name, Straße, PLZ und Ort. WO und KV bitte "
        "nicht löschen."),
    ("Stammziele", "Stammziele", "single"): ("Ziel bearbeiten",
        "Das links ausgewählte Ziel. Straße, PLZ und Ort vollständig eintragen, "
        "sonst fehlt die Anschrift im Ortsverzeichnis und der Routenlink."),
    ("Einstellungen", "Einstellungen", "single"): ("Persönliche Angaben",
        "Name, Organisationseinheit, Wohn- und Dienstanschrift. Stehen im Kopf "
        "von S1 und S2. Abteilung, Buchungsstelle und Behörde erscheinen auf S2 "
        "im Verfügungsteil; leer bleibt dort die Linie zum Ausfüllen. Einmal "
        "eintragen, bei Änderungen anpassen. Der Abrechnungszeitraum wird auf "
        "der Seite Ausdruck gesetzt."),
    ("Formularverwaltung", "Reisen", "form"): ("Formular",
        "Das Formular, mit dem die Reisen erfasst werden. Über Veröffentlichen "
        "entsteht der Link fürs Handy. Die Seite nicht löschen, sonst "
        "funktioniert der Link nicht mehr."),
    ("Prüfliste", "Einstellungen", "pruefliste.html"): ("Prüfliste",
        "Jede Reise des Zeitraums in einer Zeile, mit allem aus S1, Vermerken, "
        "Ortsverzeichnis und Fahrtenbuch. Für die Zeiterfassungsstelle."),
    ("Reisekorrektur", "Einstellungen", "single"): ("Filter",
        "Jahr eintragen und Monat wählen. Wirkt nur auf die Liste darunter. "
        "Ohne Jahr gilt das laufende, ohne Monat das ganze Jahr."),
    ("Reisekorrektur", "Reisen", "record"): ("Reisen",
        "Die Reisen im gewählten Jahr bzw. Monat, die neueste oben. Reise "
        "anklicken, rechts bearbeiten."),
    ("Reisekorrektur", "Reisen", "single"): ("Reise bearbeiten",
        "Die links gewählte Reise. Was hier geändert wird, gilt sofort. Bei "
        "den Orten wird gedruckt, was eingetragen ist -- ein falsches Feld "
        "leeren."),
}


# Nach Häufigkeit: oft Gebrauchtes oben, Einrichtung unten.
SEITEN_REIHENFOLGE = ["Ausdruck", "Reisekorrektur", "Stammziele",
                      "Prüfliste", "Einstellungen", "Formularverwaltung"]


def seiten_ordnen():
    """Bringt die Seitenliste in SEITEN_REIHENFOLGE; nicht genannte Seiten
    folgen dahinter. Idempotent."""
    rang = {n: i for i, n in enumerate(SEITEN_REIHENFOLGE)}
    seiten = sql("select p.id, p.pagePos, v.name from _grist_Pages p "
                 "join _grist_Views v on v.id = p.viewRef")
    ist = [p["id"] for p in sorted(seiten, key=lambda p: p["pagePos"])]
    seiten.sort(key=lambda p: (rang.get(ohne_icon(p["name"]), len(rang)), p["pagePos"]))
    # Grist rechnet pagePos selbst um -- verglichen wird nur die Reihenfolge.
    aktionen = [] if ist == [p["id"] for p in seiten] else [
        ["UpdateRecord", "_grist_Pages", p["id"], {"pagePos": i + 1}]
        for i, p in enumerate(seiten)]
    if aktionen:
        api("POST", "/apply", aktionen)
    print(f"  Seiten: {len(aktionen)} umsortiert")


def table1_entfernen():
    """Ein neues Grist-Dokument bringt eine leere 'Table1' mit. Nur leer
    entfernen -- hat jemand etwas hineingeschrieben, bleibt sie."""
    da = {t["id"] for t in api("GET", "/tables")["tables"]}
    if "Table1" in da and not api("GET", "/tables/Table1/records")["records"]:
        api("POST", "/apply", [["RemoveTable", "Table1"]])
        print("  Table1: leer, entfernt")


def seiten_entfernen():
    """Entfernt die Seite 'Reisen'; die Tabelle bleibt unter Raw Data
    vollständig erhalten und wird auf KORREKTUR_SEITE bearbeitet.
    Idempotent: ohne Seite passiert nichts."""
    for name in ("Reisen",):
        seite = seite_suchen(name)
        if seite:
            api("POST", "/apply", [["RemoveView", seite[0]["id"]]])
        print(f"  Seite '{name}': {'entfernt' if seite else 'nicht vorhanden'}")


def widget_texte_setzen():
    """Setzt WIDGET_TEXTE an alle passenden Widgets. Idempotent; Widgets
    ohne Eintrag bleiben unberührt."""
    aktionen = []
    for r in sql("select s.id, v.name, t.tableId, s.parentKey, s.options, s.title, s.description "
                 "from _grist_Views_section s join _grist_Views v on v.id = s.parentId "
                 "join _grist_Tables t on t.id = s.tableRef"):
        art = r["parentKey"]
        if art == "custom":
            try:
                cv = json.loads(json.loads(r["options"] or "{}").get("customView") or "{}")
                art = (cv.get("url") or "").rsplit("/", 1)[-1]
            except (ValueError, TypeError):
                continue
        soll = WIDGET_TEXTE.get((ohne_icon(r["name"]), r["tableId"], art))
        if soll and soll != (r["title"], r["description"]):
            aktionen.append(["UpdateRecord", "_grist_Views_section", r["id"],
                             {"title": soll[0], "description": soll[1]}])
    if aktionen:
        api("POST", "/apply", aktionen)
    print(f"  Titel/Beschreibungen: {len(aktionen)} gesetzt")


EINSTELLUNGEN_KARTE = [
    ("Vorname", "Name"), ("Organisationseinheit",),
    ("Wohnort_Strasse",), ("Wohnort_PLZ", "Wohnort_Ort"),
    ("Dienstort_Strasse",), ("Dienstort_PLZ", "Dienstort_Ort"),
    ("Abteilung", "Buchungsstelle"),
    ("Behoerde_Ort", "Behoerde"),
]


def karte_ergaenzen(sec, tabelle, reihen):
    """Hängt an eine bestehende Karte die Reihen an, von denen dort noch keine
    Spalte ein Feld hat. Vorhandene Felder, ihre Anordnung und Gestaltung
    bleiben unberührt. Gibt die Zahl der ergänzten Reihen zurück."""
    tid, col = spalten_ids(tabelle)
    felder = sql(f"select colRef, parentPos from _grist_Views_section_field where parentId = {sec}")
    da = {f["colRef"] for f in felder}
    fehlt = [r for r in reihen if not any(col[c] in da for c in r)]
    if not fehlt:
        return 0
    spalten = [c for r in fehlt for c in r]
    start = max((f["parentPos"] for f in felder), default=0)
    ids = iter(api("POST", "/apply", [
        ["BulkAddRecord", "_grist_Views_section_field", [None] * len(spalten),
         {"parentId": [sec] * len(spalten), "colRef": [col[c] for c in spalten],
          "parentPos": [start + i + 1 for i in range(len(spalten))]}]])["retValues"][0])
    layout = json.loads(sql(f"select layoutSpec from _grist_Views_section where id = {sec}")
                        [0]["layoutSpec"] or "{}")
    layout.setdefault("children", []).extend(
        {"leaf": next(ids)} if len(r) == 1 else {"children": [{"leaf": next(ids)} for _ in r]}
        for r in fehlt)
    api("POST", "/apply", [["UpdateRecord", "_grist_Views_section", sec,
                            {"layoutSpec": json.dumps(layout)}]])
    return len(fehlt)


def einstellungen_karte():
    """Ersetzt die Tabellenansicht auf der eigenen 'Einstellungen'-Seite durch
    ein Card-Widget: eine Zeile als Formular gelesen ist unmissverständlich,
    als Tabellenzeile wirkt sie wie eine von vielen. Felder nach
    EINSTELLUNGEN_KARTE angeordnet. Idempotent: existiert bereits eine
    angeordnete Karte auf der Seite, werden nur fehlende Reihen unten
    ergänzt -- Grist nimmt neue Spalten nicht von selbst in eine Karte auf."""
    seite = seite_suchen("Einstellungen")
    et = sql("select id from _grist_Tables where tableId = 'Einstellungen'")
    if not (seite and et):
        print("  Einstellungen-Karte: Seite oder Tabelle fehlt -- übersprungen")
        return
    vid, et = seite[0]["id"], et[0]["id"]

    if sql(f"select id from _grist_Views_section where parentId = {vid} "
           f"and tableRef = {et} and parentKey = 'single' and layoutSpec <> ''"):
        sec = sql(f"select id from _grist_Views_section where parentId = {vid} "
                  f"and tableRef = {et} and parentKey = 'single' and layoutSpec <> ''")[0]["id"]
        n = karte_ergaenzen(sec, "Einstellungen", EINSTELLUNGEN_KARTE)
        print(f"  Einstellungen-Karte: vorhanden, {n} Reihe(n) ergänzt")
        return

    alt = [s["id"] for s in sql(
        f"select id from _grist_Views_section "
        f"where parentId = {vid} and tableRef = {et} and parentKey <> 'custom'")]

    sec = karte_anlegen(vid, "Einstellungen", EINSTELLUNGEN_KARTE)
    # Nur die ersetzten Tabellen-Sections fallen aus dem Layout; alles andere
    # auf der Seite bleibt stehen. Vorher wurde die layoutSpec plattgemacht --
    # ein zweites Widget auf der Seite war danach unsichtbar (die Section blieb
    # als Karteileiche im Dokument zurueck).
    api("POST", "/apply", [
        ["UpdateRecord", "_grist_Views", vid,
         {"layoutSpec": json.dumps({"children": [{"leaf": sec}] + seiten_kinder(vid, alt),
                                    "collapsed": []})}],
        *[["RemoveRecord", "_grist_Views_section", a] for a in alt],
    ])
    print(f"  Einstellungen-Karte: angelegt (Section {sec}), Tabellenansicht entfernt")


def selbsttest():
    """Führt EINZELZIELE, REISEWEG und MAPS ohne Grist aus: was eingetragen
    ist, zählt (beide Felder gefüllt = zwei Stopps); Einzelziele zählen
    laufend je Kalenderjahr."""
    from datetime import date
    class Ort:
        def __init__(self, k="", a=""):
            self.Kuerzel, self.Adresse = k, a
        def __bool__(self):
            return bool(self.Kuerzel or self.Adresse)

    alle = []                                 # Reisen.all

    def leer(id=1, datum=date(2026, 2, 3)):
        rec = type("Rec", (), {})()
        rec.id, rec.Datum = id, datum
        for s in ORT_SLOTS:                   # alles leer als Ausgangslage
            setattr(rec, s, Ort())
            setattr(rec, f"{s}_Text", "")
        alle.append(rec)
        return rec

    reisen = type("T", (), {"all": alle})

    def lauf(formel, r=None):
        rumpf = "\n".join("  " + z for z in formel.replace("$", "rec.").splitlines())
        raum = {"Reisen": reisen}
        exec("def f(rec):\n" + rumpf, raum)
        return raum["f"](rec if r is None else r)

    def rechnen(r):
        r.Einzelziele = lauf(EINZELZIELE, r)
        return r

    rec = leer()
    rec.Ort_Beginn = Ort("BÜR", "Hauptstr. 1, Musterstadt")
    rec.Ort_1_Text = "Café Mokka\nBahnhofstr. 7, Musterstadt"  # Einzelziel, zweizeilig
    rec.Ort_2 = Ort("KITA", "Lindenweg 3, Musterstadt")
    rec.Ort_2_Text = "Haus B"                                   # beides gefüllt: zwei Stopps
    rec.Ort_3_Text = "  "                                       # nur Leerzeichen = leer
    rec.Ort_4_Text = "Hof Lindenau"
    rec.Ort_Ende = Ort("BÜR", "Hauptstr. 1, Musterstadt")
    rechnen(rec)

    assert rec.Einzelziele == ("E26-01: Café Mokka, Bahnhofstr. 7, Musterstadt\n"
                               "E26-02: Haus B\nE26-03: Hof Lindenau"), rec.Einzelziele
    weg = lauf(REISEWEG)
    assert weg == "BÜR > E26-01 > KITA > E26-02 > E26-03 > BÜR", weg
    link = lauf(MAPS)
    assert link.count("%7C") == 3, link           # vier Zwischenstopps, in Reihenfolge
    assert link.index("Lindenweg") < link.index("Haus") < link.index("Lindenau"), link
    assert "%0A" not in link, link

    # Laufend über das Jahr: zweite Reise am selben Tag und eine spätere zählen
    # weiter; eine früher datierte Reise (höhere Id) zählt nach Datum davor;
    # das neue Jahr beginnt bei 01.
    zweite = leer(id=2)
    zweite.Ort_1_Text = "Bauhof"
    assert rechnen(zweite).Einzelziele == "E26-04: Bauhof", zweite.Einzelziele
    assert lauf(REISEWEG, zweite) == "E26-04", lauf(REISEWEG, zweite)
    spaeter = leer(id=3, datum=date(2026, 3, 1))
    spaeter.Ort_1_Text = "Bauhof"
    assert rechnen(spaeter).Einzelziele == "E26-05: Bauhof", spaeter.Einzelziele
    frueher = leer(id=4, datum=date(2026, 1, 9))
    frueher.Ort_1_Text = "Bauhof"
    assert rechnen(frueher).Einzelziele == "E26-01: Bauhof", frueher.Einzelziele
    neujahr = leer(id=5, datum=date(2027, 1, 2))
    neujahr.Ort_1_Text = "Bauhof"
    assert rechnen(neujahr).Einzelziele == "E27-01: Bauhof", neujahr.Einzelziele
    alle.clear()

    # Stammziel ohne Adresse (WO/KV frisch angelegt): frueher fiel der Stopp
    # still aus dem Link und die Route war zu kurz -- jetzt gar kein Link.
    r = leer()
    r.Ort_Beginn = Ort("WO", "Beispielweg 7, Musterstadt")
    r.Ort_1 = Ort("KV", "")                   # Adresse nicht nachgetragen
    r.Ort_Ende = Ort("WO", "Beispielweg 7, Musterstadt")
    assert lauf(MAPS, r) == "", lauf(MAPS, r)
    r.Ort_1 = Ort("KV", "Verwaltungsstr. 1, Musterstadt")
    assert "Verwaltungsstr" in lauf(MAPS, r)

    # Unter zwei belegten Stopps gibt es keine Route.
    r = leer()
    r.Ort_Beginn = Ort("WO", "Beispielweg 7, Musterstadt")
    assert lauf(MAPS, r) == ""

    # Tagegeldstaffel: die vier Grenzen und der Fall, in dem Dienststaette und
    # Dienstort die Abwesenheit ganz aufbrauchen -- Rest <= 0 ergab vorher die
    # kleinste Stufe statt gar keiner.
    def stufe(abw, privat=0, dst=0, dort=0, beantragt=True):
        return lauf(STUFE, type("R", (), dict(
            Tagegeld_beantragt=beantragt, Abwesenheit_min=abw,
            Min_privat_Abzug=privat, Min_Dienststaette=dst, Min_Dienstort=dort,
            Rest_min=abw - privat - dst - dort))())

    for args, soll in [((600, 0, 500, 200), ""), ((600, 0, 600, 0), ""),
                       ((600, 0, 200, 0), "anteilig"), ((400,), ""),
                       ((500,), ">8h"), ((900,), ">=14h"), ((1500,), "24h"),
                       ((1500, 0, 0, 0, False), "")]:
        assert stufe(*args) == soll, (args, stufe(*args), soll)

    # Layout-Knoten: verschachtelte Seiten (zwei Widgets nebeneinander) tragen
    # kein eigenes 'leaf'. Beide Funktionen muessen da hineinsteigen, sonst
    # bleibt beim Aufraeumen ein Blatt einer geloeschten Section stehen.
    baum = [{"size": 16, "leaf": 15},
            {"size": 118, "children": [{"leaf": 23}, {"leaf": 22}]}]
    assert sorted(blaetter(baum)) == [15, 22, 23], list(blaetter(baum))
    assert ohne_blaetter(baum, {22}) == [{"size": 16, "leaf": 15},
                                         {"size": 118, "children": [{"leaf": 23}]}]
    assert ohne_blaetter(baum, {22, 23}) == [{"size": 16, "leaf": 15}]   # leerer Ast faellt weg
    assert ohne_blaetter(baum, set()) == baum

    # Reisekorrektur-Filter: Jahr leer = laufendes Jahr, Monat leer = ganzes Jahr.
    reisen = [type("R", (), {"Datum": d})() for d in
              (date(2025, 12, 3), date(2026, 3, 1), date(2026, 10, 2), None)]
    def filter_lauf(jahr, monat):
        rec = type("E", (), {"Korrektur_Jahr": jahr, "Korrektur_Monat": monat})()
        raum = {"Reisen": type("T", (), {"all": reisen}), "TODAY": lambda: date(2026, 10, 14)}
        exec("def f(rec):\n" + "\n".join("  " + z for z in
             KORREKTUR_REISEN.replace("$", "rec.").splitlines()), raum)
        return [r.Datum for r in raum["f"](rec)]
    assert filter_lauf(None, None) == [date(2026, 3, 1), date(2026, 10, 2)]
    assert filter_lauf(2025, None) == [date(2025, 12, 3)]
    assert filter_lauf(2026, "Oktober") == [date(2026, 10, 2)]
    assert filter_lauf(None, "Mai") == []

    print(f"Selbsttest ok ({ZWISCHENZIELE} Zwischenziele)\n  Reiseweg: {weg}")


# Beim Import (formular.py holt sich api(), ORT_SLOTS und ORT_LABEL von hier)
# passiert nichts am Dokument.
if __name__ == "__main__" and SELBSTTEST:
    selbsttest()
    sys.exit(0)

# Frühere Tabellennamen. Ein Dokument von vor der Umbenennung bekäme sonst
# leere neue Tabellen neben den alten. RenameTable zieht Formeln, Ref-Typen
# und gleichnamige Seiten selbst nach.
ALTE_TABELLEN = {"Orte": "Stammziele"}


def tabellen_umbenennen():
    da = {t["tableId"] for t in sql("select tableId from _grist_Tables")}
    aktionen = [["RenameTable", alt, neu] for alt, neu in ALTE_TABELLEN.items()
                if alt in da and neu not in da]
    if aktionen:
        api("POST", "/apply", aktionen)
    print(f"  Tabellen: {len(aktionen)} umbenannt")


# Frühere Fassung: eigene Tabelle je Freitext-Ziel, die den Freitext in
# Straße/PLZ/Ort zerlegte und unvollständige Anschriften mit ⚠️ meldete.
# Zurückgebaut -- der Freitext geht unverändert ins Ortsverzeichnis, geprüft
# wird beim Unterschreiben. Alles darin war Formel, verloren geht nichts.
# Ref-Spalten vor ihrer Zieltabelle entfernen.
#
# Tacho_Fotos: am 14.10.2026 gestrichen -- Handyfotos tragen je nach Gerät
# GPS-Koordinaten in den EXIF-Daten (oft Wohnung oder Klientenadresse), Grist
# speichert sie unverändert, und der Kilometerstand steht ohnehin im
# Fahrtenbuch. Datenminimierung. ACHTUNG: entfernt vorhandene Fotos mit.
ALTE_SPALTEN = ([f"{s}_Sync" for s in ORT_SLOTS] + ["Anschrift_Warnung", "Anschrift_Hinweis"]
                + ["Tacho_Fotos"])
ALTE_TABELLEN_WEG = ["Einzelziele", "Adressen"]


def altlasten_entfernen():
    spalten = {c["id"] for c in api("GET", "/tables/Reisen/columns")["columns"]}
    tabellen = {t["id"] for t in api("GET", "/tables")["tables"]}
    aktionen = ([["RemoveColumn", "Reisen", c] for c in ALTE_SPALTEN if c in spalten]
                + [["RemoveTable", t] for t in ALTE_TABELLEN_WEG if t in tabellen])
    if aktionen:
        api("POST", "/apply", aktionen)
    print(f"  Altlasten: {len(aktionen)} Spalte(n)/Tabelle(n) entfernt")


if __name__ == "__main__":
    print(f"Dokument {DOC} auf {URL}")
    tabellen_umbenennen()       # vor allem anderen -- sonst entstehen Doppel
    for name, spalten in (("Stammziele", STAMMZIELE), ("Reisen", REISEN), ("Einstellungen", EINSTELLUNGEN)):
        anlegen(name, spalten)      # Reihenfolge = Ref-Abhängigkeiten
        formeln_angleichen(name, spalten)

    altlasten_entfernen()       # nach formeln_angleichen: Maps_Link liest _Sync nicht mehr

    reihenfolge_ordnen()
    ort_anzeige_setzen()
    hilfsspalten_ausblenden()
    formelfehler_melden()

    if not api("GET", "/tables/Einstellungen/records")["records"]:
        api("POST", "/tables/Einstellungen/records", {"records": [{"fields": {}}]})
        print("  Einstellungen: leere Zeile angelegt")

    feste_orte_anlegen()    # fasst nur 'Stammziele' an, unabhängig von Einstellungen
    einstellungen_karte()

    zeitraum_widget()      # braucht die Ausdruck-Seite — sonst übersprungen
    ausgabe_widgets()      # dito
    ausdruck_layout()      # dito; ordnet nur ein frisch eingerichtetes Dokument
    pruefliste_widget()    # eigene Seite, getrennt freigebbar
    reisekorrektur_seite() # eigene Seite, Datumskarte + Reisen-Karte
    auswahl_seiten()       # Stammziele: Liste + Karte
    seiten_entfernen()     # erst wenn Reisekorrektur steht
    table1_entfernen()
    seiten_ordnen()
    layouts_aufraeumen()   # nach allem, was Sections anlegt oder entfernt
    widget_texte_setzen()

    print(f"""
Fertig. Rest in der Oberfläche:
  1. Seite 'Formularverwaltung' mit Formular-Widget auf Tabelle 'Reisen' anlegen
     — das Layout setzt formular.py
  2. Formular veröffentlichen, dann 'Duplicate Document' — das ist die Vorlage
""")
