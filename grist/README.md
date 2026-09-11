# Handbuch — Grist

> **Status: Konzeptidee.**

Erfassung der Dienstreise über ein Formular, Aufbereitung in der Tabelle,
standardisierte Ausgabe.

## Ablauf

1. **Vorlagendokument kopieren** — es wird in einer eigenen Kopie gearbeitet.
2. **Einmalig einrichten** — Stammdaten und die eigene Adresse in `Einstellungen` eintragen (als Karte, ein Formular), Formular veröffentlichen, Link auf dem Handy ablegen.
3. **Erfassen am Handy** — Formularlink öffnen, ausfüllen, absenden.
4. **Abrechnen am PC** — Abrechnungszeitraum wählen, standardisierte Ausgabe rendern und drucken.

## Bausteine

| Baustein | Inhalt |
|---|---|
| `Reisen` | eine Zeile je Dienstreise, gespeist aus dem veröffentlichten Formular |
| `Orte` | Reiseziele mit vollständiger Adresse; speist die Auswahlliste im Formular und die Adressauflösung |
| `Einstellungen` | Stammdaten und Abrechnungszeitraum |
| Formelspalten | Tagegeld-Staffel, bereinigte Kilometer, laufende Nummer, Reiseweg, Routenlink |
| Ausgabe-Widget | rendert die standardisierte Ausgabe zum Drucken |

## Ausgabe

[`ausgabe/ausdruck.html`](ausgabe/ausdruck.html) — S1, S2, Vermerke, Dienstorte und Fahrtenbuch als druckbare Seiten, A4 hoch, eine Datei ohne Abhängigkeiten. Im Browser öffnen und über die Druckfunktion ausgeben. Die Beispielreisen darin sind erfunden.

Im Grist-Widget hängt der Ausdruck an der Tabelle `Einstellungen`: er baut sich beim Öffnen und bei jeder Änderung am Abrechnungszeitraum neu auf. Eine neu erfasste oder korrigierte **Reise** erreicht ihn nicht von selbst — dafür der Knopf **Aktualisieren** in der Leiste über dem Ausdruck. Vor dem Drucken einmal drücken.

Schriftgrößen, Innenabstände und Rahmenstärke stehen als CSS-Variablen am Kopf der Datei.

## Aufbau der Tabellen

Vier Tabellen. Zwei werden am PC gepflegt, eine füllt das Formular, eine
entsteht von selbst.

```
Einstellungen  (genau 1 Zeile, PC, Card-Widget)   Orte  (PC, selten)
  Vorname, Name, Organisationseinheit                WO   Wohnung          Beispielweg 7 …    ← Formel
  Wohnort-/Dienstort-Adresse  ──Formel──────────▶    KV   Dienststelle     Verwaltungsstr. 1 …  ← Formel
  Abrechnungszeitraum                                KITA Kita Sonnensch.  Lindenweg 3 …
         │                                                  │
         │ Kopfzeile jedes Ausdrucks                        │ Auswahlliste im Formular
         ▼                                                  ▼
     ┌─────────────────────────────────────────────────────┐
     │  Reisen — eine Zeile je Dienstreise                 │ ◀── Handy-Formular
     │  Datum, Uhrzeiten, km-Stände, Kosten, Vermerk,      │
     │  Fotos + 7 Ortsfelder (Beginn, 1–5, Ende)           │
     └────────────────────────┬────────────────────────────┘
                              │ Ort als Freitext getippt statt ausgewählt?
                              ▼
                   Adressen  (entsteht automatisch)
                     Reise, welches Ortsfeld, der Text
```

**Einstellungen** — eine einzige Zeile, einmal bei der Einrichtung ausgefüllt,
als Card-Widget statt Tabelle: eine Zeile als Formular gelesen ist eindeutiger
als eine Zeile in einer Tabelle. Diese Tabelle ist die **einzige** Stelle, an
der persönliche Daten erfasst werden — auch die eigene Adresse steht hier als
Straße/PLZ/Ort, nicht in `Orte`.

Reiseweg und Routenlink brauchen die Wohnung und die Dienststelle trotzdem als
Zeilen in `Orte` (Kürzel `WO`/`KV`, sonst wählbar wie jeder andere Ort).
`setup.py` legt diese zwei Zeilen zwingend an; ihre Adresse tippt dort niemand
ein — eine Formel liest sie automatisch aus `Einstellungen`. Wer umzieht,
ändert die Adresse genau einmal, an der Stelle, an der er sie erwartet.

Eine Kontoverbindung wird **nicht** erfasst. IBAN- und BIC-Kasten bleiben im
S2-Vordruck stehen und werden, falls die Abrechnungsstelle sie überhaupt
braucht, von Hand ausgefüllt.

**Orte** — die wiederkehrenden Ziele mit Kürzel und Adresse. Diese Liste ist
die Auswahlliste im Formular und die Legende auf dem Ausdruck. `WO` und `KV`
stehen darin als Pflichtzeilen, ihre Adresse ist schreibgeschützt in dem Sinn,
dass sie zwar bearbeitbar aussieht, aber überschrieben wird — die Formel liest
`Kürzel = "WO"`/`"KV"` und ignoriert `Straße`/`PLZ`/`Ort` der Zeile dann.

**Reisen** — pro Dienstreise eine Zeile, aus dem Formular. Jedes der sieben
Ortsfelder ist ein **Paar**: eine Auswahlliste aus `Orte` und daneben ein
Freitextfeld für Ziele, die nicht in der Liste stehen. Ist die Auswahl gesetzt,
gewinnt sie. Dazu kommen berechnete Spalten — Reiseweg (`WO > KV > WO`),
Tagegeldstufe, dienstliche Kilometer, Routenlink, laufende Nummer.

**Adressen** — wird nie von Hand gefüllt. Sobald ein Ortsfeld als Freitext
ausgefüllt ist, legt eine Formel hier eine Zeile an: welche Reise, welches
Feld, welcher Text. Straße und PLZ kann die Abrechnungsstelle nachtragen.
Bewusst eine Zeile je Fahrt — dasselbe Ziel auf zwei Fahrten ergibt zwei
Zeilen, denn es sind zwei Vorgänge.

### Was in welchen Ausdruck fließt

| Ausdruck | Kopf aus | Zeilen aus |
|---|---|---|
| S1 / S2 | Einstellungen | Reisen im Zeitraum |
| Vermerke | Einstellungen | Reisen mit Vermerk |
| Dienstorte | Einstellungen | Orte (je höchstens einmal) + Adressen (je Eintrag, mit Datum) |
| Fahrtenbuch | — | Reisen im Zeitraum |

Die Dienstorte-Liste ist die Legende zum Reiseweg, kein Fahrtenprotokoll:
Wohnung und Dienststätte stehen fest auf 1 und 2, danach die übrigen Stammorte
nach ihrem ersten Vorkommen, danach die Einmalziele nach Datum. Deren Datum
steht in der Kürzel-Spalte, die bei ihnen ohnehin leer bleibt.
