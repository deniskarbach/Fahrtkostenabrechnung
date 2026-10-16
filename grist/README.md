# Grist — Überblick

Erfassung der Dienstreise über ein Formular, Aufbereitung in der Tabelle,
standardisierte Ausgabe.

- **[Handbuch](manual.md)** — Ablauf, Formular, Einstellungen, Drucken
- **[Formeln](formeln/README.md)** — Datenfluss, Erklärschema, jede Spalte einzeln

## Warum Grist

Der Engpass war nie die Tabelle, sondern die Erfassung am Handy: sie muss
**ohne Konto** funktionieren, direkt nach der Fahrt. Ein veröffentlichter
Grist-Formularlink leistet genau das. Alles Weitere — Rechnen, Filtern,
Drucken — steckt im selben Dokument, ohne zweite Datei und ohne Import.

## Ablauf

1. **Vorlagendokument kopieren** — es wird in einer eigenen Kopie gearbeitet.
2. **Einmalig einrichten** — Stammdaten und die eigene Adresse in
   `Einstellungen` eintragen, Adressen von `WO`/`KV` auf der Seite `Stammziele` nachtragen,
   Formular veröffentlichen, Link auf dem Handy ablegen.
3. **Erfassen am Handy** — Formularlink öffnen, ausfüllen, absenden.
4. **Abrechnen am PC** — Abrechnungszeitraum wählen, aktualisieren, drucken.

## Bausteine

| Baustein | Inhalt |
|---|---|
| `Einstellungen` | Stammdaten und Abrechnungszeitraum — die einzige Stelle mit persönlichen Daten |
| `Stammziele` | Seite „Stammziele“: Stammziele mit vollständiger Adresse; speist Auswahlliste, Routenlink und Legende |
| `Reisen` | eine Zeile je Dienstreise, gespeist aus dem veröffentlichten Formular |
| Formelspalten | Tagegeld-Staffel, bereinigte Kilometer, laufende Nummer, Reiseweg, Routenlink, Einzelziele (E26-01, E26-02 …) |
| Ausgabe-Widget | „Reisekostenabrechnung“: rendert S1/S2, Vermerke und Ortsverzeichnis zum Drucken |

## Aufbau der Tabellen

Drei Tabellen. Zwei werden am PC gepflegt, eine füllt das Formular.

```
Einstellungen  (genau 1 Zeile, PC, Card-Widget)   Stammziele  (PC, selten)
  Vorname, Name, Organisationseinheit                WO   Wohnung          Beispielweg 7 …
  Wohnort-/Dienstort-Adresse                         KV   Dienststelle     Verwaltungsstr. 1 …
  Abrechnungszeitraum                                KITA Kita Sonnensch.  Lindenweg 3 …
         │                                                  │
         │ Kopfzeile jedes Ausdrucks                        │ Auswahlliste im Formular
         ▼                                                  ▼
     ┌─────────────────────────────────────────────────────┐
     │  Reisen — eine Zeile je Dienstreise                 │ ◀── Handy-Formular
     │  Datum, Uhrzeiten, km-Stände, Kosten, Vermerk,      │
     │  Fotos + 7 Ortsfelder (Beginn, 1–5, Ende)           │
     └─────────────────────────────────────────────────────┘
```

Jedes der sieben Ortsfelder ist ein **Paar**: eine Auswahlliste aus `Stammziele` und
daneben ein Freitextfeld für Ziele, die nicht in der Liste stehen. Was
eingetragen ist, wird gedruckt — sind beide gefüllt, sind es zwei Stopps.
Einzelziele sind der Normalfall, nicht die
Ausnahme — eine reine Auswahlliste würde daran scheitern. Im Reiseweg steht
für jedes Einzelziel ein Kürzel (`E26-07`: Jahr und laufende Nummer, wie bei
den Vermerken), im Ortsverzeichnis Kürzel, Datum und der Freitext, wie er
erfasst wurde.

Einzelheiten zu jeder Tabelle und jeder Formel:
[Formeln](formeln/README.md).

## Ausgabe

[`ausgabe/ausdruck.html`](ausgabe/ausdruck.html ':ignore') — S1, S2, Vermerke und
Ortsverzeichnis als druckbare Seiten, A4 hoch, eine Datei ohne Abhängigkeiten.
Im Browser geöffnet rendert sie erfundene Beispieldaten; als Grist-Widget die
echten. Daneben
[`ausgabe/fahrtenbuch.html`](ausgabe/fahrtenbuch.html ':ignore') zum
Ausschneiden und Einkleben. Auf einer
eigenen, getrennt freigebbaren Seite liegt
[`ausgabe/pruefliste.html`](ausgabe/pruefliste.html ':ignore') — alles aus allen
Blättern in einer Zeile je Reise, für die Zeiterfassungsstelle.

| Ausdruck | Kopf aus | Zeilen aus |
|---|---|---|
| S1 / S2 | Einstellungen | Reisen im Zeitraum |
| Vermerke | Einstellungen | Reisen mit Vermerk |
| Ortsverzeichnis | Einstellungen | Stammziele (je höchstens einmal) + Einzelziele (je Eintrag, mit Datum und Nummer) |
| Fahrtenbuch | — | Reisen im Zeitraum |
| Prüfliste (eigene Seite) | Einstellungen | Reisen im Zeitraum + Orte-Legende |

## Einrichten

```
cp grist/.env.beispiel grist/.env   # dort die drei Werte eintragen
python3 grist/setup.py
```

Legt Tabellen, Spalten, Formeln, die Seiten `Ausdruck`, `Prüfliste` und `Reisekorrektur`
sowie alle Ausgabe-Widgets an.
Wiederholbar. Einzelheiten: [Einrichtung](formeln/setup.md).
