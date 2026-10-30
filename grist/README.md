# Grist — Überblick

Dienstreise am Handy über ein Formular erfassen, in Grist berechnen, als
S1/S2, Vermerke, Ortsverzeichnis und Fahrtenbuch drucken.

- **[Handbuch](manual.md)** — für die Fachkraft: einrichten, erfassen, drucken
- **[Formeln](formeln/README.md)** — Nachweis der Berechnung, für die Prüfstelle
- **[Einrichtung und Technik](formeln/setup.md)** — für die Betreuung

## Warum Grist

Der Engpass war nie die Tabelle, sondern die Erfassung am Handy: Sie muss
**ohne Konto** funktionieren, direkt nach der Fahrt. Ein veröffentlichter
Grist-Formularlink leistet das. Rechnen, Filtern und Drucken stecken im selben
Dokument.

| | Google Sheets (früher) | Grist |
|---|---|---|
| Konto zum Erfassen | Google-Konto nötig | **keines** — der Formularlink genügt |
| Korrektur einer Reise | nur in der Formularantworten-Datei | auf der Seite `Reisekorrektur` |
| Neue Formularfrage | verschiebt alle folgenden Spalten | nichts verschiebt sich |
| Ausgabe | eigene Blätter mit Formeln | Widgets, die die Tabellen lesen |

## Aufbau

```
Einstellungen  (genau 1 Zeile)                    Stammziele  (selten gepflegt)
  Vorname, Name, Organisationseinheit                WO   Wohnung          Beispielweg 7 …
  Wohnort-/Dienstort-Adresse                         KV   Dienststelle     Verwaltungsstr. 1 …
  Abrechnungszeitraum                                KITA Kita Sonnensch.  Lindenweg 3 …
         │                                                  │
         │ Kopf jedes Ausdrucks                             │ Auswahlliste im Formular
         ▼                                                  ▼
     ┌─────────────────────────────────────────────────────┐
     │  Reisen — eine Zeile je Dienstreise                 │ ◀── Handy-Formular
     │  Eingaben + Rechenspalten (Kilometer, Tagegeld,     │
     │  Reiseweg, laufende Nummer …)                       │
     └─────────────────────────────────────────────────────┘
                              │
                              ▼
        Widgets: Reisekostenabrechnung · Fahrtenbuch · Prüfliste
```

Jeder angefahrene Ort ist ein Paar aus Auswahl (Stammziel) und Freitext
(Einzelziel). Einzelziele sind der Normalfall; im Reiseweg stehen sie als
Kürzel (`E26-07`), im Ortsverzeichnis mit Datum und Freitext.

## Ordner

```
grist/
  setup.py, formular.py   legen das Grist-Dokument an (Tabellen, Seiten, Formular)
  s2_aus_vorlage.py       erzeugt S2 in ausdruck.html aus der lokalen Excel-Vorlage
  ausgabe/                Widgets, die Grist per URL lädt, und die Fahrtenbuch-Vorschau
  tests/                  sh grist/tests/alle.sh, dazu der Abnahmetest
  formeln/, manual.md     Dokumentation
```
