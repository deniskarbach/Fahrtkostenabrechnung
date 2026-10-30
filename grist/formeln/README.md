# Formeln

Nachweis der Berechnung: jede Rechenspalte mit ihrer Formel und dem, was sie
ergibt. Die Formeln hier sind dieselben wie im Grist-Dokument; ihre Quelle ist
`setup.py`.

Grist rechnet in **Python**. Eine Formel gilt für die ganze Spalte und wird je
Zeile ausgewertet: `$Feld` ist der Wert dieser Zeile, `Reisen.all` sind alle
Reisen. Neue Zeilen rechnen sofort mit. Ein leeres Zahlenfeld ist `None`; die
Formeln setzen dafür 0 (`$Feld or 0`) und begrenzen Ergebnisse, die nicht
negativ sein dürfen, mit `max(0, …)`.

## Datenfluss

```
Grist-Formular (veröffentlichter Link, Handy, ohne Konto)
   │  eine Absendung = eine Zeile
   ▼
Reisen           Eingabespalten + Rechenspalten
                 (Kilometer, Abwesenheit, Tagegeld-Stufe, Reiseweg,
                  laufende Nummer, Routenlink, Vermerk-Kennung, Einzelziele)

Einstellungen    Stammdaten + Abrechnungszeitraum  ──┐
Stammziele       Stammziele mit Adresse            ──┤
                                                     ▼
                                   Ausgabe-Widgets, gefiltert auf den Zeitraum
                                   S1/S2 · Vermerke · Ortsverzeichnis ·
                                   Fahrtenbuch · Prüfliste
```

Eingetragen wird nur im Formular, in `Einstellungen` und in `Stammziele`. Alles
andere ist Formelergebnis.

## Muster: Was eingetragen ist, zählt

Jedes der sieben Ortsfelder ist ein Paar aus Auswahl (Stammziel) und Freitext
(Einzelziel). Es gibt **keine Rangfolge**: Sind beide gefüllt, sind es zwei
Stopps, erst die Auswahl, dann der Freitext. So verschwindet nichts unbemerkt —
ein Versehen steht sichtbar im Reiseweg (`WO > KITA > E26-07 > WO`) und wird
durch Leeren des falschen Felds korrigiert. Die Regel gilt in `Einzelziele`,
`Reiseweg` und `Maps_Link`.

## Muster: Rang im Kalenderjahr

```python
alle = [r for r in Reisen.all if r.Datum and r.Datum.year == $Datum.year]
alle.sort(key=lambda r: (r.Datum, r.id))
return [r.id for r in alle].index($id) + 1
```

Alle Reisen desselben Kalenderjahres, nach Datum sortiert (bei gleichem Datum
in der Reihenfolge der Erfassung); die eigene Position ab 1 ist die Nummer.
Eine nachgetragene ältere Reise verschiebt die Nummern danach. Gezählt wird je
**Kalenderjahr**, nicht je Abrechnungszeitraum: Ein Zeitraum über den
Jahreswechsel hat zwei Nummernkreise. So zählen `Lfd_Nr`, `Einzelziele`
(`E26-07`) und `Vermerk_Label` (`V26-01`), jede für sich.

## Seiten

1. [Einstellungen](einstellungen.md) — Stammdaten und Abrechnungszeitraum
2. [Stammziele](stammziele.md) — wiederkehrende Ziele mit Adresse
3. [Reisen](reisen.md) — alle Rechenspalten
4. [Ausgabe](ausgabe.md) — was auf welchem Blatt steht
5. [Anhang](anhang.md) — Tagegeld-Staffel, was bewusst nicht erfasst wird

Für die Betreuung: [Einrichtung und Technik](setup.md).
