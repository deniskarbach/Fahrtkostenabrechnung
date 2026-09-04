[← Formeln-Übersicht](README.md)

# Vermerke

Daten ab Zeile 6. Nur Reisen mit ausgefülltem „Sonstige Informationen"
(IMPORTDATA Spalte AA) erscheinen — lückenlos, ohne Leerzeile pro
unbeschriebener Reise. Es wird direkt in diesem Blatt gearbeitet und gedruckt,
kein separates Ansichtsblatt.

| Spalte | Inhalt |
|---|---|
| A | Laufende Nr. |
| B | Label |
| C | Vermerktext |
| D:E | – (keine Formel) |
| F | Datum |

**Wichtig:**
- Kein Blattfilter („Daten > Filter erstellen") auf diesem Blatt: Filter werten
  ihre Bedingung nur bei manueller Interaktion neu aus, nicht bei
  Formel-Neuberechnung durch IMPORTRANGE — neue Vermerke blieben sonst
  versteckt. Ein vorhandener Filter ist zu entfernen.
- Quellgrenze einheitlich 1000 Zeilen (Google-Sheets-Standardgröße):
  BERECHNUNG 3:999, IMPORTDATA 2:998 (je 997 Zeilen). Hat ein Blatt weniger als
  1000 Zeilen, gibt es „Bezug nicht vorhanden"-Fehler — Zeilen per Rechtsklick ergänzen.
- Vermerke selbst bietet ab Zeile 6 nur 995 Ausgabezeilen. Bei mehr als 995
  Reisen mit Vermerk: alle drei Blätter verlängern und die Grenzen 999/998 um
  denselben Betrag erhöhen.
- Alle Spalten sind Formelergebnisse, nicht händisch beschreiben. Änderungen
  ausschließlich am Formularfeld „Sonstige Informationen" pflegen, sie laufen
  automatisch über C mit ein.


## A6 - Laufende Nummer

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

**Statement:** wie BERECHNUNG A3, aber das Zusatzkriterium
`IMPORTDATA!$AA$2:$AA$998;"<>"` in beiden `COUNTIFS` zählt nur Reisen mit
Vermerk mit; `FILTER` beschränkt die Ausgabe auf ebendiese Reisen.

**Ergebnis:** Jahres-Nummer der Reise, gezählt und angezeigt nur unter Reisen mit Vermerk.
**Muster:** Zeilengrenzen (D).


## B6 - Label

```
=ARRAYFORMULA(IF((A6:A1000="")+(F6:F1000="");"";"V"&TEXT(F6:F1000;"YY")&"-"&TEXT(A6:A1000;"00")))
```

**Statement:**
- `(A…="")+(F…="")` – Addition von WAHR/FALSCH ersetzt ODER
- `TEXT(F…;"YY")` – zweistelliges Jahr, `TEXT(A…;"00")` – Nummer mit führender Null

**Ergebnis:** Kurzkennung wie `V25-03` (V + zweistelliges Jahr + laufende Nummer).
**Sonderfall:** Fehlt Nummer oder Datum, bleibt das Label leer — sonst würde ein
leeres Datum als Serienzahl 0 (30.12.1899) stillschweigend „V99" ergeben.

A, B, C und F müssen auf derselben Zeile starten und enden, sonst paart B eine
Nummer mit dem Datum einer anderen Reise. Startzeile durchgängig 6 — wird sie
geändert, in allen vier Formeln gleichzeitig.


## C6 / F6 - Vermerktext / Datum

```
C6: =ARRAYFORMULA(IFERROR(FILTER(IMPORTDATA!AA2:AA998; IMPORTDATA!AA2:AA998<>""; BERECHNUNG!C3:C999<>"");""))
F6: =ARRAYFORMULA(IFERROR(FILTER(BERECHNUNG!C3:C999; IMPORTDATA!AA2:AA998<>""; BERECHNUNG!C3:C999<>"");""))
```

**Ergebnis:** C6 der Vermerktext aus IMPORTDATA!AA, F6 das zugehörige Reisedatum.
Beide nutzen exakt dieselben zwei Filterbedingungen → gleiche Zeilen, gleiche
Reihenfolge, damit Nummer, Label, Text und Datum zeilengleich bleiben.
**Muster:** Zeitraum-Auszug (B, ohne Datumsgrenzen) + Zeilengrenzen (D).

D:E (Ergänzung) hat keine Formel — Ergänzungen werden an der Quelle im
Formularfeld gepflegt und erscheinen über C. Werden D/E gelöscht, rückt das
Datum nach vorn — dann in B6 beide F-Bezüge auf die neue Spalte ändern.


## E1 - Stand Datum

```
=TEXTJOIN(" - ";TRUE;TEXT(Setup!$C$8;"DD.MM.YYYY");TEXT(Setup!$C$10;"DD.MM.YYYY"))
```

**Ergebnis:** Abrechnungszeitraum als Text „von - bis".
