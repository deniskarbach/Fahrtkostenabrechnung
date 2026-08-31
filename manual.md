# Handbuch

Anleitung zum Ausfüllen und Abrechnen einer Dienstreise. Technische Details zu
den einzelnen Formeln: siehe [Formeln.md](Formeln.md).

## Ablauf

1. **Google-Formular ausfüllen** – eine Dienstreise pro Formularabgabe
2. **Setup-Blatt** – Freigabe erteilen, Stammdaten und Abrechnungszeitraum prüfen
3. **Kontrolle** – Reise erscheint automatisch in BERECHNUNG
4. **Ausdruck** – S1/S2 sowie ggf. Vermerke und Druck-Fahrtenbuch drucken

## Die Blätter im Überblick

Nur Formular und Setup werden von Hand gepflegt. Alle anderen Blätter sind
reine Formelergebnisse — dort wird nichts eingetragen.

| Blatt | Was hier zu tun ist |
|---|---|
| Setup | Einmalig einrichten (URL, Freigabe), pro Abrechnung den Zeitraum setzen |
| IMPORTDATA | Nichts — automatischer Rohimport der Formularantworten |
| BERECHNUNG | Nichts, aber rot markierte Zeilen kontrollieren (unplausible Kilometer/Zeiten) |
| S1 / S2 | Nichts — ausdrucken und unterschreiben |
| Vermerke | Nichts — bei Bedarf ausdrucken |
| Druck-Fahrtenbuch | Nichts — bei Bedarf ausdrucken |
| Orte | Pflegen: neue Reiseziele mit vollständiger Adresse ergänzen |
| GoogleMapsExport | Nichts — Routenlink bei Bedarf nutzen |

## Formular ausfüllen

Pflichtangaben je Reise:

- Reisedatum (und ggf. Enddatum bei mehrtägigen Reisen)
- Reisebeginn/-ende mit Uhrzeit und Kilometerstand
- Ort Reisebeginn, Zwischenorte, Ort Reiseende
- Tagegeld beantragen? (Ja/Nein)
- Aufenthaltszeit an Dienststätte und Dienstort (in Minuten)

Optional:

- Umweg privat (km), privater Zeitabzug (Minuten)
- ÖPNV, Übernachtung, Nebenkosten, Mitnahme von Personen
- Sonstige Informationen (erscheinen automatisch im Blatt Vermerke)

## Setup-Blatt

- **Freigabe** (Feld B80 = „Ja") muss gesetzt sein, sonst bleiben die Daten gesperrt
- **URL** der Formularantworten-Datei einmalig hinterlegen, ersten Import in
  Google Sheets bestätigen
- **Abrechnungszeitraum** (C8–C10) bestimmt, welche Reisen in S1/S2 landen

![Setup-Blatt](img/screenshot_setup.png)

## Prüfen vor dem Drucken

- Rot markierte Zeilen in BERECHNUNG prüfen (unplausible Kilometer oder Zeiten)
- Reisedatum Ende vor Reisedatum Start wird im Setup-Blatt farblich markiert

## Drucken

- **S1/S2** – amtliches Formular, automatisch befüllt aus dem Abrechnungszeitraum
- **Vermerke** – nur Reisen mit ausgefülltem Feld „Sonstige Informationen"
- **Druck-Fahrtenbuch** – vollständiges Fahrtenbuch des Zeitraums

## Wenn sich das Formular ändert

Neue Formularfragen verschieben alle folgenden Spalten. Danach die Bezüge in
BERECHNUNG, Vermerke, Druck-Fahrtenbuch und GoogleMapsExport prüfen – siehe
[Anhang](formeln/anhang.md).
