[← Formeln-Übersicht](README.md)

# Einzelziele

Die Einzelziele. Wird **nie von Hand angelegt oder gepflegt** und hat keine
eigene Seite: sobald ein Ortsfeld im Formular als Freitext ausgefüllt ist und
keine Auswahl daneben steht, legt die zugehörige `_Sync`-Spalte in
[Reisen](reisen.md) hier eine Zeile an. Alles Weitere sind Formeln, die den
Freitext der Reise lesen und zerlegen. Korrigiert wird im Freitext der Reise
(Seite `Reisekorrektur`).

| Spalte | Beschriftung | Typ | Herkunft |
|---|---|---|---|
| `Reise` | Reise | Ref:Reisen | Schlüssel, von der Sync-Spalte gesetzt |
| `Slot` | Ort-Feld | Text | Schlüssel, z. B. `Ort_1` |
| `Label` | Freitext (wie erfasst) | Text | **Formel**, liest den Freitext der Reise |
| `Zerlegt` | Freitext zerlegt | Any | **Formel**, Hilfsspalte |
| `Bezeichnung` | Bezeichnung | Text | **Formel** |
| `Strasse` | Straße und Hausnummer | Text | **Formel** |
| `PLZ` | PLZ | Text | **Formel** |
| `Ort` | Ort | Text | **Formel** |
| `Adresse` | Vollständige Adresse | Text | **Formel** |
| `Datum` | Reisedatum | Date | **Formel** |
| `Anschrift_fehlt` | Anschrift fehlt | Bool | **Formel**, speist ⚠️ in der Reisekorrektur |

## Label

```python
r = $Reise
if not r or getattr(r, $Slot):
  return ""
return getattr(r, $Slot + "_Text") or ""
```

**Ergebnis:** Der Freitext des Ortsfelds, zu dem die Zeile gehört.
**Sonderfall:** Hat die Reise dort inzwischen eine Auswahl oder ist der
Freitext geleert, ist `Label` leer — die Zeile ist verwaist und erscheint in
keiner Ausgabe (Ortsverzeichnis und Prüfliste filtern auf `Label`).
**Warum Formel:** Eine Zuweisung aus der Sync-Spalte (`zeile.Label = …`)
lässt Grist nicht zu (AttributeError). Den Freitext in den Suchschlüssel zu
nehmen ginge, ließe aber bei jeder Korrektur die alte Zeile stehen.

## Zerlegt

```python
import re
teile = [t.strip() for t in re.split(r"[,\n]", $Label or "") if t.strip()]
m = re.fullmatch(r"(\d{5})\s+(\S.*)", teile[-1]) if len(teile) >= 2 else None
if not m:
  return [$Label or "", "", "", ""]
return [", ".join(teile[:-2]), teile[-2], m.group(1), m.group(2)]
```

Schema: **Bezeichnung, Straße Hausnummer, PLZ Ort** — Kommas oder
Zeilenumbrüche trennen. Entscheidend ist die **Position**, nicht die Zahl:

- das letzte Stück muss mit fünf Ziffern beginnen, danach der Ort
- das Stück davor ist die Straße, gleich welche Zahlen darin stehen
- alles davor ist die Bezeichnung (darf selbst Kommas enthalten)

| Freitext | Bezeichnung | Straße | PLZ | Ort |
|---|---|---|---|---|
| Café Mokka, Bahnhofstr. 7, 12345 Musterstadt | Café Mokka | Bahnhofstr. 7 | 12345 | Musterstadt |
| Kita Sonnenschein, Haus B, Lindenweg 3, 12345 Musterstadt | Kita Sonnenschein, Haus B | Lindenweg 3 | 12345 | Musterstadt |
| Industriestr. 10234, 12345 Musterstadt | – | Industriestr. 10234 | 12345 | Musterstadt |
| Café Mokka Musterstadt | Café Mokka Musterstadt | – | – | – (unvollständig) |

`Bezeichnung`, `Strasse`, `PLZ`, `Ort` greifen je ein Element ab
(`$Zerlegt[0]` … `$Zerlegt[3]`).
**Sonderfall:** Kein `$` als Zeilenende im Muster — Grist liest `$…` als
Spaltenbezug; daher `re.fullmatch`.
**Geprüft:** `setup.py --selbsttest` rechnet die Beispiele nach.

## Adresse

```python
", ".join(x for x in [$Strasse, ($PLZ + " " + $Ort).strip()] if x)
```

**Ergebnis:** `Bahnhofstr. 7, 12345 Musterstadt`
**Muster:** identisch zu [Stammziele → Adresse](stammziele.md#adresse).

## Anschrift_fehlt

```python
bool($Label) and not ($Strasse and $PLZ and $Ort)
```

Wahr, wenn ein Freitext da ist, aber nicht dem Schema folgt. Die Reisen-Spalten
`Anschrift_Warnung` (⚠️ in der Liste der Reisekorrektur) und
`Anschrift_Hinweis` (Text in der Karte, nennt Ortsfeld und Freitext) lesen sie
über die Sync-Spalten.

## Datum

```python
$Reise.Datum
```

**Ergebnis:** Das Datum der Fahrt, zu der dieses Einzelziel gehört. Es filtert
die Zeile auf den Abrechnungszeitraum und erscheint im Ortsverzeichnis in der
Spalte *Kürzel / Datum*.

## Eine Zeile je Fahrt

Bewusst **keine** Zusammenführung gleicher Texte. Dasselbe Ziel auf zwei
Fahrten ergibt zwei Zeilen, denn es sind zwei Vorgänge. Der Schlüssel
`Reise` + `Slot` ist immer eindeutig.

## Aufräumen

`lookupOrAddDerived` legt Zeilen an, räumt aber nie ab. Verwaiste Zeilen sind
dank leerem `Label` in keiner Ausgabe sichtbar; `setup.py` entfernt sie
zusätzlich (`einzelziele_aufraeumen`), wenn die Reise gelöscht, der Freitext
geleert oder die Auswahl gesetzt wurde. In Kopien der Vorlage bleiben sie
unsichtbar stehen — das stört nicht.
