[← Formeln-Übersicht](README.md)

# Orte

Stammdaten der wiederkehrenden Reiseziele. Eine Formel, sonst Eingabetabelle.
Diese Liste ist zugleich die Auswahlliste im Formular, die Quelle für den
Routenlink und die Legende auf dem Dienstorte-Blatt.

| Spalte | Beschriftung | Typ | Inhalt |
|---|---|---|---|
| `Kuerzel` | Kürzel | Text | erscheint im `Reiseweg` (`WO > KV > KITA > WO`) |
| `Name` | Name der Einrichtung | Text | erscheint auf dem Dienstorte-Blatt |
| `Strasse` | Straße und Hausnummer | Text | speist `Adresse` |
| `PLZ` | PLZ | Text | " |
| `Ort` | Ort | Text | " |
| `Adresse` | Vollständige Adresse | Text | **Formel**, siehe unten |

## Adresse

```python
", ".join(x for x in [$Strasse, ($PLZ + " " + $Ort).strip()] if x)
```

**Statement:**
- `($PLZ + " " + $Ort)` – PLZ und Ort zu einem Block verbinden
- `.strip()` – fehlt eines von beiden, bleibt kein einzelnes Leerzeichen übrig
- `if x` – leere Teile fallen heraus, statt einen doppelten Trenner zu erzeugen
- `", ".join(…)` – die verbliebenen Teile mit Komma verbinden

**Ergebnis:** `Lindenweg 3, 00000 Musterstadt` — die Adresse, wie sie in
`Maps_Link` und auf dem Dienstorte-Blatt erscheint.
**Sonderfall:** Ist nur die Straße gefüllt, steht auch nur sie da; sind alle
drei leer, bleibt die Zelle leer und der Ort fällt in `Maps_Link` auf den
Freitext zurück (Muster B).

Dieselbe Formel steht in [Adressen](adressen.md) — beide Tabellen sind bewusst
gleich aufgebaut, damit die Abrechnungsstelle nicht zwei Schemata im Kopf haben
muss.

## Die Pflichtzeilen WO und KV

`setup.py` legt zwei Zeilen zwingend an:

| Kürzel | Name | Adresse |
|---|---|---|
| `WO` | Wohnung | **wird nicht gesetzt** — von Hand nachtragen |
| `KV` | Dienststelle | **wird nicht gesetzt** — von Hand nachtragen |

`Reiseweg` und `Maps_Link` brauchen sie für fast jede Fahrt. Angelegt werden
nur Kürzel und Name; eine vorhandene Zeile bleibt unangetastet, eine
eingetragene Adresse wird nie überschrieben.

> **Doppelte Pflegestelle:** Die eigene Anschrift steht in
> [Einstellungen](einstellungen.md) (für die Kopfzeile) **und** hier in der
> Zeile `WO` (für Reiseweg und Routenlink). Ein früherer Versuch, `WO`/`KV`
> per Formel aus `Einstellungen` zu füllen, wurde zurückgebaut: er erzeugte
> Spalten, die bearbeitbar aussahen, aber wirkungslos blieben. Die Dopplung
> ist die verständlichere Lösung — bei einem Umzug ist die Adresse an zwei
> Stellen zu ändern.

## Was nicht hierher gehört

Ein Ziel, das nur einmal vorkommt. Dafür ist das Freitextfeld im Formular da;
es legt automatisch eine Zeile in [Adressen](adressen.md) an. Einmalorte sind
der Normalfall, nicht die Ausnahme — eine reine Auswahlliste würde daran
scheitern.
