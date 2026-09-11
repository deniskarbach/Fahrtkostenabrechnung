[← Formeln-Übersicht](README.md)

# Ausgabe

Was in der Google-Sheets-Umsetzung eigene Blätter mit Formeln sind, ist hier
**ein Widget**, das die vier Tabellen liest und daraus die Druckseiten baut:
[`ausgabe/ausdruck.html`](../ausgabe/ausdruck.html ':ignore') — S1, S2, Vermerke,
Dienstorte und Fahrtenbuch, A4 hoch, eine Datei ohne Abhängigkeiten. Ein Widget
statt vier, ein Grist-Zugriff statt vier.

Daneben steht [`ausgabe/fahrtenbuch-schnitt.html`](../ausgabe/fahrtenbuch-schnitt.html ':ignore'):
dasselbe Fahrtenbuch, aber zum Ausschneiden und Einkleben aufgeteilt. Eigenes
Widget, kein Bestandteil der Standardausgabe.

Beide Dateien lassen sich direkt im Browser öffnen — dann rendern sie erfundene
Beispieldaten. Das ist die Arbeitsweise für Layoutänderungen ohne Grist.

## Was auf welchem Blatt landet

| Blatt | Kopf aus | Zeilen aus |
|---|---|---|
| S1 / S2 | Einstellungen | Reisen im Zeitraum |
| Vermerke | Einstellungen | Reisen im Zeitraum **mit** `Vermerk` |
| Dienstorte | Einstellungen | Orte (je höchstens einmal) + Adressen (je Eintrag, mit Datum) |
| Fahrtenbuch | — | Reisen im Zeitraum |

## Zeitraumfilter

```js
const imZeitraum = d => d != null
  && (von == null || d >= von) && (bis == null || d <= bis);
```

Angewandt auf `Reisen.Datum` und auf `Adressen.Datum`. Maßgeblich ist der
**Reisebeginn** — Begründung siehe [Einstellungen](einstellungen.md#abrechnungszeitraum).

Grist liefert Datumswerte als Sekunden seit 1970, UTC-Mitternacht. Die Anzeige
rechnet deshalb ausdrücklich in UTC:

```js
const tag = s => s == null ? "" : new Date(s * 1000).toLocaleDateString("de-DE",
  { day:"2-digit", month:"2-digit", year:"numeric", timeZone:"UTC" });
```

**Sonderfall:** Ohne `timeZone:"UTC"` läge ein Datum westlich von Greenwich
einen Tag daneben.

## S1 — Reisekostenabrechnung

Je Reise eine Zeile, darunter eine Übertragszeile mit den Summen.

| S1-Spalte | Quelle |
|---|---|
| Reisedatum | `Datum`, bei `Datum_bis` ≠ `Datum` als Spanne |
| Beginn / Ende | `Beginn`, `Ende` |
| Reiseweg | `Nr. {Lfd_Nr} – {Reiseweg}` |
| vier Tagegeld-Spalten | Kreuz aus `Tagegeld_Stufe` |
| Verpflegung | `Verpflegung`, leer → `Nein` |
| ÖPNV, km, Mitnahme, Übernachtung, Nebenkosten | `OePNV`, `KM_dienstlich`, `Mitnahme_Personen`, `Uebernachtung`, `Nebenkosten` |

**Statement:**
- `kreuz(stufe, s)` – setzt `X` in genau die Spalte, deren Name der Stufe entspricht
- `eur(n)` / `zahl(n)` – geben bei `0` einen **Leerstring** aus, nicht „0,00"
- die Übertragszeile summiert dieselben fünf Felder über alle gedruckten Zeilen

**Sonderfall:** Eine Null erscheint als leere Zelle. Ein amtlicher Vordruck mit
lauter Nullen ist schwerer zu lesen als einer mit leeren Feldern.

Der Kopfblock (Titel, Antragsteller, Wohnort, Dienstort) steht im `<thead>` der
Datentabelle, nicht in einer eigenen Tabelle davor — so wiederholt er sich beim
Druck auf jeder Folgeseite.

## S2

Reiner Vordruck, keine Daten aus der Tabelle. Der HTML-Block wird nicht von
Hand gepflegt, sondern aus dem XLSX-Blatt „S2" erzeugt:

```
python3 grist/ausgabe/s2_aus_vorlage.py > /tmp/s2.html
```

S2 ist ein amtliches Formular — Ränder, Füllungen, Schriftgrößen, Zeilenhöhen
und Zellverbünde werden Zelle für Zelle aus der Vorlage übernommen statt
nachgebaut. Das Skript bricht ab, wenn

- eine als behördenspezifisch markierte Zelle nicht mehr den erwarteten Inhalt
  hat (Fingerabdruck-Prüfung, damit nichts Behördenspezifisches in das
  öffentliche Repo gerät), oder
- der erzeugte Block höher als ein A4-Blatt wäre (sonst liefe S2 still auf
  Seite 2 über).

IBAN- und BIC-Kasten bleiben leer und werden bei Bedarf von Hand ausgefüllt.

## Vermerke

Nur Reisen mit ausgefülltem Feld `Vermerk`.

| Spalte | Quelle |
|---|---|
| Nr. | zweiter Teil von `Vermerk_Label` (`V26-01` → `01`) |
| Kennung | `Vermerk_Label` |
| Text | `Vermerk` |
| Datum | `Datum` |

## Dienstorte

Die Legende zum Reiseweg, **kein Fahrtenprotokoll**. Deshalb steht jeder
Stammort höchstens einmal darin.

```js
const stammIds = ["WO", "KV"]
  .map(k => orteListe.find(o => o.Kuerzel === k))
  .filter(Boolean).map(o => o.id);
for (const r of reisen)
  for (const slot of ORT_SLOTS)
    if (r[slot] && orteNachId[r[slot]] && !stammIds.includes(r[slot]))
      stammIds.push(r[slot]);
```

**Statement:**
- `["WO", "KV"]` – Wohnung und Dienststätte führen die Liste fest an
- die Doppelschleife hängt die übrigen Stammorte in der Reihenfolge ihres **ersten Vorkommens** im Zeitraum an
- `!stammIds.includes(…)` – jeder Ort nur einmal

**Ergebnis:** Nummerierte Liste — 1 Wohnung, 2 Dienststätte, danach die
übrigen Stammorte, danach die Einmalziele nach Datum.
**Sonderfall:** Ohne diese Entdopplung erschiene die Wohnung bei zwei Reisen
viermal, je einmal als Start und als Ziel. Das war ein stiller Fehler; dagegen
läuft [`test_dienstorte.mjs`](../ausgabe/test_dienstorte.mjs).

Die Einmalziele aus `Adressen` folgen danach, jede Eintragung als eigene Zeile,
nach Datum sortiert. Das Datum steht in der Kürzel-Spalte — die bleibt bei
diesen Zeilen ohnehin leer. Daher die Überschrift *Kürzel / Datum*.

## Fahrtenbuch

Je Reise eine Zeile, Spalten 1–15 des amtlichen Fahrtenbuchs.

| Spalte | Quelle |
|---|---|
| 1 Lfd. Nr. | `Lfd_Nr` |
| 2/3 Monat, Tag | aus `Datum` |
| 4/5 von, bis | `Beginn`, `Ende` |
| 6 Reiseweg | `Reiseweg` |
| 7/8 Kilometerstand | `KM_Beginn`, `KM_Ende` |
| 9 dienstlich | `KM_dienstlich` |
| 10 außerdienstlich | `Umweg_privat` |
| 11–14 Mitgenommene Bedienstete, Unterschrift | bleiben leer, von Hand |
| 15 Vermerke | `Vermerk_Label` |

Die **Schnittversion** bricht dieselben Daten auf zwei Seiten je Zeilenblock um:
links die Spalten 1–6, rechts 7–15. Bei **100 %** drucken, an der bezeichneten
Kante schneiden, einkleben, unterschreiben.

## Escaping

Die Tabellenzellen werden als HTML zusammengesetzt und per
`insertAdjacentHTML` eingefügt. Jeder eingesetzte Wert läuft deshalb durch
`esc()`:

```js
const esc = s => String(s ?? "").replace(/[&<>"]/g,
  c => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;" }[c]));
const html = (t, ...v) => t.reduce((a, s, i) => a + esc(v[i - 1]) + s);
```

**Statement:**
- `html\`…\`` – Präfix vor dem Template-Literal; schiebt jeden `${…}`-Wert durch `esc()`
- ohne Präfix kein Schutz

Vermerk, Freitext-Orte und Adressen kommen aus einem **öffentlich
erreichbaren Formular**. Das Widget liest mit `requiredAccess: "full"` Name,
Wohnanschrift und Belege — eingeschleustes Markup wäre also teuer. Gegen den
wahrscheinlichen Rückfall (jemand ergänzt eine Zeile und vergisst das Präfix)
läuft [`test_escaping.py`](../ausgabe/test_escaping.py); dort stehen auch die
drei nachgemessenen Grenzen dieses Tests.

## Aktualisieren

```js
grist.onRecords(ausGrist);
```

`onRecords` feuert beim Aufbau und danach **nur** bei Änderungen an der
Tabelle, an der das Widget hängt — das ist `Einstellungen`, praktisch also nur
der Abrechnungszeitraum. Eine neu erfasste oder korrigierte **Reise** erreicht
das Widget nicht.

Dafür der Knopf **Aktualisieren** in der Leiste über dem Ausdruck. Ein
sichtbarer Knopf statt Polling: die Plugin-API kennt keinen Haken auf fremde
Tabellen, und still veraltet zu drucken ist der teurere Fehler.

## Herkunft der Plugin-API

```js
const quelle = document.referrer ? new URL(document.referrer).origin
              : window.location.ancestorOrigins?.[0] || "";
```

Die Plugin-API wird von der **einbettenden** Grist-Instanz geladen, nicht von
einer festen Adresse — so steht der Hostname der Instanz nicht in diesem
offenen Repo. Löscht eine strenge Referrer-Policy `document.referrer`, dient
`ancestorOrigins` als zweite Quelle; ist auch die leer, lädt das Widget nichts
und sagt es. Ein fest verdrahtetes `docs.getgrist.com` wäre doppelt falsch: die
eigene Instanz bliebe unerreichbar, und ein fremder Host bekäme einen Request
aus dem Dokument.

## Layout ändern

Schriftgrößen, Innenabstände und Rahmenstärke stehen als CSS-Variablen am Kopf
von `ausdruck.html`, je Dokument ein eigener Namensraum (`.dok-s1`,
`.dok-s2`, `.dok-vermerke`, `.dok-dienstorte`, `.dok-fahrtenbuch`), damit
gleichnamige Klassen sich nicht in die Quere kommen.

Die Widgets werden über GitHub Pages ausgeliefert. Eine Änderung wirkt erst
nach `git push`; im Grist-Tab danach hart neu laden, sonst steckt die alte
Fassung im Browser-Cache.
