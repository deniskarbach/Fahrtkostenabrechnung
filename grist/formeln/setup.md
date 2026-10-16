[← Formeln-Übersicht](README.md)

# Einrichtung (setup.py)

[`setup.py`](../setup.py) legt das Datenmodell in einem Grist-Dokument an:
Tabellen, Spalten, Formeln, Seiten, Widgets. Das Skript ist die Quelle der
Formeln — nicht der Editor.

```
cp grist/.env.beispiel grist/.env   # dort die drei Werte eintragen
python3 grist/setup.py
```

Läuft vollständig lokal, nur Standardbibliothek. Zugangsdaten stehen **nie** im
Quelltext: entweder in der Umgebung oder in `grist/.env`, beides außerhalb der
Versionierung.

```
python3 grist/setup.py --selbsttest   # prüft die Formeln ohne Grist
```

## Was ein Lauf tut, in dieser Reihenfolge

| Schritt | Wirkung |
|---|---|
| `tabellen_umbenennen` | ältere Dokumente: `Orte` per `RenameTable` in `Stammziele` umbenennen |
| `anlegen` je Tabelle | fehlende Tabellen und Spalten ergänzen, Beschriftungen nachziehen |
| `formeln_angleichen` | Rechenspalten auf den Stand des Codes bringen |
| `altlasten_entfernen` | ältere Dokumente: Tabelle `Einzelziele` (früher `Adressen`), die sieben `Ort_*_Sync` und `Anschrift_Warnung`/`Anschrift_Hinweis` entfernen — alles reine Formeln, es geht nichts verloren. Außerdem `Tacho_Fotos` (Datenminimierung, GPS in EXIF) — **die vorhandenen Fotos gehen dabei mit** |
| `reihenfolge_ordnen` | jede `_Text`-Spalte direkt hinter ihre Auswahlspalte setzen |
| `ort_anzeige_setzen` | die Ort-Auswahlspalten zeigen das **Kürzel** statt der Zeilennummer |
| `hilfsspalten_ausblenden` | Zwischenwerte aus den Tabellenansichten nehmen |
| leere `Einstellungen`-Zeile | anlegen, falls die Tabelle leer ist |
| `feste_orte_anlegen` | `WO` und `KV` als Pflichtzeilen in `Stammziele` (ohne Adresse) |
| `einstellungen_karte` | Tabellenansicht der Einstellungen durch ein Card-Widget ersetzen |
| `zeitraum_widget` | Seite `Ausdruck` anlegen (falls nötig) und die Zeitraum-Karte darauf |
| `ausgabe_widgets` | die beiden Custom-Widgets mit ihren URLs abgleichen |
| `ausdruck_layout` | Zeitraum oben, die beiden Druck-Widgets nebeneinander darunter |
| `reisekorrektur_seite` | Seite `Reisekorrektur` anlegen (falls ohne Liste): oben Karte mit `Einstellungen.Korrektur_Jahr`/`Korrektur_Monat`, darunter links (⅓) die Reisen dieses Zeitraums über `Korrektur_Reisen`, neueste oben, rechts (⅔) die Karte der gewählten Reise mit den Formularfeldern |
| `seiten_entfernen` | Seite `Reisen` entfernen; die Tabelle bleibt unter Raw Data, bearbeitet wird auf `Reisekorrektur` |
| `layouts_aufraeumen` | Layout-Knoten entfernen, die auf fremde Sections zeigen |
| `auswahl_seiten` | Stammziele: links Liste (⅓), rechts verknüpfte Karte (⅔). Nur wenn noch keine verknüpfte Karte da ist |
| `table1_entfernen` | die leere Standardtabelle `Table1` eines neuen Dokuments entfernen |
| `seiten_ordnen` | Seitenliste nach `SEITEN_REIHENFOLGE` (Häufigkeit): Ausdruck, Reisekorrektur, Stammziele, Prüfliste, Einstellungen, Formularverwaltung |
| `widget_texte_setzen` | Titel und Info-Text an jedem Widget aus `WIDGET_TEXTE` setzen (überschreibt Änderungen im Editor) |

Danach bleiben zwei Handgriffe in der Oberfläche:

1. Formular-Widget auf `Reisen` anlegen — das Layout setzt `formular.py`
2. Formular veröffentlichen, dann **Duplicate Document** — das ist die Vorlage

## Was ein erneuter Lauf anfasst — und was nicht

Das Skript ist wiederholbar. Es unterscheidet dabei bewusst:

| | Verhalten bei einem erneuten Lauf |
|---|---|
| Fehlende Tabellen, Spalten, Widgets | werden ergänzt |
| **Rechenformeln** (`isFormula`) | werden auf den Stand des Codes **zurückgesetzt** |
| Beschriftungen | werden nachgezogen, `colId` bleibt unverändert |
| Spaltentyp, Daten | bleiben unangetastet |
| Von Hand sortierte Seitenlayouts | bleiben, solange alle Widgets darin vorkommen |
| Eingetragene Adressen in `Stammziele` | werden nie überschrieben |

Rechenspalten werden zurückgesetzt, weil sie nicht im Editor getunt werden —
das fängt unter anderem ab, dass ein Snapshot-Restore `Reiseweg` oder
`Maps_Link` auf eine ältere Fassung zieht.

> **Ausnahme:** [`formular.py`](../formular.py) überschreibt die
> Layout-Spezifikation des Formulars **vollständig**. Nur mit Ansage laufen
> lassen.

## Ort-Anzeige

Damit eine Ref-Spalte das Kürzel statt der Zeilennummer zeigt, reicht es nicht,
`visibleCol` zu setzen. Grist hängt zusätzlich eine Hilfsspalte an die Spalte:

```python
["SetDisplayFormula", "Reisen", None, colRef, "$Ort_Beginn.Kuerzel"]
["UpdateRecord", "_grist_Tables_column", colRef, {"visibleCol": ziel}]
```

**Statement:**
- `SetDisplayFormula` – legt die Hilfsspalte `gristHelper_DisplayN` mit der Formel an
- `visibleCol` – merkt sich, welche Spalte der Zieltabelle gemeint ist

**Sonderfall:** Ohne `SetDisplayFormula` bliebe die Hilfsspalte aus und die
Zelle zeigte weiter die Zeilennummer.

## Selbsttest

`--selbsttest` führt die Formeln ohne Grist aus und prüft:

- **Einzelziele / Reiseweg / Routenlink** — was eingetragen ist, zählt
  (Muster B): Auswahl und Freitext im selben Ortsfeld ergeben zwei Stopps, in
  Reihenfolge; ein Feld nur mit Leerzeichen zählt nicht; mehrzeiliger
  Freitext wird einzeilig;
  die Kürzel zählen laufend je Kalenderjahr über Reisen hinweg, nach Datum
  sortiert (eine früher datierte, später erfasste Reise zählt davor; das neue
  Jahr beginnt bei `E27-01`)
- **Tagegeld-Staffel** — acht Fälle über alle vier Schwellen, darunter der
  Fall mit aufgebrauchter Rest-Zeit
- **Layout-Knoten** — `blaetter()` und `ohne_blaetter()` steigen in
  verschachtelte Knoten hinein

Weitere Tests im Repo:

| Datei | Prüft |
|---|---|
| [`ausgabe/test_ortsverzeichnis.mjs`](../ausgabe/test_ortsverzeichnis.mjs) | Ortsverzeichnis: Stammziele höchstens einmal, Reihenfolge, Einzelziele mit Kürzel, Datum und ungeprüftem Freitext |
| [`ausgabe/test_escaping.py`](../ausgabe/test_escaping.py) | kein Zeilen-Template ohne `html\`\``-Präfix |
| [`ausgabe/test_schwaerzung.py`](../ausgabe/test_schwaerzung.py) | S2-Erzeugung schwärzt und bricht bei Abweichung ab |

