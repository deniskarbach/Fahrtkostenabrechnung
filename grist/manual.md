# Anleitung

Für die Fachkraft: einrichten, erfassen, abrechnen. Kilometer, Tagegeld-Stufe,
laufende Nummern, Reiseweg und Routenlink rechnet die Tabelle selbst — wie,
steht in den [Formeln](formeln/README.md).

## Die Seiten

| Seite | Wofür |
|---|---|
| Ausdruck | Abrechnungszeitraum setzen, drucken |
| Reisekorrektur | eine erfasste Reise ändern |
| Stammziele | regelmäßige Ziele mit Adresse |
| Prüfliste | alle Angaben je Reise in einer Zeile, für die Zeiterfassungsstelle |
| Einstellungen | eigene Stammdaten |
| Formularverwaltung | das Formular, nur beim Einrichten — **nicht löschen**, sonst funktioniert der Link nicht mehr |

## Einmalig einrichten

1. **Vorlage kopieren.** Gearbeitet wird immer in der eigenen Kopie.
2. **Einstellungen:** Name, Vorname, Organisationseinheit, Wohn- und
   Dienstanschrift. Für S2 außerdem Abteilung, Buchungsstelle und Behörde;
   leer bleibt dort eine Linie zum Ausfüllen von Hand.
3. **Stammziele:** die Adressen von `WO` (Wohnung) und `KV` (Dienststelle)
   eintragen, weitere regelmäßige Ziele ergänzen. Ohne Adresse gibt es für
   Reisen über dieses Ziel keinen Routenlink.
4. **Formularverwaltung:** Formular veröffentlichen und den Link auf dem Handy oder PC als Favorit
   ablegen. Das muss in der eigenen Kopie geschehen — der Link der Vorlage
   schreibt nicht in die eigene Tabelle.

## Reise erfassen

1. Formularlink auf dem Handy öffnen (für das Schreiben ist keine Anmeldung im eigenen Konto nötig).
2. **Datum und Uhrzeiten** eintragen, z. B. `07:15`. Bei mehrtägigen Reisen das
   Enddatum angeben.
3. **Kilometerstand** bei Beginn und Ende, bei privatem Umweg dessen Kilometer.
4. **Orte:** je Ort **entweder** aus der Liste wählen **oder** in den Freitext
   schreiben: `Bezeichnung, Straße Hausnummer, PLZ Ort`, z. B.
   `Café Mokka, Bahnhofstr. 7, 12345 Musterstadt`. Sind beide Felder gefüllt,
   zählen sie als zwei Stopps. Unbekannte bzw. einmalige Orte immer in den
   Freitext.
   - **Mehr als 5 Zwischenziele:** Durch zusätzliches Befüllen der
     Freitextfelder sind maximal 10 Zwischenziele möglich, mit etwas
     Mehraufwand.
   - **Dauerhaftes Ziel:** Neue Ziele für die Auswahlliste über die Ansicht
     `Stammziele` anlegen. Bereits erfasste einmalige Ziele ändern sich
     dadurch nicht.
5. **Tagegeld, Kosten, Sonstige Informationen** nach Bedarf; Minuten und
   Beträge immer positiv. Sonstige Informationen erscheinen auf dem Blatt
   Vermerke.
6. Absenden. Eine Absendung ist eine Reise.

## Reise korrigieren

1. Seite `Reisekorrektur` öffnen.
2. Oben das Jahr eintragen (mit **Enter** bestätigen) und den Monat wählen.
   Ohne Jahr gilt das laufende, ohne Monat das ganze Jahr.
3. Links die Reise anklicken, rechts ändern.

Alles Berechnete zieht sofort nach; ein geändertes Datum verschiebt die
laufenden Nummern des Jahres.

## Stammziele pflegen

**Neues Ziel:** in der leeren Zeile unten in der Liste das Kürzel eintragen,
rechts Name, Straße, PLZ und Ort. Das Kürzel steht im Reiseweg
(`WO > KITA > WO`), der Name im Ortsverzeichnis.

Ziele, die nur einmal vorkommen, gehören nicht hierher, sondern in den
Freitext des Formulars. Bei einem Umzug die Anschrift an **zwei** Stellen
ändern: in `Einstellungen` und in der Zeile `WO`. Hinweis: Sollten nach dieser Änderung frühere Abrechnungen erneut ausgedruckt werden, erfasst der Spaltenkopf sowie das Ortsverzeichnis die neue Adresse.

## Abrechnen

1. **Seite `Ausdruck`: Abrechnungszeitraum setzen.** Es zählt das Reisedatum.
   Eine mehrtägige Reise, die vor dem Zeitraum beginnt, gehörte in die vorige
   Abrechnung.
2. **Aktualisieren** drücken. Neu erfasste oder korrigierte Reisen erscheinen
   sonst nicht.
3. **Prüfen:**
   - **Ortsverzeichnis:** Sind die Anschriften der Einzelziele (`E26-07` …)
     vollständig? Sonst den Freitext in der Reisekorrektur ergänzen.
   - **S1, Spalte „Reiseweg“:** zeigt die Nummer und die Zeiten fürs Tagegeld:
     Ges. = Abwesenheit, DSt = Dienststätte, DO = Dienstort, Priv = privater
     Abzug, Rest = die Zeit, nach der sich das Tagegeld richtet.
     `Ges.: 0:00` heißt: Uhrzeit fehlt oder ist nicht lesbar.
   - **Kilometer:** Eine auffällig niedrige Zahl deutet auf einen Zahlendreher
     im Tachostand. `0` ist richtig, wenn die ganze Fahrt als privater Umweg
     erfasst ist.
   - **Beträge mit Minus** sind Eingabefehler und ziehen die Summe herunter.
4. **Drucken** im Widget „Reisekostenabrechnung“ (S1, S2, Vermerke,
   Ortsverzeichnis) und im Widget „Fahrtenbuch“.

## Fahrtenbuch einkleben und unterschreiben

- Bei **100 %** drucken, nicht „an Seitengröße anpassen“ — sonst stimmen die
  Spaltenbreiten nicht.
- Je Zeilenblock zwei Seiten: Spalten 1–6 und 7–15. Die Hinweiszeile über
  jeder Seite sagt, welche Kante abzuschneiden ist.
- Ausschneiden, ins Fahrtenbuch einkleben, von Hand unterschreiben.
- S1/S2 unterschreiben und einreichen.

## Prüfliste

Die Seite `Prüfliste` zeigt alles aus allen Blättern in einer Zeile je Reise,
darunter die Orte-Legende — für die Zeiterfassungsstelle. Die Seite lässt sich
allein freigeben; dann sieht die Stelle nur diese Liste.
