[← Formeln](README.md)

# Stammziele

## Zweck

Die Ansicht führt wiederkehrende Reiseziele mit Kürzel und Adresse; die Adresse wird aus Straße, PLZ und Ort zusammengesetzt.
Sie gibt es, damit ein Ziel im Formular nur gewählt werden muss und für Reiseweg, Routenlink und Ortsverzeichnis einheitlich bereitsteht.
Sie umfasst die Zeilen `WO` und `KV` sowie alle weiteren eigenen Ziele.

## Funktionsweise

- Jede Zeile ist ein Ziel; das Kürzel steht im Reiseweg (`WO > KV > KITA > WO`).
- Die Liste ist die Auswahl im Formular, die Quelle des Routenlinks und die
  Legende im Ortsverzeichnis.
- `WO` (Wohnung) und `KV` (Dienststelle) sind immer vorhanden; ihre Adresse
  wird einmal nachgetragen.
- Die eigene Anschrift steht zusätzlich in [Einstellungen](einstellungen.md);
  bei einem Umzug beide ändern.
- Einmalige Ziele gehören nicht hierher, sondern in den Freitext
  ([Reisen → Einzelziele](reisen.md#einzelziele-einzelziele-ortsverzeichnis)).

| Spalte | Typ | Inhalt |
|---|---|---|
| `Kuerzel` | Text | Kürzel im Reiseweg |
| `Name` | Text | Name der Einrichtung, im Ortsverzeichnis |
| `Strasse`, `PLZ`, `Ort` | Text | Eingabe, ergibt `Adresse` |
| `Adresse` | Text | **Formel** |

## Formeln

### Adresse

```python
", ".join(x for x in [$Strasse, (($PLZ or "") + " " + ($Ort or "")).strip()] if x)
```

- **Ergebnis:** `Straße, PLZ Ort`, z. B. `Lindenweg 3, 00000 Musterstadt`.
- **Sonderfall:** Leere Teile fallen samt Komma weg. Ohne Adresse erhält keine
  Reise über dieses Ziel einen Routenlink.
