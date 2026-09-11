[← Formeln-Übersicht](README.md)

# Adressen

Die Einmalziele. Wird **nie von Hand angelegt**: sobald ein Ortsfeld im
Formular als Freitext ausgefüllt ist und keine Auswahl daneben steht, legt die
zugehörige `_Sync`-Spalte in [Reisen](reisen.md) hier eine Zeile an.

Von Hand ergänzt werden nur Straße, PLZ und Ort — der Sync-Mechanismus fasst
diese drei Felder nie an.

| Spalte | Beschriftung | Typ | Herkunft |
|---|---|---|---|
| `Reise` | Reise | Ref:Reisen | Schlüssel, von der Sync-Spalte gesetzt |
| `Slot` | Ort-Feld | Text | Schlüssel, z. B. `Ort_1` |
| `Label` | Freitext (wie erfasst) | Text | von der Sync-Spalte gesetzt |
| `Strasse` | Straße und Hausnummer | Text | **von Hand nachtragen** |
| `PLZ` | PLZ | Text | **von Hand nachtragen** |
| `Ort` | Ort | Text | **von Hand nachtragen** |
| `Adresse` | Vollständige Adresse | Text | **Formel** |
| `Datum` | Reisedatum | Date | **Formel** |

Aufbau bewusst analog zu [Orte](orte.md): gleiche Spalten `Strasse`/`PLZ`/`Ort`,
gleiche `Adresse`-Formel. Die Abrechnungsstelle trägt in beiden Tabellen
dasselbe ein, an derselben Stelle.

## Adresse

```python
", ".join(x for x in [$Strasse, ($PLZ + " " + $Ort).strip()] if x)
```

**Ergebnis:** `Dorfstr. 2, 00000 Beispieldorf`
**Sonderfall:** Solange nichts nachgetragen ist, bleibt die Zelle leer — auf
dem Dienstorte-Blatt steht dann der Name ohne Adresse.
**Muster:** identisch zu [Orte → Adresse](orte.md#adresse).

## Datum

```python
$Reise.Datum
```

**Statement:**
- `$Reise` – die Referenz auf die Reise, die diese Zeile ausgelöst hat
- `.Datum` – deren Reisedatum, durchgereicht

**Ergebnis:** Das Datum der Fahrt, zu der dieses Einmalziel gehört.
**Rechenweg:** Direkter Durchgriff über die Referenz, kein Nachschlagen.
**Sonderfall:** Ist die Reise gelöscht, liefert der Zugriff keinen Wert und die
Zeile fällt aus dem Zeitraumfilter — sie wird beim nächsten `setup.py`-Lauf
entfernt.
**Muster:** Spaltenformel (A).

Das Datum hat zwei Aufgaben: es filtert die Zeile auf den Abrechnungszeitraum,
und es erscheint auf dem Dienstorte-Blatt in der Spalte *Kürzel / Datum* — dort
weist es den Eintrag seiner Fahrt zu.

## Eine Zeile je Fahrt

Bewusst **keine** Zusammenführung gleicher Texte. Dasselbe Ziel auf zwei
Fahrten ergibt zwei Zeilen, denn es sind zwei Vorgänge; jeder wird einzeln
geprüft und mit Datum ausgewiesen. Der Schlüssel `Reise` + `Slot` ist immer
eindeutig, ein Treffer auf eine fremde Zeile also ausgeschlossen.

## Aufräumen

`lookupOrAddDerived` legt Zeilen an, räumt aber nie ab. Verwaist eine Zeile,
bleibt sie ohne Zutun für immer stehen. `setup.py` entfernt bei jedem Lauf
(`adressen_aufraeumen`) alle Zeilen, deren

- Reise gelöscht wurde,
- Freitext geleert wurde, oder
- Auswahl nachträglich gesetzt wurde (dann gewinnt sie, Muster B).

> **Zu beachten:** Eine bereits nachgetragene Anschrift geht dabei mit
> verloren. Wird der Freitext einer Fahrt geändert, bleibt die Zeile bestehen
> und nur `Label` zieht nach — die Anschrift bleibt erhalten.
