# Formeln

Nachweis der Berechnung: jede Formel mit dem, was sie ergibt.

## Datenfluss

```
Google-Formular
   │  (Formularantworten-Datei)
   ▼
Setup            URL + Freigabe + Stammdaten + Abrechnungszeitraum
   │  IMPORTRANGE
   ▼
IMPORTDATA       Rohdaten 1:1, Spalten A–AC
   │  aufbereiten (Text → Zahl, Uhrzeit, Datum)
   ▼
BERECHNUNG       eine Zeile pro Reise, fertige Rechenwerte
   │  auf Abrechnungszeitraum filtern
   ▼
S1 / S2 · Vermerke · Druck-Fahrtenbuch · GoogleMapsExport
```

Eingetragen wird nur im Formular, in Setup und bei neuen Zielen in Orte. Alle
übrigen Blätter sind Formelergebnisse.

## Seiten

Jede Seite hat dieselbe Gliederung: Zweck, Funktionsweise, Formeln.

| Seite | Inhalt |
|---|---|
| [Setup](setup.md) | Eingaben, Freigabe, Import |
| [IMPORTDATA](importdata.md) | Rohdaten, Spaltenbelegung |
| [BERECHNUNG](berechnung.md) | alle Rechengrößen |
| [S1](s1.md) · [S2](s2.md) | Vordruck der Reisekostenabrechnung |
| [Vermerke](vermerke.md) | Sonstige Informationen |
| [Druck-Fahrtenbuch](druck-fahrtenbuch.md) | Zeilen zum Einkleben |
| [Orte](orte.md) | Ziele mit Adresse |
| [GoogleMapsExport](googlemapsexport.md) | Routenlinks |
| [Anhang](anhang.md) | Tagegeld-Staffel |
