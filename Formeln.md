# Projektidee
Das Fahrtkostenformular soll Dienstreisen automatisiert erfassen und abrechnen: Google-Forms-Antworten laufen per IMPORTRANGE in die Tabelle ein und werden im Blatt BERECHNUNG so aufbereitet, dass die amtlichen Formularblätter S1/S2 nur noch fertige Werte anzeigen müssen.


## Gliederung dieses Dokuments

1. **Datenfluss** – wie eine Reise durch die Blätter läuft
2. **Erklärschema** – wie die Formel-Erklärungen aufgebaut sind
3. **Wiederkehrende Muster** – fünf Bausteine, die in fast jeder Formel stecken
4. **[Blätter](#blätter)** – je ein eigenes Dokument, in Datenfluss-Reihenfolge: Kurzzweck des Blatts, dann jede Zelle einzeln
5. **[Anhang](formeln/anhang.md)** – Tagegeld-Staffel, Wartung bei Formularänderung


## Datenfluss

```
Google-Formular
   │  (Formularantworten-Datei)
   ▼
Setup            URL + Freigabe + Stammdaten + Abrechnungszeitraum eintragen
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

Gearbeitet wird ausschließlich im Formular und im Blatt Setup. Alle übrigen
Blätter sind reine Formelergebnisse.


## Erklärschema

Jede Formel wird nach demselben Muster erklärt, maximal fünf Sätze:

- **Statement** – was die Formel technisch tut, Funktion für Funktion (Stichpunkte)
- **Ergebnis** – was am Ende in der Zelle steht, in Alltagssprache
- **Rechenweg** – wie der Wert zustande kommt, mit benannten Bezügen
- **Sonderfall** – Leerwert, Fehler, Grenzfall (nur wenn vorhanden)
- **Muster** – Verweis auf einen der fünf Bausteine unten statt Wiederholung


## Wiederkehrende Muster

### Muster A – Auto-Spalte

```
ARRAYFORMULA(IF(B3:B="";"";  … ))
```

**Statement:**
- `ARRAYFORMULA(…)` – wendet den Ausdruck auf den ganzen Spaltenbereich an
- `IF(B3:B="";"";…)` – Zeilen ohne Zeitstempel liefern Leerstring

Eine Formel oben in der Spalte füllt automatisch alle Zeilen darunter. Reisen
ohne Zeitstempel (Spalte B leer) bleiben leer statt Null oder Fehler. Neue
Formularantworten lassen die Spalte von selbst mitwachsen.

### Muster B – Zeitraum-Auszug

```
IFERROR(FILTER( Quelle ; Datum<>"" ; Datum>=Setup!C8 ; Datum<=Setup!C10 );"")
```

**Statement:**
- `FILTER(Quelle; Bed1; Bed2; Bed3)` – behält nur Zeilen, die alle Bedingungen erfüllen, und rückt sie lückenlos auf
- `IFERROR(…;"")` – FILTER ohne Treffer oder mit Längenfehler → leere Zelle

Übernimmt aus BERECHNUNG nur die Reisen im Abrechnungszeitraum (Setup C8–C10)
und listet sie lückenlos untereinander. Bei einem Fehler bleibt die Zelle leer.

### Muster C – Text zu Zahl

```
IFERROR(IF(ISNUMBER( Quelle ); Quelle ; VALUE(REGEXREPLACE( Quelle ;"[^0-9,.-]";"")));0)
```

**Statement:**
- `ISNUMBER( Quelle )` – prüft je Zeile, ob der Wert schon eine Zahl ist
- Zahl-Zweig – Wert direkt übernehmen, ohne Regex
- `REGEXREPLACE(…;"[^0-9,.-]";"")` – im Text-Zweig alles außer Ziffern, Komma, Punkt, Minus löschen
- `VALUE(…)` – Text → Zahl, im Dezimaltrennzeichen der Tabelle (Komma)
- `IFERROR(…;0)` – leeres oder unlesbares Feld → 0

Dasselbe Formularfeld kommt mal als Zahl (`10`), mal als Text (`„100,00 €"`) an —
je nachdem, was die Antworten-Tabelle automatisch erkennt. Die `ISNUMBER`-Weiche
bedient beide Fälle.

**Zu beachten:**
- `REGEXREPLACE` wandelt Zahlen nicht automatisch in Text. Die `ISNUMBER`-Weiche
  ist deshalb Pflicht, sonst wirft eine numerische Eingabe `#VALUE!`.
- `VALUE` liest im Gebietsschema der Tabelle (deutsch), erwartet also das
  Dezimal**komma**: `VALUE("100,00")` funktioniert, `VALUE("100.00")` nicht.

### Muster D – Zeilengrenzen

Neue Google-Sheets-Blätter haben 1000 Zeilen. Formeln, die zwei Blätter
zeilenweise verbinden, nutzen feste Grenzen (`BERECHNUNG!C3:C999`,
`IMPORTDATA!AA2:AA998` – je 997 Zeilen), damit beide Seiten gleich lang sind.
Offene Bereiche (`A3:A`) nur mit offenen kombinieren, begrenzte nur mit
begrenzten – sonst liefert FILTER einen Fehler und die Spalte bleibt still leer.

### Muster E – Ersatzwert 0 statt Leerstring

Zellen, mit denen andere Formeln rechnen (Subtraktion, Multiplikation), liefern
bei leerer Quelle `0` statt `""`. Ein Leerstring würde dort `#VALUE!` auslösen —
über FILTER leert dieser Fehler nicht nur die eine Zeile, sondern die ganze
Spalte in S1, Druck-Fahrtenbuch und GoogleMapsExport. Fehleingaben bleiben über
eine eigene Plausibilitätsprüfung (bedingte Formatierung) sichtbar, statt die
Zeile unbemerkt aus der Abrechnung zu nehmen.


## Blätter

Je ein eigenes Dokument, in Datenfluss-Reihenfolge:

1. [Setup](formeln/setup.md)
2. [IMPORTDATA](formeln/importdata.md)
3. [BERECHNUNG](formeln/berechnung.md)
4. [S1 – Reisekostenabrechnung](formeln/s1.md)
5. [S2 – Reisekostenabrechnung](formeln/s2.md)
6. [Vermerke](formeln/vermerke.md)
7. [Druck-Fahrtenbuch](formeln/druck-fahrtenbuch.md)
8. [Orte](formeln/orte.md)
9. [GoogleMapsExport](formeln/googlemapsexport.md)
10. [Anhang](formeln/anhang.md)
