# Formeln

Die nachfolgend aufgeführten Formeln dienen der Nachvollziehbarkeit und
Transparenz der Berechnung sowie der Prüfung der zugrunde liegenden Ergebnisse.

Grist rechnet in **Python**, nicht in einer Tabellenkalkulationssprache. Eine
Formel steht einmal für die ganze Spalte und wird je Zeile ausgewertet; `$Feld`
ist der Wert der eigenen Zeile. Die Formeln stehen im Quelltext in
[`setup.py`](../setup.py) und werden von dort ins Dokument geschrieben — das
Skript ist die Quelle, nicht der Editor.

## Gliederung dieses Dokuments

1. **Datenfluss** – wie eine Dienstreise durch die Tabellen läuft
2. **Erklärschema** – wie die Formel-Erklärungen aufgebaut sind
3. **Wiederkehrende Muster** – fünf Bausteine, die in fast jeder Formel stecken
4. **[Tabellen](#tabellen)** – je ein eigenes Dokument, in Datenfluss-Reihenfolge: Kurzzweck der Tabelle, dann jede Spalte einzeln
5. **[Anhang](anhang.md)** – Tagegeld-Staffel, Wartung bei Änderungen

## Datenfluss

```
Grist-Formular (veröffentlichter Link, Handy, ohne Konto)
   │  eine Absendung = eine Zeile
   ▼
Reisen           Eingabespalten + Rechenspalten
   │             (Kilometer, Abwesenheit, Tagegeld-Stufe, Reiseweg,
   │              laufende Nummer, Routenlink, Vermerk-Kennung)
   │
   │  Ortsfeld als Freitext ausgefüllt, ohne Auswahl?
   ▼
Adressen         eine Zeile je Fahrt und Ortsfeld — Straße/PLZ/Ort
                 trägt die Abrechnungsstelle nach

Einstellungen    Stammdaten + Abrechnungszeitraum  ──┐
Orte             Stammziele mit Adresse            ──┤
                                                     ▼
                                   Ausgabe-Widget (ausdruck.html)
                                   auf Abrechnungszeitraum gefiltert
                                   S1/S2 · Vermerke · Dienstorte · Fahrtenbuch
```

Gearbeitet wird ausschließlich im Formular sowie in `Einstellungen` und `Orte`;
in `Adressen` wird die Anschrift nachgetragen. Alle Rechenspalten sind reine
Formelergebnisse.

## Erklärschema

Jede Formel wird nach demselben Muster erklärt, maximal fünf Sätze:

- **Statement** – was die Formel technisch tut, Zeile für Zeile (Stichpunkte)
- **Ergebnis** – was am Ende in der Zelle steht, in Alltagssprache
- **Rechenweg** – wie der Wert zustande kommt, mit benannten Bezügen
- **Sonderfall** – Leerwert, Fehler, Grenzfall (nur wenn vorhanden)
- **Muster** – Verweis auf einen der fünf Bausteine unten statt Wiederholung

## Wiederkehrende Muster

### Muster A – Spaltenformel statt Zellformel

```
$Datum_Ende or $Datum
```

**Statement:**
- `$Feld` – Wert des Feldes **in derselben Zeile**
- kein Bereich, kein Mitwachsen, kein `ARRAYFORMULA`

Eine Formel gilt für die ganze Spalte und wird je Zeile ausgewertet. Neue
Zeilen rechnen sofort mit; es gibt keine „erste Zelle", die die Spalte füllt,
und damit auch keine Zeilengrenzen zu pflegen. Das ist der wesentliche
Unterschied zur Google-Sheets-Umsetzung, in der Muster A und D genau dieses
Problem lösen mussten.

### Muster B – Auswahl gewinnt vor Freitext

```
paare = [($Ort_Beginn, $Ort_Beginn_Text), … ]
teile = [(o.Kuerzel if o else "") or t for o, t in paare]
```

**Statement:**
- `paare` – die sieben Ortsfelder als Paar aus Auswahl (`Ref:Orte`) und Freitext
- `o.Kuerzel if o else ""` – ist eine Auswahl gesetzt, ihren Wert nehmen
- `… or t` – sonst den Freitext

Jeder Stopp ist ein Paar: Auswahlliste für die Stammorte, Freitext für die
Einmalziele. Sind versehentlich beide gefüllt, gewinnt die Auswahl —
stillschweigend. Dieselbe Weiche steckt in `Reiseweg`, `Maps_Link` und in den
`_Sync`-Spalten; dort sorgt sie dafür, dass ein ignorierter Freitext **keine**
Adresszeile anlegt und deshalb auch nicht im Dienstorte-Blatt auftaucht.

**Zu beachten:** `Reiseweg` nimmt aus der Auswahl das **Kürzel**,
`Maps_Link` die **Adresse**. Ein Stammort ohne Adresse fällt in `Maps_Link`
deshalb auf den Freitext zurück, im `Reiseweg` nicht.

### Muster C – Ersatzwert 0 statt Leerwert

```
($KM_Ende or 0) - ($KM_Beginn or 0)
```

**Statement:**
- `$Feld or 0` – leeres Zahlenfeld (`None`) wird zu `0`

Ein nicht ausgefülltes Zahlenfeld ist in Grist `None`, nicht `0`. Ohne die
Weiche bricht die Zeile mit einem Fehler ab, und der Fehler steht dann in der
Spalte, nicht nur in der Zelle. Betrifft alle optionalen Zahlenfelder:
`KM_Beginn`, `KM_Ende`, `Umweg_privat`, `Min_privat_Abzug`,
`Min_Dienststaette`, `Min_Dienstort`.

### Muster D – Untergrenze statt Negativwert

```
max(0, ($KM_Ende or 0) - ($KM_Beginn or 0))
```

**Statement:**
- `max(0, …)` – schneidet negative Ergebnisse auf 0 ab

Ein Zahlendreher im Tachostand oder ein privater Umweg, der größer als die
Gesamtstrecke ist, ergäbe negative Kilometer. Die würden unbemerkt in S1 und
ins Fahrtenbuch wandern und die Summe verfälschen. Abgeschnitten fallen sie als
auffällig niedrige Zahl auf. Dieselbe Überlegung steht hinter der Null-Grenze
in `Tagegeld_Stufe`: ist die Rest-Zeit aufgebraucht, gibt es **keine** Stufe,
nicht die kleinste.

### Muster E – Rang im Kalenderjahr

```
alle = [r for r in Reisen.all if r.Datum and r.Datum.year == $Datum.year]
alle.sort(key=lambda r: (r.Datum, r.id))
return [r.id for r in alle].index($id) + 1
```

**Statement:**
- `Reisen.all` – alle Zeilen der Tabelle, nicht nur die eigene
- Filter auf dasselbe Kalenderjahr
- `sort(key=(Datum, id))` – nach Datum, bei gleichem Datum nach Anlagereihenfolge
- `.index($id) + 1` – die eigene Position in dieser Reihenfolge, ab 1 gezählt

Liefert eine lückenlose Nummer je Kalenderjahr, die sich beim Nachtragen einer
älteren Reise automatisch neu vergibt. Steckt in `Lfd_Nr` (alle Reisen) und in
`Vermerk_Label` (nur Reisen mit Vermerk) — zwei getrennte Zählungen, deshalb
zwei Formeln statt einer.

**Zu beachten:** Die Zählung ist an das **Kalenderjahr** gebunden, nicht an den
Abrechnungszeitraum. Ein Zeitraum über den Jahreswechsel enthält deshalb zwei
Nummernkreise, die beide bei 1 beginnen.

## Tabellen

Je ein eigenes Dokument, in Datenfluss-Reihenfolge:

1. [Einstellungen](einstellungen.md)
2. [Orte](orte.md)
3. [Reisen](reisen.md)
4. [Adressen](adressen.md)
5. [Ausgabe](ausgabe.md)
6. [Einrichtung (setup.py)](setup.md)
7. [Anhang](anhang.md)
