[← Formeln](README.md)

# Reisekorrektur

## Zweck

Hier wird eine bereits erfasste Reise gesucht und geändert; alle Rechenwerte ziehen sofort nach.
Die Ansicht gibt es, weil Korrekturen sonst nur in den Rohdaten des Formulars möglich wären.
Sie umfasst die Reisenliste nach Jahr und Monat und die Eingabemaske der gewählten Reise.

## Funktionsweise

- Oben Jahr und Monat wählen (Felder `Korrektur_Jahr`, `Korrektur_Monat` in
  [Einstellungen](einstellungen.md)); links erscheinen die Reisen, rechts wird
  die angeklickte geändert.
- Alle Rechenspalten rechnen sofort neu.
- Die Wahl wirkt nur auf diese Liste, nicht auf den Ausdruck.

| Spalte | Typ | Inhalt |
|---|---|---|
| `Korrektur_Jahr` | Int | Jahr |
| `Korrektur_Monat` | Choice | Monat |
| `Korrektur_Reisen` | RefList:Reisen | **Formel** |

## Formeln

### Korrektur_Reisen

```python
jahr = $Korrektur_Jahr or TODAY().year
monat = ["Januar", …, "Dezember"].index($Korrektur_Monat) + 1 if $Korrektur_Monat else None
return [r for r in Reisen.all if r.Datum and r.Datum.year == jahr
        and (monat is None or r.Datum.month == monat)]
```

- **Ergebnis:** die Reisen des gewählten Jahres und Monats.
- **Sonderfall:** Ohne Jahr gilt das laufende, ohne Monat das ganze Jahr.
