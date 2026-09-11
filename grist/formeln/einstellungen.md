[← Formeln-Übersicht](README.md)

# Einstellungen

Genau eine Zeile, im Editor als Karte dargestellt. Keine Formeln — reine
Eingabetabelle. Sie speist die Kopfzeile jedes Ausdrucks und bestimmt über den
Abrechnungszeitraum, welche Reisen ausgegeben werden.

Dies ist die **einzige** Stelle, an der persönliche Daten erfasst werden.

| Spalte | Beschriftung | Typ | Wofür |
|---|---|---|---|
| `Vorname` | Vorname | Text | Kopfzeile, zusammen mit `Name` und `Organisationseinheit` |
| `Name` | Name | Text | " |
| `Organisationseinheit` | Organisationseinheit | Text | " |
| `Wohnort_Strasse` | Wohnort – Straße und Nr. | Text | Kopffeld „Wohnort" |
| `Wohnort_PLZ` | Wohnort – PLZ | Text | " |
| `Wohnort_Ort` | Wohnort – Ort | Text | " |
| `Dienstort_Strasse` | Dienstort – Straße und Nr. | Text | Kopffeld „Dienstort" |
| `Dienstort_PLZ` | Dienstort – PLZ | Text | " |
| `Dienstort_Ort` | Dienstort – Ort | Text | " |
| `Zeitraum_von` | Abrechnungszeitraum von | Date | Filter aller Ausgabeblätter |
| `Zeitraum_bis` | Abrechnungszeitraum bis | Date | " |

## Kopfzeile des Ausdrucks

Die Zusammensetzung passiert nicht in einer Formelspalte, sondern im
Ausgabe-Widget:

```js
antragsteller: [[e.Name, e.Vorname].filter(Boolean).join(" "),
                e.Organisationseinheit].filter(Boolean).join(", ")
```

**Statement:**
- `[e.Name, e.Vorname]` – Nachname zuerst, dann Vorname
- `.filter(Boolean)` – leere Felder fallen heraus, statt doppelte Trenner zu erzeugen
- `.join(" ")` / `.join(", ")` – Name mit Leerzeichen, Organisationseinheit mit Komma

**Ergebnis:** `Musterfrau Erika, Referat 42`
**Sonderfall:** Fehlt die Organisationseinheit, endet die Zeile nach dem Namen —
ohne hängendes Komma.

Wohn- und Dienstanschrift werden nach demselben Schema gesetzt:

```js
const anschrift = (strasse, plz, ort) =>
  [strasse, [plz, ort].filter(Boolean).join(" ")].filter(Boolean).join(", ");
```

**Ergebnis:** `Beispielweg 7, 00000 Musterstadt`
**Sonderfall:** Fehlt die PLZ, steht nur der Ort; fehlt die Straße, entfällt
auch das Komma.

## Abrechnungszeitraum

`Zeitraum_von` und `Zeitraum_bis` sind die einzigen Felder, die **pro
Abrechnung** angefasst werden. Sie stehen deshalb zusätzlich als Karte oben auf
der Seite `Ausdruck` — dort, wo gedruckt wird.

Die Filterung selbst steht im Widget:

```js
const imZeitraum = d => d != null
  && (von == null || d >= von) && (bis == null || d <= bis);
```

**Statement:**
- `d != null` – Zeilen ohne Datum fallen immer heraus
- `von == null || …` – ein nicht gesetztes Zeitraumende begrenzt nicht

**Ergebnis:** Wahr, wenn das Datum im Zeitraum liegt.
**Sonderfall:** Eine offene Grenze begrenzt nicht. Ist der Zeitraum gar nicht
gesetzt, erscheinen **alle** Reisen — vor dem Drucken also prüfen, dass beide
Felder gefüllt sind.

> **Mehrtägige Reisen:** Maßgeblich ist der **Reisebeginn** (`Datum`), nicht das
> Ende. Eine Reise, die vor `Zeitraum_von` beginnt und hineinreicht, wurde mit
> der früheren Abrechnung bereits erledigt; sie erneut auszugeben hieße, sie ein
> zweites Mal abzurechnen.

## Keine Kontoverbindung

IBAN und BIC werden bewusst **nicht** erfasst. Die Kontoverbindung liegt
bereits in der Bezügeabrechnung. Im S2-Vordruck bleiben beide Kästen als
Vordruck stehen und werden bei Bedarf von Hand ausgefüllt.
