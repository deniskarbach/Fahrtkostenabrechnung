# Projektidee
Das Fahrtkostenformular soll Dienstreisen automatisiert erfassen und abrechnen: Google-Forms-Antworten laufen per IMPORTRANGE in die Tabelle ein und werden im Blatt BERECHNUNG so aufbereitet, dass die amtlichen Formularblätter S1/S2 nur noch fertige Werte anzeigen müssen.


## Gliederung dieses Dokuments

1. **Datenfluss** – wie eine Reise durch die Blätter läuft
2. **Erklärschema** – wie die Formel-Erklärungen aufgebaut sind
3. **Wiederkehrende Muster** – vier Bausteine, die in fast jeder Formel stecken
4. **Blätter in Datenfluss-Reihenfolge** – Setup · IMPORTDATA · BERECHNUNG · S1 · S2 · Vermerke · Druck-Fahrtenbuch · Orte · GoogleMapsExport, je Blatt ein Kurzzweck und dann jede Zelle einzeln
5. **Anhang** – Spaltenbelegung A:AC, Tagegeld-Staffel, Wartung bei Formularänderung


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
- **Muster** – Verweis auf einen der vier Bausteine unten statt Wiederholung


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
VALUE(REGEXREPLACE(REGEXREPLACE( Text ;"[^0-9,.-]";"");",";"."))
```

**Statement:**
- innere `REGEXREPLACE(…;"[^0-9,.-]";"")` – löscht alles außer Ziffern, Komma, Punkt, Minus
- äußere `REGEXREPLACE(…;",";".")` – Dezimalkomma → Punkt
- `VALUE(…)` – Text → Zahl

Formularfelder liefern Text wie „12,50 €". Der Ausdruck entfernt alles außer
Ziffern, Komma, Punkt und Minus und macht aus dem Komma einen Punkt, sodass
eine echte Zahl übrig bleibt.

### Muster D – Zeilengrenzen

Neue Google-Sheets-Blätter haben 1000 Zeilen. Formeln, die zwei Blätter
zeilenweise verbinden, nutzen feste Grenzen (`BERECHNUNG!C3:C999`,
`IMPORTDATA!AA2:AA998` – je 997 Zeilen), damit beide Seiten gleich lang sind.
Offene Bereiche (`A3:A`) nur mit offenen kombinieren, begrenzte nur mit
begrenzten – sonst liefert FILTER einen Fehler und die Spalte bleibt still leer.


## Blatt:Setup

Import Formularantworten Google Sheets Datei [Formularantworten-Datei]

```
=IF(B80="Ja"; IMPORTRANGE(B74; "Formularantworten 1!A1"); "🔒 Bitte legitimieren")
```

**Statement:**
- `IF(B80="Ja"; …; …)` – Freigabe-Schalter, prüft eine Ja/Nein-Zelle
- `IMPORTRANGE(B74; "Formularantworten 1!A1")` – lädt einen Bereich aus einer fremden Tabellendatei über deren URL

**Ergebnis:** Holt die Formulardaten erst, wenn die Freigabe (B80) auf „Ja" steht.
**Rechenweg:** Ohne Freigabe erscheint ein Schloss-Hinweis; mit Freigabe wird die
verknüpfte Tabelle über ihre in B74 hinterlegte URL geladen.
**Sonderfall:** Der erste Import muss einmalig in Google Sheets bestätigt werden.

Bedingte Formatierung - Datumsangabe

```
=TAGTRUNC(C5)<TAGTRUNC(C3)
```

**Statement:**
- `TAGTRUNC(…)` – schneidet die Uhrzeit ab, übrig bleibt der reine Tag
- `<` – liefert WAHR/FALSCH; WAHR löst die Formatierung aus

**Ergebnis:** Färbt das Feld, wenn das Enddatum vor dem Startdatum liegt.
**Rechenweg:** Beide Datumswerte werden auf ganze Tage gekürzt und verglichen.



## Blatt:IMPORTDATA

#### Zelle A1:

```
=IF(Setup!B74=""; "⚠️ Keine URL hinterlegt"; IFERROR(IMPORTRANGE(Setup!B74; "Formularantworten 1!A1:ZZ"); "❌ Fehler beim Import (Zugriff erlaubt?)"))
```

**Statement:**
- `IF(Setup!B74=""; …; …)` – prüft zuerst, ob überhaupt eine URL hinterlegt ist
- `IMPORTRANGE(…; "Formularantworten 1!A1:ZZ")` – holt den gesamten Antwortbereich
- `IFERROR(…; "❌ …")` – Zugriffsfehler als Klartext statt #REF!

**Ergebnis:** Die kompletten Formularantworten (Spalten A–ZZ) oder eine Klartext-Fehlermeldung.
**Rechenweg:** Ist in Setup!B74 keine URL hinterlegt, kommt ein Hinweis; klappt der
Zugriff nicht, ein Fehlertext; sonst die Daten.
**Sonderfall:** Jede neue Formularfrage verschiebt alle folgenden Spalten (siehe unten).


#### Spaltenbelegung Formularantworten (finale Formularversion, A:AC)
A Zeitstempel · B E-Mail · C Dienstreisedatum · D Ende Dienstreisedatum (opt.) ·
E Reisebeginn · F km Reisebeginn · G Reiseende · H km Reiseende · I Umweg privat (km) ·
J Ort Reisebeginn · K Ort Reiseende · L–P Ort 1–5 · Q Tagegeld beantragen? ·
R Dienststätte-Minuten · S Dienstort-Minuten · T Privater Zeitabzug (Minuten, opt.) ·
U Weitere Fahrt-/Nebenkosten? · V ÖPNV · W Mitnahme Personen · X Übernachtung ·
Y Nebenkosten · Z Verpflegung · AA Sonstige Informationen · AB Screenshot · AC Weitere Belege

Jede neue Formularfrage verschiebt alle folgenden Spalten — danach IMPORTDATA-Bezüge in
BERECHNUNG, Vermerke, Druck-Fahrtenbuch und GoogleMapsExport prüfen.



## Blatt:BERECHNUNG

Kernblatt: eine Zeile je Reise, alle Rechengrößen fertig aufbereitet.

#### A3 - Laufende Nummer:

```
=MAP(B3:B; C3:C; LAMBDA(zs; dat;
      IF(dat="";"";
        COUNTIFS(C:C;">="&DATE(YEAR(dat);1;1); C:C;"<"&dat)
      + COUNTIFS(C:C;"="&dat; B:B;"<="&zs))))
```

**Statement:**
- `MAP(B3:B; C3:C; LAMBDA(zs; dat; …))` – läuft paarweise über Zeitstempel- und Datumsspalte, je Zeile ein Ergebnis
- `IF(dat="";"";…)` – Zeile ohne Datum bleibt leer
- `COUNTIFS(C:C;">="&DATE(YEAR(dat);1;1); C:C;"<"&dat)` – zählt Reisen ab 1.1. des Jahres bis vor diesem Datum
- `+ COUNTIFS(C:C;"="&dat; B:B;"<="&zs)` – plus Reisen am selben Tag mit früherem Zeitstempel
- `&` in den Kriterien – setzt den Vergleichstext (z. B. `">=45292"`) zusammen

**Ergebnis:** Fortlaufende Nummer der Reise innerhalb ihres Kalenderjahres.
**Rechenweg:** Zählt alle Reisen desselben Jahres mit früherem Datum; bei gleichem
Datum entscheidet der Formular-Zeitstempel (Spalte B) über die Reihenfolge.
**Sonderfall:** Zeilen ohne Datum bekommen keine Nummer.


#### B3 - Zeitstempel:

```
=ARRAYFORMULA(IMPORTDATA!A2:A)
```

**Statement:**
- `ARRAYFORMULA(IMPORTDATA!A2:A)` – reicht die komplette Quellspalte als Array durch, ohne Umformung

**Ergebnis:** Zeitpunkt der Formularabgabe, 1:1 aus IMPORTDATA übernommen.
**Rechenweg:** Direkte Übernahme der Spalte A.
**Sonderfall:** Dient in allen anderen Spalten als „gibt es diese Reise?"-Marke für Muster A.


#### C3 - Reisedatum Start:

```
=ARRAYFORMULA(IFERROR(TO_DATE(DATEVALUE(IMPORTDATA!C2:C))))
```

**Statement:**
- `DATEVALUE(…)` – wandelt Datumstext in eine Datums-Serienzahl
- `TO_DATE(…)` – stempelt die Zahl als Datumstyp, damit Sheets sie als Datum formatiert
- `IFERROR(…)` ohne zweites Argument – bei Fehler bleibt die Zelle leer

**Ergebnis:** Das Startdatum der Reise als echtes Datum.
**Rechenweg:** Der Datumstext aus dem Formular wird in einen Datumswert umgewandelt.
**Sonderfall:** Unlesbare Werte bleiben leer.


#### D3 - Reisebeginn Uhrzeit:

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!E2:E;"")))
```

**Statement:**
- `IF(B3:B="";"";…)` – Leerzeilenschutz (Muster A)
- `IFERROR(IMPORTDATA!E2:E;"")` – Wert durchreichen, Fehler → leer

**Ergebnis:** Uhrzeit des Reisebeginns aus dem Formular.
**Muster:** Auto-Spalte (A).


#### E3 - Reisedatum Ende:

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(TO_DATE(DATEVALUE(IMPORTDATA!D2:D));C3:C)))
```

**Statement:**
- `DATEVALUE(IMPORTDATA!D2:D)` – optionales Enddatum in Datumszahl
- `TO_DATE(…)` – stempelt die Zahl als Datumstyp (wie C3)
- `IFERROR(…;C3:C)` – schlägt das fehl (Feld leer), wird das Startdatum als Ersatzwert genommen

**Ergebnis:** Das Enddatum der Reise.
**Rechenweg:** Aus dem optionalen Formularfeld; ist es leer, gilt das Startdatum (eintägige Reise).
**Muster:** Auto-Spalte (A).

**Anzeige (C und E):** `DATEVALUE` liefert eine Datums-Seriennummer ohne Datumstyp.
Wächst die ARRAYFORMULA um eine neue Antwort, setzt Sheets das Zahlenformat der
gesamten Spalte auf den Typ des Formelergebnisses zurück — ein von Hand gesetztes
Format `TT.MM.JJJJ` ist danach weg und es steht wieder 46073 in der Zelle.
`TO_DATE` macht aus der Zahl einen echten Datumswert; das zurückgesetzte Format ist
dann ein Datumsformat, der Wert bleibt rechenbar (Filter auf Setup!C8/C10 gehen weiter).
**Wenn es trotzdem verschwindet:** Skript (Erweiterungen › Apps Script) mit
Trigger „Bei Änderung" statt Handformatierung:

```
function fixDatumsformat() {
  const b = SpreadsheetApp.getActive().getSheetByName("BERECHNUNG");
  ["C3:C1000","E3:E1000"].forEach(r => b.getRange(r).setNumberFormat("dd.mm.yyyy"));
}
```

**Statement:**
- `getSheetByName("BERECHNUNG")` – holt das Blatt über seinen Namen
- `["C3:C1000","E3:E1000"].forEach(r => …)` – beide Bereiche nacheinander abarbeiten
- `setNumberFormat("dd.mm.yyyy")` – Zahlenformat neu setzen, überschreibt den Reset


#### F3 - Reiseende Uhrzeit:

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!G2:G;"")))
```

**Statement:**
- wie D3, Quelle ist Spalte G statt E

**Ergebnis:** Uhrzeit des Reiseendes aus dem Formular.
**Muster:** Auto-Spalte (A).


#### G3 - Kilometer Beginn:

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(IMPORTDATA!F2:F);"")))
```

**Statement:**
- `VALUE(IMPORTDATA!F2:F)` – Formulartext in Zahl wandeln
- `IFERROR(…;"")` – nicht-numerische Eingabe → leer statt #VALUE!

**Ergebnis:** Tachostand zu Beginn der Reise als Zahl.
**Rechenweg:** Formularwert in eine Zahl gewandelt.
**Muster:** Auto-Spalte (A); nicht-numerische Eingaben bleiben leer.


#### H3 - Kilometer Ende:

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(IMPORTDATA!H2:H);"")))
```

**Statement:**
- wie G3, Quelle ist Spalte H statt F

**Ergebnis:** Tachostand am Ende der Reise als Zahl.
**Rechenweg:** Formularwert in eine Zahl gewandelt.
**Muster:** Auto-Spalte (A); nicht-numerische Eingaben bleiben leer.


#### I3 - Umweg privat (km):

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IF(IMPORTDATA!I2:I="";0;VALUE(IMPORTDATA!I2:I));0)))
```

**Statement:**
- `IF(IMPORTDATA!I2:I="";0;VALUE(…))` – leeres Feld ergibt 0, sonst die Zahl
- `IFERROR(…;0)` – auch fehlerhafte Eingaben werden zu 0

**Ergebnis:** Privat gefahrene Zusatzkilometer.
**Rechenweg:** Aus dem optionalen Formularfeld; keine Angabe zählt als 0.
**Muster:** Auto-Spalte (A).


#### J3 - Wegstrecke Gesamt (km):

```
=ARRAYFORMULA(IF(B3:B="";"";H3:H-G3:G))
```

**Statement:**
- `H3:H-G3:G` – Subtraktion zweier Spalten, zeilenweise durch ARRAYFORMULA

**Ergebnis:** Alle auf der Reise gefahrenen Kilometer.
**Rechenweg:** Tachostand Ende minus Tachostand Beginn.
**Muster:** Auto-Spalte (A).


#### K3 - Wegstrecke bereinigt (km):

```
=ARRAYFORMULA(IF(B3:B="";"";H3:H-G3:G-I3:I))
```

**Statement:**
- `H3:H-G3:G-I3:I` – wie J3, zusätzlich minus Spalte I (privater Umweg)

**Ergebnis:** Die rein dienstlich gefahrenen Kilometer — die abrechnungsrelevante Größe.
**Rechenweg:** Gesamtstrecke minus privater Umweg (Ende − Beginn − Umweg).
**Muster:** Auto-Spalte (A).


#### L3 - Reiseweg:
Reihenfolge: Ort Reisebeginn (J), Ort 1–5 (L:P), Ort Reiseende (K).

```
=BYROW(CHOOSECOLS(IMPORTDATA!J2:P; 1; 3; 4; 5; 6; 7; 2); LAMBDA(zeile; IF(INDEX(zeile; 1)=""; ""; SUBSTITUTE(SUBSTITUTE(TEXTJOIN(" > "; TRUE; zeile); "Wohnort"; "WO"); "Kreisverwaltung"; "KV"))))
```

**Statement:**
- `CHOOSECOLS(IMPORTDATA!J2:P; 1;3;4;5;6;7;2)` – sortiert die Spalten in Reisereihenfolge um (J, L–P, dann K)
- `BYROW(…; LAMBDA(zeile; …))` – verarbeitet jede Zeile einzeln zu einem Textwert
- `INDEX(zeile;1)=""` – ohne Startort keine Ausgabe
- `TEXTJOIN(" > "; TRUE; zeile)` – Orte verketten, `TRUE` überspringt leere Zellen
- `SUBSTITUTE(SUBSTITUTE(…))` – „Wohnort" → „WO", „Kreisverwaltung" → „KV"

**Ergebnis:** Der Reiseweg als Text, z. B. `WO > KV > Musterstadt > WO`.
**Rechenweg:** Ort Reisebeginn, Orte 1–5 und Ort Reiseende werden in dieser
Reihenfolge mit „ > " verbunden.
**Sonderfall:** „Wohnort"/„Kreisverwaltung" werden zu „WO"/„KV" abgekürzt; ohne Startort bleibt die Zelle leer.


#### M3:T3 - Tagegeld-Gruppe
M:P = Staffel-Kreuze, Q:T = die vier Zeitgrößen, aus denen sie sich ergeben.
Maßgeblich sind nicht die rohen Zeiten, sondern:
- bereinigte Abwesenheit `S-T` für die 8:01-Schwelle (Anspruch dem Grunde nach)
- Rest-Zeit `S-T-Q-R` für die Staffelstufe (Herabstufung)

S bleibt bewusst die rohe Spanne Reiseende−Reisebeginn — sie ist der Nachweis
gegenüber dem Fahrtenbuch und darf nicht stillschweigend gekürzt werden. Der
private Abzug steht als eigene, prüfbare Größe daneben.


#### M3 - Tagegeld Anteilig ≤8h:

```
=ARRAYFORMULA(IF((IMPORTDATA!Q2:Q="Ja")*ISNUMBER(S3:S)*(ROUND((S3:S-T3:T)*60)>=481)*(ROUND((S3:S-T3:T-Q3:Q-R3:R)*60)<481);"X";""))
```

**Statement:**
- `(…)*(…)*(…)` – Multiplikation von WAHR/FALSCH (1/0) ersetzt UND; nur wenn alle 1 sind, ist das Produkt 1
- `IMPORTDATA!Q2:Q="Ja"` – Tagegeld beantragt?
- `ISNUMBER(S3:S)` – gültige Zeitspanne vorhanden?
- `ROUND((S3:S-T3:T)*60)>=481` – bereinigte Abwesenheit in ganzen Minuten, Schwelle 8:01 h
- `ROUND((S3:S-T3:T-Q3:Q-R3:R)*60)<481` – Rest-Zeit bleibt unter der Schwelle
- `IF(…;"X";"")` – Kreuz oder leer

**Ergebnis:** „X", wenn für die Reise die kleinste Tagegeldstufe gilt.
**Rechenweg:** Tagegeld wurde beantragt, die bereinigte Abwesenheit erreicht
mindestens 8:01 h (481 Minuten), aber die Rest-Zeit bleibt darunter.
**Muster:** Auto-Spalte (A).


#### N3 - Tagegeld >8h:

```
=ARRAYFORMULA(IF((IMPORTDATA!Q2:Q="Ja")*ISNUMBER(S3:S)*(ROUND((S3:S-T3:T)*60)>=481)*(ROUND((S3:S-T3:T-Q3:Q-R3:R)*60)>=481)*(ROUND((S3:S-T3:T-Q3:Q-R3:R)*60)<840);"X";""))
```

**Statement:**
- Aufbau wie M3, nur andere Rest-Zeit-Grenzen: `>=481` und `<840` (8:01 h bis unter 14 h)

**Ergebnis:** „X" für die mittlere Stufe.
**Rechenweg:** Wie M3, aber die Rest-Zeit liegt zwischen 8:01 h und 14 h (481–839 Minuten).
**Muster:** Auto-Spalte (A).

#### O3 - Tagegeld ≥14h:

```
=ARRAYFORMULA(IF((IMPORTDATA!Q2:Q="Ja")*ISNUMBER(S3:S)*(ROUND((S3:S-T3:T)*60)>=481)*(ROUND((S3:S-T3:T-Q3:Q-R3:R)*60)>=840)*(ROUND((S3:S-T3:T-Q3:Q-R3:R)*60)<1440);"X";""))
```

**Statement:**
- Aufbau wie M3, Rest-Zeit-Grenzen `>=840` und `<1440` (14 h bis unter 24 h)

**Ergebnis:** „X" für die große Stufe.
**Rechenweg:** Wie M3, aber die Rest-Zeit liegt zwischen 14 h und 24 h (840–1439 Minuten).
**Muster:** Auto-Spalte (A).


#### P3 - Tagegeld 24h:

```
=ARRAYFORMULA(IF((IMPORTDATA!Q2:Q="Ja")*ISNUMBER(S3:S)*(ROUND((S3:S-T3:T)*60)>=481)*(ROUND((S3:S-T3:T-Q3:Q-R3:R)*60)>=1440);"X";""))
```

**Statement:**
- Aufbau wie M3, nur eine Rest-Zeit-Grenze und nach oben offen: `>=1440` (ab 24 h)

**Ergebnis:** „X" für einen vollen Abwesenheitstag (Zwischentag einer mehrtägigen Reise).
**Rechenweg:** Wie M3, aber die Rest-Zeit erreicht 24 h (1440 Minuten).
**Muster:** Auto-Spalte (A).


#### Q3 - Dauer Aufenthalt Dienststätte (h mit dez):

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!R2:R/60;"")))
```

**Statement:**
- `IMPORTDATA!R2:R/60` – Minuten durch 60 = Dezimalstunden
- `IFERROR(…;"")` – keine oder unlesbare Angabe → leer

**Ergebnis:** Zeit an der eigenen Dienststätte, in Dezimalstunden.
**Rechenweg:** Formularangabe in Minuten geteilt durch 60.
**Muster:** Auto-Spalte (A).


#### R3 - Aufenthalt Dienstort (h mit dez):

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!S2:S/60;"")))
```

**Statement:**
- wie Q3, Quelle ist Spalte S statt R

**Ergebnis:** Zeit am auswärtigen Dienstort, in Dezimalstunden.
**Rechenweg:** Formularangabe in Minuten geteilt durch 60.
**Muster:** Auto-Spalte (A).


#### S3 - Abwesenheit Dienstort / Dienststätte (h mit dez):

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(((E3:E+F3:F)-(C3:C+D3:D))*24;"")))
```

**Statement:**
- `E3:E+F3:F` bzw. `C3:C+D3:D` – Datum und Uhrzeit zu einem Zeitpunkt addieren (beides Serienzahlen)
- `(…)-(…)` – Differenz in Tagen
- `*24` – Tage in Stunden umrechnen

**Ergebnis:** Gesamte Reisedauer von Beginn bis Ende, in Dezimalstunden.
**Rechenweg:** (Enddatum + Enduhrzeit) minus (Startdatum + Startuhrzeit), mal 24 in Stunden umgerechnet.
**Sonderfall:** Bleibt bewusst ungekürzt — der private Abzug wird erst in T separat geführt.
**Muster:** Auto-Spalte (A).


#### T3 - Privater Zeitabzug (h mit dez):
Optionales Formularfeld — leer bedeutet "kein Abzug", nicht "unbekannt", daher
0 statt "": M3:P3 rechnen mit T und würden bei "" #VALUE! liefern.

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!T2:T/60;0)))
```

**Statement:**
- `IMPORTDATA!T2:T/60` – Minuten in Dezimalstunden
- `IFERROR(…;0)` – Ersatzwert bewusst 0 statt "", damit M3:P3 weiterrechnen können

**Ergebnis:** Privat veranlasste Zeit, die von der Abwesenheit abzuziehen ist, in Dezimalstunden.
**Rechenweg:** Optionales Formularfeld in Minuten geteilt durch 60.
**Sonderfall:** Leer zählt als 0, damit die Tagegeld-Formeln nicht #VALUE! liefern.
**Muster:** Auto-Spalte (A).


#### Plausibilitätsprüfung (bedingte Formatierung auf T3:T)
Privater Abzug darf die Rest-Zeit nicht negativ machen:

```
=UND($T3<>"";$S3-$T3-$Q3-$R3<0)
```

**Statement:**
- `UND(…;…)` – beide Bedingungen müssen zutreffen
- `$T3<>""` – nur Zeilen mit eingetragenem Abzug prüfen
- `$S3-$T3-$Q3-$R3<0` – Rest-Zeit ist negativ
- `$` nur vor der Spalte – die Regel wandert zeilenweise über den Bereich

**Ergebnis:** Markiert die Zelle, wenn der private Abzug die Rest-Zeit ins Negative zieht.
**Rechenweg:** Prüft, ob T ausgefüllt ist und S − T − Q − R kleiner als 0 wird.
**Sonderfall:** Trifft das zu, stimmt eine der Zeitangaben nicht.


#### U3 - Verpflegung:

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!Z2:Z;"")))
```

**Statement:**
- `IFERROR(IMPORTDATA!Z2:Z;"")` – Text unverändert durchreichen, Fehler → leer

**Ergebnis:** Angabe zu unentgeltlicher Verpflegung aus dem Formular.
**Muster:** Auto-Spalte (A).


#### V3 - ÖPNV:

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(REGEXREPLACE(REGEXREPLACE(IMPORTDATA!V2:V;"[^0-9,.-]";"");",";"."));"")))
```

**Statement:**
- `REGEXREPLACE(…;"[^0-9,.-]";"")` – Währungszeichen und Text entfernen
- `REGEXREPLACE(…;",";".")` – Komma zu Punkt
- `VALUE(…)` – Ergebnis als Zahl

**Ergebnis:** ÖPNV-Kosten als Zahl.
**Muster:** Auto-Spalte (A) + Text zu Zahl (C).


#### W3 - Mitnahme Personenzahl:

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(IMPORTDATA!W2:W);"")))
```

**Statement:**
- `VALUE(IMPORTDATA!W2:W)` – ohne Regex, da hier eine reine Zahl erwartet wird

**Ergebnis:** Anzahl mitgenommener Personen.
**Rechenweg:** Formularwert in eine Zahl gewandelt.
**Muster:** Auto-Spalte (A).


#### X3 - Übernachtung:

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(REGEXREPLACE(REGEXREPLACE(IMPORTDATA!X2:X;"[^0-9,.-]";"");",";"."));"")))
```

**Statement:**
- wie V3, Quelle ist Spalte X

**Ergebnis:** Übernachtungskosten als Zahl.
**Muster:** Auto-Spalte (A) + Text zu Zahl (C).


#### Y3 - Nebenkosten:

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(REGEXREPLACE(REGEXREPLACE(IMPORTDATA!Y2:Y;"[^0-9,.-]";"");",";"."));"")))
```

**Statement:**
- wie V3, Quelle ist Spalte Y

**Ergebnis:** Sonstige Nebenkosten als Zahl.
**Muster:** Auto-Spalte (A) + Text zu Zahl (C).



## Blatt:ReisekostenabrechnungS1

Amtliches Formular, Seite 1. Kopf (A3/E3/J3) aus Setup, ab Zeile 7 je Spalte ein
Zeitraum-Auszug aus BERECHNUNG (Muster B).

#### A3 - Name & Organisationseinheit:

```
=TEXTJOIN(" "; TRUE; Setup!C17; Setup!C19) & ", " & TEXTJOIN(" "; TRUE; Setup!C61) & "-" & TEXTJOIN(""; TRUE; Setup!C63)
```

**Statement:**
- `TEXTJOIN(" "; TRUE; …)` – verbindet Felder mit Leerzeichen; `TRUE` lässt leere Felder weg, sodass kein doppeltes Trennzeichen entsteht
- `& ", " &` und `& "-" &` – feste Trennzeichen zwischen den Gruppen

**Ergebnis:** „Vorname Name, Amt-Kürzel" für den Formularkopf.
**Rechenweg:** Setzt die genannten Setup-Felder mit Leerzeichen, Komma und Bindestrich zusammen.


#### E3 - Anschrift Antragssteller/in:

```
=TEXTJOIN(" "; TRUE; Setup!C26; Setup!C28) & "," & TEXTJOIN(" "; TRUE; Setup!C30; Setup!C32)
```

**Statement:**
- `TEXTJOIN(" "; TRUE; …)` – erst Straße + Hausnummer, dann PLZ + Ort
- `& "," &` – trennt Straße von der Ortsangabe

**Ergebnis:** „Straße Nr., PLZ Ort" der antragstellenden Person.
**Rechenweg:** Vier Setup-Felder zu einer Adresszeile verbunden.


#### J3 - Dienstort:

```
=TEXTJOIN(" "; TRUE; Setup!C48; Setup!C50) & ", " & TEXTJOIN(" "; TRUE; Setup!C52; Setup!C54)
```

**Statement:**
- wie E3, nur mit den Dienstort-Feldern

**Ergebnis:** Anschrift des Dienstorts als eine Zeile.
**Rechenweg:** Vier Setup-Felder zu einer Adresszeile verbunden.


#### A7 - Reisedatum:

```
=ARRAYFORMULA(IFERROR(FILTER(
  LET(start; TEXT(BERECHNUNG!C3:C;"DD.MM.YYYY");
      ende; TEXT(BERECHNUNG!E3:E;"DD.MM.YYYY");
      IF(OR(BERECHNUNG!C3:C=BERECHNUNG!E3:E; BERECHNUNG!E3:E="");
         start; start&" - "&ende));
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `LET(start; …; ende; …; Ausdruck)` – benennt Zwischenergebnisse, damit sie nur einmal berechnet werden
- `TEXT(…;"DD.MM.YYYY")` – Datumszahl in lesbaren Text
- `OR(C=E; E="")` – eintägig oder Ende nicht gesetzt
- `start&" - "&ende` – sonst die Spanne als Text
- `FILTER(…)` + `IFERROR(…;"")` – Muster B

**Ergebnis:** Pro Reise ein Datum, bei mehrtägigen Reisen „Start - Ende".
**Rechenweg:** Start- und Enddatum werden formatiert; sind sie gleich (oder Ende leer),
erscheint nur ein Datum.
**Muster:** Zeitraum-Auszug (B).


#### B7 - Beginn:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!D3:D;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!D3:D; …)` – Quelle Spalte D, Bedingungen wie Muster B

**Ergebnis:** Uhrzeit des Reisebeginns je Reise.
**Muster:** Zeitraum-Auszug (B).


#### C7 - Ende:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!F3:F;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!F3:F; …)` – Quelle Spalte F, Bedingungen wie Muster B

**Ergebnis:** Uhrzeit des Reiseendes je Reise.
**Muster:** Zeitraum-Auszug (B).


#### D7 - Reiseweg:

```
=ARRAYFORMULA(IFERROR(FILTER(
  "Nr. "&BERECHNUNG!A3:A
  &"  –  ("&"Ges.: "&TEXT(BERECHNUNG!S3:S/24;"[H]:MM")
  &" | DSt: "&TEXT(BERECHNUNG!Q3:Q/24;"[H]:MM")
  &" | DO: "&TEXT(BERECHNUNG!R3:R/24;"[H]:MM")
  &IF(BERECHNUNG!T3:T>0;" | Priv: "&TEXT(BERECHNUNG!T3:T/24;"[H]:MM");"")
  &" | Rest: "&TEXT((BERECHNUNG!S3:S-BERECHNUNG!T3:T-BERECHNUNG!Q3:Q-BERECHNUNG!R3:R)/24;"[H]:MM")&")";
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `&` – setzt Fixtexte und Werte zu einer Zeile zusammen
- `/24` – rechnet Dezimalstunden in den Tagesbruch zurück, den TEXT als Zeit versteht
- `TEXT(…;"[H]:MM")` – Stunden:Minuten; die eckigen Klammern erlauben Werte über 24 h
- `IF(BERECHNUNG!T3:T>0; …;"")` – Priv-Teil nur bei tatsächlichem Abzug einblenden
- `FILTER(…)` + `IFERROR(…;"")` – Muster B

**Ergebnis:** Eine Textzeile je Reise mit Nummer und allen Zeiten, z. B.
`Nr. 3 – (Ges.: 9:15 | DSt: 1:00 | DO: 4:30 | Rest: 3:45)`.
**Rechenweg:** Die Stundenwerte aus BERECHNUNG S/Q/R/T werden als Stunden:Minuten formatiert.
**Sonderfall:** Der private Anteil (Priv) wird nur angezeigt, wenn er größer als 0 ist.
**Muster:** Zeitraum-Auszug (B).


#### E7 - Tagegeld Anteilig ≤8 Stunden:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!M3:M;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!M3:M; …)` – Quelle Spalte M, Bedingungen wie Muster B

**Ergebnis:** Übernimmt das Kreuz der kleinsten Staffelstufe aus BERECHNUNG M.
**Muster:** Zeitraum-Auszug (B).


#### F7 - Tagegeld mehr als 8 Stunden:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!N3:N;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!N3:N; …)` – Quelle Spalte N, Bedingungen wie Muster B

**Ergebnis:** Übernimmt das Kreuz der mittleren Staffelstufe aus BERECHNUNG N.
**Muster:** Zeitraum-Auszug (B).


#### G7 - Tagegeld mindestens 14 Stunden:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!O3:O;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!O3:O; …)` – Quelle Spalte O, Bedingungen wie Muster B

**Ergebnis:** Übernimmt das Kreuz der großen Staffelstufe aus BERECHNUNG O.
**Muster:** Zeitraum-Auszug (B).


#### H7 - Tagegeld 24 Stunden:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!P3:P;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!P3:P; …)` – Quelle Spalte P, Bedingungen wie Muster B

**Ergebnis:** Übernimmt das Kreuz für den vollen Abwesenheitstag aus BERECHNUNG P.
**Muster:** Zeitraum-Auszug (B).


#### I7 - Unentgeltliche Verpflegung:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!U3:U;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!U3:U; …)` – Quelle Spalte U, Bedingungen wie Muster B

**Ergebnis:** Verpflegungsangabe je Reise (BERECHNUNG U).
**Muster:** Zeitraum-Auszug (B).


#### J7 - Fahrtkosten ÖPNV:

```
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!V3:V>0;BERECHNUNG!V3:V;"");
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `IF(BERECHNUNG!V3:V>0; …;"")` – Nullwerte werden zu Leerstring, bevor gefiltert wird
- `FILTER(…)` – Bedingungen wie Muster B

**Ergebnis:** ÖPNV-Kosten je Reise (BERECHNUNG V), nur wenn größer als 0.
**Muster:** Zeitraum-Auszug (B).


#### K7 - Fahrtkosten Wegstrecke bereinigt:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!K3:K;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!K3:K; …)` – Quelle Spalte K, Bedingungen wie Muster B

**Ergebnis:** Die dienstlichen Kilometer je Reise (BERECHNUNG K).
**Muster:** Zeitraum-Auszug (B).


#### L7 - Mitnahme von Personen:

```
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!W3:W>0;BERECHNUNG!W3:W;"");
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `IF(BERECHNUNG!W3:W>0; …;"")` – Nullen ausblenden
- `FILTER(…)` – Bedingungen wie Muster B

**Ergebnis:** Personenzahl je Reise (BERECHNUNG W), nur wenn größer als 0.
**Muster:** Zeitraum-Auszug (B).


#### M7 - Übernachtungskosten:

```
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!X3:X>0;BERECHNUNG!X3:X;"");
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `IF(BERECHNUNG!X3:X>0; …;"")` – Nullen ausblenden
- `FILTER(…)` – Bedingungen wie Muster B

**Ergebnis:** Übernachtungskosten je Reise (BERECHNUNG X), nur wenn größer als 0.
**Muster:** Zeitraum-Auszug (B).


#### N7 - Nebenkosten:

```
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!Y3:Y>0;BERECHNUNG!Y3:Y;"");
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `IF(BERECHNUNG!Y3:Y>0; …;"")` – Nullen ausblenden
- `FILTER(…)` – Bedingungen wie Muster B

**Ergebnis:** Nebenkosten je Reise (BERECHNUNG Y), nur wenn größer als 0.
**Muster:** Zeitraum-Auszug (B).


## Blatt:ReisekostenabrechnungS2

Seite 2 des amtlichen Formulars, nur Bankverbindung.

#### C5 - IBAN:

```
=TEXTJOIN(" "; TRUE; Setup!C39)
```

**Statement:**
- `TEXTJOIN(" "; TRUE; Setup!C39)` – hier nur eine Zelle; TEXTJOIN dient als einheitliche Hülle und liefert bei Leerzelle "" statt 0

**Ergebnis:** IBAN aus Setup!C39.
**Rechenweg:** Direkter Durchgriff auf das Setup-Feld.


#### C7 - BIC:

```
=TEXTJOIN(" "; TRUE; Setup!C41)
```

**Statement:**
- wie C5, Quelle ist Setup!C41

**Ergebnis:** BIC aus Setup!C41.
**Rechenweg:** Direkter Durchgriff auf das Setup-Feld.


## Blatt:Vermerke

Daten beginnen ab Zeile 6, Spalten: A Lfd. Nr., B Label, C Vermerktext, F Datum.
Die Liste ist lückenlos: A/C/F filtern per FILTER auf Reisen mit ausgefülltem
"Sonstige Informationen" (IMPORTDATA Spalte AA), Reisen ohne Vermerk erzeugen
keine Leerzeile. In Vermerke wird direkt gearbeitet und gedruckt — kein
Blattfilter, kein separates Ansichtsblatt.
Kein Blattfilter ("Daten > Filter erstellen") auf diesem Blatt: Filter werten
ihre Bedingung nur bei manueller Interaktion neu aus, nicht wenn eine Zelle sich
durch Formel-Neuberechnung (IMPORTRANGE) ändert — neu eintreffende Vermerke
blieben sonst versteckt. Ein evtl. vorhandener Filter ist zu entfernen.
WICHTIG: Quellgrenze einheitlich 1000 (Google-Sheets-Standardgröße neuer
Blätter), damit die Zeile in BERECHNUNG und IMPORTDATA garantiert existiert:
BERECHNUNG 3:999 und IMPORTDATA 2:998 — je 997 Zeilen. Hat ein Blatt WENIGER als
1000 Zeilen, "Bezug nicht vorhanden"-Fehler: Zeilen über Rechtsklick ergänzen.
Vermerke selbst startet erst auf Zeile 6 und hat bis Zeile 1000 nur 995
Ausgabezeilen. Erst wenn tatsächlich mehr als 995 Reisen einen Vermerk tragen,
läuft das FILTER-Ergebnis über das Blattende und liefert #REF — dann Vermerke um
die fehlenden Zeilen verlängern. Braucht ihr mehr als 997 Reisen: die Grenzen
999/998 um denselben Betrag erhöhen, in Vermerke die 1000er-Bezüge mitziehen,
UND vorher in allen drei Blättern per Rechtsklick genügend Zeilen anfügen.
In Vermerke wird NICHT händisch geschrieben — jede Spalte ist Formelergebnis.
Detailbeschreibungen sowie alle Änderungen und Ergänzungen werden ausschließlich
an der Quelle gepflegt (Formularantwort, Feld "Sonstige Infos") und laufen von
dort über C mit ein. Nur so bleibt die gefilterte Liste zuordnungssicher: eine
händische Spalte hinge an der Zeilenposition und würde verrutschen, sobald ein
Vermerk nachgetragen wird.
Hinweis: IMPORTDATA-Spalte für "Sonstige Informationen" ist AA (finale Formularversion).

#### A6 - Laufende Nummer:

```
=ARRAYFORMULA(IFERROR(FILTER(
  MAP(BERECHNUNG!B3:B999; BERECHNUNG!C3:C999; IMPORTDATA!AA2:AA998; LAMBDA(zs; dat; txt;
      IF(OR(dat=""; txt=""); "";
        COUNTIFS(BERECHNUNG!$C$3:$C$999;">="&DATE(YEAR(dat);1;1); BERECHNUNG!$C$3:$C$999;"<"&dat; IMPORTDATA!$AA$2:$AA$998;"<>")
      + COUNTIFS(BERECHNUNG!$C$3:$C$999;"="&dat; BERECHNUNG!$B$3:$B$999;"<="&zs; IMPORTDATA!$AA$2:$AA$998;"<>"))));
  IMPORTDATA!AA2:AA998<>"";
  BERECHNUNG!C3:C999<>""
);""))
```

**Statement:**
- `MAP(…; …; …; LAMBDA(zs; dat; txt; …))` – läuft über drei Spalten gleichzeitig (Zeitstempel, Datum, Vermerktext)
- `OR(dat=""; txt="")` – ohne Datum oder ohne Vermerk keine Nummer
- `COUNTIFS(…; IMPORTDATA!$AA$2:$AA$998;"<>")` – das Zusatzkriterium `"<>"` (= nicht leer) zählt nur Reisen mit Vermerk mit
- `FILTER(…; AA<>""; C<>"")` – Ausgabe auf ebendiese Reisen beschränken

**Ergebnis:** Jahres-Nummer der Reise, aber nur Reisen mit Vermerk mitgezählt und angezeigt.
**Rechenweg:** Wie BERECHNUNG A3, jedoch zählen nur Reisen mit ausgefülltem „Sonstige
Informationen"; das Ergebnis wird auf ebendiese Reisen gefiltert.
**Sonderfall:** Reisen ohne Vermerk erzeugen keine Zeile.
**Muster:** Zeilengrenzen (D).


#### B6 - Label:
Beide Quellspalten prüfen, nicht nur A: bei leerem Datum liefert TEXT(;"YY") die
Serienzahl 0 = 30.12.1899 und damit stillschweigend "V99". Lieber kein Label als
ein falsches Jahr.
WICHTIG: A, B, C und F müssen auf derselben Zeile starten und dieselbe Endzeile
haben, sonst paart B eine Nummer mit dem Datum einer anderen Reise. Startzeile
hier durchgängig 6 — wird sie geändert, in allen vier Formeln gleichzeitig.

```
=ARRAYFORMULA(IF((A6:A1000="")+(F6:F1000="");"";"V"&TEXT(F6:F1000;"YY")&"-"&TEXT(A6:A1000;"00")))
```

**Statement:**
- `(A…="")+(F…="")` – Addition von WAHR/FALSCH ersetzt ODER; Summe größer 0 heißt „mindestens eins leer"
- `TEXT(F…;"YY")` – zweistelliges Jahr aus dem Datum
- `TEXT(A…;"00")` – Nummer mit führender Null
- `"V"&…&"-"&…` – zum Label zusammensetzen

**Ergebnis:** Kurzkennung wie `V25-03` (V + zweistelliges Jahr + laufende Nummer).
**Rechenweg:** Baut sich aus Datum (F) und Nummer (A) derselben Zeile zusammen.
**Sonderfall:** Fehlt Nummer oder Datum, bleibt das Label leer, um kein falsches Jahr zu erzeugen.


#### C6 - Vermerktext (aus Formular):

```
=ARRAYFORMULA(IFERROR(FILTER(
  IMPORTDATA!AA2:AA998;
  IMPORTDATA!AA2:AA998<>"";
  BERECHNUNG!C3:C999<>""
);""))
```

**Statement:**
- `FILTER(IMPORTDATA!AA2:AA998; AA<>""; C<>"")` – Quelle und erste Bedingung sind dieselbe Spalte: nur Zeilen mit Vermerktext
- zweite Bedingung `BERECHNUNG!C3:C999<>""` – nur echte Reisen (Datum vorhanden)

**Ergebnis:** Der Text aus dem Formularfeld „Sonstige Informationen".
**Rechenweg:** Filtert IMPORTDATA Spalte AA auf Reisen mit Text, in Reihenfolge des Reisedatums.
**Muster:** Zeitraum-Auszug (B, ohne Datumsgrenzen) + Zeilengrenzen (D).


#### D:E - Ergänzung: entfällt, keine Formel
Ergänzungen werden an der Quelle im Formularfeld "Sonstige Informationen"
gepflegt und erscheinen über C. Werden D/E gelöscht, rückt das Datum nach vorn —
dann in B6 beide F-Bezüge auf die neue Spalte ändern.


#### F6 - Datum:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!C3:C999;
  IMPORTDATA!AA2:AA998<>"";
  BERECHNUNG!C3:C999<>""
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!C3:C999; …)` – andere Quelle, aber exakt dieselben zwei Bedingungen wie C6 → gleiche Zeilen, gleiche Reihenfolge

**Ergebnis:** Reisedatum zu jedem Vermerk.
**Rechenweg:** Dieselbe Filterbedingung wie C6 — so bleiben Nummer, Label, Text und Datum zeilengleich.
**Muster:** Zeitraum-Auszug (B) + Zeilengrenzen (D).


#### E1 - Stand Datum:

```
=TEXTJOIN(" - ";TRUE;TEXT(Setup!$C$8;"DD.MM.YYYY");TEXT(Setup!$C$10;"DD.MM.YYYY"))
```

**Statement:**
- `TEXT(…;"DD.MM.YYYY")` – beide Datumswerte als Text formatieren
- `TEXTJOIN(" - ";TRUE;…)` – mit Bindestrich verbinden, leere Felder überspringen

**Ergebnis:** Abrechnungszeitraum als Text „von - bis".
**Rechenweg:** Die beiden Setup-Datumsfelder formatiert und mit „ - " verbunden.


## Blatt:Druck-Fahrtenbuch

Druckansicht des Fahrtenbuchs, Daten ab Zeile 4. Jede Spalte ein Zeitraum-Auszug
aus BERECHNUNG (Muster B).

#### A4 - Laufende Nummer:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!A3:A;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!A3:A; …)` – Quelle Spalte A, Bedingungen wie Muster B

**Ergebnis:** Jahres-Nummer der Reise (BERECHNUNG A).
**Muster:** Zeitraum-Auszug (B).


#### B4 - Monat:

```
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!C3:C="";"";MONTH(BERECHNUNG!C3:C));
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `MONTH(…)` – Monatszahl aus dem Datum
- `IF(C="";"";…)` – verhindert, dass leere Zellen als Monat 12 (1899) erscheinen
- `FILTER(…)` – Bedingungen wie Muster B

**Ergebnis:** Monat des Reisedatums als Zahl.
**Muster:** Zeitraum-Auszug (B).


#### C4 - Tag:

```
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!C3:C="";"";DAY(BERECHNUNG!C3:C));
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- wie B4, nur `DAY(…)` statt `MONTH(…)`

**Ergebnis:** Tag des Reisedatums als Zahl.
**Muster:** Zeitraum-Auszug (B).


#### D4 - Reisebeginn Uhrzeit:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!D3:D;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!D3:D; …)` – Quelle Spalte D, Bedingungen wie Muster B

**Ergebnis:** Uhrzeit des Reisebeginns (BERECHNUNG D).
**Muster:** Zeitraum-Auszug (B).


#### E4 - Reiseende Uhrzeit:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!F3:F;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!F3:F; …)` – Quelle Spalte F, Bedingungen wie Muster B

**Ergebnis:** Uhrzeit des Reiseendes (BERECHNUNG F).
**Muster:** Zeitraum-Auszug (B).


#### F4 - Reiseweg:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!L3:L;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!L3:L; …)` – Quelle Spalte L, Bedingungen wie Muster B

**Ergebnis:** Der Reiseweg-Text aus BERECHNUNG L.
**Muster:** Zeitraum-Auszug (B).


#### G4 - Kilometerstand Beginn:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!G3:G;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!G3:G; …)` – Quelle Spalte G, Bedingungen wie Muster B

**Ergebnis:** Tachostand zu Reisebeginn (BERECHNUNG G).
**Muster:** Zeitraum-Auszug (B).


#### H4 - Kilometerstand Ende:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!H3:H;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!H3:H; …)` – Quelle Spalte H, Bedingungen wie Muster B

**Ergebnis:** Tachostand zu Reiseende (BERECHNUNG H).
**Muster:** Zeitraum-Auszug (B).


#### I4 - Kilometer dienstlich:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!K3:K;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!K3:K; …)` – Quelle Spalte K, Bedingungen wie Muster B

**Ergebnis:** Bereinigte dienstliche Kilometer (BERECHNUNG K).
**Muster:** Zeitraum-Auszug (B).


#### J4 - Kilometer privat:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!I3:I;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!I3:I; …)` – Quelle Spalte I, Bedingungen wie Muster B

**Ergebnis:** Privater Umweg in Kilometern (BERECHNUNG I).
**Muster:** Zeitraum-Auszug (B).


#### K4:N4 - händische Eintragung (keine Formel)


#### O4 - Vermerk (Label):
Baut das Label selbst aus BERECHNUNG/IMPORTDATA (identische Logik wie
Vermerke!A4/B4), statt es aus Vermerke nachzuschlagen — Vermerke ist gefiltert
und daher nicht mehr zeilengleich zu BERECHNUNG, ein Bezug darauf wäre wieder
positionsabhängig. Reisen ohne Vermerk bleiben leer.

```
=ARRAYFORMULA(IFERROR(FILTER(
  MAP(BERECHNUNG!B3:B999; BERECHNUNG!C3:C999; IMPORTDATA!AA2:AA998; LAMBDA(zs; dat; txt;
      IF(OR(dat=""; txt=""); "";
        "V"&TEXT(dat;"YY")&"-"&TEXT(
          COUNTIFS(BERECHNUNG!$C$3:$C$999;">="&DATE(YEAR(dat);1;1); BERECHNUNG!$C$3:$C$999;"<"&dat; IMPORTDATA!$AA$2:$AA$998;"<>")
        + COUNTIFS(BERECHNUNG!$C$3:$C$999;"="&dat; BERECHNUNG!$B$3:$B$999;"<="&zs; IMPORTDATA!$AA$2:$AA$998;"<>")
        ;"00"))));
  BERECHNUNG!C3:C999<>"";
  BERECHNUNG!C3:C999>=Setup!$C$8;
  BERECHNUNG!C3:C999<=Setup!$C$10
);""))
```

**Statement:**
- `MAP(…; LAMBDA(zs; dat; txt; …))` und die beiden `COUNTIFS` – identisch zu Vermerke A6
- `"V"&TEXT(dat;"YY")&"-"&TEXT(…;"00")` – Label wird direkt hier gebildet, nicht aus Vermerke geholt
- `FILTER(…)` – hier mit den drei Zeitraum-Bedingungen (Muster B), nicht mit der Vermerk-Bedingung
- Reisen ohne Vermerk liefern "" und bleiben als Leerzelle in der Liste stehen

**Ergebnis:** Das Vermerk-Label `V25-03` je Reise, leer wenn kein Vermerk.
**Rechenweg:** Baut Label und Nummer mit derselben Logik wie Vermerke A6/B6 direkt aus
BERECHNUNG/IMPORTDATA, gefiltert auf den Abrechnungszeitraum.
**Sonderfall:** Ein Bezug auf das gefilterte Blatt Vermerke würde verrutschen — deshalb Neuberechnung.
**Muster:** Zeitraum-Auszug (B) + Zeilengrenzen (D).


## Blatt:Orte

Stammdaten der Reiseziele, Daten beginnen ab Zeile 6. Spalte A = Nr., Spalte B
= Kürzel (identisch zum Formularwert, außer WO/KV — siehe unten), Spalte C:D
= vollständiger Name der Einrichtung, Spalte E:M = vollständige Adresse
(Straße Hausnummer, PLZ Ort — je nach Zusammenführung über mehrere Zellen
verteilt oder in E zusammengefasst).

WO (Wohnort) und KV (Kreisverwaltung) stehen als normale Zeilen in diesem Blatt
— Kürzel "WO"/"KV" in Spalte B, Adresse wie bei jedem anderen Ort in E:M. Das
Formular liefert bei Start/Ziel den Langtext "Wohnort"/"Kreisverwaltung", bei
Wegpunkten das Kürzel "WO"/"KV"; GoogleMapsExport!G3 gleicht das per SUBSTITUTE
an, wie bereits BERECHNUNG!L3, und schlägt beides hier nach.

Setup C26/C28/C30/C32 (Wohnort) bzw. C48/C50/C52/C54 (Kreisverwaltung) sind eine
ZWEITE, unabhängige Pflegestelle derselben Adressen — sie speisen
ReisekostenabrechnungS1 E3/J3. GoogleMapsExport!G3 nutzt sie nicht mehr.
Adressänderungen müssen daher an beiden Stellen gepflegt werden.

Keine Formeln — reine Nachschlagetabelle. GoogleMapsExport!G3 sucht hier die
vollständige Adresse zu jedem Kürzel.


## Blatt:GoogleMapsExport

Daten ab Zeile 3, wie BERECHNUNG. Fasst Lfd. Nummer, Datum, Reiseweg, Zeiten,
dienstliche Kilometer und einen fertigen Google-Maps-Routenlink pro Reise im
Abrechnungszeitraum zusammen — ersetzt das manuelle Eintippen jedes Ortes in
Maps durch einen Klick. Liefert weiterhin nur die Route, die Tacho-km bzw.
Formularangaben widerspiegelt; Maps zeigt bei ≥3 Orten (Wegpunkte) ohnehin
keine Alternativrouten mehr an, unabhängig von Link oder Handeingabe.

WICHTIG (gilt für jedes FILTER im Dokument): Datenbereich und Bedingung müssen
exakt gleich viele Zeilen haben, sonst liefert FILTER einen Fehler und die
umschließende IFERROR macht daraus eine leere Zelle — die Spalte bleibt still
leer statt sichtbar kaputt. Offenes `A3:A` reicht bis Blattende (998 Zeilen),
`C3:C999` hat 997. Deshalb: offene Bereiche nur mit offenen Bedingungen
kombinieren (A3:A ↔ C3:C), begrenzte nur mit begrenzten. A3–F3 filtern offene
BERECHNUNG-Spalten und nutzen daher C3:C; G3 baut sein Array aus
IMPORTDATA!J2:P998 (997 Zeilen) und braucht dort C3:C999.

#### J1 - Abrechnungszeitraum:

```
=TEXTJOIN(" - ";TRUE;TEXT(Setup!$C$8;"DD.MM.YYYY");TEXT(Setup!$C$10;"DD.MM.YYYY"))
```

**Statement:**
- identisch zu Vermerke E1: `TEXT(…)` formatiert, `TEXTJOIN(" - ";TRUE;…)` verbindet

**Ergebnis:** Abrechnungszeitraum als Text „von - bis" (wie Vermerke E1).
**Rechenweg:** Die beiden Setup-Datumsfelder formatiert und verbunden.


#### A3 - Laufende Nummer:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!A3:A;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!A3:A; …)` – Quelle Spalte A, Bedingungen wie Muster B

**Ergebnis:** Jahres-Nummer der Reise (BERECHNUNG A).
**Muster:** Zeitraum-Auszug (B).


#### B3 - Datum:

```
=ARRAYFORMULA(IFERROR(FILTER(
  TEXT(BERECHNUNG!C3:C;"DD.MM.YYYY");
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `TEXT(BERECHNUNG!C3:C;"DD.MM.YYYY")` – Datum als Text, damit die Ausgabe kein Zellformat braucht
- `FILTER(…)` – Bedingungen wie Muster B

**Ergebnis:** Reisedatum als Text im Format TT.MM.JJJJ.
**Muster:** Zeitraum-Auszug (B).


#### C3 - Wegstrecke:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!L3:L;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!L3:L; …)` – Quelle Spalte L, Bedingungen wie Muster B

**Ergebnis:** Der Reiseweg-Text aus BERECHNUNG L.
**Muster:** Zeitraum-Auszug (B).


#### D3 - Beginn:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!D3:D;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!D3:D; …)` – Quelle Spalte D, Bedingungen wie Muster B

**Ergebnis:** Uhrzeit des Reisebeginns (BERECHNUNG D).
**Muster:** Zeitraum-Auszug (B).


#### E3 - Ende:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!F3:F;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!F3:F; …)` – Quelle Spalte F, Bedingungen wie Muster B

**Ergebnis:** Uhrzeit des Reiseendes (BERECHNUNG F).
**Muster:** Zeitraum-Auszug (B).


#### F3 - Kilometer dienstlich:

```
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!K3:K;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:**
- `FILTER(BERECHNUNG!K3:K; …)` – Quelle Spalte K, Bedingungen wie Muster B

**Ergebnis:** Bereinigte dienstliche Kilometer (BERECHNUNG K).
**Muster:** Zeitraum-Auszug (B).


#### G3 - Routenlink:
Löst Formular-Kürzel gegen Orte!B (Wegpunkte) bzw. Setup (Start/Ziel WO/KV)
zu vollständigen Adressen auf und baut daraus einen anklickbaren
Google-Maps-Link. Nicht gefundene Kürzel bleiben als Rohtext im Link stehen
(sichtbar falsch statt still falsch, siehe Prüfzelle unten).

```
=ARRAYFORMULA(IFERROR(FILTER(
  BYROW(CHOOSECOLS(IMPORTDATA!J2:P998; 1;3;4;5;6;7;2); LAMBDA(zeile;
    LET(
      codes; IFERROR(FILTER(zeile; zeile<>""); {""});
      adr;   MAP(codes; LAMBDA(k;
               LET(kk; TRIM(SUBSTITUTE(SUBSTITUTE(k;"Wohnort";"WO");"Kreisverwaltung";"KV"));
                 IF(kk=""; "";
                   LET(z; XMATCH(kk; Orte!$B$6:$B$200);
                     IF(ISNA(z); kk;
                        TEXTJOIN(" "; TRUE; CHOOSEROWS(Orte!$E$6:$M$200; z))))))));
      n;     COUNTA(adr);
      IF(n<2; "";
        HYPERLINK(
          "https://www.google.com/maps/dir/?api=1&origin="&ENCODEURL(INDEX(adr;1))
          &"&destination="&ENCODEURL(INDEX(adr;n))
          &IF(n>2; "&waypoints="&ENCODEURL(TEXTJOIN("|";TRUE;
               FILTER(adr; (SEQUENCE(1;n)>1)*(SEQUENCE(1;n)<n)))); "");
          "Route"
        )
      )
    )
  ));
  BERECHNUNG!C3:C999<>"";
  BERECHNUNG!C3:C999>=Setup!$C$8 - 0*COUNTA(Orte!$B$6:$M$200);
  BERECHNUNG!C3:C999<=Setup!$C$10
);""))
```

**Statement:**
- `CHOOSECOLS(IMPORTDATA!J2:P998; 1;3;4;5;6;7;2)` – Spalten in Reisereihenfolge umsortieren (Start, Wegpunkte, Ziel)
- `BYROW(…; LAMBDA(zeile; …))` – jede Reise einzeln verarbeiten
- `codes; IFERROR(FILTER(zeile; zeile<>""); {""})` – leere Ortsfelder verwerfen
- `MAP(codes; LAMBDA(k; …))` – jedes Kürzel einzeln auflösen
- `TRIM(SUBSTITUTE(SUBSTITUTE(k;…)))` – Langtext auf Kürzel normalisieren, Leerzeichen abschneiden
- `XMATCH(kk; Orte!$B$6:$B$200)` – Zeilennummer im Orte-Blatt suchen; `ISNA` → Kürzel bleibt Rohtext
- `CHOOSEROWS(Orte!$E$6:$M$200; z)` + `TEXTJOIN(" ";TRUE;…)` – Adresszellen dieser Zeile zu einer Adresse verbinden
- `n; COUNTA(adr)` – Anzahl aufgelöster Orte; `IF(n<2;"";…)` – unter zwei Orten keine Route
- `ENCODEURL(…)` – Adressen URL-sicher kodieren
- `FILTER(adr; (SEQUENCE(1;n)>1)*(SEQUENCE(1;n)<n))` – alles zwischen Erstem und Letztem = Wegpunkte
- `HYPERLINK(url; "Route")` – klickbarer Link mit fester Beschriftung
- `- 0*COUNTA(Orte!$B$6:$M$200)` – rechnerisch wirkungslos, registriert nur Orte als Abhängigkeit

WO und KV werden NICHT mehr per Sonderfall gegen Setup aufgelöst, sondern sind
normale Zeilen in Orte (Kürzel "WO"/"KV" in Spalte B, Adresse in E:M). Das
SUBSTITUTE bleibt, weil das Formular bei Start/Ziel den Langtext
"Wohnort"/"Kreisverwaltung" liefert und bei Wegpunkten das Kürzel — beides wird
auf den Orte-Schlüssel normalisiert. Vorher zeigte der Link für WO/KV
dauerhaft die Setup-Adresse und ignorierte jede Änderung in Orte.

Das `- 0*COUNTA(Orte!$B$6:$M$200)` in der zweiten FILTER-Bedingung ändert den
Vergleichswert nicht, soll Sheets aber zwingen, `Orte` als Abhängigkeit der Zelle
zu tracken (in der `LAMBDA`-Closure von `BYROW`/`MAP` steht der Bereich sonst
allein). Ungeprüft, ob überhaupt nötig — testweise entfernen; aktualisieren sich
Orte-Änderungen weiterhin sofort, kann der Zusatz ersatzlos weg.

ACHTUNG: Der No-op darf NICHT an das `BYROW`-Ergebnis gehängt werden
(`BYROW(...) & IF(...;"";"")`). Jede Verkettung mit `&` wandelt einen
`HYPERLINK`-Wert in seinen reinen Label-Text um — die Zelle zeigt dann „Route"
ohne Link. Deshalb steht die Referenz in der Bedingung, nicht in den Daten.

**Ergebnis:** Ein anklickbarer „Route"-Link, der die Reise direkt in Google Maps öffnet.
**Rechenweg:** Für jeden Ort der Reise wird das Kürzel gegen Orte!B (auch WO/KV) zu einer
vollständigen Adresse aufgelöst; daraus entsteht ein Maps-Link mit Start, Ziel und Zwischenzielen.
**Sonderfall:** Weniger als zwei Orte → kein Link; ein nicht gefundenes Kürzel bleibt als
Rohtext im Link stehen (sichtbar falsch statt still falsch).
**Muster:** Zeitraum-Auszug (B) + Zeilengrenzen (D).

Prüfzelle bei rohem Kürzel im Link statt Adresse:

```
=XMATCH("<Kürzel>"; Orte!B6:B200)
```

**Statement:**
- `XMATCH(Suchwert; Bereich)` – gibt die Position im Bereich zurück, `#N/A` wenn nicht gefunden

#N/A → Kürzel in Orte!B weicht vom Formularwert ab (Groß-/Kleinschreibung,
Leerzeichen, Tippfehler).


## Anhang

### Tagegeld-Staffel (Kurzregel)
1. **Anspruch dem Grunde nach:** bereinigte Abwesenheit `S−T` ≥ 8:01 h (481 Minuten).
2. **Stufe** nach Rest-Zeit `S−T−Q−R`:
   - unter 8:01 h → M (anteilig ≤8 h)
   - 8:01 h bis unter 14 h → N (>8 h)
   - 14 h bis unter 24 h → O (≥14 h)
   - ab 24 h → P (24 h)
3. Ohne „Tagegeld beantragen? = Ja" kein Kreuz.

### Wartung bei Formularänderung
Jede neue Formularfrage verschiebt alle folgenden Spalten. Danach die
IMPORTDATA-Bezüge in BERECHNUNG, Vermerke, Druck-Fahrtenbuch und
GoogleMapsExport prüfen. Zeilengrenzen (Muster D) einheitlich bei 999/998
halten; wird mehr Platz gebraucht, alle drei Blätter per Rechtsklick verlängern
und die Grenzen um denselben Betrag erhöhen.
