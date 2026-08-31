[← Formeln-Übersicht](../Formeln.md)

# GoogleMapsExport

Daten ab Zeile 3, wie BERECHNUNG. Fasst Lfd. Nummer, Datum, Reiseweg, Zeiten,
dienstliche Kilometer und einen fertigen Google-Maps-Routenlink pro Reise im
Abrechnungszeitraum zusammen — ersetzt das manuelle Eintippen jedes Ortes in
Maps durch einen Klick.

WICHTIG (gilt für jedes FILTER im Dokument): Datenbereich und Bedingung müssen
exakt gleich viele Zeilen haben, sonst liefert FILTER einen Fehler und die
umschließende IFERROR macht daraus eine leere Zelle — die Spalte bleibt still
leer statt sichtbar kaputt. Offenes `A3:A` reicht bis Blattende (998 Zeilen),
`C3:C999` hat 997. Offene Bereiche daher nur mit offenen Bedingungen kombinieren
(A3:A ↔ C3:C), begrenzte nur mit begrenzten. A3–F3 filtern offene
BERECHNUNG-Spalten und nutzen daher C3:C; G3 baut sein Array aus
IMPORTDATA!J2:P998 (997 Zeilen) und braucht dort C3:C999.

## J1 - Abrechnungszeitraum

```
=TEXTJOIN(" - ";TRUE;TEXT(Setup!$C$8;"DD.MM.YYYY");TEXT(Setup!$C$10;"DD.MM.YYYY"))
```

**Ergebnis:** Abrechnungszeitraum als Text „von - bis" (wie Vermerke E1).


## A3:F3 - Zeitraum-Auszüge

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


## G3 - Routenlink

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

**Statement:**
- `CHOOSECOLS(IMPORTDATA!J2:P998; 1;3;4;5;6;7;2)` – Spalten in Reisereihenfolge umsortieren (Start, Wegpunkte, Ziel)
- `BYROW(…; LAMBDA(zeile; …))` – jede Reise einzeln verarbeiten
- `codes; IFERROR(FILTER(zeile; zeile<>""); {""})` – leere Ortsfelder verwerfen
- `MAP(codes; LAMBDA(k; …))` – jedes Kürzel einzeln auflösen
- `TRIM(SUBSTITUTE(SUBSTITUTE(k;…)))` – Langtext auf Kürzel normalisieren (Formular liefert bei Start/Ziel „Wohnort"/„Kreisverwaltung", bei Wegpunkten das Kürzel „WO"/„KV" — beides wird auf den Orte-Schlüssel gebracht)
- `XMATCH(kk; Orte!$B$6:$B$200)` – Zeile im Orte-Blatt suchen; `ISNA` → Kürzel bleibt Rohtext
- `CHOOSEROWS(Orte!$E$6:$M$200; z)` + `TEXTJOIN(" ";TRUE;…)` – Adresszellen dieser Zeile zu einer Adresse verbinden
- `n; COUNTA(adr)` – Anzahl aufgelöster Orte; unter zwei Orten keine Route
- `ENCODEURL(…)` – Adressen URL-sicher kodieren
- `FILTER(adr; (SEQUENCE(1;n)>1)*(SEQUENCE(1;n)<n))` – alles zwischen Erstem und Letztem = Wegpunkte
- `HYPERLINK(url; "Route")` – klickbarer Link mit fester Beschriftung
- `- 0*COUNTA(Orte!$B$6:$M$200)` – ändert den Vergleichswert nicht, sorgt aber dafür, dass Sheets `Orte` als Abhängigkeit dieser Zelle erkennt (in der `LAMBDA`-Closure von `BYROW`/`MAP` sonst nicht sichtbar)

WO und KV sind normale Zeilen in Orte (Kürzel „WO"/„KV" in Spalte B, Adresse in E:M),
nicht mehr per Sonderfall gegen Setup aufgelöst.

ACHTUNG: Der No-op darf NICHT an das `BYROW`-Ergebnis gehängt werden
(`BYROW(...) & IF(...;"";"")`). Jede Verkettung mit `&` wandelt einen
`HYPERLINK`-Wert in seinen reinen Label-Text um — die Zelle zeigt dann „Route"
ohne Link. Deshalb steht die Referenz in der Bedingung, nicht in den Daten.

**Ergebnis:** Ein anklickbarer „Route"-Link, der die Reise direkt in Google Maps öffnet.
**Sonderfall:** Weniger als zwei Orte → kein Link; ein nicht gefundenes Kürzel bleibt als
Rohtext im Link stehen.
**Muster:** Zeitraum-Auszug (B) + Zeilengrenzen (D).

Prüfzelle bei rohem Kürzel im Link statt Adresse:

```
=XMATCH("<Kürzel>"; Orte!B6:B200)
```

`#N/A` → Kürzel in Orte!B weicht vom Formularwert ab (Groß-/Kleinschreibung,
Leerzeichen, Tippfehler).
