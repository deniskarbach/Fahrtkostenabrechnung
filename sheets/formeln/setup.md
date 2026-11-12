[← Formeln](README.md)

# Setup

## Zweck

Das Blatt nimmt die Stammdaten, die Freigabe, den Link zur Formularantworten-Datei und den Abrechnungszeitraum (C8–C10) auf.
Es gibt das Blatt, damit alle Eingaben außer dem Formular an einer Stelle liegen.
Es umfasst den Import der Antworten und die Datumsprüfung.

## Funktionsweise

- Nur Setup (und bei neuen Zielen das Blatt [Orte](orte.md)) wird von Hand
  gepflegt.
- Der erste Import muss einmalig in Google Sheets bestätigt werden.

## Formeln

### Import der Formularantworten

```
=IF(B80="Ja"; IMPORTRANGE(B74; "Formularantworten 1!A1"); "🔒 Bitte legitimieren")
```

**Aufbau:**
- `IF(B80="Ja"; …; …)` – Freigabe-Schalter
- `IMPORTRANGE(B74; "Formularantworten 1!A1")` – lädt einen Bereich aus der Datei, deren URL in B74 steht

**Ergebnis:** Die Formulardaten erscheinen erst, wenn die Freigabe (B80) auf „Ja" steht.
**Sonderfall:** Ohne Freigabe erscheint ein Schloss-Hinweis.

### Bedingte Formatierung – Datumsangabe

```
=TAGTRUNC(C5)<TAGTRUNC(C3)
```

**Ergebnis:** Färbt das Feld, wenn das Enddatum vor dem Startdatum liegt.
**Aufbau:** `TAGTRUNC` schneidet die Uhrzeit ab; `<` liefert WAHR/FALSCH, WAHR löst die Formatierung aus.
