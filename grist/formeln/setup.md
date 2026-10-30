[← Formeln-Übersicht](README.md)

# Einrichtung und Technik

Für die Betreuung: wie das Grist-Dokument entsteht, wie die Widgets arbeiten,
wie getestet wird. Wer abrechnet oder prüft, braucht diese Seite nicht.

## Einrichten

```
cp grist/.env.beispiel grist/.env   # GRIST_URL, GRIST_API_KEY, GRIST_DOC_ID eintragen
python3 grist/setup.py
```

Nur Standardbibliothek. Zugangsdaten stehen nie im Quelltext, sondern in der
Umgebung oder in `grist/.env` (nicht versioniert). [`setup.py`](../setup.py)
ist die Quelle aller Formeln, nicht der Editor.

Ein Lauf:

- **Datenmodell:** legt fehlende Tabellen und Spalten an, zieht Beschriftungen
  nach und setzt alle Rechenformeln auf den Stand des Codes.
- **Ältere Dokumente:** benennt `Orte` in `Stammziele` um und entfernt
  Altlasten (Tabelle `Einzelziele`, `Ort_*_Sync`, `Anschrift_*`,
  `Tacho_Fotos` — **vorhandene Tachofotos gehen dabei verloren**).
- **Spalten:** setzt jede `_Text`-Spalte hinter ihre Auswahl, lässt die
  Ortsauswahl das Kürzel zeigen, blendet Zwischenwerte aus.
- **Pflichtdaten:** legt eine leere `Einstellungen`-Zeile und die Stammziele
  `WO`/`KV` (ohne Adresse) an, falls sie fehlen.
- **Seiten:** Einstellungen als Karte, `Ausdruck` (Zeitraum oben, zwei
  Druck-Widgets darunter), `Prüfliste`, `Reisekorrektur` und `Stammziele`
  (links Liste, rechts Karte); entfernt die Seite `Reisen` und eine leere
  `Table1`; ordnet die Seitenliste nach `SEITEN_REIHENFOLGE`.
- **Texte:** setzt Titel und Info-Text jedes Widgets aus `WIDGET_TEXTE` —
  Änderungen im Editor werden dabei überschrieben.
- **Meldungen:** nennt Stammziele ohne Adresse und Formelspalten mit Fehlern.

Danach von Hand in der Oberfläche:

1. Seite `Formularverwaltung` mit einem Formular-Widget auf `Reisen` anlegen
   und ans Ende ziehen; das Layout setzt [`formular.py`](../formular.py).
2. Formular veröffentlichen, dann **Duplicate Document** — das ist die Vorlage.

### Was ein erneuter Lauf anfasst

| | Verhalten |
|---|---|
| Fehlende Tabellen, Spalten, Widgets | werden ergänzt |
| Rechenformeln (`isFormula`) | werden auf den Stand des Codes **zurückgesetzt** — auch nach einem Snapshot-Restore |
| Beschriftungen | werden nachgezogen, `colId` bleibt |
| Spaltentyp, Daten, Adressen in `Stammziele` | bleiben |
| Von Hand angeordnete Seitenlayouts | bleiben, solange alle Widgets darin vorkommen |

**Ausnahme:** `formular.py` baut die Layout-Spezifikation des Formulars
**komplett neu**. Nur mit Ansage laufen lassen.

## Formular ändern

Grist-Formeln greifen über die Spalten-ID (`$KM_Ende`), nicht über die
Position. Eine neue Frage verschiebt deshalb nichts.

| Änderung | Schritt |
|---|---|
| Neues Eingabefeld | in die passende Spaltenliste in `setup.py`, Skript laufen lassen |
| Feld umbenannt | nur `label` ändern — `colId` und Formeln bleiben |
| Feld entfällt | Spalte im Editor löschen; sonst legt `setup.py` sie wieder an |
| Formularlayout | `formular.py` |
| Mehr Zwischenziele | `ZWISCHENZIELE` in `setup.py` erhöhen (heute 5), Skript laufen lassen; `ORT_SLOTS` in `ausdruck.html` und `pruefliste.html` von Hand mitziehen, sie stehen dort fest im Quelltext; dann `formular.py` |

## Ausgabe-Widgets

**Auslieferung:** Die Dateien in `ausgabe/` lädt Grist über GitHub Pages
(`AUSGABE_BASIS_URL` in `setup.py`). Eine Änderung wirkt nach `git push`; im
Grist-Tab danach hart neu laden. Umbenennen oder Verschieben ändert die
Adresse: Der nächste Lauf legt das Widget neu an, das Seitenlayout geht
verloren. Skripte, Tests und Doku gehören deshalb nicht in `ausgabe/`.

**Ohne Grist:** Jede Datei lässt sich direkt im Browser öffnen und zeigt dann
erfundene Beispieldaten — so wird das Layout geändert. Schriftgrößen,
Abstände und Rahmen stehen als CSS-Variablen am Kopf, in `ausdruck.html` je
Blatt unter einem eigenen Namensraum (`.dok-s1`, `.dok-s2` …).
`fahrtenbuch-preview.html` zeigt das Fahrtenbuch als ganzes Querblatt und ist
noch kein Widget.

**Daten:** Die Widgets hängen an `Einstellungen` und lesen mit
`requiredAccess: "full"` alle Tabellen. `grist.onRecords` feuert nur bei
Änderungen an `Einstellungen` — praktisch beim Zeitraum. Eine neue oder
korrigierte Reise kommt erst mit dem Knopf **Aktualisieren** an; die
Plugin-API kennt keinen Haken auf fremde Tabellen. Datumswerte liefert Grist
als Sekunden seit 1970, UTC-Mitternacht; angezeigt wird mit
`timeZone: "UTC"`, sonst läge ein Datum westlich von Greenwich einen Tag
daneben.

**Plugin-API:** wird von der einbettenden Grist-Instanz geladen
(`document.referrer`, ersatzweise `location.ancestorOrigins`), nicht von einer
festen Adresse. So steht der Hostname nicht im öffentlichen Repo, und kein
fremder Host bekommt Anfragen. Fehlen beide Quellen, lädt das Widget nichts und
sagt es.

**Escaping:** Zellen werden als HTML zusammengesetzt. Jeder Wert läuft durch
`esc()`, über das Präfix `` html`…` `` vor dem Template-Literal; ohne Präfix
kein Schutz. Vermerk, Freitext und Adressen kommen aus einem öffentlichen
Formular. Links in der Prüfliste entstehen per DOM-API (`a.href = …`), nicht
als HTML.

**Drucken:** nie per `window.print()` im Widget. Im Grist-Iframe greifen die
`@page`-Regeln nicht zuverlässig (Windows/Edge druckt dann hoch, die Ursache
ist nicht abschließend geklärt). `drucken()` öffnet die fertigen Blätter in
einem eigenen Fenster, wo `@page` immer gilt. Die Prüfliste ist 266 mm breit:
Sie passt so auch bei den Standardrändern des Dialogs (271,6 mm nutzbar),
falls jemand über Grists „Widget drucken“ geht. Der S1-Kopf ist zweigeteilt,
weil Chrome einen `<thead>` von rund 81 mm Höhe nicht auf Folgeseiten
wiederholt.

**Doppelter Code:** Die Sortierung der Orte-Legende steht in `ausdruck.html`
und `pruefliste.html` — die Widgets sind bewusst eigenständige Dateien.
`test_pruefliste.mjs` prüft, dass beide dieselbe Liste liefern.

## S2 erzeugen

S2 wird nicht von Hand gepflegt, sondern aus dem Blatt „S2“ der lokalen
Vorlage `ReisekostenabrechnungFINAL.xlsx` erzeugt (nicht versioniert):

```
python3 grist/s2_aus_vorlage.py > /tmp/s2.html
```

Die Ausgabe ersetzt in `ausdruck.html` den Block zwischen `<table class="s2">`
und `</table>`. Übernommen werden Ränder, Füllungen, Schriften, Zeilenhöhen,
Zellverbünde, Rich Text innerhalb von Zellen (Unterstreichungen, Fettdruck)
und die gezeichneten Unterschriftslinien aus dem Zeichnungsteil der XLSX.

Das Skript bricht ab, wenn eine behördenspezifische Zelle nicht mehr den
erwarteten Inhalt hat (Fingerabdruck, damit nichts davon ins öffentliche Repo
gerät), wenn S2 höher als ein A4-Blatt würde oder wenn die Vorlage andere
Formen als waagrechte Linien enthält. Nach einem Vorlagenwechsel:
`--fingerabdruecke`.

Geschwärzt werden vier Zellen (`SCHWAERZEN`); das Widget füllt sie aus
`Einstellungen`. Läuft das Repo später intern, entfallen die Schwärzung, die
vier Spalten und der Füllblock: `SCHWAERZEN` leeren, S2 neu erzeugen.

## Ort-Anzeige

Damit eine Ref-Spalte das Kürzel statt der Zeilennummer zeigt, braucht Grist
neben `visibleCol` eine Hilfsspalte:

```python
["SetDisplayFormula", "Reisen", None, colRef, "$Ort_Beginn.Kuerzel"]
["UpdateRecord", "_grist_Tables_column", colRef, {"visibleCol": ziel}]
```

Ohne `SetDisplayFormula` zeigt die Zelle weiter die Zeilennummer.

## Tests

Alle Offline-Tests, ohne Grist und ohne API-Kontingent:

```
sh grist/tests/alle.sh
```

| Test | Prüft |
|---|---|
| `setup.py --selbsttest` | die Formeln ohne Grist: Ortsfelder und Kürzel (Muster, Jahreswechsel, Leerzeichen, mehrzeiliger Freitext), Tagegeld-Schwellen, Uhrzeit-Schreibweisen, Adresse mit leeren Feldern, Layout-Knoten |
| [`test_druckseiten.mjs`](../tests/test_druckseiten.mjs) | jedes Blatt beginnt auf einer neuen Druckseite |
| [`test_s1_null_km.mjs`](../tests/test_s1_null_km.mjs) | S1 zeigt 0 km statt einer leeren Zelle |
| [`test_s1_zeitaufschluesselung.mjs`](../tests/test_s1_zeitaufschluesselung.mjs) | S1-Spalte „Reiseweg“ zeigt die Zeitaufschlüsselung |
| [`test_fahrtenbuch_zeit.mjs`](../tests/test_fahrtenbuch_zeit.mjs) | Fahrtenbuch Spalte 11: `DSt \| DO` einzeilig |
| [`test_fahrtenbuch_leer.mjs`](../tests/test_fahrtenbuch_leer.mjs) | ohne Reisen im Zeitraum ein leeres Blattpaar mit Spaltenköpfen |
| [`test_ortsverzeichnis.mjs`](../tests/test_ortsverzeichnis.mjs) | Reihenfolge, Stammziele je einmal, Einzelziele mit Kürzel und Datum, S2-Felder |
| [`test_pruefliste.mjs`](../tests/test_pruefliste.mjs) | Spalten, Werte, Legende gleich dem Ortsverzeichnis, Druckbreite und Druckweg |
| [`test_escaping.py`](../tests/test_escaping.py) | kein Zeilen-Template ohne `` html`…` `` |
| [`test_schwaerzung.py`](../tests/test_schwaerzung.py) | S2-Erzeugung schwärzt und bricht bei Abweichung ab (braucht die lokale Vorlage) |

**Abnahmetest** vor einer Freigabe, gegen Grist — rund 200 API-Aufrufe,
deshalb nicht in `alle.sh`:

```
python3 grist/tests/abnahme/abnahme.py
```

Legt eine Kopie des Dokuments ohne Daten an, schreibt 35 erfundene Testreisen
(Grenzwerte, Fehleingaben, Markup, Jahreswechsel), vergleicht jede Rechenspalte
mit einem unabhängigen Soll-Modell und prüft Ausdruck, Fahrtenbuch und
Prüfliste als Druck-PDF aus Chrome. Bricht ab, wenn die Kopie das echte
Dokument wäre. Die Kopie bleibt stehen und wird bei Bedarf in Grist gelöscht.
