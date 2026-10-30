# Grist — Überblick

Erfassung der Dienstreise über ein Formular, Aufbereitung in der Tabelle,
standardisierte Ausgabe.

- **[Handbuch](manual.md)** — für die Fachkraft: Ablauf, Formular, Einstellungen, Drucken
- **[Formeln](formeln/README.md)** — Nachweis der Berechnung: Datenfluss, Erklärschema, jede Spalte einzeln
- **[Einrichtung](formeln/setup.md)** — das Grist-Dokument per Skript anlegen, Tests

## Warum Grist

Der Engpass war nie die Tabelle, sondern die Erfassung am Handy: sie muss
**ohne Konto** funktionieren, direkt nach der Fahrt. Ein veröffentlichter
Grist-Formularlink leistet genau das. Alles Weitere — Rechnen, Filtern,
Drucken — steckt im selben Dokument, ohne zweite Datei und ohne Import.

Gegenüber der Google-Sheets-Umsetzung:

| | Google Sheets | Grist |
|---|---|---|
| Konto zum Erfassen | Google-Konto nötig | **keines** — der Formularlink genügt |
| Korrektur einer Reise | nur in der Formularantworten-Datei | auf der Seite `Reisekorrektur` |
| Neue Formularfrage | verschiebt alle folgenden Spalten, Bezüge prüfen | Formeln greifen über Spalten-IDs, kein Versatz |
| Ausgabe | eigene Blätter mit Formeln | ein Widget, das die Tabellen liest |

## Bausteine

| Baustein | Inhalt |
|---|---|
| `Einstellungen` | Stammdaten und Abrechnungszeitraum — die einzige Stelle mit persönlichen Daten |
| `Stammziele` | Seite „Stammziele“: Stammziele mit vollständiger Adresse; speist Auswahlliste, Routenlink und Legende |
| `Reisen` | eine Zeile je Dienstreise, gespeist aus dem veröffentlichten Formular |
| Formelspalten | Tagegeld-Staffel, bereinigte Kilometer, laufende Nummer, Reiseweg, Routenlink, Einzelziele (E26-01, E26-02 …) |
| Ausgabe-Widgets | „Reisekostenabrechnung“ (S1/S2, Vermerke, Ortsverzeichnis), „Fahrtenbuch“, „Prüfliste“ — siehe [Ausgabe](#ausgabe) |

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
     │  Belege + 7 Ortsfelder (Beginn, 1–5, Ende)          │
     └─────────────────────────────────────────────────────┘
```

Jedes der sieben Ortsfelder ist ein **Paar** aus Auswahlliste (`Stammziele`)
und Freitext für Ziele, die nicht in der Liste stehen — solche Einzelziele
sind der Normalfall, nicht die Ausnahme. Im Reiseweg steht für jedes
Einzelziel ein Kürzel (`E26-07`), im Ortsverzeichnis Kürzel, Datum und der
Freitext. Die Regel dahinter: [Muster B](formeln/README.md#muster-b--was-eingetragen-ist-zählt).

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

Was auf welchem Blatt landet und woher: [Ausgabe](formeln/ausgabe.md).

## Ordner

```
grist/
  setup.py, formular.py   Einrichtung des Grist-Dokuments (Tabellen, Seiten, Formular)
  s2_aus_vorlage.py       erzeugt den S2-Block in ausdruck.html aus der lokalen XLSX-Vorlage
  ausgabe/                die Widgets, die Grist per URL lädt, und
                          fahrtenbuch-preview.html (ganzes Fahrtenbuch quer, noch kein Widget)
  tests/                  Offline-Tests (sh grist/tests/alle.sh) und Abnahmetest
  formeln/, manual.md     Dokumentation
```

> **Zu beachten:** Die Dateien in `ausgabe/` lädt Grist über ihre
> GitHub-Pages-Adresse. Umbenennen oder Verschieben ändert die Adresse — der
> nächste Setup-Lauf legt die Widgets dann neu an, und das eingestellte
> Seitenlayout geht verloren. Skripte, Tests und Dokumentation gehören
> deshalb nicht in diesen Ordner.
