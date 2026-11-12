[← Formeln](README.md)

# Einstellungen

## Zweck

Hier stehen die eigenen Stammdaten und der Abrechnungszeitraum, genau eine Zeile.
Die Ansicht gibt es, damit persönliche Daten an einer einzigen Stelle liegen und jeder Ausdruck daraus seinen Kopf bekommt.
Sie umfasst Name, Anschriften, die S2-Angaben und den Zeitraum.

## Funktionsweise

- Die Zeile liefert den Kopf jedes Ausdrucks: `Name Vorname, Organisationseinheit`
  und Anschriften als `Straße, PLZ Ort`. Leere Felder fallen samt Trennzeichen
  weg.
- Leere S2-Felder bleiben als Linie zum Ausfüllen von Hand.
- Der Abrechnungszeitraum wird auf der Seite `Ausdruck` gesetzt. Eine Reise
  erscheint, wenn ihr Reisedatum (`Datum`) zwischen `Zeitraum_von` und
  `Zeitraum_bis` liegt, beide Tage eingeschlossen. Eine leere Grenze begrenzt
  nicht; ohne Zeitraum erscheinen alle Reisen. Reisen ohne Datum erscheinen
  nie. Eine mehrtägige Reise, die vor `Zeitraum_von` beginnt, gehört zur
  früheren Abrechnung.
- `Korrektur_Jahr` und `Korrektur_Monat` gehören zur Seite
  [Reisekorrektur](reisekorrektur.md).

| Spalte | Typ | Wofür |
|---|---|---|
| `Vorname`, `Name`, `Organisationseinheit` | Text | Kopf: Antragsteller/in |
| `Wohnort_Strasse`, `_PLZ`, `_Ort` | Text | Kopf: Wohnort |
| `Dienstort_Strasse`, `_PLZ`, `_Ort` | Text | Kopf: Dienstort |
| `Abteilung`, `Buchungsstelle`, `Behoerde_Ort`, `Behoerde` | Text | S2 |
| `Zeitraum_von`, `Zeitraum_bis` | Date | Abrechnungszeitraum |

## Formeln

Keine.
