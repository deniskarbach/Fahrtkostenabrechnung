# Changelog

Alle nennenswerten Änderungen an diesem Projekt.

## [Unreleased]
- Repo aufgeräumt: `grist/ausgabe/` enthält nur noch die Widgets, die Grist
  per URL lädt; Tests nach `grist/tests/` mit Gesamtaufruf `alle.sh`,
  Abnahmetest nach `grist/tests/abnahme/`, S2-Generator nach `grist/`,
  Screenshots nach `sheets/img/` (auf der Doku-Seite fehlten sie bisher).
  Grist in Seitenleiste und README vor Sheets („frühere Umsetzung“).
  Versehentlich versionierte LibreOffice-Sperrdatei entfernt
- Grist, Befunde aus dem Abnahmetest (35 Testreisen):
  - Stammziel ohne PLZ/Ort: `Adresse` fängt leere Felder ab — vorher stand im
    Ortsverzeichnis „E,TypeError“ und der Routenlink war kaputt
  - Fahrtenbuch: 17 Zeilen je Block wie im Original-Fahrtenbuch (vorher 26,
    die 26. rutschte auf eine eigene Seite)
  - negative Minuten zählen in der Tagegeld-Rechnung als 0
  - negative Beträge erscheinen im Ausdruck mit Minus, statt leer zu bleiben
    und trotzdem in die Summe einzugehen
  - Uhrzeiten: Trennzeichen und Zusätze egal (`7.15`, `07:15 Uhr`, `7:15 UHR`)
  - S1 über mehrere Seiten: jede Folgeseite wiederholt den Spaltenkopf; Titel
    und Antragsteller nur auf Seite 1 (vorher hatten Folgeseiten gar keinen Kopf)
- Grist S2: Unterstreichung und Fettdruck innerhalb von Zellen werden aus der
  Vorlage übernommen (Rich Text) — u. a. die Leerstelle nach „1. KK
  anweisen,", Buchungsjahr, „z. d. A."; nur die Ziffern „1.–3." sind fett.
  Abteilung, Buchungsstelle, Ort und Name der Behörde kommen aus neuen
  Feldern in `Einstellungen`, leer bleibt die Linie. Die drei gezeichneten
  Unterschriftslinien über „(Datum)" / „(Unterschrift, Dienstbezeichnung)"
  werden aus dem Zeichnungsteil der Vorlage übernommen
- Grist Fahrtenbuch: Reiseweg zweizeilig in 7 pt, die Zeilenhöhe bleibt fest
  bei 6,35 mm. Vorher machte ein umbrechender Reiseweg die Zeile auf Seite 1
  höher als auf Seite 2, die Hälften passten nicht mehr aufeinander
- Grist Fahrtenbuch: Spalte 11 zeigt nur noch `DSt | DO`, einzeilig in 8 pt
  statt fünf Werten zweizeilig in 5,6 pt
- Grist: Einzelziele vereinfacht — keine eigene Tabelle, kein Zerlegen, keine
  ⚠️-Prüfung mehr. Der Freitext steht ungeprüft unter „Adresse" im
  Ortsverzeichnis, mit Kürzel und Datum; im Reiseweg (Fahrtenbuch,
  Prüfliste) steht nur das Kürzel `E26-07` — laufend je Jahr wie bei den
  Vermerken, vergeben in der Rechenspalte `Reisen.Einzelziele`.
- Grist: keine Rangfolge mehr zwischen Auswahl und Freitext eines Ortsfelds —
  was eingetragen ist, wird gedruckt; beide gefüllt ergeben zwei Stopps.
  Vorher gewann die Auswahl, ein Freitext daneben verschwand ohne Spur
- Grist: Tachofotos gestrichen (Formularfeld und Spalte `Tacho_Fotos`) —
  Handyfotos können GPS-Koordinaten in den EXIF-Daten tragen, Grist speichert
  sie unverändert; der Kilometerstand steht ohnehin im Fahrtenbuch Ältere Dokumente verlieren beim nächsten
  Lauf Tabelle `Einzelziele`, die `Ort_*_Sync`- und `Anschrift_*`-Spalten
- Sheets S1: Spalte „Tagegeld Anteilig" entfernt (im Originalformular nicht
  vorhanden) — anteiliges Tagegeld erscheint als `(X)` in „mehr als 8 Stunden",
  S1 reicht jetzt von A bis M
- Sheets Druck-Fahrtenbuch: Spalte K gibt die Zeitwerte der Reise aus
  (Ges, Rest, DSt, DO, Pr), zweizeilig mit ` | ` als Trenner
- Grist: dieselben beiden Anpassungen — S1 im Ausdruck ohne Spalte „Tagegeld
  Anteilig" (`(X)` in „mehr als 8 Stunden"), Fahrtenbuch-Schnittversion mit
  den Zeitwerten in Spalte 11
- Grist-Dokumentation vervollständigt, im Aufbau der Sheets-Doku: `grist/manual.md`
  (Handbuch) und `grist/formeln/` mit Erklärschema, Mustern A–E und je einem
  Dokument pro Tabelle

## 2026-09-01
- Repo in zwei eigenständige Bereiche getrennt: `sheets/` und `grist/`
- `.gitignore` für `*.xlsx` und `*.pdf` — Vorlagen und Ausdrucke bleiben lokal, das Repo ist öffentlich
- Grist-Handbuch angelegt: Ablauf und Bausteine
- Prototyp `grist/ausgabe/s1.html`: S1-Raster als druckbare Seite, Beispieldaten erfunden

## 2026-08-31
- Docsify-Dokumentation aufgesetzt (`index.html`, `README.md`, `_sidebar.md`, `manual.md`)

## 2026-08-28
- Formeln dokumentiert: Gliederung, Erklärschema, Statement-Blöcke
- Formeln an finale Formularversion (A:AC) angepasst, privater Zeitabzug ergänzt

## 2026-08-27
- Fix Vermerke-Filterung: nur Reisen mit Sonstige-Infos zeigen Datum/Text

## 2026-08-26
- Tagegeld-Formeln korrigiert: Herabstufung auf Anteilig via Rest-Zeit, exakte 8:01-Schwelle
- Formeln für Vermerke- und Druck-Fahrtenbuch-Blätter ergänzt, WO/KV-Kürzel im Reiseweg
- Initial commit
