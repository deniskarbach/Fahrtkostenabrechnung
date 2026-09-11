[← Formeln-Übersicht](README.md)

# Anhang

## Tagegeld-Staffel (Kurzregel)

Zwei Prüfungen nacheinander, mit **zwei verschiedenen** Größen:

1. **Anspruch dem Grunde nach** — `Abwesenheit_min − Min_privat_Abzug` ≥ 481
   Minuten (8:01 h). Darunter gibt es kein Kreuz.
2. **Stufe** — ergibt sich aus `Rest_min`, also zusätzlich abzüglich der
   Aufenthalte an Dienststätte und Dienstort.

Ohne `Tagegeld beantragen? = Ja` bleibt die Spalte in jedem Fall leer.

| Rest-Zeit | `Tagegeld_Stufe` | S1-Spalte |
|---|---|---|
| 0 oder weniger | *(leer)* | — |
| unter 8:01 h | `anteilig` | anteilig |
| 8:01 h bis unter 14 h | `>8h` | >8h |
| 14 h bis unter 24 h | `>=14h` | ≥14h |
| ab 24 h | `24h` | 24h |

Die Null-Grenze ist bewusst: fressen Dienststätte und Dienstort die Abwesenheit
vollständig auf, gibt es **keine** Stufe, nicht die kleinste.

## Zeitrechnung

| Größe | Bedeutung |
|---|---|
| 481 Minuten | 8:01 h — die Schwelle „mehr als 8 Stunden" |
| 840 Minuten | 14 h |
| 1440 Minuten | 24 h, zugleich ein voller Kalendertag |

`Abwesenheit_min` zählt je zusätzlichem Kalendertag 1440 Minuten und addiert
die Differenz der Uhrzeiten. Eine Reise über Mitternacht **ohne** Enddatum wird
erkannt und um einen Tag korrigiert; für mehrere Nächte ist das Enddatum
zwingend.

## Mehr Zwischenziele

`ZWISCHENZIELE` in [`setup.py`](../setup.py) steuert, wie viele Ortsfelder es
zwischen Beginn und Ende gibt (derzeit **5**). Daraus leiten sich Spalten,
Beschriftungen, `Reiseweg`, `Maps_Link` und die Sync-Spalten automatisch ab.

Beim Ändern:

1. `ZWISCHENZIELE` erhöhen, `python3 grist/setup.py` erneut laufen lassen —
   die fehlenden Spalten kommen hinzu.
2. `ORT_SLOTS` in [`ausgabe/ausdruck.html`](../ausgabe/ausdruck.html) mitziehen.
   Die Liste steht dort **fest im Quelltext** und wird für das Dienstorte-Blatt
   gebraucht; sie wächst nicht von selbst mit.
3. Formularlayout mit `formular.py` neu setzen.

## Wartung bei Formularänderung

Anders als in der Google-Sheets-Umsetzung verschiebt eine neue Formularfrage
**nichts**: Grist-Formeln greifen über die Spalten-ID (`$KM_Ende`), nicht über
die Spaltenposition. Es gibt deshalb kein Gegenstück zu „Muster D —
Zeilengrenzen" und keine Bezüge, die nach einer Formularänderung zu prüfen
wären.

Was zu tun bleibt:

| Änderung | Schritt |
|---|---|
| Neues Eingabefeld | in die passende Spaltenliste in `setup.py` eintragen, Skript laufen lassen |
| Feld umbenannt | nur `label` ändern — die `colId` und damit alle Formeln bleiben |
| Feld entfällt | Spalte im Editor löschen; `setup.py` legt sie sonst erneut an |
| Formularlayout | `formular.py` — überschreibt die Layout-Spezifikation vollständig |

## Widgets ausliefern

Die beiden Ausgabe-Widgets liegen als statische Dateien im Repo und werden über
GitHub Pages ausgeliefert. Die URL steht in `setup.py` als
`AUSGABE_BASIS_URL`. Eine Änderung an `ausdruck.html` oder
`fahrtenbuch-schnitt.html` wirkt erst nach `git push`; im Grist-Tab danach hart
neu laden.

## Was bewusst nicht erfasst wird

| | Begründung |
|---|---|
| IBAN / BIC | liegen in der Bezügeabrechnung; die Kästen bleiben als Vordruck stehen |
| Adresse von `WO`/`KV` per Formel aus `Einstellungen` | zurückgebaut — erzeugte Spalten, die bearbeitbar aussahen, aber wirkungslos blieben |
| Zusammenführung gleicher Freitext-Ziele | zwei Fahrten sind zwei Vorgänge und werden einzeln geprüft |
