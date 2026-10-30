[← Formeln-Übersicht](README.md)

# Einstellungen

Genau eine Zeile, als Karte dargestellt — die **einzige** Stelle mit
persönlichen Daten. Sie liefert den Kopf jedes Ausdrucks und den
Abrechnungszeitraum.

| Spalte | Beschriftung | Typ | Wofür |
|---|---|---|---|
| `Vorname`, `Name`, `Organisationseinheit` | Vorname, Name, Organisationseinheit | Text | Kopf: Antragsteller/in |
| `Wohnort_Strasse`, `_PLZ`, `_Ort` | Wohnort – Straße und Hausnummer, PLZ, Ort | Text | Kopf: Wohnort |
| `Dienstort_Strasse`, `_PLZ`, `_Ort` | Dienstort – Straße und Hausnummer, PLZ, Ort | Text | Kopf: Dienstort |
| `Abteilung` | Abteilung (S2) | Text | S2, Verfügungsteil |
| `Buchungsstelle` | Buchungsstelle (S2, nach „€ bei:“) | Text | S2, Zeile „1. KK anweisen, … € bei:“ |
| `Behoerde_Ort` | Behörde – Ort (S2, vor dem Datum) | Text | S2, „Ort, Datum“ |
| `Behoerde` | Behörde – Name (S2, unter „3. z. d. A.“) | Text | S2, unter „3. z. d. A.“ |
| `Zeitraum_von`, `Zeitraum_bis` | Abrechnungszeitraum von / bis | Date | welche Reisen ausgegeben werden |
| `Korrektur_Jahr`, `Korrektur_Monat` | Jahr, Monat | Int, Choice | Seite `Reisekorrektur`: filtert die Liste der Reisen |
| `Korrektur_Reisen` | Reisen in Jahr/Monat | RefList:Reisen | **Formel**, speist diese Liste |

Im Kopf steht die Person als `Name Vorname, Organisationseinheit`
(`Musterfrau Erika, Referat 42`), jede Anschrift als `Straße, PLZ Ort`. Leere
Felder fallen samt Trennzeichen weg. Bleibt ein S2-Feld leer, steht dort die
Linie zum Ausfüllen von Hand.

Der Abrechnungszeitraum wird nur auf der Seite `Ausdruck` gesetzt, dort, wo
gedruckt wird. Wie er filtert: [Ausgabe → Zeitraum](ausgabe.md#zeitraum).

## Korrektur_Reisen

```python
jahr = $Korrektur_Jahr or TODAY().year
monat = ["Januar", …, "Dezember"].index($Korrektur_Monat) + 1 if $Korrektur_Monat else None
return [r for r in Reisen.all if r.Datum and r.Datum.year == jahr
        and (monat is None or r.Datum.month == monat)]
```

Die Reisen des gewählten Jahres und Monats für die Liste auf der Seite
`Reisekorrektur`. Ohne Jahr gilt das laufende, ohne Monat das ganze Jahr. Wirkt
nur auf diese Liste, nicht auf den Ausdruck.
