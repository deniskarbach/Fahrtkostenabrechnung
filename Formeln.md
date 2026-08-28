# Projektidee
Das Fahrtkostenformular soll Dienstreisen automatisiert erfassen und abrechnen: Google-Forms-Antworten laufen per IMPORTRANGE in die Tabelle ein und werden im Blatt BERECHNUNG so aufbereitet, dass die amtlichen Formularblätter S1/S2 nur noch fertige Werte anzeigen müssen.


## Blatt:Setup

Import Formularantworten Google Sheets Datei [Formularantworten-Datei]

=IF(B80="Ja"; IMPORTRANGE(B74; "Formularantworten 1!A1"); "🔒 Bitte legitimieren")

Bedingte Formatierung - Datumsangabe

=TAGTRUNC(C5)<TAGTRUNC(C3)



## Blatt:IMPORTDATA

#### Zelle A1:
=IF(Setup!B74=""; "⚠️ Keine URL hinterlegt"; IFERROR(IMPORTRANGE(Setup!B74; "Formularantworten 1!A1:ZZ"); "❌ Fehler beim Import (Zugriff erlaubt?)"))


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

#### A3 - Laufende Nummer:
=MAP(B3:B; C3:C; LAMBDA(zs; dat;
      IF(dat="";"";
        COUNTIFS(C:C;">="&DATE(YEAR(dat);1;1); C:C;"<"&dat)
      + COUNTIFS(C:C;"="&dat; B:B;"<="&zs))))


#### B3 - Zeitstempel:
=ARRAYFORMULA(IMPORTDATA!A2:A)


#### C3 - Reisedatum Start:
=ARRAYFORMULA(IFERROR(DATEVALUE(IMPORTDATA!C2:C)))


#### D3 - Reisebeginn Uhrzeit:
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!E2:E;"")))


#### E3 - Reisedatum Ende:
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(DATEVALUE(IMPORTDATA!D2:D);C3:C)))


#### F3 - Reiseende Uhrzeit:
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!G2:G;"")))


#### G3 - Kilometer Beginn:
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(IMPORTDATA!F2:F);"")))


#### H3 - Kilometer Ende:
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(IMPORTDATA!H2:H);"")))


#### I3 - Umweg privat (km):
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IF(IMPORTDATA!I2:I="";0;VALUE(IMPORTDATA!I2:I));0)))


#### J3 - Wegstrecke Gesamt (km):
=ARRAYFORMULA(IF(B3:B="";"";H3:H-G3:G))


#### K3 - Wegstrecke bereinigt (km):
=ARRAYFORMULA(IF(B3:B="";"";H3:H-G3:G-I3:I))


#### L3 - Reiseweg:
Reihenfolge: Ort Reisebeginn (J), Ort 1–5 (L:P), Ort Reiseende (K).
=BYROW(CHOOSECOLS(IMPORTDATA!J2:P; 1; 3; 4; 5; 6; 7; 2); LAMBDA(zeile; IF(INDEX(zeile; 1)=""; ""; SUBSTITUTE(SUBSTITUTE(TEXTJOIN(" > "; TRUE; zeile); "Wohnort"; "WO"); "Kreisverwaltung"; "KV"))))


#### M3:T3 - Tagegeld-Gruppe
M:P = Staffel-Kreuze, Q:T = die vier Zeitgrößen, aus denen sie sich ergeben.
Maßgeblich sind nicht die rohen Zeiten, sondern:
- bereinigte Abwesenheit `S-T` für die 8:01-Schwelle (Anspruch dem Grunde nach)
- Rest-Zeit `S-T-Q-R` für die Staffelstufe (Herabstufung)

S bleibt bewusst die rohe Spanne Reiseende−Reisebeginn — sie ist der Nachweis
gegenüber dem Fahrtenbuch und darf nicht stillschweigend gekürzt werden. Der
private Abzug steht als eigene, prüfbare Größe daneben.


#### M3 - Tagegeld Anteilig ≤8h:
=ARRAYFORMULA(IF((IMPORTDATA!Q2:Q="Ja")*ISNUMBER(S3:S)*(ROUND((S3:S-T3:T)*60)>=481)*(ROUND((S3:S-T3:T-Q3:Q-R3:R)*60)<481);"X";""))


#### N3 - Tagegeld >8h:
=ARRAYFORMULA(IF((IMPORTDATA!Q2:Q="Ja")*ISNUMBER(S3:S)*(ROUND((S3:S-T3:T)*60)>=481)*(ROUND((S3:S-T3:T-Q3:Q-R3:R)*60)>=481)*(ROUND((S3:S-T3:T-Q3:Q-R3:R)*60)<840);"X";""))

#### O3 - Tagegeld ≥14h:
=ARRAYFORMULA(IF((IMPORTDATA!Q2:Q="Ja")*ISNUMBER(S3:S)*(ROUND((S3:S-T3:T)*60)>=481)*(ROUND((S3:S-T3:T-Q3:Q-R3:R)*60)>=840)*(ROUND((S3:S-T3:T-Q3:Q-R3:R)*60)<1440);"X";""))


#### P3 - Tagegeld 24h:
=ARRAYFORMULA(IF((IMPORTDATA!Q2:Q="Ja")*ISNUMBER(S3:S)*(ROUND((S3:S-T3:T)*60)>=481)*(ROUND((S3:S-T3:T-Q3:Q-R3:R)*60)>=1440);"X";""))


#### Q3 - Dauer Aufenthalt Dienststätte (h mit dez):
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!R2:R/60;"")))


#### R3 - Aufenthalt Dienstort (h mit dez):
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!S2:S/60;"")))


#### S3 - Abwesenheit Dienstort / Dienststätte (h mit dez):
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(((E3:E+F3:F)-(C3:C+D3:D))*24;"")))


#### T3 - Privater Zeitabzug (h mit dez):
Optionales Formularfeld — leer bedeutet "kein Abzug", nicht "unbekannt", daher
0 statt "": M3:P3 rechnen mit T und würden bei "" #VALUE! liefern.

=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!T2:T/60;0)))


#### Plausibilitätsprüfung (bedingte Formatierung auf T3:T)
Privater Abzug darf die Rest-Zeit nicht negativ machen:
=UND($T3<>"";$S3-$T3-$Q3-$R3<0)


#### U3 - Verpflegung:
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!Z2:Z;"")))


#### V3 - ÖPNV:
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(REGEXREPLACE(REGEXREPLACE(IMPORTDATA!V2:V;"[^0-9,.-]";"");",";"."));"")))


#### W3 - Mitnahme Personenzahl:
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(IMPORTDATA!W2:W);"")))


#### X3 - Übernachtung:
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(REGEXREPLACE(REGEXREPLACE(IMPORTDATA!X2:X;"[^0-9,.-]";"");",";"."));"")))


#### Y3 - Nebenkosten:
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(REGEXREPLACE(REGEXREPLACE(IMPORTDATA!Y2:Y;"[^0-9,.-]";"");",";"."));"")))



## Blatt:ReisekostenabrechnungS1

#### A3 - Name & Organisationseinheit:
=TEXTJOIN(" "; TRUE; Setup!C17; Setup!C19) & ", " & TEXTJOIN(" "; TRUE; Setup!C61) & "-" & TEXTJOIN(""; TRUE; Setup!C63)


#### E3 - Anschrift Antragssteller/in:
=TEXTJOIN(" "; TRUE; Setup!C26; Setup!C28) & "," & TEXTJOIN(" "; TRUE; Setup!C30; Setup!C32)


#### J3 - Dienstort:
=TEXTJOIN(" "; TRUE; Setup!C48; Setup!C50) & ", " & TEXTJOIN(" "; TRUE; Setup!C52; Setup!C54)


#### A7 - Reisedatum:
=ARRAYFORMULA(IFERROR(FILTER(
  LET(start; TEXT(BERECHNUNG!C3:C;"DD.MM.YYYY");
      ende; TEXT(BERECHNUNG!E3:E;"DD.MM.YYYY");
      IF(OR(BERECHNUNG!C3:C=BERECHNUNG!E3:E; BERECHNUNG!E3:E="");
         start; start&" - "&ende));
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### B7 - Beginn:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!D3:D;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### C7 - Ende:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!F3:F;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### D7 - Reiseweg:
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


#### E7 - Tagegeld Anteilig ≤8 Stunden:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!M3:M;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### F7 - Tagegeld mehr als 8 Stunden:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!N3:N;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### G7 - Tagegeld mindestens 14 Stunden:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!O3:O;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### H7 - Tagegeld 24 Stunden:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!P3:P;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### I7 - Unentgeltliche Verpflegung:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!U3:U;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### J7 - Fahrtkosten ÖPNV:
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!V3:V>0;BERECHNUNG!V3:V;"");
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### K7 - Fahrtkosten Wegstrecke bereinigt:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!K3:K;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### L7 - Mitnahme von Personen:
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!W3:W>0;BERECHNUNG!W3:W;"");
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### M7 - Übernachtungskosten:
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!X3:X>0;BERECHNUNG!X3:X;"");
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### N7 - Nebenkosten:
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!Y3:Y>0;BERECHNUNG!Y3:Y;"");
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


## Blatt:ReisekostenabrechnungS2

#### C5 - IBAN:
=TEXTJOIN(" "; TRUE; Setup!C39)


#### C7 - BIC:
=TEXTJOIN(" "; TRUE; Setup!C41)


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
=ARRAYFORMULA(IFERROR(FILTER(
  MAP(BERECHNUNG!B3:B999; BERECHNUNG!C3:C999; IMPORTDATA!AA2:AA998; LAMBDA(zs; dat; txt;
      IF(OR(dat=""; txt=""); "";
        COUNTIFS(BERECHNUNG!$C$3:$C$999;">="&DATE(YEAR(dat);1;1); BERECHNUNG!$C$3:$C$999;"<"&dat; IMPORTDATA!$AA$2:$AA$998;"<>")
      + COUNTIFS(BERECHNUNG!$C$3:$C$999;"="&dat; BERECHNUNG!$B$3:$B$999;"<="&zs; IMPORTDATA!$AA$2:$AA$998;"<>"))));
  IMPORTDATA!AA2:AA998<>"";
  BERECHNUNG!C3:C999<>""
);""))


#### B6 - Label:
Beide Quellspalten prüfen, nicht nur A: bei leerem Datum liefert TEXT(;"YY") die
Serienzahl 0 = 30.12.1899 und damit stillschweigend "V99". Lieber kein Label als
ein falsches Jahr.
WICHTIG: A, B, C und F müssen auf derselben Zeile starten und dieselbe Endzeile
haben, sonst paart B eine Nummer mit dem Datum einer anderen Reise. Startzeile
hier durchgängig 6 — wird sie geändert, in allen vier Formeln gleichzeitig.

=ARRAYFORMULA(IF((A6:A1000="")+(F6:F1000="");"";"V"&TEXT(F6:F1000;"YY")&"-"&TEXT(A6:A1000;"00")))


#### C6 - Vermerktext (aus Formular):
=ARRAYFORMULA(IFERROR(FILTER(
  IMPORTDATA!AA2:AA998;
  IMPORTDATA!AA2:AA998<>"";
  BERECHNUNG!C3:C999<>""
);""))


#### D:E - Ergänzung: entfällt, keine Formel
Ergänzungen werden an der Quelle im Formularfeld "Sonstige Informationen"
gepflegt und erscheinen über C. Werden D/E gelöscht, rückt das Datum nach vorn —
dann in B6 beide F-Bezüge auf die neue Spalte ändern.


#### F6 - Datum:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!C3:C999;
  IMPORTDATA!AA2:AA998<>"";
  BERECHNUNG!C3:C999<>""
);""))


#### E1 - Stand Datum:
=TEXTJOIN(" - ";TRUE;TEXT(Setup!$C$8;"DD.MM.YYYY");TEXT(Setup!$C$10;"DD.MM.YYYY"))


## Blatt:Druck-Fahrtenbuch

#### A4 - Laufende Nummer:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!A3:A;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### B4 - Monat:
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!C3:C="";"";MONTH(BERECHNUNG!C3:C));
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### C4 - Tag:
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!C3:C="";"";DAY(BERECHNUNG!C3:C));
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### D4 - Reisebeginn Uhrzeit:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!D3:D;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### E4 - Reiseende Uhrzeit:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!F3:F;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### F4 - Reiseweg:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!L3:L;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### G4 - Kilometerstand Beginn:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!G3:G;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### H4 - Kilometerstand Ende:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!H3:H;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### I4 - Kilometer dienstlich:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!K3:K;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### J4 - Kilometer privat:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!I3:I;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### K4:N4 - händische Eintragung (keine Formel)


#### O4 - Vermerk (Label):
Baut das Label selbst aus BERECHNUNG/IMPORTDATA (identische Logik wie
Vermerke!A4/B4), statt es aus Vermerke nachzuschlagen — Vermerke ist gefiltert
und daher nicht mehr zeilengleich zu BERECHNUNG, ein Bezug darauf wäre wieder
positionsabhängig. Reisen ohne Vermerk bleiben leer.

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


## Blatt:Orte

Stammdaten der Reiseziele, Daten beginnen ab Zeile 6. Spalte A = Nr., Spalte B
= Kürzel (identisch zum Formularwert, außer WO/KV — siehe unten), Spalte C:D
= vollständiger Name der Einrichtung, Spalte E:M = vollständige Adresse
(Straße Hausnummer, PLZ Ort — je nach Zusammenführung über mehrere Zellen
verteilt oder in E zusammengefasst).

WO (Wohnort) und KV (Kreisverwaltung) stehen NICHT in diesem Blatt, sondern
in Setup (C26/C28/C30/C32 bzw. C48/C50/C52/C54) — dieselbe Quelle wie
ReisekostenabrechnungS1 E3/J3. Das Formular liefert bei Start/Ziel den
Langtext "Wohnort"/"Kreisverwaltung", bei Wegpunkten das Kürzel "WO"/"KV";
GoogleMapsExport!G3 gleicht das per SUBSTITUTE an, wie bereits BERECHNUNG!L3.


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
=TEXTJOIN(" - ";TRUE;TEXT(Setup!$C$8;"DD.MM.YYYY");TEXT(Setup!$C$10;"DD.MM.YYYY"))


#### A3 - Laufende Nummer:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!A3:A;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### B3 - Datum:
=ARRAYFORMULA(IFERROR(FILTER(
  TEXT(BERECHNUNG!C3:C;"DD.MM.YYYY");
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### C3 - Wegstrecke:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!L3:L;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### D3 - Beginn:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!D3:D;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### E3 - Ende:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!F3:F;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### F3 - Kilometer dienstlich:
=ARRAYFORMULA(IFERROR(FILTER(
  BERECHNUNG!K3:K;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### G3 - Routenlink:
Löst Formular-Kürzel gegen Orte!B (Wegpunkte) bzw. Setup (Start/Ziel WO/KV)
zu vollständigen Adressen auf und baut daraus einen anklickbaren
Google-Maps-Link. Nicht gefundene Kürzel bleiben als Rohtext im Link stehen
(sichtbar falsch statt still falsch, siehe Prüfzelle unten).

=ARRAYFORMULA(IFERROR(FILTER(
  BYROW(CHOOSECOLS(IMPORTDATA!J2:P998; 1;3;4;5;6;7;2); LAMBDA(zeile;
    LET(
      codes; IFERROR(FILTER(zeile; zeile<>""); {""});
      adr;   MAP(codes; LAMBDA(k;
               LET(kk; TRIM(SUBSTITUTE(SUBSTITUTE(k;"Wohnort";"WO");"Kreisverwaltung";"KV"));
                 IF(kk=""; "";
                   IF(kk="WO"; TEXTJOIN(" ";TRUE;Setup!$C$26;Setup!$C$28)&", "&TEXTJOIN(" ";TRUE;Setup!$C$30;Setup!$C$32);
                   IF(kk="KV"; TEXTJOIN(" ";TRUE;Setup!$C$48;Setup!$C$50)&", "&TEXTJOIN(" ";TRUE;Setup!$C$52;Setup!$C$54);
                     LET(z; XMATCH(kk; Orte!$B$6:$B$200);
                       IF(ISNA(z); kk;
                          TEXTJOIN(" "; TRUE; CHOOSEROWS(Orte!$E$6:$M$200; z))))))))));
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
  BERECHNUNG!C3:C999>=Setup!$C$8;
  BERECHNUNG!C3:C999<=Setup!$C$10
);""))

Prüfzelle bei rohem Kürzel im Link statt Adresse:
=XMATCH("<Kürzel>"; Orte!B6:B200)
#N/A → Kürzel in Orte!B weicht vom Formularwert ab (Groß-/Kleinschreibung,
Leerzeichen, Tippfehler).
