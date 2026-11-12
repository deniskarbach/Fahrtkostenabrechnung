[← Formeln](README.md)

# Orte

## Zweck

Das Blatt ordnet jedem Kürzel eine Adresse zu; Daten ab Zeile 6, keine Formeln.
Es gibt das Blatt, damit GoogleMapsExport aus den Kürzeln Adressen für den Routenlink bildet.
Es umfasst alle Reiseziele inklusive `WO` und `KV`.

## Funktionsweise

- `WO` (Wohnort) und `KV` (Kreisverwaltung) stehen als normale Zeilen darin.
- Das Formular liefert bei Start und Ziel den Langtext „Wohnort"/
  „Kreisverwaltung", bei Wegpunkten das Kürzel; GoogleMapsExport!G3 gleicht
  beides an und schlägt es hier nach.
- Die Adressen von Wohnort und Kreisverwaltung stehen zusätzlich in Setup
  (C26–C32 bzw. C48–C54) und speisen S1 E3/J3. Bei einer Änderung beide
  Stellen pflegen.

## Formeln

Keine. Spalten:

| Spalte | Inhalt |
|---|---|
| A | Nr. |
| B | Kürzel (= Formularwert) |
| C:D | Name der Einrichtung |
| E:M | Adresse (Straße Hausnummer, PLZ Ort) |
