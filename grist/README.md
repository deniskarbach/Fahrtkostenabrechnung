# Handbuch — Grist

> **Status: Konzeptidee.**

Erfassung der Dienstreise über ein Formular, Aufbereitung in der Tabelle,
standardisierte Ausgabe.

## Ablauf

1. **Vorlagendokument kopieren** — es wird in einer eigenen Kopie gearbeitet.
2. **Einmalig einrichten** — Stammdaten und Orte eintragen, Formular veröffentlichen, Link auf dem Handy ablegen.
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

[`ausgabe/s1.html`](ausgabe/s1.html) — S1 als druckbare Seite, A4 hoch, eine Datei ohne Abhängigkeiten. Im Browser öffnen und über die Druckfunktion ausgeben. Die Beispielreisen darin sind erfunden.

Schriftgrößen, Innenabstände und Rahmenstärke stehen als CSS-Variablen am Kopf der Datei.

## Aufbau der Tabellen

Wird ergänzt, sobald das Vorlagendokument steht: Spalten und Typen von `Reisen`, die Verknüpfung zu `Orte`, die Formelspalten.
