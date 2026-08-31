[← Formeln-Übersicht](../Formeln.md)

# Druck-Fahrtenbuch

Druckansicht des Fahrtenbuchs, Daten ab Zeile 4. Jede Spalte ein Zeitraum-Auszug
aus BERECHNUNG (Muster B).

## A4, D4:J4 - Zeitraum-Auszüge

```
=ARRAYFORMULA(IFERROR(FILTER(BERECHNUNG!<Spalte>3:<Spalte>; BERECHNUNG!C3:C<>""; BERECHNUNG!C3:C>=Setup!$C$8; BERECHNUNG!C3:C<=Setup!$C$10);""))
```

| Zelle | Quelle (BERECHNUNG) | Ergebnis |
|---|---|---|
| A4 | A | Laufende Nummer |
| D4 | D | Uhrzeit Reisebeginn |
| E4 | F | Uhrzeit Reiseende |
| F4 | L | Reiseweg (Text) |
| G4 | G | Kilometerstand Beginn |
| H4 | H | Kilometerstand Ende |
| I4 | K | Kilometer dienstlich (bereinigt) |
| J4 | I | Kilometer privat (Umweg) |


## B4 / C4 - Monat / Tag

```
=ARRAYFORMULA(IFERROR(FILTER(
  IF(BERECHNUNG!C3:C="";"";MONTH(BERECHNUNG!C3:C));
  BERECHNUNG!C3:C<>"";
  BERECHNUNG!C3:C>=Setup!$C$8;
  BERECHNUNG!C3:C<=Setup!$C$10
);""))
```

**Statement:** wie oben, aber `MONTH(…)` (B4) bzw. `DAY(…)` (C4) auf das Datum
angewendet; `IF(C="";"";…)` verhindert, dass eine leere Zelle als Monat/Tag der
Serienzahl 0 (30.12.1899) erscheint.

**Ergebnis:** Monat bzw. Tag des Reisedatums als Zahl.


## K4:N4 - händische Eintragung (keine Formel)


## O4 - Vermerk (Label)

Baut das Label selbst aus BERECHNUNG/IMPORTDATA (identische Logik wie
Vermerke!A6/B6), statt es aus Vermerke nachzuschlagen — Vermerke ist gefiltert
und daher nicht mehr zeilengleich zu BERECHNUNG.

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

**Ergebnis:** Das Vermerk-Label `V25-03` je Reise, leer wenn kein Vermerk.
**Muster:** Zeitraum-Auszug (B) + Zeilengrenzen (D).
