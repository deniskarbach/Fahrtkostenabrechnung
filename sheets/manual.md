# Anleitung

Für die Fachkraft: einrichten, erfassen, abrechnen. Kilometer, Tagegeld-Stufe,
laufende Nummern, Reiseweg und Routenlink rechnet die Tabelle selbst — wie,
steht in den [Formeln](formeln/README.md).

## Die Blätter

Von Hand gepflegt werden nur Formular, Setup und Orte. Alle anderen Blätter
sind Formelergebnisse; dort wird nichts eingetragen.

| Blatt | Wofür | Aufgabe |
|---|---|---|
| Setup | Verknüpfung zur Formularantworten-Datei, Stammdaten, Abrechnungszeitraum | einrichten, pro Abrechnung Zeitraum setzen |
| IMPORTDATA | Rohübernahme der Formularantworten | — |
| BERECHNUNG | Zeiten, Kilometer, Tagegeld je Reise | — |
| S1 / S2 | Vordruck zur Erstattung | drucken, unterschreiben |
| Vermerke | „Sonstige Informationen" der Reisen | bei Bedarf drucken |
| Druck-Fahrtenbuch | Zeilen zum Einkleben ins Fahrtenbuch | drucken, unterschreiben |
| Orte | Adressen der Reiseziele | neue Ziele ergänzen |
| GoogleMapsExport | Routenlink je Reise | bei Bedarf nutzen |

## Einmalig einrichten

1. **Setup:** Stammdaten eintragen (Person, Wohn- und Dienstanschrift, Bankverbindung).
2. **URL** der Formularantworten-Datei hinterlegen.
3. **Freigabe** auf „Ja" setzen (Feld B80) und den ersten Import in Google
   Sheets bestätigen. Ohne Freigabe bleiben die Daten gesperrt.

![Setup-Blatt](img/screenshot_setup.png ':size=480')

*Blatt „Setup"*

## Reise erfassen

Das Formular am PC oder Handy öffnen (Google-Konto nötig), ausfüllen,
absenden. Eine Absendung ist eine Reise.

![Formular Dienstreise](img/screenshot_formular.png ':size=480')

*Formular „Dienstreise" – Startseite*

1. **Allgemeine Angaben:** Reisedatum (bei mehrtägigen Reisen Enddatum),
   Reisebeginn und Reiseende mit Uhrzeit und Kilometerstand, optional Umweg
   privat (km).
2. **Orte:** Ort Reisebeginn, bis zu fünf Zwischenorte, Ort Reiseende.
3. **Tagegeld:** „Tagegeld beantragen?"; bei „Ja" Aufenthaltszeit an
   Dienststätte und Dienstort (Minuten), optional privater Zeitabzug (Minuten).
4. **Weitere Kosten:** „Weitere Fahrt-/Nebenkosten?"; bei „Ja" ÖPNV,
   Übernachtung, Nebenkosten, Mitnahme von Personen.
5. **Sonstiges:** unentgeltliche Verpflegung, Sonstige Informationen (erscheinen
   im Blatt Vermerke), Screenshot, weitere Belege.

## Reise korrigieren

Nur in der Formularantworten-Datei ändern, nicht in den Blättern. Alles
Berechnete zieht nach.

## Neue Orte ergänzen

Im Blatt `Orte` Kürzel und vollständige Adresse eintragen. Soll der Ort
dauerhaft im Formular auswählbar sein, ihn zusätzlich dort ergänzen.

## Abrechnen

1. **Setup:** Abrechnungszeitraum setzen (C8–C10, höchstens 2 Monate).
2. **Prüfen:** Erscheinen in S1 und Druck-Fahrtenbuch alle Reisen des Zeitraums?
3. **Drucken:** S1 und S2, Druck-Fahrtenbuch, bei Bedarf Vermerke und Orte.
4. S1/S2 unterschreiben und einreichen.

## Fahrtenbuch einkleben und unterschreiben

- Druck-Fahrtenbuch bei **100 %** drucken.
- Ausschneiden, ins Fahrtenbuch einkleben, von Hand in der Spalte
  „Unterschrift" unterschreiben.

## Wenn sich das Formular ändert

Neue Formularfragen verschieben alle folgenden Spalten. Danach die Bezüge in
BERECHNUNG, Vermerke, Druck-Fahrtenbuch und GoogleMapsExport prüfen
([IMPORTDATA](formeln/importdata.md)).
