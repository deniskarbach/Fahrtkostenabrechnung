# Grist — Überblick

Dienstreisen werden via Handy oder PC über ein Formular erfasst, in Grist automatisch berechnet, und entsprechend einer Vorgabe als
S1/S2, Vermerke, Ortsverzeichnis und Fahrtenbuch gedruckt.

- **[Anleitung](manual.md)** — für die Fachkraft: einrichten, erfassen, drucken
- **[Formeln](formeln/README.md)** — Nachweis der Berechnung, für die Prüfstelle
- **[Einrichtung und Technik](formeln/setup.md)** — für die Betreuung

## Aufbau

```
Formular (Handy)  →  Reisen  →  Ausdruck, Prüfliste
Stammziele        →  Auswahlliste im Formular
Einstellungen     →  Kopf des Ausdrucks
```

- **Reisen:** eine Zeile je Dienstreise, Eingaben und Rechenspalten.
- **Stammziele:** wiederkehrende Ziele, z. B. `WO`, `KV`, `KITA`.
- **Einstellungen:** eine Zeile mit Name, Anschriften und S2-Angaben.
- **Ausdruck:** Widgets Reisekostenabrechnung und Fahrtenbuch.

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
