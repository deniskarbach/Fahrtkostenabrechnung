[← Formeln-Übersicht](README.md)

# BERECHNUNG

Kernblatt: eine Zeile je Reise, alle Rechengrößen fertig aufbereitet.

## A3 - Laufende Nummer

```
=MAP(B3:B; C3:C; LAMBDA(zs; dat;
      IF(dat="";"";
        COUNTIFS(C:C;">="&DATE(YEAR(dat);1;1); C:C;"<"&dat)
      + COUNTIFS(C:C;"="&dat; B:B;"<="&zs))))
```

**Statement:**
- `MAP(B3:B; C3:C; LAMBDA(zs; dat; …))` – läuft paarweise über Zeitstempel- und Datumsspalte, je Zeile ein Ergebnis
- `COUNTIFS(C:C;">="&DATE(YEAR(dat);1;1); C:C;"<"&dat)` – zählt Reisen ab 1.1. des Jahres bis vor diesem Datum
- `+ COUNTIFS(C:C;"="&dat; B:B;"<="&zs)` – plus Reisen am selben Tag mit früherem Zeitstempel

**Ergebnis:** Fortlaufende Nummer der Reise innerhalb ihres Kalenderjahres.
**Sonderfall:** Zeilen ohne Datum bekommen keine Nummer.


## B3 - Zeitstempel

```
=ARRAYFORMULA(IMPORTDATA!A2:A)
```

**Ergebnis:** Zeitpunkt der Formularabgabe, 1:1 aus IMPORTDATA übernommen.
Dient in allen anderen Spalten als „gibt es diese Reise?"-Marke für Muster A.


## C3 / E3 - Reisedatum Start / Ende

```
C3: =ARRAYFORMULA(IFERROR(TO_DATE(INT(IF(ISNUMBER(IMPORTDATA!C2:C);IMPORTDATA!C2:C;DATEVALUE(TRIM(IMPORTDATA!C2:C)))))))
E3: =ARRAYFORMULA(IF(B3:B="";"";IFERROR(TO_DATE(INT(IF(ISNUMBER(IMPORTDATA!D2:D);IMPORTDATA!D2:D;DATEVALUE(TRIM(IMPORTDATA!D2:D)))));C3:C)))
```

**Statement:**
- `ISNUMBER(…)` – prüft je Zeile, ob schon ein Datums-/Zahlenwert vorliegt; kommt er als Text, wird `DATEVALUE(TRIM(…))` geparst
- `INT(…)` – schneidet eine eventuelle Uhrzeit ab, übrig bleibt der reine Tag
- `TO_DATE(…)` – stempelt die Zahl als Datumstyp
- E3: `IFERROR(…;C3:C)` – bleibt das optionale Enddatum-Feld leer, gilt das Startdatum (eintägige Reise)

**Ergebnis:** Start- bzw. Enddatum der Reise als echtes Datum.
**Sonderfall:** Leere und unlesbare Werte bleiben leer (C3) bzw. fallen auf das Startdatum zurück (E3).

Die `ISNUMBER`-Weiche macht die Formel unabhängig von der Zellformatierung in
IMPORTDATA: liegt bereits ein Datums-/Zahlenwert vor, wird `DATEVALUE` gar nicht
erst aufgerufen. `TO_DATE` sorgt zusätzlich dafür, dass die Zelle nach dem
Wachsen der ARRAYFORMULA als Datum angezeigt bleibt (nicht als nackte
Seriennummer) und weiter gegen Setup!C8/C10 filterbar ist.

Zusätzliche Absicherung der Anzeige per Apps-Script-Trigger „Bei Änderung"
(Erweiterungen › Apps Script), läuft automatisch:

```
function fixDatumsformat() {
  const b = SpreadsheetApp.getActive().getSheetByName("BERECHNUNG");
  ["C3:C1000","E3:E1000"].forEach(r => b.getRange(r).setNumberFormat("dd.mm.yyyy"));
}
```


## D3 / F3 - Uhrzeit Reisebeginn / -ende

| Zelle | Quelle (IMPORTDATA) |
|---|---|
| D3 | E |
| F3 | G |

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!E2:E;"")))
```

**Muster:** Auto-Spalte (A).


## G3 / H3 - Kilometer Beginn / Ende

| Zelle | Quelle (IMPORTDATA) |
|---|---|
| G3 | F |
| H3 | H |

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IF(ISNUMBER(IMPORTDATA!F2:F);IMPORTDATA!F2:F;VALUE(REGEXREPLACE(IMPORTDATA!F2:F;"[^0-9,.-]";"")));0)))
```

**Ergebnis:** Tachostand als Zahl.
**Sonderfall:** Unlesbare Eingabe wird 0 — sichtbar über die Plausibilitätsprüfung bei K3.
**Muster:** Auto-Spalte (A) + Text zu Zahl (C) + Ersatzwert 0 (E).


## I3 - Umweg privat (km)

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IF(IMPORTDATA!I2:I="";0;VALUE(IMPORTDATA!I2:I));0)))
```

**Ergebnis:** Privat gefahrene Zusatzkilometer, optionales Feld, keine Angabe zählt als 0.
**Muster:** Auto-Spalte (A).


## J3 / K3 - Wegstrecke Gesamt / bereinigt (km)

```
J3: =ARRAYFORMULA(IF(B3:B="";"";H3:H-G3:G))
K3: =ARRAYFORMULA(IF(B3:B="";"";H3:H-G3:G-I3:I))
```

**Ergebnis:** J3 alle gefahrenen Kilometer (Ende − Beginn); K3 die rein
dienstlichen Kilometer (zusätzlich minus privater Umweg I) — die
abrechnungsrelevante Größe.
**Muster:** Auto-Spalte (A).


## Plausibilitätsprüfung (bedingte Formatierung auf K3:K)

```
=UND($B3<>"";ODER($G3=0;$H3=0;$K3<=0))
```

**Ergebnis:** Färbt die Zeile, wenn ein Tachostand 0 ist (Ersatzwert oder
Fehleingabe, Muster E) oder K3 nicht positiv ist.


## L3 - Reiseweg

Reihenfolge: Ort Reisebeginn (J), Ort 1–5 (L:P), Ort Reiseende (K).

```
=BYROW(CHOOSECOLS(IMPORTDATA!J2:P; 1; 3; 4; 5; 6; 7; 2); LAMBDA(zeile; IF(INDEX(zeile; 1)=""; ""; SUBSTITUTE(SUBSTITUTE(TEXTJOIN(" > "; TRUE; zeile); "Wohnort"; "WO"); "Kreisverwaltung"; "KV"))))
```

**Statement:**
- `CHOOSECOLS(…; 1;3;4;5;6;7;2)` – sortiert die Spalten in Reisereihenfolge um (J, L–P, dann K)
- `BYROW(…; LAMBDA(zeile; …))` – verarbeitet jede Zeile einzeln zu einem Textwert
- `TEXTJOIN(" > "; TRUE; zeile)` – Orte verketten, leere Zellen übersprungen
- `SUBSTITUTE(SUBSTITUTE(…))` – „Wohnort" → „WO", „Kreisverwaltung" → „KV"

**Ergebnis:** Der Reiseweg als Text, z. B. `WO > KV > Musterstadt > WO`.
**Sonderfall:** Ohne Startort bleibt die Zelle leer.


## M3:T3 - Tagegeld-Gruppe

M:P sind die Staffel-Kreuze, Q:T die vier Zeitgrößen, aus denen sie sich ergeben.
Maßgeblich sind nicht die rohen Zeiten, sondern:
- bereinigte Abwesenheit `S-T` für die 8:01-Schwelle (Anspruch dem Grunde nach)
- Rest-Zeit `S-T-Q-R` für die Staffelstufe

S bleibt die rohe Spanne Reiseende−Reisebeginn (Nachweis gegenüber dem
Fahrtenbuch), der private Abzug T steht als eigene, prüfbare Größe daneben.

### M3:P3 - Staffel-Kreuze

```
=ARRAYFORMULA(IF((IMPORTDATA!Q2:Q="Ja")*ISNUMBER(S3:S)*(ROUND((S3:S-T3:T)*60)>=481)*<Rest-Zeit-Bedingung>;"X";""))
```

**Statement:**
- `(…)*(…)*(…)` – Multiplikation von WAHR/FALSCH (1/0) ersetzt UND
- `IMPORTDATA!Q2:Q="Ja"` – Tagegeld beantragt?
- `ROUND((S3:S-T3:T)*60)>=481` – Anspruch dem Grunde nach: bereinigte Abwesenheit ≥ 8:01 h (481 Min)
- `<Rest-Zeit-Bedingung>` – `ROUND((S3:S-T3:T-Q3:Q-R3:R)*60)` gegen die Staffelgrenze geprüft

| Spalte | Rest-Zeit-Bedingung (Minuten) | Ergebnis |
|---|---|---|
| M | < 481 | Tagegeld anteilig ≤8h |
| N | 481–839 | Tagegeld >8h |
| O | 840–1439 | Tagegeld ≥14h |
| P | ≥ 1440 | Tagegeld 24h (voller Abwesenheitstag) |

**Muster:** Auto-Spalte (A).


## Q3 / R3 - Aufenthalt Dienststätte / Dienstort (h mit dez)

| Zelle | Quelle (IMPORTDATA) |
|---|---|
| Q3 | R |
| R3 | S |

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!R2:R/60;0)))
```

**Ergebnis:** Formularangabe in Minuten geteilt durch 60.
**Muster:** Auto-Spalte (A) + Ersatzwert 0 (E) – M3:P3 rechnen mit diesen Spalten weiter.


## S3 - Abwesenheit Dienstort / Dienststätte (h mit dez)

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(((E3:E+F3:F)-(C3:C+D3:D))*24;0)))
```

**Statement:**
- `E3:E+F3:F` bzw. `C3:C+D3:D` – Datum und Uhrzeit zu einem Zeitpunkt addieren (beides Serienzahlen)
- `(…)-(…)` – Differenz in Tagen, `*24` – in Stunden umgerechnet

**Ergebnis:** Gesamte Reisedauer von Beginn bis Ende, in Dezimalstunden.
**Sonderfall:** Bleibt bewusst ungekürzt — der private Abzug wird erst in T separat geführt.
**Muster:** Auto-Spalte (A) + Ersatzwert 0 (E).


## T3 - Privater Zeitabzug (h mit dez)

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!T2:T/60;0)))
```

**Ergebnis:** Privat veranlasste Zeit, die von der Abwesenheit abzuziehen ist, in Dezimalstunden.
**Sonderfall:** Optionales Feld; leer zählt als 0 (kein Abzug), nicht als „unbekannt".
**Muster:** Auto-Spalte (A) + Ersatzwert 0 (E).


## Plausibilitätsprüfung (bedingte Formatierung auf T3:T)

```
=UND($T3<>"";$S3-$T3-$Q3-$R3<0)
```

**Ergebnis:** Markiert die Zelle, wenn der private Abzug die Rest-Zeit ins Negative zieht — dann stimmt eine der Zeitangaben nicht.


## U3 - Verpflegung

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IMPORTDATA!Z2:Z;"")))
```

**Ergebnis:** Angabe zu unentgeltlicher Verpflegung aus dem Formular.
**Muster:** Auto-Spalte (A).


## V3 / W3 / X3 / Y3 - ÖPNV, Mitnahme, Übernachtung, Nebenkosten

| Zelle | Quelle (IMPORTDATA) | Bedeutung |
|---|---|---|
| V3 | V | ÖPNV-Kosten |
| W3 | W | Anzahl mitgenommener Personen |
| X3 | X | Übernachtungskosten |
| Y3 | Y | Sonstige Nebenkosten |

```
=ARRAYFORMULA(IF(B3:B="";"";IFERROR(IF(ISNUMBER(IMPORTDATA!V2:V);IMPORTDATA!V2:V;VALUE(REGEXREPLACE(IMPORTDATA!V2:V;"[^0-9,.-]";"")));0)))
```

**Ergebnis:** Zahl, 0 wenn nichts eingetragen wurde. Freitext (z. B. „2 Personen") wird auf die Ziffer reduziert.
**Muster:** Auto-Spalte (A) + Text zu Zahl (C).
