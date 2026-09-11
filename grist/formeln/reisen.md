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
| `Tacho_Fotos` | Tachofotos (Beginn und Ende) | Attachments |
| `Umweg_privat` | Privater Umweg (km) | Int |
| `Ort_Beginn`, `Ort_1` … `Ort_5`, `Ort_Ende` | Ort-Auswahl | Ref:Orte |
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

Erscheint auf S1 vor dem Reiseweg (`Nr. 3 – WO > KV > WO`) und in Spalte 1 des
Fahrtenbuchs. Wird eine ältere Reise nachgetragen, vergeben sich alle Nummern
des Jahres neu — die Nummer ist also keine Belegnummer, sondern eine Position.

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

## Reiseweg

```python
paare = [($Ort_Beginn, $Ort_Beginn_Text), … , ($Ort_Ende, $Ort_Ende_Text)]
teile = [(o.Kuerzel if o else "") or t for o, t in paare]
return " > ".join(x for x in teile if x)
```

**Statement:**
- `paare` – die sieben Ortsfelder als Paar aus Auswahl und Freitext
- `(o.Kuerzel if o else "") or t` – Auswahl gewinnt, sonst Freitext
- `if x` – nicht ausgefüllte Stopps fallen heraus, statt Lücken zu erzeugen
- `" > ".join(…)` – die verbliebenen Stopps zur Wegkette verbinden

**Ergebnis:** `WO > KV > Beispieldorf > WO`
**Sonderfall:** Sind alle sieben Felder leer, bleibt die Zelle leer.
**Muster:** Auswahl gewinnt (B).

Erscheint auf S1 (hinter der laufenden Nummer) und in Spalte 6 des
Fahrtenbuchs. Aus der Auswahl wird das **Kürzel** genommen — die Legende dazu
ist das Dienstorte-Blatt.

---

## Maps_Link — Routenlink

```python
import urllib.parse as u
paare = [($Ort_Beginn, $Ort_Beginn_Text), … , ($Ort_Ende, $Ort_Ende_Text)]
adr = [x for x in [(o.Adresse if o else "") or t for o, t in paare] if x]
if len(adr) < 2:
  return ""
link = ("https://www.google.com/maps/dir/?api=1&origin=" + u.quote(adr[0])
        + "&destination=" + u.quote(adr[-1]))
if len(adr) > 2:
  link += "&waypoints=" + u.quote("|".join(adr[1:-1]))
return link
```

**Statement:**
- `(o.Adresse if o else "") or t` – wie `Reiseweg`, aber mit der **Adresse** statt dem Kürzel
- `if len(adr) < 2` – unter zwei Stationen gibt es keine Route
- `u.quote(…)` – Adressen für die URL kodieren (Leerzeichen, Umlaute, Komma)
- `adr[1:-1]` – alles zwischen Start und Ziel wird zu `waypoints`, mit `|` getrennt

**Ergebnis:** Klickbarer Google-Maps-Link über alle Stationen der Reise.
**Rechenweg:** Erste Adresse als `origin`, letzte als `destination`, alles
dazwischen als `waypoints`.
**Sonderfall:** Ein Stammort **ohne** eingetragene Adresse fällt auf den
Freitext zurück und, fehlt auch der, ganz heraus. Deshalb die Adressen von `WO`
und `KV` nachtragen.
**Muster:** Auswahl gewinnt (B).

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

---

## Ort_*_Sync — Adressen-Sync

Sieben unsichtbare Formelspalten, eine je Ortsfeld. Sie legen die Zeilen in
[Adressen](adressen.md) an. Beispiel `Ort_Beginn_Sync`:

```python
if $Ort_Beginn or not $Ort_Beginn_Text:
  return None
rec = Adressen.lookupOrAddDerived(Reise=$id, Slot="Ort_Beginn")
rec.Label = $Ort_Beginn_Text
return rec
```

**Statement:**
- `if $Ort_Beginn` – ist die Auswahl gesetzt, entsteht **keine** Adresszeile
- `or not …_Text` – ohne Freitext ebenfalls nicht
- `lookupOrAddDerived(Reise=$id, Slot=…)` – sucht die Zeile zu diesem Paar aus Reise und Ortsfeld und legt sie an, falls es sie nicht gibt
- `rec.Label = …` – der Freitext wird **nach** dem Nachschlagen zugewiesen

**Ergebnis:** Ein Verweis auf die zugehörige Adresszeile.
**Sonderfall:** Gewinnt die Auswahl (Muster B), entsteht keine Zeile — sonst
stünde der ignorierte Freitext trotzdem im Dienstorte-Blatt.
**Muster:** Auswahl gewinnt (B).

**Zu beachten:**

- Der Schlüssel ist **Reise + Ortsfeld**, beides zusammen ist eindeutig. Damit
  bekommt jede Fahrt ihre eigene Zeile; dasselbe Ziel auf zwei Fahrten ergibt
  zwei Zeilen, denn es sind zwei Vorgänge.
- `Label` steht bewusst **nicht** im Schlüssel: der Schlüssel soll die Zeile
  identifizieren, nicht ihren Inhalt tragen. Eine spätere Korrektur des
  Freitextes zieht so oder so nach — Grist leitet die Zeile bei jeder
  Neuberechnung neu ab (nachgemessen in
  [`test_lookuporadd.py`](../test_lookuporadd.py), Test 3).
- `lookupOrAddDerived` legt Zeilen an, räumt aber nie ab. Wird eine Reise
  gelöscht, der Freitext geleert oder nachträglich eine Auswahl gesetzt, bleibt
  die Adresszeile stehen. `setup.py` entfernt sie bei jedem Lauf
  (`adressen_aufraeumen`).

Die sieben Spalten sind in der Tabellenansicht ausgeblendet — sie haben keinen
eigenen Aussagewert. Im Editor über *Hidden columns* jederzeit wieder
einblendbar.
