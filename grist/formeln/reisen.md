[← Formeln-Übersicht](README.md)

# Reisen

Eine Zeile je Dienstreise. Die Eingabespalten füllt das Formular, die
Rechenspalten stehen unten einzeln. Wird eine Reise korrigiert, rechnen alle
Rechenspalten sofort neu. Die Zwischenwerte `KM_gesamt`, `Rest_min` und
`Einzelziele` sind in der Tabellenansicht ausgeblendet.

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

Die Uhrzeiten sind Text, so wie sie eingetippt wurden; gelesen werden sie erst
in `Abwesenheit_min`.

## Datum_bis — Reisedatum bis

```python
$Datum_Ende or $Datum
```

Das Enddatum der Reise, ohne Enddatum das Reisedatum. Im Ausdruck erscheint
eine mehrtägige Reise als Spanne (`03.02.2026 - 04.02.2026`).

## Lfd_Nr — Laufende Nummer

```python
if not $Datum:
  return None
alle = [r for r in Reisen.all if r.Datum and r.Datum.year == $Datum.year]
alle.sort(key=lambda r: (r.Datum, r.id))
return [r.id for r in alle].index($id) + 1
```

Fortlaufende Nummer je Kalenderjahr, nach Datum sortiert, bei gleichem Datum
in der Reihenfolge der Erfassung ([Rang im Kalenderjahr](README.md#muster-rang-im-kalenderjahr)).
Ohne Datum gibt es keine Nummer. Wird eine ältere Reise nachgetragen,
verschieben sich die Nummern danach — die Nummer ist eine Position, keine
Belegnummer. Steht auf S1 (Spalte „Reiseweg“) und im Fahrtenbuch (Spalte 1).

## KM_gesamt / KM_dienstlich — Kilometer

```python
KM_gesamt:     max(0, ($KM_Ende or 0) - ($KM_Beginn or 0))
KM_dienstlich: max(0, $KM_gesamt - ($Umweg_privat or 0))
```

Endstand minus Anfangsstand, davon der private Umweg. Leere Felder zählen als
0. Ein negatives Ergebnis, etwa durch einen Zahlendreher, wird 0.
`KM_dienstlich` steht auf S1 (Spalte km) und im Fahrtenbuch (Spalte 9).

## Abwesenheit_min — Abwesenheit (Minuten)

```python
import re
def minuten(s):
  z = re.findall(r"\d+", str(s or ""))
  return int(z[0]) * 60 + int(z[1]) if len(z) >= 2 else None
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

Die Dauer der Abwesenheit, Grundlage des Tagegelds: je zusätzlichem
Kalendertag 1440 Minuten, dazu die Differenz der Uhrzeiten.

- **Uhrzeiten:** Die ersten beiden Zahlen gelten als Stunden und Minuten, die
  Schreibweise ist egal (`7:15`, `7.15`, `07:15 Uhr`). Eine einzelne Zahl
  (`715`) ist mehrdeutig und gilt als fehlend.
- **Fehlende Angaben:** Fehlt eine Uhrzeit oder das Datum, oder liegt das
  Enddatum vor dem Reisedatum, ist das Ergebnis 0. Auf S1 fällt das als
  „Ges.: 0:00“ auf.
- **Über Mitternacht** ohne Enddatum wird ein Tag addiert (22:00 → 06:00 =
  8 h). Für mehrere Nächte ist das Enddatum nötig.

## Rest_min — Rest-Zeit (Minuten)

```python
$Abwesenheit_min - max(0, $Min_privat_Abzug or 0)
                 - max(0, $Min_Dienststaette or 0) - max(0, $Min_Dienstort or 0)
```

Die Abwesenheit abzüglich privatem Zeitabzug und der Aufenthalte an
Dienststätte und Dienstort. Negative Eingaben zählen als 0, damit ein Minus
keine Zeit hinzufügt. Das Ergebnis kann negativ werden; `Tagegeld_Stufe`
vergibt dann keine Stufe.

## Tagegeld_Stufe — Tagegeld-Stufe

```python
if not $Tagegeld_beantragt:
  return ""
if ($Abwesenheit_min or 0) - max(0, $Min_privat_Abzug or 0) < 481:
  return ""
r = $Rest_min
if r <= 0:   return ""
if r < 481:  return "anteilig"
if r < 840:  return ">8h"
if r < 1440: return ">=14h"
return "24h"
```

Drei Prüfungen nacheinander:

1. Tagegeld beantragt? Sonst bleibt die Zelle leer.
2. **Anspruch dem Grunde nach:** Abwesenheit minus privater Abzug mindestens
   481 Minuten (8:01 h). Sonst leer.
3. **Stufe** nach `Rest_min`: 0 oder weniger leer, unter 481 `anteilig`,
   unter 840 `>8h`, unter 1440 `>=14h`, sonst `24h`.

S1 kreuzt die passende Spalte an; `anteilig` erscheint als `(X)` unter „mehr
als 8 Stunden“. Die Staffel als Tabelle steht im [Anhang](anhang.md).

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

Je Freitext-Ziel der Reise eine Zeile aus Kürzel und Text:

```
E26-07: Café Mokka, Bahnhofstr. 7, 12345 Musterstadt
```

Das Kürzel zählt laufend über alle Einzelziele des Kalenderjahres
([Rang im Kalenderjahr](README.md#muster-rang-im-kalenderjahr)). Ein Freitext zählt
auch dann, wenn im selben Ortsfeld eine Auswahl steht
([was eingetragen ist, zählt](README.md#muster-was-eingetragen-ist-zählt)). Zeilenumbrüche
werden zu Kommas, ein Feld nur mit Leerzeichen zählt nicht. Der Text wird
nicht geprüft: Ob die Anschrift vollständig ist, sieht die Person im
Ortsverzeichnis.

Hier entstehen die Kürzel, die `Reiseweg` und Ortsverzeichnis verwenden. Wie
bei `Lfd_Nr` verschiebt eine nachgetragene Reise die späteren Kürzel des
Jahres.

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

Die angefahrenen Orte als Kette, z. B. `WO > KV > E26-07 > WO`: für eine
Auswahl das Kürzel des Stammziels, für einen Freitext das Kürzel aus
`Einzelziele`. Sind beide Felder eines Orts gefüllt, sind es zwei Stopps
([was eingetragen ist, zählt](README.md#muster-was-eingetragen-ist-zählt)); leere Felder
fallen heraus. Steht im Fahrtenbuch (Spalte 6) und in der Prüfliste,
aufgelöst werden die Kürzel im Ortsverzeichnis.

## Maps_Link — Routenlink

```python
import urllib.parse as u
adr = []
for o, t in [($Ort_Beginn, $Ort_Beginn_Text), … ]:
  if o and not o.Adresse:
    return ""
  if o:
    adr.append(o.Adresse)
  t = ", ".join(x.strip() for x in (t or "").splitlines() if x.strip())
  if t:
    adr.append(t)
if len(adr) < 2:
  return ""
link = ("https://www.google.com/maps/dir/?api=1&origin=" + u.quote(adr[0])
        + "&destination=" + u.quote(adr[-1]))
if len(adr) > 2:
  link += "&waypoints=" + u.quote("|".join(adr[1:-1]))
return link
```

Ein Google-Maps-Link über alle Stationen: die erste als Start, die letzte als
Ziel, dazwischen die Zwischenhalte. Für eine Auswahl wird die Adresse des
Stammziels genommen, für einen Freitext der Text selbst. Unter zwei Stationen
gibt es keinen Link.

Fehlt einem angefahrenen Stammziel die Anschrift, bleibt der Link **ganz**
leer: Eine Route ohne diesen Halt sähe vollständig aus und wäre doch zu kurz.
Der Link dient der Prüfung der Strecke und steht nur in der Prüfliste.

## Vermerk_Label — Vermerk-Kennung

```python
if not $Vermerk or not $Datum:
  return ""
mit = [r for r in Reisen.all if r.Vermerk and r.Datum and r.Datum.year == $Datum.year]
mit.sort(key=lambda r: (r.Datum, r.id))
n = [r.id for r in mit].index($id) + 1
return "V%s-%02d" % ($Datum.strftime("%y"), n)
```

Die Kennung `V26-01` für jede Reise mit Vermerk, laufend je Kalenderjahr und
nur über Reisen mit Vermerk gezählt
([Rang im Kalenderjahr](README.md#muster-rang-im-kalenderjahr)). Ohne Vermerk bleibt
die Zelle leer. Steht auf dem Vermerke-Blatt und im Fahrtenbuch (Spalte 15).
