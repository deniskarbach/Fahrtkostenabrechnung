# Handbuch

Anleitung zum Ausfüllen und Abrechnen einer Dienstreise. 
Technische Details zu den einzelnen Formeln: siehe [Formeln.md](Formeln.md).

## Ablauf

1. **Google-Formular:Dienstreise** – jeweils eine Dienstreise pro Formulareingabe ausfüllen.
2. **Blatt:Setup** – einmalig Stammdaten und Freigabe erteilen, Zur Abrechnung Abrechnungszeitraum eingeben (max. 2 Monate), blaue Platzhalter nutzen.
3. **Automatisierung** – Dienstreisen erscheinen automatisch in den Blättern: S1, Fahrtenbuch-Druck, Vermerke, GoogleMapsExport sowie in den geschützen Blättern IMPORTDATA und BERECHNUNG.
4. **Ausdruck** – S1 & S2, Fahrtenbuch-Druck sowie Orte und ggf. Vermerke drucken. 

## Die Blätter im Überblick

Nur Formular und Setup werden von Hand gepflegt. Alle anderen Blätter sind reine Formelergebnisse — dort wird nichts am PC eingetragen. Diese funktionieren automatisch.

**Automatisch berechnet und ausgegeben werden:**
- Tagegeld-Staffel (anteilig ≤8h, >8h, ≥14h, 24h) je nach Abwesenheitsdauer
- Dienstlich gefahrene Kilometer, bereinigt um private Umwege
- Reiseweg als Text mit allen angefahrenen Orten
- Fahrt- und Nebenkosten: ÖPNV, Übernachtung, Mitnahme von Personen, sonstige Nebenkosten
- Google-Maps-Routenlink zur Reise

Ausgegeben in S1/S2, Druck-Fahrtenbuch, Vermerke und GoogleMapsExport.

| Blatt | Was hier zu tun ist |
|---|---|
| Setup | Einmalig einrichten (Personendaten, URL, Freigabe), **Wichtig:** pro Abrechnung den exakten Zeitraum setzen |
| IMPORTDATA | Nichts — automatischer Rohimport der Formularantworten |
| BERECHNUNG | Nichts - automatische Berechnung der importierten Werte aus IMPORTDATA |
| S1 / S2 | Nichts — ausdrucken und unterschreiben |
| Vermerke | Nichts — bei Bedarf ausdrucken. Händisch nach Ausdruck ggf. Detailbeschreibung |
| Druck-Fahrtenbuch | Nichts - ausdrucken und händisch in der Spalte Unterschrift unterschreiben |
| Orte | Pflegen: neue Reiseziele mit vollständiger Adresse ergänzen. **Wichtig:** Sollten diese Adressen dauerhaft als Auswahl im Formular nutzbar sein, müssen diese ebenenfalls ins Formular aufgenommen werden. |
| GoogleMapsExport | Nichts — Routenlink bei Bedarf nutzen |

## Formular ausfüllen

Das Formular gliedert sich in fünf Abschnitte, zwei davon mit bedingten Detailfragen.

**1. Allgemeine Angaben zur Dienstreise**
- Reisedatum (bei mehrtägigen Reisen zusätzlich Enddatum, optional)
- Reisebeginn: Uhrzeit und Kilometerstand
- Reiseende: Uhrzeit und Kilometerstand
- Umweg privat (km, optional)

**2. Angefahrene Orte**
- Ort Reisebeginn, bis zu fünf Zwischenorte, Ort Reiseende

**3a. Tagegeld – Abfrage**
- Tagegeld beantragen? (Ja/Nein)

**3b. Tagegeld – Details** *(nur bei „Ja" in 3a)*
- Aufenthaltszeit an Dienststätte und Dienstort (in Minuten)
- Privater Zeitabzug (Minuten, optional)

**4a. Weitere Fahrt- und Nebenkosten – Abfrage**
- Weitere Fahrt-/Nebenkosten? (Ja/Nein)

**4b. Weitere Fahrt- und Nebenkosten – Details** *(nur bei „Ja" in 4a)*
- ÖPNV, Übernachtung, Nebenkosten, Mitnahme von Personen

**5. Sonstiges und Nachweise**
- Unentgeltliche Verpflegung
- Sonstige Informationen (erscheinen automatisch im Blatt Vermerke)
- Screenshot, weitere Belege

## Setup-Blatt

- **Freigabe** (Feld B80 = „Ja") muss gesetzt sein, sonst bleiben die Daten gesperrt
- **URL** der Formularantworten-Datei einmalig hinterlegen, ersten Import in
  Google Sheets bestätigen
- **Abrechnungszeitraum** (C8–C10) bestimmt, welche Reisen in S1, Fahrtenbuch-Druck ausgegeben werden.

<a href="img/screenshot_setup.png" target="_blank" rel="noopener">
  <img src="img/screenshot_setup.png" alt="Setup-Blatt (zum Vergrößern anklicken)" style="width:480px;height:300px;object-fit:cover;object-position:top;border:1px solid #ddd;">
</a>

## Prüfen vor dem Drucken & Einreichung

- **Wichtig:** Änderungen an Dienstreiseinformationen können ausschließlich in der Quelle (Formularantworten) getätigt werden, in den einzelnen Blättern nicht.
- Anzeige und Ausgabe der Daten im Abrechnungszeitraum korrekt?


## Drucken

- **S1/S2** – amtliches Formular, automatisch befüllt aus dem Abrechnungszeitraum
- **Vermerke** – nur Reisen mit ausgefülltem Feld „Sonstige Informationen"
- **Druck-Fahrtenbuch** – vollständiges Fahrtenbuch des Zeitraums
- **Orte** – vollständige Liste der bekannten Orte im Fahrtenbuch

## "Einkleben" und Unterschreiben
- **Druck-Fahrtenbuch** ausdrucken bei 100%. Anschließend ausschneiden und ins Fahrtenbuch einkleben. **Wichtig:**Unterschrift händisch in das entsprechende Feld nach einkleben.
- Weitere Dateien wie üblich bei Einreichung behandeln.

## Wenn sich das Formular ändert

Neue Formularfragen verschieben alle folgenden Spalten. Danach die Bezüge in
BERECHNUNG, Vermerke, Druck-Fahrtenbuch und GoogleMapsExport prüfen – siehe
[Anhang](formeln/anhang.md).
