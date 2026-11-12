# Formeln

Nachweis der Berechnung: jede Rechenspalte mit ihrer Formel und dem, was sie
ergibt.

Grist rechnet in **Python**. Eine Formel gilt für die ganze Spalte und wird je
Zeile ausgewertet: `$Feld` ist der Wert dieser Zeile, `Reisen.all` sind alle
Reisen. Neue Zeilen rechnen sofort mit. Ein leeres Zahlenfeld ist `None`; die
Formeln setzen dafür 0 (`$Feld or 0`) und begrenzen Ergebnisse, die nicht
negativ sein dürfen, mit `max(0, …)`.

## Datenfluss

```
Grist-Formular (veröffentlichter Link, Handy, ohne Konto)
   │  eine Absendung = eine Zeile
   ▼
Reisen           Eingabespalten + Rechenspalten
                 (Kilometer, Abwesenheit, Tagegeld-Stufe, Reiseweg,
                  laufende Nummer, Routenlink, Vermerk-Kennung, Einzelziele)

Einstellungen    Stammdaten                        ──┐
Stammziele       Stammziele mit Adresse            ──┤
Ausdruck         Abrechnungszeitraum               ──┤
                                                     ▼
                                   Ausgabe-Widgets, gefiltert auf den Zeitraum
                                   S1/S2 · Vermerke · Ortsverzeichnis ·
                                   Fahrtenbuch · Prüfliste
```

Eingetragen wird nur im Formular, in `Einstellungen`, in `Stammziele` und mit dem Zeitraum auf `Ausdruck`. Alles
andere ist Formelergebnis.

## Seiten

Jede Seite hat dieselbe Gliederung: Zweck, Funktionsweise, Formeln.

| Seite | Inhalt |
|---|---|
| [Formularverwaltung](formularverwaltung.md) | Formular zur Erfassung |
| [Einstellungen](einstellungen.md) | Stammdaten, Kopf des Ausdrucks |
| [Reisekorrektur](reisekorrektur.md) | Reisen ändern |
| [Stammziele](stammziele.md) | wiederkehrende Ziele mit Adresse |
| [Reisen](reisen.md) | alle Rechenspalten |
| [Ausdruck](ausdruck.md) | Abrechnungszeitraum, S1, S2, Vermerke, Ortsverzeichnis, Fahrtenbuch |
| [Prüfliste](pruefliste.md) | eine Zeile je Reise |
| [Anhang](anhang.md) | Tagegeld-Staffel |

Für die Betreuung: [Einrichtung und Technik](setup.md).
