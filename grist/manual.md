# Handbuch

Anleitung zum Erfassen und Abrechnen einer Dienstreise mit Grist.
Technische Details zu den einzelnen Formeln: siehe [Formeln](formeln/README.md).

## Gliederung

1. [Der Prozess auf einen Blick](#der-prozess-auf-einen-blick)
2. [Ablauf](#ablauf)
3. [Die Tabellen im Überblick](#die-tabellen-im-überblick)
4. [Einrichten](#einrichten)
5. [Formular ausfüllen](#formular-ausfüllen)
6. [Einstellungen](#einstellungen)
7. [Orte pflegen](#orte-pflegen)
8. [Prüfen vor dem Drucken & Einreichung](#prüfen-vor-dem-drucken--einreichung)
9. [Drucken](#drucken)
10. ["Einkleben" und Unterschreiben](#einkleben-und-unterschreiben)
11. [Wenn sich das Formular ändert](#wenn-sich-das-formular-ändert)

---

## Der Prozess auf einen Blick

Von der Formulareingabe bis zur unterschriftsreifen Abrechnung sind nur drei
eigene Handgriffe nötig — alles dazwischen übernimmt die Tabelle automatisch:

1. **Formular ausfüllen** (pro Reise, am Handy)
2. **Abrechnungszeitraum setzen** (pro Abrechnung)
3. **Ausdrucken und unterschreiben**

**Was die Tabelle automatisch übernimmt, statt es von Hand zu tun:**

| Ohne dieses Tool | Mit dieser Tabelle |
|---|---|
| Kilometer manuell berechnen und plausibilisieren | automatisch berechnet, um private Umwege bereinigt |
| Tagegeld-Staffel per Hand anhand der Abwesenheitszeiten ermitteln | automatisch anhand der Zeitschwellen berechnet |
| Standardisierte Ausgabe S1/S2 von Hand ausfüllen | automatisch aus dem Abrechnungszeitraum befüllt |
| Fahrtenbuch manuell führen | automatisch als Druck-Fahrtenbuch erstellt |
| Route in Google Maps von Hand eintippen | fertiger Routenlink je Reise |
| Vermerke/Besonderheiten separat dokumentieren | automatisch aus „Sonstige Informationen" gesammelt |
| Reisenummerierung von Hand pflegen | automatisch fortlaufend je Kalenderjahr vergeben |
| Unbekannte Ziele in einer Extraliste sammeln | Freitext-Ziel legt automatisch eine Adresszeile an |

**Unterschiede zur Google-Sheets-Umsetzung:**

| | Google Sheets | Grist |
|---|---|---|
| Konto zum Erfassen | Google-Konto nötig | **keines** — der Formularlink genügt |
| Korrektur einer Reise | nur in der Formularantworten-Datei | direkt in der Tabelle `Reisen` |
| Neue Formularfrage | verschiebt alle folgenden Spalten, Bezüge prüfen | Formeln greifen über Spalten-IDs, kein Versatz |
| Ausgabe | eigene Blätter mit Formeln | ein Widget, das die Tabellen liest |

---

## Ablauf

1. **Vorlagendokument kopieren** — es wird immer in einer eigenen Kopie
   gearbeitet, nie im Vorlagendokument selbst.
2. **Tabelle `Einstellungen`** — einmalig Stammdaten und die eigene Adresse
   eintragen.
3. **Tabelle `Orte`** — die Adressen von `WO` (Wohnung) und `KV`
   (Dienststelle) nachtragen, weitere regelmäßige Ziele ergänzen.
4. **Formular veröffentlichen** und den Link auf dem Handy ablegen.
5. **Erfassen am Handy** — Formularlink öffnen, ausfüllen, absenden. Eine
   Reise pro Absendung.
6. **Abrechnen am PC** — auf der Seite `Ausdruck` den Abrechnungszeitraum
   setzen, **Aktualisieren**, **Drucken**.

---

## Die Tabellen im Überblick

Von Hand gepflegt werden nur `Einstellungen` und `Orte`. `Reisen` füllt das
Formular, `Adressen` entsteht von selbst.

| | Tabelle | Wozu sie da ist | Was hier zu tun ist |
|---|---|---|---|
| ✍️ | Einstellungen | Stammdaten der Person, eigene Wohn- und Dienstanschrift, Abrechnungszeitraum. Die **einzige** Stelle, an der persönliche Daten stehen | **Einrichten & pflegen.** Einmalig Name, Organisationseinheit, Anschriften; **pro Abrechnung** den Zeitraum setzen |
| ✍️ | Orte | Stammziele mit Kürzel und vollständiger Adresse — speist die Auswahlliste im Formular, den Routenlink und die Legende auf dem Ausdruck | **Pflegen.** `WO` und `KV` sind Pflichtzeilen, ihre Adresse eintragen; neue regelmäßige Ziele ergänzen |
| ✅ | Reisen | Eine Zeile je Dienstreise aus dem Formular, dazu alle Rechenspalten (Kilometer, Tagegeld-Stufe, Reiseweg, laufende Nummer, Routenlink) | **Nichts.** Eine Korrektur ist hier trotzdem möglich — anders als bei Google Sheets |
| ✍️ | Adressen | Die Einmalziele: sobald ein Ortsfeld als Freitext ausgefüllt wurde, entsteht hier automatisch eine Zeile | **Adresse nachtragen.** Straße/PLZ/Ort ergänzen, damit das Dienstorte-Blatt vollständig ist |
| 🖨️ | Ausdruck (Seite) | Abrechnungszeitraum und drei Widgets: Ausdruck (S1/S2, Vermerke, Dienstorte, Fahrtenbuch), Fahrtenbuch zum Einkleben, Routenlinks (Google Maps) | **Zeitraum setzen, aktualisieren, drucken bzw. Route öffnen** |

✍️ von Hand pflegen · ✅ läuft automatisch · 🖨️ ausdrucken/unterschreiben

**Automatisch berechnet und ausgegeben werden:**

- Tagegeld-Staffel (anteilig, >8h, ≥14h, 24h) je nach Abwesenheitsdauer
- Dienstlich gefahrene Kilometer, bereinigt um private Umwege
- Reiseweg als Text mit allen angefahrenen Orten (`WO > KV > WO`)
- Fahrt- und Nebenkosten: ÖPNV, Übernachtung, Mitnahme von Personen, Nebenkosten
- Google-Maps-Routenlink zur Reise
- Laufende Nummer und Vermerk-Kennung je Kalenderjahr

---

## Einrichten

Das Datenmodell legt `setup.py` an — Tabellen, Spalten, Formeln, die Seite
`Ausdruck` samt Widgets. Einzelheiten: [Einrichtung](formeln/setup.md).

```
cp grist/.env.beispiel grist/.env   # dort die drei Werte eintragen
python3 grist/setup.py
```

Das Skript ist wiederholbar: bestehende Spalten bleiben, fehlende kommen
hinzu, Rechenformeln werden auf den Stand des Codes gebracht. Von Hand
gesetzte Beschriftungen und Layouts bleiben unangetastet.

Danach bleiben zwei Handgriffe in der Oberfläche:

1. Formular-Widget auf `Reisen` anlegen — das Layout setzt `formular.py`
2. Formular veröffentlichen, dann **Duplicate Document** — das ist die Vorlage

---

## Formular ausfüllen

Ausfüllbar am PC oder auf dem Handy. **Ein Konto ist nicht nötig** — der
veröffentlichte Formularlink genügt. Das war der Grund für Grist: die
Erfassung passiert direkt nach der Fahrt, auf dem Handy, ohne Anmeldung.

Eine Absendung = eine Dienstreise. Das Formular gliedert sich in fünf
Abschnitte:

**1. Allgemeine Angaben zur Dienstreise**
- Reisedatum (bei mehrtägigen Reisen zusätzlich Enddatum, optional)
- Reisebeginn und Reiseende als Uhrzeit `HH:MM`
- Kilometerstand bei Beginn und Ende
- Privater Umweg (km, optional)
- Tachofotos (Beginn und Ende)

**2. Angefahrene Orte**

Sieben Felder: Ort Reisebeginn, Ort 1 bis Ort 5, Ort Reiseende. Jedes Feld
ist ein **Paar**:

- **Auswahlliste** aus `Orte` — für die regelmäßigen Ziele
- **Freitext** daneben — für alles, was nicht in der Liste steht

Ist die Auswahl gesetzt, gewinnt sie; der Freitext wird dann ignoriert.
Einmalziele sind der Normalfall, nicht die Ausnahme — deshalb das Paar.
Für jedes Freitext-Ziel entsteht automatisch eine Zeile in `Adressen`.

**3. Tagegeld**
- Tagegeld beantragen? (Ja/Nein)
- Aufenthalt an Dienststätte und am Dienstort (in Minuten)
- Privater Zeitabzug (Minuten, optional)

**4. Weitere Fahrt- und Nebenkosten**
- ÖPNV, Übernachtung, Nebenkosten (jeweils EUR)
- Mitnahme von Personen (Anzahl)

**5. Sonstiges und Nachweise**
- Unentgeltliche Verpflegung (Ja/Nein)
- Sonstige Informationen — erscheinen automatisch auf dem Blatt *Vermerke*
- Belege

---

## Einstellungen

Eine einzige Zeile, als Karte dargestellt: eine Zeile als Formular gelesen ist
eindeutiger als eine Zeile in einer Tabelle.

| Feld | Wofür |
|---|---|
| Vorname, Name, Organisationseinheit | Kopfzeile jedes Ausdrucks |
| Wohnort – Straße, PLZ, Ort | Kopfzeile („Wohnort") |
| Dienstort – Straße, PLZ, Ort | Kopfzeile („Dienstort") |
| Abrechnungszeitraum von / bis | **pro Abrechnung setzen** — bestimmt, welche Reisen ausgegeben werden |

Der Abrechnungszeitraum steht zusätzlich als Karte oben auf der Seite
`Ausdruck` — dort, wo gedruckt wird.

**Eine Kontoverbindung wird nicht erfasst.** IBAN- und BIC-Kasten bleiben im
S2-Vordruck stehen und werden, falls die Abrechnungsstelle sie überhaupt
braucht, von Hand ausgefüllt.

> **Zu beachten:** Die eigene Anschrift steht hier — und für Reiseweg und
> Routenlink zusätzlich als Zeile `WO` in `Orte`. Bei einem Umzug ändert sie
> sich an beiden Stellen.

---

## Orte pflegen

Die wiederkehrenden Ziele mit Kürzel und Adresse. Diese Liste ist die
Auswahlliste im Formular und die Legende auf dem Ausdruck.

| Spalte | Inhalt |
|---|---|
| Kürzel | erscheint im Reiseweg (`WO > KV > KITA > WO`) |
| Name der Einrichtung | erscheint auf dem Dienstorte-Blatt |
| Straße und Hausnummer, PLZ, Ort | speisen den Routenlink |
| Vollständige Adresse | Formel, wird nicht eingetragen |

`WO` (Wohnung) und `KV` (Dienststelle) legt `setup.py` als Pflichtzeilen an —
**ohne Adresse**. Die ist dort einmal nachzutragen, wie bei jedem anderen Ort
auch.

Ein Ziel, das nur einmal vorkommt, gehört **nicht** hierher: dafür ist das
Freitextfeld im Formular da. Es landet automatisch in `Adressen`.

---

## Prüfen vor dem Drucken & Einreichung

- **Abrechnungszeitraum** gesetzt? Er entscheidet, welche Reisen erscheinen.
- **Aktualisieren** im Widget gedrückt? Eine neu erfasste Reise erreicht den
  Ausdruck nicht von selbst — siehe [Drucken](#drucken).
- **Adressen** vollständig? Freitext-Ziele stehen zunächst ohne Straße und PLZ
  in der Tabelle `Adressen`; auf dem Dienstorte-Blatt bleibt die Adressspalte
  sonst leer.
- **Kilometer** plausibel? Ein Zahlendreher im Tachostand ergibt 0 dienstliche
  Kilometer, keine negative Zahl — er fällt also nicht durch einen Fehlerwert
  auf, sondern durch eine auffällig niedrige Zahl. Eine `0` auf S1 ist nicht
  zwangsläufig ein Fehler: bei einer Fahrt, die vollständig als „Privater
  Umweg" erfasst wurde (z. B. eine reine Verwaltungsfahrt ohne
  erstattungsfähige Strecke), ist sie das erwartete, gedruckte Ergebnis.
- Eine Korrektur ist direkt in der Tabelle `Reisen` möglich. Alle
  Rechenspalten ziehen sofort nach.

> **Mehrtägige Reisen:** Gefiltert wird über den **Reisebeginn**. Eine Reise,
> die vor dem Zeitraum beginnt und hineinreicht, gehört in die vorige
> Abrechnung und erscheint hier bewusst nicht.

---

## Drucken

Auf der Seite `Ausdruck` liegen drei Widgets:

| Widget | Inhalt |
|---|---|
| **Ausdruck** | S1, S2, Vermerke, Dienstorte und Fahrtenbuch — alle Seiten in einem Druckauftrag |
| **Fahrtenbuch (Schnittversion)** | dasselbe Fahrtenbuch, aber zum Ausschneiden und Einkleben aufgeteilt |
| **Routenlinks (Google Maps)** | keine Druckseite, sondern eine Arbeitsliste: je Reise ein klickbarer „Route"-Link, um die gefahrene Strecke in Google Maps nachzuvollziehen und zu prüfen |

Die beiden Druck-Widgets haben oben eine Leiste mit zwei Knöpfen:

- **Drucken** — öffnet den Druckdialog. Grist versteckt „Widget drucken" sonst
  im Drei-Punkte-Menü.
- **Aktualisieren** — baut den Ausdruck aus dem aktuellen Tabellenstand neu
  auf.

> **Wichtig:** Der Ausdruck baut sich beim Öffnen und bei jeder Änderung am
> Abrechnungszeitraum neu auf. Eine neu erfasste oder korrigierte **Reise**
> erreicht ihn **nicht** von selbst. Vor dem Drucken einmal **Aktualisieren**
> drücken.

**Routenlinks** hat nur **Aktualisieren** — es gibt dort nichts zu drucken,
nur Links zum Öffnen. Derselbe Hinweis gilt trotzdem: eine neu erfasste Reise
erscheint erst nach einem Klick auf **Aktualisieren**.

Was auf welchem Blatt landet:

| Blatt | Kopf aus | Zeilen aus |
|---|---|---|
| S1 / S2 | Einstellungen | Reisen im Zeitraum |
| Vermerke | Einstellungen | Reisen mit ausgefülltem Feld „Sonstige Informationen" |
| Dienstorte | Einstellungen | Orte (je höchstens einmal) + Adressen (je Eintrag, mit Datum) |
| Fahrtenbuch | — | Reisen im Zeitraum |
| Routenlinks | — | Reisen im Zeitraum |

**Spalte „Reiseweg" auf S1:** Der Vordruck verlangt dort nur die laufende
Nummer, „bei Führung eines Fahrtenbuches" — genau das steht im Spaltenkopf,
und ein Fahrtenbuch liegt bei dieser Ausgabe ohnehin immer bei. Statt den
Reiseweg dort ein zweites Mal zu zeigen, steht in der Zelle die
Zeitaufschlüsselung zur Tagegeld-Prüfung, z. B.:

> Nr. 67  –  (Ges.: 8:55 | DSt: 0:00 | DO: 0:00 | Rest: 8:55)

Ges. = Abwesenheit insgesamt, DSt = Aufenthalt Dienststätte, DO = Aufenthalt
Dienstort, Priv (nur falls eingetragen) = privater Zeitabzug, Rest = das,
was von der Tagegeld-Staffel übrig bleibt. Der eigentliche Reiseweg
(`WO > KV > WO`) steht stattdessen im Fahrtenbuch.

---

## "Einkleben" und Unterschreiben

- **Fahrtenbuch (Schnittversion)** bei **100 %** ausdrucken — nicht „an
  Seitengröße anpassen", sonst stimmen die Spaltenbreiten nicht.
- Je Zeilenblock entstehen zwei Seiten: links die Spalten 1–6, rechts 7–15.
  Die Hinweiszeile über jeder Seite sagt, welche Kante auszuschneiden ist.
- Ausschneiden, ins Fahrtenbuch einkleben, **Unterschrift von Hand** in die
  entsprechende Spalte.
- S1/S2 unterschreiben und wie üblich einreichen.

---

## Wenn sich das Formular ändert

Anders als bei Google Sheets verschiebt eine neue Formularfrage hier nichts:
Grist-Formeln greifen über die Spalten-ID (`$KM_Ende`), nicht über die
Spaltenposition. Ein Umbenennen der Beschriftung lässt die Formeln
unberührt.

Was trotzdem zu tun ist:

- **Neues Feld:** in `setup.py` in die passende Spaltenliste eintragen und das
  Skript erneut laufen lassen. Es ergänzt nur, was fehlt.
- **Mehr Zwischenziele:** `ZWISCHENZIELE` in `setup.py` erhöhen und das Skript
  erneut laufen lassen — Spalten, Formeln und das Ausgabe-Widget richten sich
  danach. Im Widget ist `ORT_SLOTS` mitzuziehen, siehe
  [Anhang](formeln/anhang.md).
- **Geändertes Formularlayout:** `formular.py` baut die Layout-Spezifikation
  des Formulars komplett neu — nur mit Ansage laufen lassen.
