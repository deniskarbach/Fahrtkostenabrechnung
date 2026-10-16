[← Formeln-Übersicht](README.md)

# Reisen

Kerntabelle: eine Zeile je Dienstreise, aus dem Formular. Die Eingabespalten
füllt das Formular, die Rechenspalten stehen unten einzeln.

Anders als in der Google-Sheets-Umsetzung darf eine Reise hier **direkt
korrigiert** werden — es gibt keine getrennte Antwortendatei, auf die die
Tabelle nur lesend zugreift. Alle Rechenspalten ziehen sofort nach.

## Eingabespalten

| Spalte | Beschriftung | Typ |
|---|---|---|
| `Datum` | Reisedatum | Date |
| `Datum_Ende` | Enddatum (nur mehrtägig) | Date |
| `Beginn` / `Ende` | Reisebeginn / Reiseende (HH:MM) | Text |
| `KM_Beginn` / `KM_Ende` | Kilometerstand Beginn / Ende | Int |
| `Umweg_privat` | Privater Umweg (km) | Int |
| `Ort_Beginn`, `Ort_1` … `Ort_5`, `Ort_Ende` | Ort-Auswahl | Ref:Stammziele |
| `Ort_Beginn_Text` … `Ort_Ende_Text` | Ort-Freitext | Text |
| `Tagegeld_beantragt` | Tagegeld beantragen? | Bool |
| `Min_Dienststaette` | Aufenthalt Dienststätte (Minuten) | Int |
| `Min_Dienstort` | Aufenthalt Dienstort (Minuten) | Int |
| `Min_privat_Abzug` | Privater Zeitabzug (Minuten) | Int |
| `Verpflegung` | Unentgeltliche Verpflegung | Choice (Ja/Nein) |
| `OePNV`, `Uebernachtung`, `Nebenkosten` | Kosten (EUR) | Numeric |
| `Mitnahme_Personen` | Mitnahme von Personen (Anzahl) | Int |
| `Vermerk` | Sonstige Informationen | Text |
| `Belege` | Belege | Attachments |

Die **Uhrzeiten sind Text**, nicht Zeitwerte — das Formular liefert sie als
`HH:MM`. Geparst werden sie erst in `Abwesenheit_min`, die dort eingebaute
`minuten()`-Funktion macht die Formel gegen unlesbare Eingaben unempfindlich.

---

## Datum_bis — Reisedatum bis

```python
$Datum_Ende or $Datum
```

**Ergebnis:** Das Enddatum der Reise; bei eintägigen Reisen das Startdatum.
**Rechenweg:** Ist das optionale Feld `Datum_Ende` leer, gilt `Datum`.
**Muster:** Spaltenformel (A).

Wird von `Abwesenheit_min` gebraucht und im Ausdruck für die Datumsspanne
(`03.02.2026 - 04.02.2026`). Ist sie gleich `Datum`, druckt das Widget nur ein
Datum.

---

## Lfd_Nr — Laufende Nummer

```python
if not $Datum:
  return None
alle = [r for r in Reisen.all if r.Datum and r.Datum.year == $Datum.year]
alle.sort(key=lambda r: (r.Datum, r.id))
return [r.id for r in alle].index($id) + 1
```

**Ergebnis:** Fortlaufende Nummer der Reise innerhalb ihres Kalenderjahres.
**Sonderfall:** Zeilen ohne Datum bekommen keine Nummer (`None`).
**Muster:** Rang im Kalenderjahr (E).

Erscheint auf S1 in der Spalte „Reiseweg" (siehe [Ausgabe → S1](ausgabe.md#s1--reisekostenabrechnung))
und in Spalte 1 des Fahrtenbuchs. Wird eine ältere Reise nachgetragen,
vergeben sich alle Nummern des Jahres neu — die Nummer ist also keine
Belegnummer, sondern eine Position.

---

## KM_gesamt / KM_dienstlich — Kilometer

```python
KM_gesamt:     max(0, ($KM_Ende or 0) - ($KM_Beginn or 0))
KM_dienstlich: max(0, $KM_gesamt - ($Umweg_privat or 0))
```

**Statement:**
- `($KM_Ende or 0)` – leeres Tachofeld zählt als 0 statt Fehler
- `max(0, …)` – negative Differenz wird abgeschnitten

**Ergebnis:** Gefahrene Strecke insgesamt bzw. der dienstlich veranlasste
Anteil nach Abzug des privaten Umwegs.
**Rechenweg:** Endstand minus Anfangsstand, davon der private Umweg.
**Sonderfall:** Zahlendreher im Tachostand oder ein Umweg größer als die
Gesamtstrecke ergeben 0, nicht eine negative Zahl.
**Muster:** Ersatzwert 0 (C), Untergrenze (D).

`KM_dienstlich` geht nach S1 (Spalte „km") und ins Fahrtenbuch (Spalte 9).
`KM_gesamt` ist nur ein Zwischenwert und in der Tabellenansicht ausgeblendet.

---

## Abwesenheit_min — Abwesenheit (Minuten)

```python
def minuten(s):
  try:
    h, m = str(s).split(":")
    return int(h) * 60 + int(m)
  except Exception:
    return None
a, b = minuten($Beginn), minuten($Ende)
if a is None or b is None or not $Datum:
  return 0
tage = ($Datum_bis - $Datum).days if $Datum_bis else 0
if tage < 0:
  return 0
total = tage * 1440 + b - a
if total < 0:
  total += 1440
return total
```

**Statement:**
- `minuten(s)` – zerlegt `"07:15"` in Stunden und Minuten und rechnet in Minuten um; alles Unlesbare ergibt `None`
- `if a is None or b is None …` – fehlt eine Uhrzeit oder das Datum, ist die Abwesenheit 0
- `tage = ($Datum_bis - $Datum).days` – volle Tage zwischen Beginn und Ende
- `if tage < 0` – Enddatum vor dem Startdatum: 0 statt einer negativen Dauer
- `total = tage * 1440 + b - a` – ganze Tage plus die Differenz der Uhrzeiten
- `if total < 0: total += 1440` – Reise über Mitternacht ohne Enddatum

**Ergebnis:** Dauer der Abwesenheit in Minuten — Grundlage der Tagegeld-Staffel.
**Rechenweg:** Je angefangenem Zusatztag 1440 Minuten, dazu die Uhrzeitdifferenz.
**Sonderfall:** Unlesbare oder fehlende Uhrzeit ergibt 0, nicht einen Fehler —
der Fehler stünde sonst in der ganzen Spalte und leerte S1.
**Muster:** Untergrenze (D).

Zwei Fälle, die leicht verwechselt werden:

| Eingabe | `tage` | Rechnung | Ergebnis |
|---|---|---|---|
| 01.02., 22:00 → 06:00, **ohne** Enddatum | 0 | −960 → +1440 | 480 (8 h) |
| 01.02.→02.02., 22:00 → 06:00 | 1 | 1440 − 960 | 480 (8 h) |

Beide liefern dasselbe. Das Enddatum ist für eine Nachtfahrt also nicht
zwingend — für eine Reise über mehrere Nächte schon.

---

## Rest_min — Rest-Zeit (Minuten)

```python
$Abwesenheit_min - ($Min_privat_Abzug or 0)
                 - ($Min_Dienststaette or 0) - ($Min_Dienstort or 0)
```

**Ergebnis:** Die Abwesenheit, bereinigt um privaten Zeitabzug und um die
Aufenthalte an Dienststätte und Dienstort.
**Rechenweg:** Von der Abwesenheit werden die drei Minutenfelder abgezogen.
**Sonderfall:** Kann negativ werden, wenn die Aufenthalte zusammen länger sind
als die Abwesenheit; `Tagegeld_Stufe` fängt das ab.
**Muster:** Ersatzwert 0 (C).

Zwischenwert, in der Tabellenansicht ausgeblendet. Er bestimmt die **Stufe**;
über den Anspruch **dem Grunde nach** entscheidet dagegen `Abwesenheit_min`
abzüglich des privaten Abzugs — siehe [Anhang](anhang.md).

---

## Tagegeld_Stufe — Tagegeld-Stufe

```python
if not $Tagegeld_beantragt:
  return ""
if ($Abwesenheit_min or 0) - ($Min_privat_Abzug or 0) < 481:
  return ""
r = $Rest_min
if r <= 0:   return ""
if r < 481:  return "anteilig"
if r < 840:  return ">8h"
if r < 1440: return ">=14h"
return "24h"
```

**Statement:**
- `if not $Tagegeld_beantragt` – ohne Antrag keine Stufe, unabhängig von der Dauer
- `… < 481` – Anspruch dem Grunde nach: bereinigte Abwesenheit mindestens 8:01 h
- `if r <= 0` – Rest-Zeit vollständig aufgebraucht: **keine** Stufe
- die vier Schwellen 481 / 840 / 1440 Minuten

**Ergebnis:** Einer der Werte `anteilig`, `>8h`, `>=14h`, `24h` oder leer.
**Rechenweg:** Zuerst die Anspruchsprüfung über die Abwesenheit, dann die
Einstufung über die Rest-Zeit.
**Sonderfall:** Fressen Dienststätte und Dienstort die Abwesenheit vollständig
auf, ist die Stufe leer, nicht die kleinste.
**Muster:** Ersatzwert 0 (C), Untergrenze (D).

Das Widget setzt aus diesem Wert das Kreuz in eine der vier S1-Spalten:

```js
const kreuz = (stufe, s) => stufe === s ? "X" : "";
```

Die Staffel als Kurzregel steht im [Anhang](anhang.md).

---

## Einzelziele — Einzelziele (Ortsverzeichnis)

```python
def frei(r):
  return [", ".join(x.strip() for x in (t or "").splitlines() if x.strip())
          for t in [r.Ort_Beginn_Text, … , r.Ort_Ende_Text]]
if not $Datum:
  return ""
vorher = [r for r in Reisen.all if r.Datum and r.Datum.year == $Datum.year
          and (r.Datum, r.id) < ($Datum, $id)]
n = sum(1 for r in vorher for t in frei(r) if t)
zeilen = []
for t in frei(rec):
  if t:
    n += 1
    zeilen.append("E%s-%02d: %s" % ($Datum.strftime("%y"), n, t))
return "\n".join(zeilen)
```

**Statement:**
- `frei(r)` – die Freitexte einer Reise, auch neben einer Auswahl (Muster B);
  Zeilenumbrüche werden zu `, `, Leerzeilen fallen weg
- `vorher` – die Reisen desselben Kalenderjahres, die nach Datum (bei gleichem
  Datum nach Zeilen-Id) **vor** dieser liegen; ihre Freitext-Ziele werden gezählt
- `"E%s-%02d: %s"` – je Ziel eine Zeile aus Kürzel (`E`, zweistelliges Jahr,
  laufende Nummer) und Freitext

**Ergebnis:**
```
E26-07: Café Mokka, Bahnhofstr. 7, 12345 Musterstadt
E26-08: Hof Lindenau
```
**Sonderfall:** Ohne Freitext-Ziel bleibt die Zelle leer. Ein Feld nur mit
Leerzeichen zählt nicht.
**Muster:** Was eingetragen ist, zählt (B), Rang im Kalenderjahr (E).

Die einzige Stelle, an der die Kürzel entstehen. `Reiseweg` setzt sie in die
Wegkette, das Ortsverzeichnis druckt sie mit Datum und Freitext. Aufbau wie
`Vermerk_Label` (`V26-01`): das Kürzel ist für sich allein eindeutig.

**Zu beachten:** Eine nachträglich erfasste oder umdatierte Reise verschiebt
die Kürzel aller späteren Einzelziele des Jahres — wie bei `Lfd_Nr` und
`Vermerk_Label`. Ein bereits gedruckter Ausdruck passt dann nicht mehr zur
Tabelle.

Der Freitext wird **nicht** geprüft oder zerlegt. Er steht im Ortsverzeichnis
so, wie er erfasst wurde; ob die Anschrift vollständig ist, kontrolliert die
Person beim Unterschreiben. Korrigiert wird im Freitext der Reise.

Ausgeblendet in der Tabellenansicht (Hilfsspalte).

---

## Reiseweg

```python
e = iter(z.split(":")[0] for z in $Einzelziele.splitlines())
teile = []
for o, t in [($Ort_Beginn, $Ort_Beginn_Text), … , ($Ort_Ende, $Ort_Ende_Text)]:
  if o:
    teile.append(o.Kuerzel)
  if (t or "").strip():
    teile.append(next(e, "?"))
return " > ".join(x for x in teile if x)
```

**Statement:**
- `e` – die Kürzel aus `Einzelziele` (`E26-07`, `E26-08` …) in Reihenfolge der Ortsfelder
- `if o` – aus der Auswahl wird das Kürzel genommen
- `next(e, "?")` – bei ausgefülltem Freitext das nächste Kürzel, auch wenn
  daneben eine Auswahl steht (dann zwei Stopps)
- `if x` – nicht ausgefüllte Stopps fallen heraus, statt Lücken zu erzeugen
- `" > ".join(…)` – die verbliebenen Stopps zur Wegkette verbinden

**Ergebnis:** `WO > KV > E26-07 > E26-08 > WO`
**Sonderfall:** Sind alle sieben Felder leer, bleibt die Zelle leer.
**Muster:** Was eingetragen ist, zählt (B).

Erscheint in Spalte 6 des Fahrtenbuchs und in der Prüfliste. Die Legende zu
Kürzeln und Nummern ist das Ortsverzeichnis. Die Zelle im Fahrtenbuch fasst
etwa zwei Zeilen — der volle Freitext mehrerer Ziele passte nicht hinein,
deshalb nur das Kürzel.

---

## Maps_Link — Routenlink

```python
import urllib.parse as u
adr = []
for o, t in [($Ort_Beginn, $Ort_Beginn_Text), … ]:
  if o and not o.Adresse:
    return ""                # Stammziel ohne Anschrift -> lieber kein Link
  if o:
    adr.append(o.Adresse)
  t = ", ".join(x.strip() for x in (t or "").splitlines() if x.strip())
  if t:
    adr.append(t)            # leere Felder fallen still heraus
if len(adr) < 2:
  return ""
link = ("https://www.google.com/maps/dir/?api=1&origin=" + u.quote(adr[0])
        + "&destination=" + u.quote(adr[-1]))
if len(adr) > 2:
  link += "&waypoints=" + u.quote("|".join(adr[1:-1]))
return link
```

**Statement:**
- `if o and not o.Adresse: return ""` – ein Stammziel ohne Anschrift macht
  die ganze Route unbrauchbar, nicht nur sich selbst
- `if o` – aus der Auswahl die **Adresse** (im `Reiseweg` das Kürzel)
- `t = ", ".join(…)` – Freitext einzeilig, wie in `Einzelziele`
- `if t` – der Freitext selbst als weiterer Stopp; ein leeres Feld ist keiner
- `if len(adr) < 2` – unter zwei Stationen gibt es keine Route
- `u.quote(…)` – Adressen für die URL kodieren (Leerzeichen, Umlaute, Komma)
- `adr[1:-1]` – alles zwischen Start und Ziel wird zu `waypoints`, mit `|` getrennt

**Ergebnis:** Klickbarer Google-Maps-Link über alle Stationen der Reise.
**Rechenweg:** Erste Adresse als `origin`, letzte als `destination`, alles
dazwischen als `waypoints`.
**Sonderfall:** Fehlt einem angefahrenen Stammziel die Anschrift, bleibt die
Zelle **ganz** leer. Früher fiel nur dieser eine Stopp aus dem Link — die Route
sah vollständig aus, war aber zu kurz, und genau das fiel niemandem auf. Deshalb
die Adressen von `WO` und `KV` nachtragen; `setup.py` nennt beim Lauf jeden
Ort ohne Anschrift beim Kürzel.
**Muster:** Was eingetragen ist, zählt (B).

Google Maps liest den Freitext mitsamt Bezeichnung („Café Mokka, Bahnhofstr. 7,
12345 Musterstadt"). Folgt er dem Schema nicht, ist die Route eben ungenau.

Dient der Prüfung der gefahrenen Strecke, nicht der Abrechnung — der Link wird
nicht gedruckt.

---

## Vermerk_Label — Vermerk-Kennung

```python
if not $Vermerk or not $Datum:
  return ""
mit = [r for r in Reisen.all if r.Vermerk and r.Datum and r.Datum.year == $Datum.year]
mit.sort(key=lambda r: (r.Datum, r.id))
n = [r.id for r in mit].index($id) + 1
return "V%s-%02d" % ($Datum.strftime("%y"), n)
```

**Statement:**
- `if not $Vermerk` – ohne Text keine Kennung
- Filter auf Reisen **mit** Vermerk im selben Kalenderjahr
- `"V%s-%02d"` – `V`, zweistelliges Jahr, Bindestrich, zweistellige Nummer

**Ergebnis:** `V26-01` — die Kennung, unter der der Vermerk auf dem
Vermerke-Blatt und in Spalte 15 des Fahrtenbuchs auftaucht.
**Sonderfall:** Reisen ohne Vermerk bleiben leer und werden nicht mitgezählt.
**Muster:** Rang im Kalenderjahr (E).

Eigene Zählung, unabhängig von `Lfd_Nr`: die dritte Reise des Jahres kann den
ersten Vermerk tragen.
