[← Formeln-Übersicht](README.md)

# Stammziele

Die wiederkehrenden Reiseziele mit Kürzel und Adresse. Die Liste ist zugleich
die Auswahl im Formular, die Quelle für den Routenlink und die Legende im
Ortsverzeichnis.

| Spalte | Beschriftung | Typ | Inhalt |
|---|---|---|---|
| `Kuerzel` | Kürzel | Text | steht im Reiseweg (`WO > KV > KITA > WO`) |
| `Name` | Name der Einrichtung | Text | steht im Ortsverzeichnis |
| `Strasse`, `PLZ`, `Ort` | Straße und Hausnummer, PLZ, Ort | Text | ergeben `Adresse` |
| `Adresse` | Vollständige Adresse | Text | **Formel** |

## Adresse

```python
", ".join(x for x in [$Strasse, (($PLZ or "") + " " + ($Ort or "")).strip()] if x)
```

`Straße, PLZ Ort`, z. B. `Lindenweg 3, 00000 Musterstadt`. Leere Teile fallen
samt Komma weg. Ist die Adresse leer, bekommt keine Reise über dieses Ziel
einen Routenlink.

## WO und KV

Zwei Zeilen sind immer da: `WO` (Wohnung) und `KV` (Dienststelle). Sie werden
ohne Adresse angelegt; die Adresse wird von Hand nachgetragen und danach nie
überschrieben.

Die eigene Anschrift steht damit an zwei Stellen: in
[Einstellungen](einstellungen.md) für den Kopf des Ausdrucks, hier in `WO` für
Reiseweg und Routenlink. Bei einem Umzug ändern sich beide. Eine Formel, die
`WO` aus den Einstellungen füllt, wurde verworfen: Die Felder sahen
bearbeitbar aus und blieben wirkungslos.

Ziele, die nur einmal vorkommen, gehören nicht hierher, sondern in den
Freitext des Formulars ([Reisen → Einzelziele](reisen.md#einzelziele-einzelziele-ortsverzeichnis)).
