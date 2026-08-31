[← Formeln-Übersicht](../Formeln.md)

# Setup

Import Formularantworten Google Sheets Datei "[Formularantworten-Datei]"

```
=IF(B80="Ja"; IMPORTRANGE(B74; "Formularantworten 1!A1"); "🔒 Bitte legitimieren")
```

**Statement:**
- `IF(B80="Ja"; …; …)` – Freigabe-Schalter, prüft eine Ja/Nein-Zelle
- `IMPORTRANGE(B74; "Formularantworten 1!A1")` – lädt einen Bereich aus einer fremden Tabellendatei über deren URL

**Ergebnis:** Holt die Formulardaten erst, wenn die Freigabe (B80) auf „Ja" steht.
**Rechenweg:** Ohne Freigabe erscheint ein Schloss-Hinweis; mit Freigabe wird die
verknüpfte Tabelle über ihre in B74 hinterlegte URL geladen.
**Sonderfall:** Der erste Import muss einmalig in Google Sheets bestätigt werden.

Bedingte Formatierung - Datumsangabe

```
=TAGTRUNC(C5)<TAGTRUNC(C3)
```

**Statement:**
- `TAGTRUNC(…)` – schneidet die Uhrzeit ab, übrig bleibt der reine Tag
- `<` – liefert WAHR/FALSCH; WAHR löst die Formatierung aus

**Ergebnis:** Färbt das Feld, wenn das Enddatum vor dem Startdatum liegt.
**Rechenweg:** Beide Datumswerte werden auf ganze Tage gekürzt und verglichen.
