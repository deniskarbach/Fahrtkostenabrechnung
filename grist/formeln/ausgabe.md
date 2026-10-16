[← Formeln-Übersicht](README.md)

# Ausgabe

Was in der Google-Sheets-Umsetzung eigene Blätter mit Formeln sind, ist hier
**ein Widget**, das die vier Tabellen liest und daraus die Druckseiten baut:
[`ausgabe/ausdruck.html`](../ausgabe/ausdruck.html ':ignore') — S1, S2, Vermerke und
Ortsverzeichnis, A4 hoch, eine Datei ohne Abhängigkeiten. Ein Widget
statt vier, ein Grist-Zugriff statt vier. In Grist heißt es „Reisekostenabrechnung“.

Das Fahrtenbuch (quer) ist herausgelöst und steht in
[`ausgabe/fahrtenbuch-preview.html`](../ausgabe/fahrtenbuch-preview.html ':ignore') — eine
Vorbereitung, noch kein Widget. Der Abschnitt [Fahrtenbuch](#fahrtenbuch)
beschreibt diese Datei.

Daneben steht ein eigenständiges Widget, kein Bestandteil der
Standardausgabe:
[`ausgabe/fahrtenbuch.html`](../ausgabe/fahrtenbuch.html ':ignore')
(das Fahrtenbuch, aber zum Ausschneiden und Einkleben aufgeteilt).

Dazu [`ausgabe/pruefliste.html`](../ausgabe/pruefliste.html ':ignore') auf einer
eigenen Seite: alles aus allen Blättern in einer Zeile je Reise, für die
Zeiterfassungsstelle — siehe [unten](#prüfliste-zeiterfassungsstelle).

Alle drei Dateien lassen sich direkt im Browser öffnen — dann rendern sie
erfundene Beispieldaten. Das ist die Arbeitsweise für Layoutänderungen ohne
Grist.

## Was auf welchem Blatt landet

| Blatt | Kopf aus | Zeilen aus |
|---|---|---|
| S1 / S2 | Einstellungen | Reisen im Zeitraum |
| Vermerke | Einstellungen | Reisen im Zeitraum **mit** `Vermerk` |
| Ortsverzeichnis | Einstellungen | Stammziele (je höchstens einmal) + Einzelziele (je Eintrag, mit Kürzel und Datum) |
| Fahrtenbuch | — | Reisen im Zeitraum |
| Prüfliste | Einstellungen | Reisen im Zeitraum + Stammziele/Einzelziele als Legende |

## Zeitraumfilter

```js
const imZeitraum = d => d != null
  && (von == null || d >= von) && (bis == null || d <= bis);
```

Angewandt auf `Reisen.Datum`; die Einzelziele kommen aus denselben Reisen. Maßgeblich ist der
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
| drei Tagegeld-Spalten | Kreuz aus `Tagegeld_Stufe`; `anteilig` als `(X)` in „mehr als 8 Stunden" |
| Verpflegung | `Verpflegung`, leer → `Nein` |
| ÖPNV, km, Mitnahme, Übernachtung, Nebenkosten | `OePNV`, `KM_dienstlich`, `Mitnahme_Personen`, `Uebernachtung`, `Nebenkosten` |

**Statement:**
- `kreuz(stufe, s)` – setzt `X` in genau die Spalte, deren Name der Stufe entspricht
- `kreuz8h(stufe)` – wie `kreuz` für `>8h`, zusätzlich `(X)` bei `anteilig`: der amtliche Vordruck hat keine eigene Spalte „Tagegeld anteilig"
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

## Ortsverzeichnis

Die Legende zum Reiseweg, **kein Fahrtenprotokoll**. Deshalb steht jedes
Stammziel höchstens einmal darin.

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
- die Doppelschleife hängt die übrigen Stammziele in der Reihenfolge ihres **ersten Vorkommens** im Zeitraum an
- `!stammIds.includes(…)` – jeder Ort nur einmal

**Ergebnis:** Nummerierte Liste — 1 Wohnung, 2 Dienststätte, danach die
übrigen Stammziele, danach die Einzelziele nach Datum.
**Sonderfall:** Ohne diese Entdopplung erschiene die Wohnung bei zwei Reisen
viermal, je einmal als Start und als Ziel. Das war ein stiller Fehler; dagegen
läuft [`test_ortsverzeichnis.mjs`](../ausgabe/test_ortsverzeichnis.mjs).

Die Einzelziele folgen danach, jede Eintragung als eigene Zeile, nach Datum
sortiert. Sie kommen aus der Rechenspalte
[`Reisen.Einzelziele`](reisen.md#einzelziele--einzelziele-ortsverzeichnis),
die auch das Kürzel vergibt — das Widget zählt nicht selbst, sonst könnten
Fahrtenbuch und Ortsverzeichnis auseinanderlaufen.

```js
const ausEinzelziele = reisen.flatMap(r => (r.Einzelziele || "").split("\n")
  .filter(Boolean).map(z => {
    const i = z.indexOf(": ");
    return { kuerzel: `${z.slice(0, i)}\n${tag(r.Datum)}`, name: "", adresse: z.slice(i + 2) };
  }));
```

In der Spalte *Kürzel / Datum* steht oben das Kürzel aus dem Reiseweg
(`E26-07`), darunter das Datum der Fahrt. Der Freitext steht vollständig und **ungeprüft** unter
*Adresse*, die Namensspalte bleibt leer. Ob die Anschrift vollständig ist,
kontrolliert die Person beim Unterschreiben.

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
| 11 Name, Amtsbezeichnung | im Ausdruck leer; in der Schnittversion die Zeitwerte, siehe unten |
| 12–14 Kilometer, Vergütungsbetrag, Unterschrift | bleiben leer, von Hand |
| 15 Vermerke | `Vermerk_Label` |

Die **Schnittversion** bricht dieselben Daten auf zwei Seiten je Zeilenblock um:
links die Spalten 1–6, rechts 7–15. Bei **100 %** drucken, an der bezeichneten
Kante schneiden, einkleben, unterschreiben.

### Spalte 11 der Schnittversion

```js
const fbZeit = r => !r.Lfd_Nr ? "" :
    `Ges ${stunden(r.Abwesenheit_min)} | Rest ${stunden(r.Rest_min)}\n`
  + `DSt ${stunden(r.Min_Dienststaette)} | DO ${stunden(r.Min_Dienstort)}`
  + ` | Pr ${stunden(r.Min_privat_Abzug)}`;
```

**Ergebnis:** `Ges 10:00 | Rest 7:45` über `DSt 1:00 | DO 0:30 | Pr 0:45` —
dieselben Zeiten wie in der [S1-Spalte „Reiseweg"](#spalte-reiseweg), wie in
der Sheets-Version (Druck-Fahrtenbuch K4).
**Sonderfall:** Anders als auf S1 erscheint der private Abzug (Pr) immer, auch
mit 0:00. Die Zelle ist in 5,6 pt gesetzt und bricht nur am festen Umbruch:
eine dritte Zeile würde die Zeile höher machen als ihr Gegenstück auf der
linken Seite, und die beiden Hälften passten nicht mehr aneinander.

## Prüfliste (Zeiterfassungsstelle)

Eigenes Widget, [`ausgabe/pruefliste.html`](../ausgabe/pruefliste.html ':ignore') --
**ohne Vorbild in der Sheets-Umsetzung.** Dort muss die Stelle, die den Antrag
final bearbeitet, zwischen S1, Vermerken, Ortsverzeichnis, Fahrtenbuch und
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
[Ortsverzeichnis](#ortsverzeichnis), damit die Kürzel im Reiseweg ohne Blattwechsel
auflösbar sind.

### Drucken: eigenes Fenster, und warum nicht 277mm

Zwei Fallen, beide aufgetreten:

- **`window.print()` aus dem Widget öffnete den Dialog in Hochformat.**
  Beobachtet, Ursache **nicht abschließend geklärt**: eine naheliegende
  Erklärung wäre, dass der Dialog die `@page`-Regel aus dem iframe nicht
  übernimmt — die galt zunächst als widerlegt, weil `ausdruck.html` sein
  damaliges Fahrtenbuch (`@page fahrtenbuch { size: A4 landscape }`) unter
  macOS/Chrome korrekt quer druckte; unter Windows/Edge fiel es später
  genauso auf Hochformat zurück. `drucken()` schreibt das fertige Blatt deshalb in ein
  **eigenes Fenster**, wo es Top-Level-Dokument ist und `@page` in jedem Fall
  greift — das umgeht die offene Frage, statt sie zu beantworten.
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
- Route-Zelle: kein `html\`…\`` (ein eingebettetes `<a>` würde escaped);
  der Link steht erst als `data-link` (läuft durch `esc()`) und wird danach
  per DOM-API (`a.href = …`) zum `<a>`. Leerer `Maps_Link` (unter zwei Orten
  oder Ort ohne Anschrift) → Zelle ohne Link, kein Fehler

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
`.dok-s2`, `.dok-vermerke`, `.dok-ortsverzeichnis`), damit
gleichnamige Klassen sich nicht in die Quere kommen.

Die Widgets werden über GitHub Pages ausgeliefert. Eine Änderung wirkt erst
nach `git push`; im Grist-Tab danach hart neu laden, sonst steckt die alte
Fassung im Browser-Cache.
