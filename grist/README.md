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
   `Einstellungen` eintragen, Adressen von `WO`/`KV` in `Orte` nachtragen,
   Formular veröffentlichen, Link auf dem Handy ablegen.
3. **Erfassen am Handy** — Formularlink öffnen, ausfüllen, absenden.
4. **Abrechnen am PC** — Abrechnungszeitraum wählen, aktualisieren, drucken.

## Bausteine

| Baustein | Inhalt |
|---|---|
| `Einstellungen` | Stammdaten und Abrechnungszeitraum — die einzige Stelle mit persönlichen Daten |
| `Orte` | Stammziele mit vollständiger Adresse; speist Auswahlliste, Routenlink und Legende |
| `Reisen` | eine Zeile je Dienstreise, gespeist aus dem veröffentlichten Formular |
| `Adressen` | Einmalziele aus den Freitextfeldern; entsteht automatisch |
| Formelspalten | Tagegeld-Staffel, bereinigte Kilometer, laufende Nummer, Reiseweg, Routenlink |
| Ausgabe-Widget | rendert S1/S2, Vermerke, Dienstorte und Fahrtenbuch zum Drucken |

## Aufbau der Tabellen

Vier Tabellen. Zwei werden am PC gepflegt, eine füllt das Formular, eine
entsteht von selbst.

```
Einstellungen  (genau 1 Zeile, PC, Card-Widget)   Orte  (PC, selten)
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
     └────────────────────────┬────────────────────────────┘
                              │ Ort als Freitext getippt statt ausgewählt?
                              ▼
                   Adressen  (entsteht automatisch)
                     Reise, welches Ortsfeld, der Text
```

Jedes der sieben Ortsfelder ist ein **Paar**: eine Auswahlliste aus `Orte` und
daneben ein Freitextfeld für Ziele, die nicht in der Liste stehen. Ist die
Auswahl gesetzt, gewinnt sie. Einmalziele sind der Normalfall, nicht die
Ausnahme — eine reine Auswahlliste würde daran scheitern.

Einzelheiten zu jeder Tabelle und jeder Formel:
[Formeln](formeln/README.md).

## Ausgabe

[`ausgabe/ausdruck.html`](ausgabe/ausdruck.html ':ignore') — S1, S2, Vermerke, Dienstorte
und Fahrtenbuch als druckbare Seiten, A4 hoch, eine Datei ohne Abhängigkeiten.
Im Browser geöffnet rendert sie erfundene Beispieldaten; als Grist-Widget die
echten. Daneben
[`ausgabe/fahrtenbuch-schnitt.html`](ausgabe/fahrtenbuch-schnitt.html ':ignore') zum
Ausschneiden und Einkleben, und
[`ausgabe/routenlinks.html`](ausgabe/routenlinks.html ':ignore') — klickbare
Google-Maps-Routen je Reise, zur Prüfung der gefahrenen Strecke. Auf einer
eigenen, getrennt freigebbaren Seite liegt
[`ausgabe/pruefliste.html`](ausgabe/pruefliste.html ':ignore') — alles aus allen
Blättern in einer Zeile je Reise, für die Zeiterfassungsstelle.

| Ausdruck | Kopf aus | Zeilen aus |
|---|---|---|
| S1 / S2 | Einstellungen | Reisen im Zeitraum |
| Vermerke | Einstellungen | Reisen mit Vermerk |
| Dienstorte | Einstellungen | Orte (je höchstens einmal) + Adressen (je Eintrag, mit Datum) |
| Fahrtenbuch | — | Reisen im Zeitraum |
| Routenlinks | — | Reisen im Zeitraum |
| Prüfliste (eigene Seite) | Einstellungen | Reisen im Zeitraum + Orte-Legende |

## Einrichten

```
cp grist/.env.beispiel grist/.env   # dort die drei Werte eintragen
python3 grist/setup.py
```

Legt Tabellen, Spalten, Formeln, die Seiten `Ausdruck` und `Prüfliste`
sowie alle Ausgabe-Widgets an.
Wiederholbar. Einzelheiten: [Einrichtung](formeln/setup.md).
