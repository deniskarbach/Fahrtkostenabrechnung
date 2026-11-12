[← Formeln](README.md)

# GoogleMapsExport

## Zweck

Das Blatt erzeugt je Reise im Abrechnungszeitraum einen Google-Maps-Routenlink; Daten ab Zeile 3.
Es gibt das Blatt, damit die gefahrene Strecke ohne Abtippen der Orte geprüft werden kann.
Es umfasst Nummer, Datum, Reiseweg, Zeiten, dienstliche Kilometer und den Link.

## Funktionsweise

- A3–F3 sind Zeitraum-Auszüge aus BERECHNUNG, G3 baut den Routenlink aus den
  Ortsfeldern in IMPORTDATA und der Tabelle [Orte](orte.md).
- Bei jedem `FILTER` müssen Datenbereich und Bedingung gleich viele Zeilen
  haben, sonst bleibt die Spalte still leer. Offene Bereiche (`A3:A`) nur mit
  offenen kombinieren, begrenzte (`C3:C999`) nur mit begrenzten. A3–F3 nutzen
  `C3:C`; G3 nutzt `IMPORTDATA!J2:P998` (997 Zeilen) und `C3:C999`.

## Formeln

### J1 - Abrechnungszeitraum

```
=TEXTJOIN(" - ";TRUE;TEXT(Setup!$C$8;"DD.MM.YYYY");TEXT(Setup!$C$10;"DD.MM.YYYY"))
```

**Ergebnis:** Abrechnungszeitraum als Text „von - bis" (wie Vermerke E1).


### A3:F3 - Zeitraum-Auszüge

```
=ARRAYFORMULA(IFERROR(FILTER(<Quelle>; BERECHNUNG!C3:C<>""; BERECHNUNG!C3:C>=Setup!$C$8; BERECHNUNG!C3:C<=Setup!$C$10);""))
```

| Zelle | Quelle (BERECHNUNG) | Ergebnis |
|---|---|---|
| A3 | A | Laufende Nummer |
| B3 | `TEXT(C3:C;"DD.MM.YYYY")` | Reisedatum als Text |
| C3 | L | Reiseweg (Text) |
| D3 | D | Uhrzeit Reisebeginn |
| E3 | F | Uhrzeit Reiseende |
| F3 | K | Kilometer dienstlich (bereinigt) |


### G3 - Routenlink

Löst Formular-Kürzel gegen Orte!B (auch WO/KV) zu vollständigen Adressen auf
und baut daraus einen anklickbaren Google-Maps-Link. Nicht gefundene Kürzel
bleiben als Rohtext im Link stehen (sichtbar falsch statt still falsch, siehe
Prüfzelle unten).

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

**Aufbau:**
- `CHOOSECOLS(…; 1;3;4;5;6;7;2)` bringt die Ortsfelder in Reisereihenfolge, `BYROW` verarbeitet jede Reise einzeln, leere Felder fallen weg.
- Je Kürzel: „Wohnort"/„Kreisverwaltung" werden zu „WO"/„KV" normalisiert, `XMATCH` sucht die Zeile in `Orte`, `CHOOSEROWS` + `TEXTJOIN` bilden die Adresse. Nicht gefundene Kürzel bleiben Rohtext.
- Erster Ort = Start, letzter = Ziel, die dazwischen = Wegpunkte; `ENCODEURL` kodiert die Adressen, `HYPERLINK` macht den Link „Route".
- `- 0*COUNTA(Orte!…)` in der Datumsbedingung ändert nichts am Wert, lässt Sheets aber `Orte` als Abhängigkeit erkennen. Nicht an das `BYROW`-Ergebnis anhängen: `&` macht aus dem Link reinen Text.

**Ergebnis:** Ein anklickbarer „Route"-Link, der die Reise direkt in Google Maps öffnet.
**Sonderfall:** Weniger als zwei Orte → kein Link; ein nicht gefundenes Kürzel bleibt als
Rohtext im Link stehen.

Prüfzelle bei rohem Kürzel im Link statt Adresse:

```
=XMATCH("<Kürzel>"; Orte!B6:B200)
```

`#N/A` → Kürzel in Orte!B weicht vom Formularwert ab (Groß-/Kleinschreibung,
Leerzeichen, Tippfehler).
