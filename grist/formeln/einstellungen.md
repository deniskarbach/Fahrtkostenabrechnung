[← Formeln](README.md)

# Einstellungen

## Zweck

Hier stehen die eigenen Stammdaten, genau eine Zeile.
Die Ansicht gibt es, damit persönliche Daten an einer einzigen Stelle liegen und jeder Ausdruck daraus seinen Kopf bekommt.
Sie umfasst Name, Anschriften und die S2-Angaben.

## Funktionsweise

- Die Zeile liefert den Kopf jedes Ausdrucks: `Name Vorname, Organisationseinheit`
  und Anschriften als `Straße, PLZ Ort`. Leere Felder fallen samt Trennzeichen
  weg.
- Leere S2-Felder bleiben als Linie zum Ausfüllen von Hand.
- `Korrektur_Jahr` und `Korrektur_Monat` gehören zur Seite
  [Reisekorrektur](reisekorrektur.md).

| Spalte | Typ | Wofür |
|---|---|---|
| `Vorname`, `Name`, `Organisationseinheit` | Text | Kopf: Antragsteller/in |
| `Wohnort_Strasse`, `_PLZ`, `_Ort` | Text | Kopf: Wohnort |
| `Dienstort_Strasse`, `_PLZ`, `_Ort` | Text | Kopf: Dienstort |
| `Abteilung`, `Buchungsstelle`, `Behoerde_Ort`, `Behoerde` | Text | S2 |

## Formeln

Keine.
