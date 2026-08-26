# Projektidee
Das Fahrtkostenformular soll Dienstreisen automatisiert erfassen und abrechnen: Google-Forms-Antworten laufen per IMPORTRANGE in die Tabelle ein und werden im Blatt BERECHNUNG so aufbereitet, dass die amtlichen Formularblätter S1/S2 nur noch fertige Werte anzeigen müssen.


## Blatt:Setup

Import Formularantworten Google Sheets Datei [Formularantworten-Datei]

=IF(B80="Ja"; IMPORTRANGE(B74; "Formularantworten 1!A1"); "🔒 Bitte legitimieren")



## Blatt:IMPORTDATA

#### Zelle A1:
=IF(Setup!B74=""; "⚠️ Keine URL hinterlegt"; IFERROR(IMPORTRANGE(Setup!B74; "Formularantworten 1!A1:ZZ"); "❌ Fehler beim Import (Zugriff erlaubt?)"))



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
=BYROW(CHOOSECOLS(IMPORTDATA!J2:O; 1; 3; 4; 5; 6; 2); LAMBDA(zeile; IF(INDEX(zeile; 1)=""; ""; TEXTJOIN(" – "; TRUE; zeile))))


#### M3 - Tagegeld Anteilig ≤8h:
=ARRAYFORMULA(IF((IMPORTDATA!Q2:Q="Ja")*ISNUMBER(S3:S)*(S3:S>=0)*(S3:S<=8);"X";""))


#### N3 - Tagegeld >8h:
=ARRAYFORMULA(IF((IMPORTDATA!Q2:Q="Ja")*ISNUMBER(S3:S)*(S3:S>8)*(S3:S<14);"X";""))

#### O3 - Tagegeld ≥14h:
=ARRAYFORMULA(IF((IMPORTDATA!Q2:Q="Ja")*ISNUMBER(S3:S)*(S3:S>=14)*(S3:S<24);"X";""))


#### P3 - Tagegeld 24h:
=ARRAYFORMULA(IF((IMPORTDATA!Q2:Q="Ja")*ISNUMBER(S3:S)*(S3:S>=24);"X";""))


#### Q3 - Dauer Aufenthalt Dienststätte (h mit dez):
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!R2:R/60;"")))


#### R3 - Aufenthalt Dienstort (h mit dez):
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!S2:S/60;"")))


#### S3 - Abwesenheit Dienstort / Dienststätte (h mit dez):
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(((E3:E+F3:F)-(C3:C+D3:D))*24;"")))


#### T3 - Verpflegung:
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!Y2:Y;"")))


#### U3 - ÖPNV:
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(REGEXREPLACE(REGEXREPLACE(IMPORTDATA!U2:U;"[^0-9,.-]";"");",";"."));"")))


#### V3 - Mitnahme Personenzahl:
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(IMPORTDATA!V2:V);"")))


#### W3 - Übernachtung:
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(REGEXREPLACE(REGEXREPLACE(IMPORTDATA!W2:W;"[^0-9,.-]";"");",";"."));"")))



##### X3 - Nebenkosten:
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(VALUE(REGEXREPLACE(REGEXREPLACE(IMPORTDATA!X2:X;"[^0-9,.-]";"");",";"."));"")))



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
  BERECHNUNG!A3:A
  &" – ["&"Ges.: "&TEXT(BERECHNUNG!S3:S/24;"[H]:MM")
  &" | DSt: "&TEXT(BERECHNUNG!Q3:Q/24;"[H]:MM")
  &" | DO: "&TEXT(BERECHNUNG!R3:R/24;"[H]:MM")
  &" | Rest: "&TEXT((BERECHNUNG!S3:S-BERECHNUNG!Q3:Q-BERECHNUNG!R3:R)/24;"[H]:MM")&"]";
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
  BERECHNUNG!T3:T;
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### J7 - Fahrtkosten ÖPNV:
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!U3:U>0;BERECHNUNG!U3:U;"");
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
  IF(BERECHNUNG!V3:V>0;BERECHNUNG!V3:V;"");
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### M7 - Übernachtungskosten:
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!W3:W>0;BERECHNUNG!W3:W;"");
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


#### N7 - Nebenkosten:
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!X3:X>0;BERECHNUNG!X3:X;"");
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))


## Blatt:ReisekostenabrechnungS2

#### C5 - IBAN:
=TEXTJOIN(" "; TRUE; Setup!C39)


#### C7 - BIC:
=TEXTJOIN(" "; TRUE; Setup!C41)
