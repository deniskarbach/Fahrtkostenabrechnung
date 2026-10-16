#!/usr/bin/env python3
"""Abnahmetest: 35 Testreisen (teils absichtlich fehlerhaft) in einer
Grist-Kopie OHNE Daten, Rechenspalten gegen ein unabhängiges Soll-Modell,
Ausgabe-Widgets als Druck-PDF im Browser.

Läuft gegen Grist und verbraucht API-Kontingent (rund 200 Aufrufe, der
Großteil für den Setup-Lauf auf der Kopie) -- deshalb nicht Teil von alle.sh.

    python3 grist/tests/abnahme/abnahme.py                 # neue Kopie anlegen und testen
    GRIST_TEST_DOC_ID=… python3 grist/tests/abnahme/abnahme.py   # vorhandene, leere Kopie

Die Kopie entsteht aus GRIST_DOC_ID (grist/.env) "as template": Struktur,
keine Daten. Das Skript bricht ab, wenn die Testkopie das echte Dokument ist
oder schon Reisen enthält. Nur erfundene Daten. Druck-PDFs und DOM-Abzüge
landen in einem temporären Ordner, der am Ende genannt wird.
"""
import json, os, pathlib, re, subprocess, sys, tempfile, urllib.request
from datetime import datetime, timezone

GRIST = pathlib.Path(__file__).resolve().parents[2]
REPO = GRIST.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SLOTS = ["Ort_Beginn", "Ort_1", "Ort_2", "Ort_3", "Ort_4", "Ort_5", "Ort_Ende"]

# Echtes Dokument aus .env/Umgebung -- nur als Quelle der Kopie und als Sperre.
env = dict(os.environ)
envdatei = GRIST / ".env"
if envdatei.exists():
    for z in envdatei.read_text(encoding="utf-8").splitlines():
        if "=" in z and not z.strip().startswith("#"):
            k, v = z.split("=", 1)
            env.setdefault(k.strip(), v.strip().strip('"\''))
ECHT, URL, KEY = env.get("GRIST_DOC_ID", ""), env.get("GRIST_URL", "").rstrip("/"), env.get("GRIST_API_KEY", "")
if not (ECHT and URL and KEY):
    sys.exit("GRIST_URL, GRIST_API_KEY und GRIST_DOC_ID nötig (grist/.env).")


def roh(method, pfad, daten=None):
    req = urllib.request.Request(f"{URL}/api{pfad}", method=method,
        data=json.dumps(daten).encode() if daten is not None else None,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read() or b"{}")


TEST = env.get("GRIST_TEST_DOC_ID")
if not TEST:
    ws = roh("GET", f"/docs/{ECHT}")["workspace"]["id"]
    TEST = roh("POST", f"/docs/{ECHT}/copy", {"workspaceId": ws, "asTemplate": True,
        "documentName": f"TEST Abnahme {datetime.now():%Y-%m-%d %H:%M} (Kopie ohne Daten)"})
    print(f"Testkopie angelegt: {TEST}")
if TEST == ECHT:
    sys.exit("GRIST_TEST_DOC_ID ist das echte Dokument -- Abbruch.")

# Ab hier zeigt alles auf die Testkopie: setup.py liest GRIST_DOC_ID beim Import.
os.environ["GRIST_DOC_ID"] = TEST
sys.path.insert(0, str(GRIST))
from setup import api                      # noqa: E402

if api("GET", "/tables/Reisen/records")["records"]:
    sys.exit("Die Testkopie enthält schon Reisen -- frische Kopie nehmen (GRIST_TEST_DOC_ID weglassen).")

print("Setup-Lauf auf der Testkopie …")
lauf = subprocess.run([sys.executable, str(GRIST / "setup.py")], capture_output=True, text=True,
                      env={**os.environ, "GRIST_DOC_ID": TEST})
if lauf.returncode:
    sys.exit("Setup-Lauf gescheitert:\n" + lauf.stdout[-1500:] + lauf.stderr[-1500:])
print("  " + "\n  ".join(z for z in lauf.stdout.splitlines() if "FORMELFEHLER" in z or "Formeln:" in z))


# ---------------------------------------------------------------- Testdaten

def d(y, m, t):
    return int(datetime(y, m, t, tzinfo=timezone.utc).timestamp())


eid = api("GET", "/tables/Einstellungen/records")["records"][0]["id"]
api("PATCH", "/tables/Einstellungen/records", {"records": [{"id": eid, "fields": {
    "Vorname": "Erika", "Name": "Testperson", "Organisationseinheit": "Referat 99",
    "Wohnort_Strasse": "Beispielweg 7", "Wohnort_PLZ": "00000", "Wohnort_Ort": "Musterstadt",
    "Dienstort_Strasse": "Amtsstr. 1", "Dienstort_PLZ": "00000", "Dienstort_Ort": "Musterstadt",
    "Zeitraum_von": d(2026, 1, 1), "Zeitraum_bis": d(2026, 3, 31),
    "Abteilung": "T-99", "Buchungsstelle": "9.9.9.9.9.999999",
    "Behoerde_Ort": "Teststadt", "Behoerde": "Testbehörde des Musterkreises",
    "Korrektur_Jahr": 2026, "Korrektur_Monat": "Februar"}}]})

sz = {r["fields"]["Kuerzel"]: r["id"] for r in api("GET", "/tables/Stammziele/records")["records"]}
api("PATCH", "/tables/Stammziele/records", {"records": [
    {"id": sz["WO"], "fields": {"Strasse": "Beispielweg 7", "PLZ": "00000", "Ort": "Musterstadt"}},
    {"id": sz["KV"], "fields": {"Strasse": "Amtsstr. 1", "PLZ": "00000", "Ort": "Musterstadt"}}]})
neu = api("POST", "/tables/Stammziele/records", {"records": [
    {"fields": {"Kuerzel": "KITA-A", "Name": "Kita Sonnenschein", "Strasse": "Lindenweg 3", "PLZ": "00001", "Ort": "Beispieldorf"}},
    {"fields": {"Kuerzel": "KITA-B", "Name": "Kita Regenbogen & Co <i>", "Strasse": "Am Bach 2", "PLZ": "00002", "Ort": "Talheim"}},
    {"fields": {"Kuerzel": "JA", "Name": "Jugendamt Außenstelle"}},          # ohne Adresse
]})["records"]
sz.update(zip(["KITA-A", "KITA-B", "JA"], [r["id"] for r in neu]))
WO, KV, KA, KB, JA = sz["WO"], sz["KV"], sz["KITA-A"], sz["KITA-B"], sz["JA"]


def reise(datum, beginn="08:00", ende="16:00", km=(10000, 10040), orte=None, **f):
    r = {"Datum": datum, "Beginn": beginn, "Ende": ende, "KM_Beginn": km[0], "KM_Ende": km[1],
         "Ort_Beginn": WO, "Ort_1": KV, "Ort_Ende": WO}
    if orte is not None:
        r.update({s: 0 for s in SLOTS})
        r.update(orte)
    r.update(f)
    return r


LANG = ("Umleitung wegen Vollsperrung der B 49 zwischen zwei Ortschaften, dadurch erheblicher "
        "Umweg über Landstraßen; zusätzlich Wartezeit an einer Baustellenampel. ") * 5 + "<b>fett?</b> & Ende"
TB = {"Tagegeld_beantragt": True}

FAELLE = [
 ("T01", "Dezember 2025, außerhalb Zeitraum", reise(d(2025,12,15), "08:00", "16:30", Min_Dienststaette=120, **TB)),
 ("T02", "mehrtägig über Jahreswechsel, Freitext", reise(d(2025,12,30), "07:00", "18:00", Datum_Ende=d(2026,1,2), **TB,
         orte={"Ort_Beginn": WO, "Ort_1_Text": "Tagungshaus Waldblick, Waldweg 1, 00003 Waldstadt", "Ort_Ende": WO})),
 ("T03", "zwei Freitextziele, Vermerk", reise(d(2026,1,5), "07:30", "16:30", Vermerk="Umleitung B 49", **TB,
         orte={"Ort_Beginn": WO, "Ort_1_Text": "Café Mokka, Bahnhofstr. 7, 00000 Musterstadt", "Ort_2_Text": "Bauhof, Industriestr. 4, 00000 Musterstadt", "Ort_Ende": WO})),
 ("T04", "zweite Reise am selben Tag", reise(d(2026,1,5), "13:00", "15:30",
         orte={"Ort_Beginn": KV, "Ort_1_Text": "Schule am Berg, Bergstr. 9, 00004 Bergen", "Ort_Ende": KV})),
 ("T05", "Uhrzeit '7.15'", reise(d(2026,1,7), "7.15", "16:00", **TB)),
 ("T06", "Uhrzeit '07:15 Uhr' / '16:00 UHR'", reise(d(2026,1,8), "07:15 Uhr", "16:00 UHR", **TB)),
 ("T07", "Uhrzeit '7:5'", reise(d(2026,1,9), "7:5", "17:05", **TB)),
 ("T08", "Nachtfahrt ohne Enddatum", reise(d(2026,1,12), "22:00", "02:00", **TB)),
 ("T09", "km Ende < Beginn", reise(d(2026,1,13), km=(12354, 12339))),
 ("T10", "Umweg größer als Strecke", reise(d(2026,1,14), km=(10000, 10030), Umweg_privat=40)),
 ("T11", "km mit Tausenderpunkt", reise(d(2026,1,15), km=("12.345", "12.390"))),
 ("T12", "Enddatum vor Reisedatum", reise(d(2026,1,16), "08:00", "17:00", Datum_Ende=d(2026,1,14), **TB)),
 ("T13", "Dienststätte länger als Abwesenheit", reise(d(2026,1,19), "08:00", "12:00", Min_Dienststaette=300, **TB)),
 ("T14", "negativer privater Abzug", reise(d(2026,1,20), "07:00", "15:00", Min_privat_Abzug=-60, **TB)),
 ("T15", "12h ohne Tagegeld-Antrag", reise(d(2026,1,21), "06:00", "18:00")),
 ("T16", "genau 8:00h", reise(d(2026,1,22), "08:00", "16:00", **TB)),
 ("T17", "8:01h", reise(d(2026,1,23), "08:00", "16:01", **TB)),
 ("T18", "genau 14:00h", reise(d(2026,1,26), "06:00", "20:00", **TB)),
 ("T19", "13:59h", reise(d(2026,1,27), "06:00", "19:59", **TB)),
 ("T20", "Auswahl und Freitext im selben Ortsfeld", reise(d(2026,2,2), orte={"Ort_Beginn": WO, "Ort_1": KA, "Ort_1_Text": "Haus B", "Ort_Ende": WO})),
 ("T21", "Freitext nur Leerzeichen", reise(d(2026,2,3), orte={"Ort_Beginn": WO, "Ort_1": KV, "Ort_2_Text": "   ", "Ort_Ende": WO})),
 ("T22", "Freitext mehrzeilig", reise(d(2026,2,4), orte={"Ort_Beginn": WO, "Ort_1_Text": "Café Mokka\nBahnhofstr. 7\n00000 Musterstadt", "Ort_Ende": WO})),
 ("T23", "Freitext mit Markup", reise(d(2026,2,5), orte={"Ort_Beginn": WO, "Ort_1_Text": "<script>alert(1)</script> Kita & Hort", "Ort_Ende": WO})),
 ("T24", "Freitext mit Doppelpunkt", reise(d(2026,2,6), orte={"Ort_Beginn": WO, "Ort_1_Text": "Treffpunkt: Parkplatz Nord, Am Markt 1, 00000 Musterstadt", "Ort_Ende": WO})),
 ("T25", "alle 7 Ortsfelder, 5 Freitextziele", reise(d(2026,2,9), "06:00", "21:00", **TB, orte={"Ort_Beginn": WO,
         **{f"Ort_{i}_Text": f"Einrichtung {i} mit langem Namen, Langestraße {i}, 0000{i} Langendorf" for i in range(1, 6)}, "Ort_Ende": WO})),
 ("T26", "Stammziel ohne Adresse", reise(d(2026,2,10), orte={"Ort_Beginn": WO, "Ort_1": JA, "Ort_Ende": WO})),
 ("T27", "sehr langer Vermerk mit Markup", reise(d(2026,2,11), Vermerk=LANG)),
 ("T28", "ÖPNV '4,50', weitere Kosten", reise(d(2026,2,12), OePNV="4,50", Uebernachtung=89.0, Nebenkosten=6.5, Mitnahme_Personen=2, Verpflegung="Ja")),
 ("T29", "negative Nebenkosten", reise(d(2026,2,13), Nebenkosten=-10.0)),
 ("T30", "Doppelerfassung von T29", reise(d(2026,2,13), Nebenkosten=-10.0)),
 ("T31", "keine Orte", reise(d(2026,2,17), orte={})),
 ("T32", "nur Ort Reisebeginn", reise(d(2026,2,18), orte={"Ort_Beginn": WO})),
 ("T33", "letzter Tag des Zeitraums, mehrtägig", reise(d(2026,3,31), "07:00", "17:00", Datum_Ende=d(2026,4,2), **TB,
         orte={"Ort_Beginn": WO, "Ort_1": KB, "Ort_Ende": WO})),
 ("T34", "außerhalb Zeitraum, Freitext", reise(d(2026,4,1), orte={"Ort_Beginn": WO, "Ort_1_Text": "Außerhalb, Weg 1, 00009 Fernstadt", "Ort_Ende": WO})),
 ("T35", "ohne Reisedatum", reise(None, Vermerk="ohne Datum", orte={"Ort_Beginn": WO, "Ort_1_Text": "Ohne Datum, Weg 2, 00009 Nirgendwo", "Ort_Ende": WO})),
]
ids = [r["id"] for r in api("POST", "/tables/Reisen/records",
       {"records": [{"fields": f} for _, _, f in FAELLE]})["records"]]
K = dict(zip(ids, [k for k, _, _ in FAELLE]))
BESCHR = {k: b for k, b, _ in FAELLE}
print(f"{len(ids)} Testreisen angelegt.")


# ---------------------------------------------------------------- Soll-Modell
# Unabhängig von setup.py geschrieben, nach den fachlichen Regeln: Uhrzeit =
# erste zwei Zahlen, negative Minuten zählen als 0, Freitext zählt auch neben
# einer Auswahl, Kürzel und Nummern laufend je Kalenderjahr nach (Datum, id).

def zeilen(t):
    return [dict(zip(t, w)) for w in zip(*t.values())]


daten = {t: api("GET", f"/tables/{t}/data") for t in ("Einstellungen", "Stammziele", "Reisen")}
R, S = zeilen(daten["Reisen"]), {z["id"]: z for z in zeilen(daten["Stammziele"])}
tag = lambda s: datetime.fromtimestamp(s, timezone.utc).date() if isinstance(s, (int, float)) else None


def zeit(s):
    z = re.findall(r"\d+", str(s or ""))
    return int(z[0]) * 60 + int(z[1]) if len(z) >= 2 else None


def frei(r):
    return [", ".join(x.strip() for x in (r.get(f"{s}_Text") or "").splitlines() if x.strip()) for s in SLOTS]


lfd, ez, vm, zaehler = {}, {}, {}, {}
for r in sorted((r for r in R if tag(r["Datum"])), key=lambda r: (tag(r["Datum"]), r["id"])):
    j = tag(r["Datum"]).year
    z = zaehler.setdefault(j, {"lfd": 0, "ez": 0, "vm": 0})
    z["lfd"] += 1; lfd[r["id"]] = z["lfd"]
    ez[r["id"]] = []
    for t in frei(r):
        if t:
            z["ez"] += 1; ez[r["id"]].append((f"E{j % 100:02d}-{z['ez']:02d}", t))
    if r.get("Vermerk"):
        z["vm"] += 1; vm[r["id"]] = f"V{j % 100:02d}-{z['vm']:02d}"


def soll(r):
    s = {}
    a, b = zeit(r["Beginn"]), zeit(r["Ende"])
    d0, d1 = tag(r["Datum"]), tag(r.get("Datum_Ende")) or tag(r["Datum"])
    abw = 0 if a is None or b is None or not d0 or d1 < d0 else (d1 - d0).days * 1440 + b - a
    s["Abwesenheit_min"] = abw + 1440 if abw < 0 else abw
    priv, dst, dort = (max(0, r.get(k) or 0) for k in ("Min_privat_Abzug", "Min_Dienststaette", "Min_Dienstort"))
    s["Rest_min"] = s["Abwesenheit_min"] - priv - dst - dort
    rr, st = s["Rest_min"], ""
    if r.get("Tagegeld_beantragt") and s["Abwesenheit_min"] - priv >= 481 and rr > 0:
        st = "anteilig" if rr < 481 else ">8h" if rr < 840 else ">=14h" if rr < 1440 else "24h"
    s["Tagegeld_Stufe"] = st
    s["KM_gesamt"] = max(0, r["KM_Ende"] - r["KM_Beginn"])
    s["KM_dienstlich"] = max(0, s["KM_gesamt"] - (r.get("Umweg_privat") or 0))
    s["Lfd_Nr"] = lfd.get(r["id"])
    kz, weg = iter(ez.get(r["id"], [])), []
    for sl, t in zip(SLOTS, frei(r)):
        if r.get(sl): weg.append(S[r[sl]]["Kuerzel"])
        if t: weg.append(next(kz, ("?",))[0])
    s["Reiseweg"] = " > ".join(weg)
    s["Einzelziele"] = "\n".join(f"{k}: {t}" for k, t in ez.get(r["id"], []))
    stopps = sum(bool(r.get(sl)) + bool(t) for sl, t in zip(SLOTS, frei(r)))
    s["Maps_Link?"] = stopps >= 2 and not any(r.get(sl) and not S[r[sl]]["Adresse"] for sl in SLOTS)
    s["Vermerk_Label"] = vm.get(r["id"], "")
    return s


fehlerzellen, abweichungen = [], []
for r in sorted(R, key=lambda r: K[r["id"]]):
    for sp, w in r.items():
        if isinstance(w, list) and w[:1] == ["E"]:
            fehlerzellen.append(f"{K[r['id']]}.{sp}: {w[1]}")
    for sp, sw in soll(r).items():
        ist = bool(r["Maps_Link"]) if sp == "Maps_Link?" else r[sp]
        if ist != sw:
            abweichungen.append(f"{K[r['id']]} {sp}: ist={ist!r} soll={sw!r}  [{BESCHR[K[r['id']]]}]")
for z in zeilen(daten["Stammziele"]):
    if isinstance(z["Adresse"], list):
        fehlerzellen.append(f"Stammziele {z['Kuerzel']}.Adresse: {z['Adresse'][1]}")

e = zeilen(daten["Einstellungen"])[0]
feb = sorted(K[i] for i in (e["Korrektur_Reisen"] or ["L"])[1:])
if feb != [f"T{n}" for n in range(20, 33)]:
    abweichungen.append(f"Reisekorrektur Februar 2026: {feb}")


# ---------------------------------------------------------------- Ausgabe im Browser

aus = pathlib.Path(tempfile.mkdtemp(prefix="abnahme-"))
STUB = """<script>
const __DATEN = %s;
window.grist = { docApi: { fetchTable: async n => JSON.parse(JSON.stringify(__DATEN[n])) },
                 ready() {}, onRecords() {} };
ausGrist().then(() => { document.title = "FERTIG"; }, e => { document.title = "FEHLER " + e; });
</script>
"""
befunde_ausgabe, seiten = [], {}
if not pathlib.Path(CHROME).exists():
    befunde_ausgabe.append("Chrome nicht gefunden -- Ausgabe nicht geprüft")
else:
    # Testdaten enthalten "</script>" -- im eingebetteten Block maskieren,
    # sonst endet er dort und das alert() blockiert den Browser.
    block = STUB % json.dumps(daten).replace("</", "<\\/")
    for datei in ("ausdruck.html", "fahrtenbuch.html", "pruefliste.html"):
        quelle = (GRIST / "ausgabe" / datei).read_text(encoding="utf-8")
        kopf, _, fuss = quelle.rpartition("</body>")     # das letzte: im JS steht auch eins
        ziel = aus / datei
        ziel.write_text(kopf + block + "</body>" + fuss, encoding="utf-8")
        chrome = [CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
                  f"--user-data-dir={aus / 'profil'}"]        # eigenes Profil: das normale ist gesperrt
        dom = subprocess.run(chrome + ["--dump-dom", f"file://{ziel}"],
                             capture_output=True, text=True, timeout=90).stdout
        subprocess.run(chrome + ["--no-pdf-header-footer", f"--print-to-pdf={ziel}.pdf", f"file://{ziel}"],
                       capture_output=True, timeout=90)
        dom = re.sub(r"const __DATEN = .*?;\nwindow.grist", "", dom, flags=re.S)
        (aus / f"{datei}.dom.html").write_text(dom, encoding="utf-8")
        if "<title>FERTIG</title>" not in dom:
            befunde_ausgabe.append(f"{datei}: Rendern nicht abgeschlossen")
        for muster in ("undefined", "NaN", "[object", "TypeError", "<script>alert"):
            if muster in dom:
                befunde_ausgabe.append(f"{datei}: '{muster}' im Ausdruck")
        try:
            import pymupdf
            seiten[datei] = len(pymupdf.open(f"{ziel}.pdf"))
        except ImportError:
            pass

    von, bis = tag(e["Zeitraum_von"]), tag(e["Zeitraum_bis"])
    im_zeitraum = sum(1 for r in R if tag(r["Datum"]) and von <= tag(r["Datum"]) <= bis)
    soll_fb = -(-im_zeitraum // 17) * 2
    if "fahrtenbuch.html" in seiten and seiten["fahrtenbuch.html"] != soll_fb:
        befunde_ausgabe.append(f"Fahrtenbuch: {seiten['fahrtenbuch.html']} Druckseiten, erwartet {soll_fb} "
                               f"({im_zeitraum} Reisen, 17 je Block, je Block 2 Seiten)")


# ---------------------------------------------------------------- Bericht

print(f"\nFormelfehler-Zellen: {fehlerzellen or 'keine'}")
print(f"Abweichungen Ist/Soll: {len(abweichungen)}")
for z in abweichungen:
    print("  " + z)
print(f"Ausgabe: {', '.join(f'{k} {v} S.' for k, v in seiten.items()) or '-'}")
for z in befunde_ausgabe:
    print("  !! " + z)
print(f"\nPDFs und DOM-Abzüge: {aus}")
print(f"Testkopie: {TEST} (bei Bedarf in Grist löschen)")
sys.exit(1 if fehlerzellen or abweichungen or befunde_ausgabe else 0)
