[← Formeln-Übersicht](README.md)

# Ausgabe

Was in der Google-Sheets-Umsetzung eigene Blätter mit Formeln sind, ist hier
**ein Widget**, das die vier Tabellen liest und daraus die Druckseiten baut:
[`ausgabe/ausdruck.html`](../ausgabe/ausdruck.html ':ignore') — S1, S2, Vermerke,
Dienstorte und Fahrtenbuch, A4 hoch, eine Datei ohne Abhängigkeiten. Ein Widget
statt vier, ein Grist-Zugriff statt vier.

Daneben stehen zwei eigenständige Widgets, kein Bestandteil der
Standardausgabe:
[`ausgabe/fahrtenbuch-schnitt.html`](../ausgabe/fahrtenbuch-schnitt.html ':ignore')
(dasselbe Fahrtenbuch, aber zum Ausschneiden und Einkleben aufgeteilt) und
[`ausgabe/routenlinks.html`](../ausgabe/routenlinks.html ':ignore') (Gegenstück
zum Sheets-Blatt „GoogleMapsExport", siehe [unten](#routenlinks-google-maps)).

Dazu [`ausgabe/pruefliste.html`](../ausgabe/pruefliste.html ':ignore') auf einer
eigenen Seite: alles aus allen Blättern in einer Zeile je Reise, für die
Zeiterfassungsstelle — siehe [unten](#prüfliste-zeiterfassungsstelle).

Alle vier Dateien lassen sich direkt im Browser öffnen — dann rendern sie
erfundene Beispieldaten. Das ist die Arbeitsweise für Layoutänderungen ohne
Grist.

## Was auf welchem Blatt landet

| Blatt | Kopf aus | Zeilen aus |
|---|---|---|
| S1 / S2 | Einstellungen | Reisen im Zeitraum |
| Vermerke | Einstellungen | Reisen im Zeitraum **mit** `Vermerk` |
| Dienstorte | Einstellungen | Orte (je höchstens einmal) + Adressen (je Eintrag, mit Datum) |
| Fahrtenbuch | — | Reisen im Zeitraum |
| Routenlinks | — | Reisen im Zeitraum |
| Prüfliste | Einstellungen | Reisen im Zeitraum + Orte/Adressen als Legende |

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
| Reiseweg | `s1Zeile(r)`, siehe unten |
| vier Tagegeld-Spalten | Kreuz aus `Tagegeld_Stufe` |
| Verpflegung | `Verpflegung`, leer → `Nein` |
| ÖPNV, km, Mitnahme, Übernachtung, Nebenkosten | `OePNV`, `KM_dienstlich`, `Mitnahme_Personen`, `Uebernachtung`, `Nebenkosten` |

**Statement:**
- `kreuz(stufe, s)` – setzt `X` in genau die Spalte, deren Name der Stufe entspricht
- `eur(n)` / `zahl(n)` – geben bei `0` einen **Leerstring** aus, nicht „0,00"
- die Übertragszeile summiert dieselben fünf Felder über alle gedruckten Zeilen

### Spalte „Reiseweg"

Der amtliche Vordruck verlangt hier nur die laufende Nummer, **wenn ein
Fahrtenbuch geführt wird** — genau das steht im Spaltenkopf. Da diese
Ausgabe immer ein Fahrtenbuch mitliefert, wäre der eigentliche Reiseweg an
dieser Stelle eine Dopplung dessen, was dort ohnehin steht. Statt der bloßen
Nummer zeigt die Spalte deshalb die Zeiten, aus denen sich die
Tagegeld-Stufe ergibt — zur Prüfung beim Unterschreiben, wie in der
Sheets-Version:

```js
const s1Zeile = r => {
  if (!r.Lfd_Nr) return "";
  const priv = r.Min_privat_Abzug > 0 ? ` | Priv: ${stunden(r.Min_privat_Abzug)}` : "";
  return `Nr. ${r.Lfd_Nr}  –  (Ges.: ${stunden(r.Abwesenheit_min)}`
       + ` | DSt: ${stunden(r.Min_Dienststaette)} | DO: ${stunden(r.Min_Dienstort)}`
       + `${priv} | Rest: ${stunden(r.Rest_min)})`;
};
```

**Statement:**
- `stunden(min)` – wandelt Minuten in `H:MM`, auch über 24 h hinaus (mehrtägige Reisen)
- `priv` – der Priv-Teil erscheint nur, wenn ein privater Zeitabzug eingetragen ist

**Ergebnis:** `Nr. 67  –  (Ges.: 8:55 | DSt: 0:00 | DO: 0:00 | Rest: 8:55)`
**Rechenweg:** Ges. = `Abwesenheit_min`, DSt = `Min_Dienststaette`,
DO = `Min_Dienstort`, Rest = `Rest_min` — dieselben vier Werte, aus denen
`Tagegeld_Stufe` die Stufe ableitet (siehe [Reisen](reisen.md#tagegeld_stufe--tagegeld-stufe)).
**Sonderfall:** War die Sache vorher (bis inkl. Commit `e0db8dc`): die Spalte
zeigte `Reiseweg` — identisch zu dem, was ohnehin im Fahrtenbuch steht, und
ohne jeden Bezug zur Tagegeld-Prüfung, die diese Spalte laut Vordruck
eigentlich leisten soll.

**Sonderfall:** Bei ÖPNV, Mitnahme, Übernachtung und Nebenkosten erscheint eine
Null als leere Zelle — ein amtlicher Vordruck mit lauter Nullen ist schwerer zu
lesen als einer mit leeren Feldern für tatsächlich nicht angefallene Kosten.

**Ausnahme km:** Dienstliche Kilometer werden **immer** gedruckt, auch `0` —
anders als die vier Kostenfelder ist die Spalte nicht optional, sondern zu
jeder Reise berechnet. Eine Fahrt, die vollständig als privater Umweg erfasst
wurde (z. B. eine reine Verwaltungsfahrt ohne erstattungsfähige Strecke), muss
als `0` erkennbar bleiben — eine leere Zelle sähe nach vergessener Eingabe aus.
Das Fahrtenbuch (`f.kmDienstlich ?? ""`) hatte das schon richtig; S1 zog vorher
fälschlich `zahl()` heran und blendete die `0` aus.

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

## Routenlinks (Google Maps)

Eigenes Widget, [`ausgabe/routenlinks.html`](../ausgabe/routenlinks.html ':ignore') --
Gegenstück zum Sheets-Blatt
[GoogleMapsExport](../../sheets/formeln/googlemapsexport.md ':ignore'). Die
`.md`-Doku dort beschreibt nur die Formeln; Kopfblock, Tabellenkopf und
Spaltenreihenfolge sind aus der **Vorlage selbst** übernommen
(`ReisekostenabrechnungFINAL.xlsx`, Blatt „GoogleMapsExport" -- dieselbe Datei,
aus der auch [S2](#s2) entsteht), nicht aus der Formeldoku nacherfunden.

**Kopfblock:** Titel, Antragssteller/Wohnort/Dienstort wie bei S1 -- in der
Vorlage über zwei Zeilen gemergt. Der dortige Titel „REISEKOSTENRECHNUNG" ist
erkennbar aus S1 kopiert (für eine Routenliste sachlich falsch) und hier durch
„Routenlinks" ersetzt; der Rest des Kopfblocks (Antragssteller/Wohnort/
Dienstort) ist unverändert übernommen, gebaut mit derselben `anschrift()`-Logik
wie in [Einstellungen](einstellungen.md#kopfzeile-des-ausdrucks).

**Tabellenkopf**, exakt in der Reihenfolge der Vorlage -- **abweichend** von
der Reihenfolge in der Sheets-Formeldoku, die Reiseweg vor Beginn/Ende listet:

| Spalte (Vorlage) | Quelle |
|---|---|
| Nr. | `Lfd_Nr` |
| Datum | `Datum` |
| Reisebeginn | `Beginn` |
| Reiseende | `Ende` |
| Wegstrecke | `Reiseweg` |
| KM dienstlich | `KM_dienstlich` |
| Routenlink | `Maps_Link`, verlinkt als „Route" |

Kein Druckformular wie ausdruck.html, trotz des formellen Kopfblocks: die
Sheets-Vorlage nennt für dieses Blatt selbst keine Druckanweisung („Nichts.
Routenlink bei Bedarf nutzen" -- ein Link ist auf Papier ohnehin nicht
klickbar). Deshalb Bildschirm-Maße statt A4/mm, kein „Drucken"-Knopf, nur
„Aktualisieren".

**Statement (Route-Zelle):**
- bekommt kein `html\`…\`` -- ein eingebettetes `<a>` würde darin selbst
  escaped und der Link ginge kaputt
- stattdessen steht der Link zunächst als `data-link`-Attribut (läuft dort
  ganz normal durch `esc()`) und wird erst danach per DOM-API
  (`a.href = …`) zum `<a>` -- der Wert wird nie als HTML geparst, das ist
  sicherer als ein von Hand zusammengesetztes `<a href="…">`

**Ergebnis:** Ein „Route"-Link, der die Reise direkt in Google Maps öffnet,
in einem neuen Tab (`target="_blank"`, das Widget-Iframe bleibt bestehen).
**Sonderfall:** Weniger als zwei Orte → `Maps_Link` ist leer → keine Zelle
mit Link, kein Fehler.

Deutlich einfacher als die Sheets-Version: dort löst eine `BYROW`/`MAP`/
`XMATCH`-Formel Formular-Kürzel gegen `Orte` auf, weil das Formular rohen
Text liefert. In Grist ist ein Ortsfeld eine echte `Ref:Orte`-Referenz --
die Auflösung passiert schon in `Maps_Link` selbst (siehe
[Reisen](reisen.md#maps_link--routenlink)), hier wird nur noch gelesen.

## Prüfliste (Zeiterfassungsstelle)

Eigenes Widget, [`ausgabe/pruefliste.html`](../ausgabe/pruefliste.html ':ignore') --
**ohne Vorbild in der Sheets-Umsetzung.** Dort muss die Stelle, die den Antrag
final bearbeitet, zwischen S1, Vermerken, Dienstorten, Fahrtenbuch und
GoogleMapsExport hin- und herblättern, um eine Reise vollständig zu beurteilen.
Hier steht alles davon in **einer Zeile je Reise**, A4 quer, 22 Spalten:

| Gruppe | Spalten | Quelle |
|---|---|---|
| — | Nr., Reisedatum | `Lfd_Nr`, `Datum` (mehrtägig als Spanne, wie S1) |
| Uhrzeit | Beginn, Ende | `Beginn`, `Ende` |
| — | Reiseweg | `Reiseweg` |
| Tagegeld für | Ges., DSt, DO, Priv, Rest, Stufe | `Abwesenheit_min`, `Min_Dienststaette`, `Min_Dienstort`, `Min_privat_Abzug`, `Rest_min`, `Tagegeld_Stufe` |
| — | Unentgeltliche Verpflegung | `Verpflegung` |
| Kilometerstand | Beginn, Ende | `KM_Beginn`, `KM_Ende` |
| Wegstrecke | privat, dienstl. | `Umweg_privat`, `KM_dienstlich` |
| Fahrt- und Nebenkosten | ÖPNV, Mitn., Übernachtung, Nebenkosten | `OePNV`, `Mitnahme_Personen`, `Uebernachtung`, `Nebenkosten` |
| — | Vermerk, Route | `Vermerk_Label`, `Maps_Link` |

Darunter die **Orte-Legende** — dieselben Zeilen wie das
[Dienstorte-Blatt](#dienstorte), damit die Kürzel im Reiseweg ohne Blattwechsel
auflösbar sind.

### Drucken: eigenes Fenster, und warum nicht 277mm

Zwei Fallen, beide aufgetreten:

- **`window.print()` aus dem Widget öffnete den Dialog in Hochformat.** Das
  Widget läuft in einem iframe, und dort übernimmt der Druckdialog die
  `@page`-Regel (`size: A4 landscape`) nicht zuverlässig. `drucken()` schreibt
  das fertige Blatt deshalb in ein **eigenes Fenster**, wo es
  Top-Level-Dokument ist und `@page` sicher greift.
- **Auch im Querformat wurde rechts abgeschnitten.** A4 quer misst 297mm;
  greift `@page` mit 10mm Rand, bleiben 277mm — greift sie nicht, gelten die
  Standardränder des Dialogs (~12,7mm je Seite) und es bleiben nur
  **271,6mm**. Die Tabelle war auf 275mm ausgelegt, also genau dazwischen.
  Jetzt 252mm, damit sie in beiden Fällen passt.

`test_pruefliste.mjs` prüft beides: die Breitensumme jeder der drei Tabellen
gegen 271,6mm, und dass der Knopf über ein eigenes Fenster druckt statt über
`window.print()`.

**Statement:**
- Spaltenbegriffe absichtlich aus S1 übernommen („Tagegeld für",
  „Unentgeltliche Verpflegung", „Wegstrecke", „Mitnahme von Personen") --
  die Stelle soll die gewohnte Ansicht wiedererkennen, nicht eine neue lernen
- die Tagegeldzeiten stehen als **eigene Spalten**, nicht als Textzeile wie in
  der [S1-Spalte „Reiseweg"](#spalte-reiseweg) -- einzeln prüfbar statt nur lesbar
- Route-Zelle wie in [Routenlinks](#routenlinks-google-maps): erst `data-link`,
  dann per DOM-API zum `<a>`

**Sonderfall:** Die Sortierlogik der Orte-Legende steht in **zwei** Dateien
(`pruefliste.html` und `ausdruck.html`) -- die Widgets sind bewusst
eigenständige Einzeldateien ohne gemeinsames Modul. Gegen ein Auseinanderlaufen
prüft [`test_pruefliste.mjs`](../ausgabe/test_pruefliste.mjs) beide Blätter auf
dieselbe Liste; der Wächter wurde mit einer absichtlich gebrochenen Sortierung
gegengetestet.

### Eigene Seite, nicht die Ausdruck-Seite

`setup.py` legt die Prüfliste über `pruefliste_widget()` auf eine **eigene**
Grist-Seite (`PRUEFLISTE`), nicht neben die Druck-Widgets. Grund: eine
Grist-Freigabe geht über Seiten. Läge das Widget auf der Ausdruck-Seite,
bekäme die Zeiterfassungsstelle bei einer Freigabe zwangsläufig auch S1/S2,
Vermerke und Fahrtenbuch mit zu sehen.

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
