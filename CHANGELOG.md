# Changelog

Alle nennenswerten Änderungen an diesem Projekt.

## [Unreleased]
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
