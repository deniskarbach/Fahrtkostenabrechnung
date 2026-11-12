[← Formeln](README.md)

# Ausdruck

## Zweck

Die Seite ist der Ort, an dem abgerechnet wird: Hier wird der Abrechnungszeitraum gesetzt und gedruckt.
Sie gibt es, damit Zeitraum und Ausgabe an einer Stelle liegen und der Zeitraum nicht in den Einstellungen gesucht werden muss.
Sie umfasst zwei Custom Widgets: „Reisekostenabrechnung“ mit S1, S2, Vermerke und Ortsverzeichnis sowie „Fahrtenbuch“.

## Funktionsweise

- Der Zeitraum steht in [Einstellungen](einstellungen.md) (`Zeitraum_von`, `Zeitraum_bis`); eine Reise erscheint, wenn ihr Reisedatum darin liegt.
- **Aktualisieren** liest neu erfasste oder korrigierte Reisen ein.
- Die Widgets rechnen nichts Eigenes außer Summen und Formatierung; alle Werte kommen aus [Reisen](reisen.md).

| Widget | Enthält | Format |
|---|---|---|
| Reisekostenabrechnung | [S1](#s1), [S2](#s2), [Vermerke](#vermerke), [Ortsverzeichnis](#ortsverzeichnis) | A4 hoch |
| Fahrtenbuch | [Fahrtenbuch](#fahrtenbuch) | A4 quer |

## Formeln

Beide Widgets sind HTML-Seiten mit JavaScript ([`ausdruck.html`](grist/ausgabe/ausdruck.html ':ignore'), [`fahrtenbuch.html`](grist/ausgabe/fahrtenbuch.html ':ignore')). Sie lesen die Tabellen `Einstellungen`, `Stammziele` und `Reisen` und rechnen nur das, was unten steht; alles Übrige sind fertige Spalten aus [Reisen](reisen.md). Die Abschnitte nennen zuerst die gemeinsamen Berechnungen, dann je Bereich Zuordnung und Berechnung.

### Reisen im Zeitraum (beide Widgets)

```js
const imZeitraum = d => d != null && (von == null || d >= von) && (bis == null || d <= bis);
reisen = zeilen(fetchTable("Reisen")).filter(r => imZeitraum(r.Datum)).sort((a, b) => a.Datum - b.Datum)
```

- **Ergebnis:** die Reisen, deren Reisedatum zwischen `Zeitraum_von` und `Zeitraum_bis` liegt, beide Tage eingeschlossen, aufsteigend nach Datum.
- **Sonderfall:** Eine leere Grenze begrenzt nicht; ohne Datum erscheint eine Reise nie. Maßgeblich ist der Reisebeginn: Eine mehrtägige Reise, die vor `Zeitraum_von` beginnt, gehört zur früheren Abrechnung.

### Datum

```js
const tag = s => s == null ? "" : new Date(s * 1000).toLocaleDateString("de-DE",
  { day:"2-digit", month:"2-digit", year:"numeric", timeZone:"UTC" });
```

- **Ergebnis:** `TT.MM.JJJJ`. Grist liefert Datumswerte als Sekunden seit 1970 (UTC), `tag` rechnet sie um.

### Stunden:Minuten

```js
const stunden = min => {
  min = Math.round(min ?? 0);
  const vz = min < 0 ? "-" : "";
  min = Math.abs(min);
  return `${vz}${Math.trunc(min / 60)}:${String(min % 60).padStart(2, "0")}`;
};
```

- **Ergebnis:** Minuten als `H:MM`, z. B. `535` → `8:55`.
- **Sonderfall:** Auch über 24 Stunden (`26:30`); leer gilt als `0:00`.

## Widget „Reisekostenabrechnung“

### S1

Seite 1 des amtlichen Vordrucks: je Reise im Zeitraum eine Zeile mit Zeiten, Tagegeld, Kilometern und Kosten, darunter der Übertrag mit den Summen.

- Der Kopf kommt aus [Einstellungen](einstellungen.md).
- Läuft S1 über mehrere Seiten, wiederholt jede Folgeseite den Spaltenkopf; Titel und Antragsteller stehen nur auf Seite 1.
- Kosten von 0 bleiben leer. Kilometer stehen immer da, auch `0`. Negative Beträge erscheinen mit Minus und gehen in die Summe ein.

| S1-Spalte | Quelle |
|---|---|
| Reisedatum | `Datum`, mehrtägig als Spanne bis `Datum_bis` |
| Beginn / Ende | `Beginn`, `Ende` |
| Reiseweg | `Lfd_Nr` und Zeitaufschlüsselung (unten) |
| Tagegeld (drei Spalten) | Kreuz nach `Tagegeld_Stufe`; `anteilig` als `(X)` unter „mehr als 8 Stunden“ |
| Unentgeltliche Verpflegung | `Verpflegung`, leer = `Nein` |
| ÖPNV, km, Mitnahme, Übernachtung, Nebenkosten | `OePNV`, `KM_dienstlich`, `Mitnahme_Personen`, `Uebernachtung`, `Nebenkosten` |
| Übertrag | Summe jeder Kostenspalte über alle gelisteten Reisen |

**Spalte „Reiseweg“**

```
Nr. 67  –  (Ges.: 8:55 | DSt: 0:00 | DO: 0:00 | Rest: 8:55)
```

- **Ergebnis:** die laufende Nummer, dazu die Zeiten, aus denen sich die Tagegeld-Stufe ergibt: Ges. = `Abwesenheit_min`, DSt = `Min_Dienststaette`, DO = `Min_Dienstort`, Priv = `Min_privat_Abzug` (nur wenn eingetragen), Rest = `Rest_min`.
- **Sonderfall:** `Ges.: 0:00` heißt: Uhrzeit fehlt oder ist nicht lesbar.

**Berechnung (JavaScript)**

```js
const s1Zeile = r => {
  if (!r.Lfd_Nr) return "";
  const priv = r.Min_privat_Abzug > 0 ? ` | Priv: ${stunden(r.Min_privat_Abzug)}` : "";
  return `Nr. ${r.Lfd_Nr}  –  (Ges.: ${stunden(r.Abwesenheit_min)}`
       + ` | DSt: ${stunden(r.Min_Dienststaette)} | DO: ${stunden(r.Min_Dienstort)}`
       + `${priv} | Rest: ${stunden(r.Rest_min)})`;
};
```

- **Ergebnis:** der Text der Spalte „Reiseweg“; `Priv` erscheint nur bei einem privaten Zeitabzug über 0. Ohne laufende Nummer bleibt die Zelle leer.

```js
const kreuz   = (stufe, s) => stufe === s ? "X" : "";
const kreuz8h = stufe => stufe === "anteilig" ? "(X)" : kreuz(stufe, ">8h");
// Spalten: kreuz8h(stufe) · kreuz(stufe, ">=14h") · kreuz(stufe, "24h")
```

- **Ergebnis:** In genau einer der drei Tagegeld-Spalten steht ein Kreuz, nach `Tagegeld_Stufe`. `anteilig` erscheint als `(X)` unter „mehr als 8 Stunden“, weil der Vordruck keine eigene Spalte dafür hat.
- **Sonderfall:** Ohne Stufe bleiben alle drei Spalten leer.

```js
const eur  = n => n ? n.toLocaleString("de-DE", { minimumFractionDigits:2, maximumFractionDigits:2 }) : "";
const zahl = n => n ? String(n) : "";
summe[k] += r[k]   // k = oepnv, km, mitnahme, uebernachtung, neben
```

- **Ergebnis:** Beträge mit zwei Dezimalstellen und Dezimalkomma (`12,50`), Anzahlen als Zahl. Die Zeile „Übertrag“ summiert jede Kostenspalte über alle gelisteten Reisen. Die Kilometer werden als Zahl ausgegeben, die Summe ohne Formatierung.
- **Sonderfall:** `0` bleibt leer, Kilometer stehen immer da (auch `0`). Negative Beträge erscheinen mit Minus und gehen in die Summe ein. Die Verpflegung zeigt `Nein`, wenn nichts eingetragen ist (`r.Verpflegung || "Nein"`).

```js
datum: r.Datum_bis && r.Datum_bis !== r.Datum ? `${tag(r.Datum)} - ${tag(r.Datum_bis)}` : tag(r.Datum)
```

- **Ergebnis:** bei mehrtägigen Reisen die Spanne `03.02.2026 - 04.02.2026`, sonst ein Datum.

**Kopf (JavaScript)**

```js
antragsteller: [[e.Name, e.Vorname].filter(Boolean).join(" "), e.Organisationseinheit].filter(Boolean).join(", ")
anschrift = (strasse, plz, ort) => [strasse, [plz, ort].filter(Boolean).join(" ")].filter(Boolean).join(", ")
```

- **Ergebnis:** `Name Vorname, Organisationseinheit` und Anschriften als `Straße, PLZ Ort`. Leere Teile fallen samt Trennzeichen weg.

### S2

Seite 2 des amtlichen Vordrucks (Verfügungsteil). Vier Felder kommen aus [Einstellungen](einstellungen.md); ein leeres Feld bleibt als Linie zum Ausfüllen von Hand. IBAN und BIC bleiben leer.

| Feld auf S2 | Quelle |
|---|---|
| Abteilung | `Abteilung` |
| „… € bei:“ | `Buchungsstelle` |
| Ort vor dem Datum | `Behoerde_Ort` |
| unter „3. z. d. A.“ | `Behoerde` |

```js
el.textContent = wert || S2_LINIE[id];
```

- **Ergebnis:** der Wert aus [Einstellungen](einstellungen.md). Ist das Feld leer, bleibt die Linie der Vorlage stehen (zum Ausfüllen von Hand); sie wird beim ersten Lauf gemerkt, damit ein später geleertes Feld sie zurückbringt.

### Vermerke

Die „Sonstigen Informationen“ als Nachweis: nur Reisen im Zeitraum mit ausgefülltem `Vermerk`, nach Datum. Die Kennung (`V26-01`) steht auch im Fahrtenbuch, Spalte 15.

| Spalte | Quelle |
|---|---|
| Nr. | Nummer aus `Vermerk_Label` (`V26-01` → `01`) |
| Kennung | `Vermerk_Label` |
| Text | `Vermerk` |
| Datum | `Datum` |

```js
reisen.filter(r => r.Vermerk).map(r => ({ nr: (r.Vermerk_Label || "").split("-")[1] || "", label: r.Vermerk_Label, text: r.Vermerk, datum: tag(r.Datum) }))
```

- **Ergebnis:** je Reise mit Vermerk eine Zeile; die Nummer ist der Teil der Kennung nach dem Bindestrich (`V26-01` → `01`).

### Ortsverzeichnis

Die Legende zu den Kürzeln im Reiseweg. Gelistet wird, was im Zeitraum vorkommt:

1. `WO` und `KV` zuerst,
2. die übrigen Stammziele in der Reihenfolge ihres ersten Vorkommens, jedes nur einmal,
3. jedes Einzelziel einzeln, nach Datum; der Freitext steht ungeprüft unter „Adresse“.

| Spalte | Quelle |
|---|---|
| Kürzel | `Stammziele.Kuerzel` bzw. Kürzel aus `Reisen.Einzelziele` (`E26-07`) |
| Name | `Stammziele.Name` |
| Adresse | `Stammziele.Adresse` bzw. der Freitext |
| Datum (nur Einzelziele) | `Datum` der Reise |

```js
const stammIds = ["WO", "KV"].map(k => orteListe.find(o => o.Kuerzel === k)).filter(Boolean).map(o => o.id);
for (const r of reisen)
  for (const slot of ORT_SLOTS)
    if (r[slot] && orteNachId[r[slot]] && !stammIds.includes(r[slot])) stammIds.push(r[slot]);
```

- **Ergebnis:** die Stammziele, `WO` und `KV` zuerst, dann die übrigen in der Reihenfolge ihres ersten Vorkommens im Zeitraum (Slots: `Ort_Beginn`, `Ort_1` … `Ort_5`, `Ort_Ende`), jedes höchstens einmal.

```js
reisen.flatMap(r => (r.Einzelziele || "").split("\n").filter(Boolean).map(z => {
  const i = z.indexOf(": ");
  return { kuerzel: `${z.slice(0, i)}\n${tag(r.Datum)}`, name: "", adresse: z.slice(i + 2) };
}))
```

- **Ergebnis:** je Zeile aus `Reisen.Einzelziele` ein Eintrag: Kürzel (`E26-07`) und Reisedatum untereinander, der Freitext ungeprüft als Adresse.

Die Kürzel der Einzelziele zählt [`Reisen.Einzelziele`](reisen.md#einzelziele-einzelziele-ortsverzeichnis), nicht das Widget.

## Widget „Fahrtenbuch“

### Fahrtenbuch

Die Reisen als Zeilen für das amtliche Fahrtenbuch, Spalten 1–15: ausschneiden, einkleben, unterschreiben.

- Je Reise im Zeitraum eine Zeile.
- Gedruckt wird in Blöcken zu 17 Zeilen: eine Seite mit den Spalten 1–6, die nächste mit 7–15. Eine Hinweiszeile nennt die abzuschneidende Kante.
- Spalte 11 zeigt nur DSt und DO, damit die Zeile einzeilig bleibt. Die volle Aufschlüsselung steht in [S1](#s1) und in der [Prüfliste](pruefliste.md).

| Spalte | Quelle |
|---|---|
| 1 Lfd. Nr. | `Lfd_Nr` |
| 2/3 Monat, Tag | aus `Datum` |
| 4/5 von, bis | `Beginn`, `Ende` |
| 6 Reiseweg | `Reiseweg` |
| 7/8 Kilometerstand | `KM_Beginn`, `KM_Ende` |
| 9 dienstlich | `KM_dienstlich` |
| 10 außerdienstlich | `Umweg_privat` |
| 11 Name, Amtsbezeichnung | `DSt 1:00 \| DO 0:30` aus `Min_Dienststaette`, `Min_Dienstort` |
| 12–14 Kilometer, Vergütung, Unterschrift | leer, von Hand |
| 15 Vermerke | `Vermerk_Label` |

**Berechnung (JavaScript)**

```js
const monatTag = s => { const d = new Date(s * 1000);
  return { monat: zweistellig(d.getUTCMonth() + 1), tag: zweistellig(d.getUTCDate()) }; };
```

- **Ergebnis:** Spalten 2 und 3 als zweistellige Zahlen (`02`, `03`), aus dem Reisedatum in UTC.

```js
const fbZeit = r => !r.Lfd_Nr ? "" : `DSt ${stunden(r.Min_Dienststaette)} | DO ${stunden(r.Min_Dienstort)}`;
```

- **Ergebnis:** Spalte 11, z. B. `DSt 1:00 | DO 0:30`; beide Werte stehen immer da, auch `0:00`. Ohne laufende Nummer bleibt die Zelle leer.

```js
const ROWS_PRO_SEITE = 17;
bloecke = Math.max(1, Math.ceil(fahrten.length / ROWS_PRO_SEITE))
```

- **Ergebnis:** Die Reisen werden in Blöcken zu 17 Zeilen gedruckt, je Block eine Seite mit den Spalten 1–6 und eine mit 7–15. Die Hinweiszeile nennt die Seitenzahl und die abzuschneidende Kante.
- **Sonderfall:** Ohne Reisen entsteht ein leeres Blattpaar mit Spaltenköpfen. `Umweg_privat` ohne Eintrag wird `0`.
