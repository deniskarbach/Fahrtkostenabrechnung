[← Formeln-Übersicht](README.md)

# Einrichtung (setup.py)

[`setup.py`](../setup.py) legt das Datenmodell in einem Grist-Dokument an:
Tabellen, Spalten, Formeln, Seiten, Widgets. Das Skript ist die Quelle der
Formeln — nicht der Editor.

```
cp grist/.env.beispiel grist/.env   # dort die drei Werte eintragen
python3 grist/setup.py
```

Läuft vollständig lokal, nur Standardbibliothek. Zugangsdaten stehen **nie** im
Quelltext: entweder in der Umgebung oder in `grist/.env`, beides außerhalb der
Versionierung.

```
python3 grist/setup.py --selbsttest   # prüft die Formeln ohne Grist
```

## Was ein Lauf tut, in dieser Reihenfolge

| Schritt | Wirkung |
|---|---|
| `anlegen` je Tabelle | fehlende Tabellen und Spalten ergänzen, Beschriftungen nachziehen |
| `formeln_angleichen` | Rechenspalten auf den Stand des Codes bringen |
| Sync-Spalten | die sieben `Ort_*_Sync` anlegen (brauchen `Adressen`, deshalb zuletzt) |
| `reihenfolge_ordnen` | jede `_Text`-Spalte direkt hinter ihre Auswahlspalte setzen |
| `ort_anzeige_setzen` | die Ort-Auswahlspalten zeigen das **Kürzel** statt der Zeilennummer |
| `hilfsspalten_ausblenden` | Zwischenwerte aus den Tabellenansichten nehmen |
| `adressen_aufraeumen` | verwaiste Adresszeilen entfernen |
| leere `Einstellungen`-Zeile | anlegen, falls die Tabelle leer ist |
| `feste_orte_anlegen` | `WO` und `KV` als Pflichtzeilen in `Orte` (ohne Adresse) |
| `einstellungen_karte` | Tabellenansicht der Einstellungen durch ein Card-Widget ersetzen |
| `zeitraum_widget` | Seite `Ausdruck` anlegen (falls nötig) und die Zeitraum-Karte darauf |
| `ausgabe_widgets` | die beiden Custom-Widgets mit ihren URLs abgleichen |
| `ausdruck_layout` | Zeitraum oben, die beiden Druck-Widgets nebeneinander darunter |
| `layouts_aufraeumen` | Layout-Knoten entfernen, die auf fremde Sections zeigen |

Danach bleiben zwei Handgriffe in der Oberfläche:

1. Formular-Widget auf `Reisen` anlegen — das Layout setzt `formular.py`
2. Formular veröffentlichen, dann **Duplicate Document** — das ist die Vorlage

## Was ein erneuter Lauf anfasst — und was nicht

Das Skript ist wiederholbar. Es unterscheidet dabei bewusst:

| | Verhalten bei einem erneuten Lauf |
|---|---|
| Fehlende Tabellen, Spalten, Widgets | werden ergänzt |
| **Rechenformeln** (`isFormula`) | werden auf den Stand des Codes **zurückgesetzt** |
| Beschriftungen | werden nachgezogen, `colId` bleibt unverändert |
| Spaltentyp, Daten | bleiben unangetastet |
| Von Hand sortierte Seitenlayouts | bleiben, solange alle Widgets darin vorkommen |
| Eingetragene Adressen in `Orte` | werden nie überschrieben |

Rechenspalten werden zurückgesetzt, weil sie nicht im Editor getunt werden —
das fängt unter anderem ab, dass ein Snapshot-Restore `Reiseweg` oder
`Maps_Link` auf eine ältere Fassung zieht.

> **Ausnahme:** [`formular.py`](../formular.py) überschreibt die
> Layout-Spezifikation des Formulars **vollständig**. Nur mit Ansage laufen
> lassen.

## Ort-Anzeige

Damit eine Ref-Spalte das Kürzel statt der Zeilennummer zeigt, reicht es nicht,
`visibleCol` zu setzen. Grist hängt zusätzlich eine Hilfsspalte an die Spalte:

```python
["SetDisplayFormula", "Reisen", None, colRef, "$Ort_Beginn.Kuerzel"]
["UpdateRecord", "_grist_Tables_column", colRef, {"visibleCol": ziel}]
```

**Statement:**
- `SetDisplayFormula` – legt die Hilfsspalte `gristHelper_DisplayN` mit der Formel an
- `visibleCol` – merkt sich, welche Spalte der Zieltabelle gemeint ist

**Sonderfall:** Ohne `SetDisplayFormula` bliebe die Hilfsspalte aus und die
Zelle zeigte weiter die Zeilennummer.

## Selbsttest

`--selbsttest` führt die Formeln ohne Grist aus und prüft:

- **Reiseweg / Routenlink** — Auswahl gewinnt vor Freitext (Muster B), ein
  gesetzter Freitext neben einer Auswahl darf nicht im Link auftauchen
- **Tagegeld-Staffel** — acht Fälle über alle vier Schwellen, darunter der
  Fall mit aufgebrauchter Rest-Zeit
- **Layout-Knoten** — `blaetter()` und `ohne_blaetter()` steigen in
  verschachtelte Knoten hinein

Weitere Tests im Repo:

| Datei | Prüft |
|---|---|
| [`ausgabe/test_dienstorte.mjs`](../ausgabe/test_dienstorte.mjs) | Dienstorte-Liste: Stammorte höchstens einmal, Reihenfolge, Einmalziele mit Datum |
| [`ausgabe/test_escaping.py`](../ausgabe/test_escaping.py) | kein Zeilen-Template ohne `html\`\``-Präfix |
| [`ausgabe/test_schwaerzung.py`](../ausgabe/test_schwaerzung.py) | S2-Erzeugung schwärzt und bricht bei Abweichung ab |
| [`test_lookuporadd.py`](../test_lookuporadd.py) | `lookupOrAddDerived` gegen eine normale Tabelle |

> **Zu beachten:** `test_lookuporadd.py` läuft gegen das **echte** Dokument aus
> `grist/.env`. Es legt zwei Wegwerf-Tabellen an und räumt sie wieder ab.
