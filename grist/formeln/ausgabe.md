[← Formeln-Übersicht](README.md)

# Ausgabe

Drei Widgets lesen die Tabellen und setzen daraus die Druckseiten. Sie rechnen
nichts Eigenes außer Summen und Formatierung — alle Werte kommen aus den
Rechenspalten.

| Widget | Seite in Grist | Blätter |
|---|---|---|
| Reisekostenabrechnung ([`ausdruck.html`](../ausgabe/ausdruck.html ':ignore')) | Ausdruck | S1, S2, Vermerke, Ortsverzeichnis — A4 hoch |
| Fahrtenbuch ([`fahrtenbuch.html`](../ausgabe/fahrtenbuch.html ':ignore')) | Ausdruck | Fahrtenbuch zum Einkleben — A4 quer |
| Prüfliste ([`pruefliste.html`](../ausgabe/pruefliste.html ':ignore')) | Prüfliste | eine Zeile je Reise — A4 quer |

| Blatt | Kopf aus | Zeilen aus |
|---|---|---|
| S1 / S2 | Einstellungen | Reisen im Zeitraum |
| Vermerke | Einstellungen | Reisen im Zeitraum mit `Vermerk` |
| Ortsverzeichnis | Einstellungen | Stammziele (je höchstens einmal) + Einzelziele |
| Fahrtenbuch | — | Reisen im Zeitraum |
| Prüfliste | Einstellungen | Reisen im Zeitraum + Orte-Legende |

## Zeitraum

Eine Reise erscheint, wenn ihr **Reisedatum** (`Datum`) zwischen
`Zeitraum_von` und `Zeitraum_bis` liegt, beide Tage eingeschlossen. Eine leere
Grenze begrenzt nicht; ist gar kein Zeitraum gesetzt, erscheinen alle Reisen.
Reisen ohne Datum erscheinen nie.

Maßgeblich ist der Reisebeginn: Eine mehrtägige Reise, die vor `Zeitraum_von`
beginnt, gehört zur früheren Abrechnung und erscheint hier nicht — sonst würde
sie zweimal abgerechnet.

## S1 — Reisekostenabrechnung

Je Reise eine Zeile, darunter der Übertrag mit den Summen.

| S1-Spalte | Quelle |
|---|---|
| Reisedatum | `Datum`, mehrtägig als Spanne bis `Datum_bis` |
| Beginn / Ende | `Beginn`, `Ende` |
| Reiseweg | `Lfd_Nr` und Zeitaufschlüsselung, siehe unten |
| Tagegeld (drei Spalten) | Kreuz nach `Tagegeld_Stufe`; `anteilig` als `(X)` unter „mehr als 8 Stunden“ |
| Unentgeltliche Verpflegung | `Verpflegung`, leer = `Nein` |
| ÖPNV, km, Mitnahme, Übernachtung, Nebenkosten | `OePNV`, `KM_dienstlich`, `Mitnahme_Personen`, `Uebernachtung`, `Nebenkosten` |

**Spalte „Reiseweg“:** Der Vordruck verlangt hier die laufende Nummer, wenn
ein Fahrtenbuch geführt wird — das liegt immer bei. Dazu stehen die Zeiten,
aus denen sich die Tagegeld-Stufe ergibt:

```
Nr. 67  –  (Ges.: 8:55 | DSt: 0:00 | DO: 0:00 | Rest: 8:55)
```

Ges. = `Abwesenheit_min`, DSt = `Min_Dienststaette`, DO = `Min_Dienstort`,
Priv = `Min_privat_Abzug` (nur wenn eingetragen), Rest = `Rest_min`. Der
Reiseweg selbst steht im Fahrtenbuch.

**Nullen und Minus:** Kosten von 0 bleiben leer, damit der Vordruck lesbar
bleibt. Kilometer stehen immer da, auch `0` — eine leere Zelle sähe nach
vergessener Eingabe aus. Negative Beträge erscheinen mit Minus, weil sie auch
in die Summe eingehen.

Läuft S1 über mehrere Seiten, wiederholt jede Folgeseite den Spaltenkopf;
Titel und Antragsteller stehen nur auf Seite 1.

## S2

Der amtliche Vordruck, Zelle für Zelle aus der Excel-Vorlage übernommen. Aus
der Tabelle kommen nur `Abteilung`, `Buchungsstelle`, `Behoerde_Ort` und
`Behoerde` aus [Einstellungen](einstellungen.md); leer bleibt dort die Linie.
IBAN und BIC bleiben leer und werden bei Bedarf von Hand eingetragen.

## Vermerke

Nur Reisen mit ausgefülltem `Vermerk`.

| Spalte | Quelle |
|---|---|
| Nr. | Nummer aus `Vermerk_Label` (`V26-01` → `01`) |
| Kennung | `Vermerk_Label` |
| Text | `Vermerk` |
| Datum | `Datum` |

## Ortsverzeichnis

Die Legende zu den Kürzeln im Reiseweg, kein Fahrtenprotokoll:

1. `WO` und `KV` zuerst,
2. dann die übrigen Stammziele in der Reihenfolge, in der sie im Zeitraum
   zum ersten Mal vorkommen — jedes nur einmal,
3. dann jedes Einzelziel einzeln, nach Datum: Kürzel und Datum, daneben der
   Freitext ungeprüft unter „Adresse“.

Die Kürzel der Einzelziele kommen aus
[`Reisen.Einzelziele`](reisen.md#einzelziele--einzelziele-ortsverzeichnis);
das Widget zählt nicht selbst, damit Fahrtenbuch und Ortsverzeichnis nicht
auseinanderlaufen.

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
| 11 Name, Amtsbezeichnung | `DSt 1:00 \| DO 0:30` aus `Min_Dienststaette`, `Min_Dienstort` |
| 12–14 Kilometer, Vergütung, Unterschrift | leer, von Hand |
| 15 Vermerke | `Vermerk_Label` |

Gedruckt wird zum Einkleben in das Original-Fahrtenbuch: je Block 17 Zeilen
wie im Original, auf einer Seite die Spalten 1–6, auf der nächsten 7–15.
Spalte 11 zeigt nur DSt und DO, damit die Zeile einzeilig bleibt und beide
Hälften gleich hoch sind; die volle Aufschlüsselung steht auf S1 und in der
Prüfliste.

## Prüfliste

Für die Zeiterfassungsstelle: alles, was sonst auf S1, Vermerken,
Ortsverzeichnis und Fahrtenbuch verteilt ist, in **einer Zeile je Reise**.
Die Spaltenbegriffe sind die aus S1.

| Gruppe | Spalten | Quelle |
|---|---|---|
| — | Nr., Reisedatum | `Lfd_Nr`, `Datum` (mehrtägig als Spanne) |
| Uhrzeit | Beginn, Ende | `Beginn`, `Ende` |
| — | Reiseweg | `Reiseweg` |
| Tagegeld für | Ges., DSt, DO, Priv, Rest, Stufe | `Abwesenheit_min`, `Min_Dienststaette`, `Min_Dienstort`, `Min_privat_Abzug`, `Rest_min`, `Tagegeld_Stufe` |
| — | Unentgeltliche Verpflegung | `Verpflegung` |
| Kilometerstand | Beginn, Ende | `KM_Beginn`, `KM_Ende` |
| Wegstrecke | privat, dienstl. | `Umweg_privat`, `KM_dienstlich` |
| Fahrt- und Nebenkosten | ÖPNV, Mitn., Übernachtung, Nebenkosten | `OePNV`, `Mitnahme_Personen`, `Uebernachtung`, `Nebenkosten` |
| — | Vermerk, Route | `Vermerk_Label`, `Maps_Link` |

Darunter die Orte-Legende, zeilengleich mit dem Ortsverzeichnis.

Die Prüfliste liegt auf einer **eigenen Seite**, weil Grist Seiten einzeln
freigibt: So sieht die Zeiterfassungsstelle nur diese Liste, nicht S1/S2 und
Fahrtenbuch.

Wie die Widgets technisch arbeiten: [Einrichtung und Technik](setup.md#ausgabe-widgets).
