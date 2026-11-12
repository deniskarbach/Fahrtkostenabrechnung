[← Formeln](README.md)

# Prüfliste

## Zweck

Die Seite zeigt je Reise alle Angaben aus S1, Vermerken, Ortsverzeichnis und Fahrtenbuch in einer Zeile.
Sie gibt es für die Zeiterfassungsstelle, die damit prüft, ohne die Druckseiten durchzugehen.
Sie umfasst die Reisezeilen mit Routenlink und darunter die Orte-Legende.

## Funktionsweise

- Das Widget „Prüfliste“ liegt auf der eigenen Seite `Prüfliste`. Die Seite
  lässt sich allein freigeben; dann sieht die Stelle nur diese Liste.
- Darunter steht die Orte-Legende, gleich dem [Ortsverzeichnis](ausdruck.md#ortsverzeichnis).
- Die Spaltenbegriffe sind die aus [S1](ausdruck.md#s1).

## Formeln

| Gruppe | Spalten | Quelle |
|---|---|---|
| — | Nr., Reisedatum | `Lfd_Nr`, `Datum` (mehrtägig als Spanne) |
| Uhrzeit | Beginn, Ende | `Beginn`, `Ende` |
| — | Reiseweg | `Reiseweg` |
| Tagegeld für | Ges, DSt, DO, Priv, Rest, Stufe | `Abwesenheit_min`, `Min_Dienststaette`, `Min_Dienstort`, `Min_privat_Abzug`, `Rest_min`, `Tagegeld_Stufe` |
| — | Unentgeltliche Verpflegung | `Verpflegung` |
| Kilometerstand | Beginn, Ende | `KM_Beginn`, `KM_Ende` |
| Wegstrecke | privat, dienstl. | `Umweg_privat`, `KM_dienstlich` |
| Fahrt- und Nebenkosten | ÖPNV, Mitn., Übernachtung, Nebenkosten | `OePNV`, `Mitnahme_Personen`, `Uebernachtung`, `Nebenkosten` |
| — | Vermerk, Route | `Vermerk_Label`, `Maps_Link` |
