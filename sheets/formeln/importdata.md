[← Formeln-Übersicht](README.md)

# IMPORTDATA

Rohübernahme der Formularantworten, unverändert, Spalten A–ZZ.

## Zelle A1

```
=IF(Setup!B74=""; "⚠️ Keine URL hinterlegt"; IFERROR(IMPORTRANGE(Setup!B74; "Formularantworten 1!A1:ZZ"); "❌ Fehler beim Import (Zugriff erlaubt?)"))
```

| Fall | Ergebnis |
|---|---|
| Setup!B74 leer | „⚠️ Keine URL hinterlegt" |
| Zugriff schlägt fehl | „❌ Fehler beim Import (Zugriff erlaubt?)" |
| sonst | vollständige Formulardaten |

## Spaltenbelegung (finale Formularversion, A:AC)

| Spalte | Feld |
|---|---|
| A | Zeitstempel |
| B | E-Mail |
| C | Dienstreisedatum |
| D | Ende Dienstreisedatum (opt.) |
| E | Reisebeginn (Uhrzeit) |
| F | km Reisebeginn |
| G | Reiseende (Uhrzeit) |
| H | km Reiseende |
| I | Umweg privat (km) |
| J | Ort Reisebeginn |
| K | Ort Reiseende |
| L–P | Ort 1–5 |
| Q | Tagegeld beantragen? |
| R | Dienststätte-Minuten |
| S | Dienstort-Minuten |
| T | Privater Zeitabzug (Minuten, opt.) |
| U | Weitere Fahrt-/Nebenkosten? |
| V | ÖPNV |
| W | Mitnahme Personen |
| X | Übernachtung |
| Y | Nebenkosten |
| Z | Verpflegung |
| AA | Sonstige Informationen |
| AB | Screenshot |
| AC | Weitere Belege |

Jede neue Formularfrage verschiebt alle folgenden Spalten — danach IMPORTDATA-Bezüge in
BERECHNUNG, Vermerke, Druck-Fahrtenbuch und GoogleMapsExport prüfen.
