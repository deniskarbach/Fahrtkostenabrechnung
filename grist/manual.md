# Handbuch

Anleitung zum Erfassen und Abrechnen einer Dienstreise mit Grist.
Technische Details zu den einzelnen Formeln: siehe [Formeln](formeln/README.md).

## Gliederung

1. [Der Prozess auf einen Blick](#der-prozess-auf-einen-blick)
2. [Ablauf](#ablauf)
3. [Die Tabellen im Überblick](#die-tabellen-im-überblick)
4. [Formular ausfüllen](#formular-ausfüllen)
5. [Einstellungen](#einstellungen)
6. [Stammziele pflegen](#stammziele-pflegen)
7. [Prüfen vor dem Drucken & Einreichung](#prüfen-vor-dem-drucken--einreichung)
8. [Drucken](#drucken)
9. [Prüfliste für die Zeiterfassungsstelle](#prüfliste-für-die-zeiterfassungsstelle)
10. ["Einkleben" und Unterschreiben](#einkleben-und-unterschreiben)

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
| Vermerke/Besonderheiten separat dokumentieren | automatisch aus „Sonstige Informationen“ gesammelt |
| Reisenummerierung von Hand pflegen | automatisch fortlaufend je Kalenderjahr vergeben |
| Einmalige Ziele samt Anschrift in einer Extraliste sammeln | Freitext-Ziel steht mit Kürzel und Datum im Ortsverzeichnis |


---

## Ablauf

Einmalig beim Einrichten:

1. **Vorlagendokument kopieren** — es wird immer in einer eigenen Kopie
   gearbeitet, nie im Vorlagendokument selbst.
2. **Seite `Einstellungen`** — Stammdaten und die eigene Adresse eintragen,
   siehe [Einstellungen](#einstellungen).
3. **Seite `Stammziele`** — die Adressen von `WO` (Wohnung) und `KV`
   (Dienststelle) nachtragen, weitere regelmäßige Ziele ergänzen, siehe
   [Stammziele pflegen](#stammziele-pflegen).
4. **Formular veröffentlichen** — auf der Seite `Formularverwaltung`, und den
   Link auf dem Handy ablegen. Das geschieht in der **eigenen Kopie**: der
   Formularlink der Vorlage schreibt nicht in die eigene Tabelle.

Danach je Reise und je Abrechnung:

5. **Erfassen am Handy** — Formularlink öffnen, ausfüllen, absenden. Eine
   Reise pro Absendung, siehe [Formular ausfüllen](#formular-ausfüllen).
6. **Abrechnen am PC** — auf der Seite `Ausdruck` den Abrechnungszeitraum
   setzen, **Aktualisieren**, **Drucken**, siehe [Drucken](#drucken).

---

## Die Tabellen im Überblick

Von Hand gepflegt werden nur `Einstellungen` und `Stammziele`. `Reisen` füllt das
Formular.

| | Tabelle | Wozu sie da ist | Was hier zu tun ist |
|---|---|---|---|
| ✍️ | Einstellungen | Stammdaten der Person, eigene Wohn- und Dienstanschrift. Die **einzige** Stelle, an der persönliche Daten stehen | **Einrichten & pflegen.** Einmalig Name, Organisationseinheit, Anschriften |
| ✍️ | Stammziele | Stammziele mit Kürzel und vollständiger Adresse — speist die Auswahlliste im Formular, den Routenlink und die Legende auf dem Ausdruck | **Pflegen.** Links Ziel wählen, rechts ändern. `WO` und `KV` sind Pflichtzeilen, ihre Adresse eintragen; neue regelmäßige Ziele in der leeren Zeile unten in der Liste ergänzen |
| ✅ | Reisen (nur Raw Data) | Eine Zeile je Dienstreise aus dem Formular, dazu alle Rechenspalten (Kilometer, Tagegeld-Stufe, Reiseweg, laufende Nummer, Routenlink). Keine eigene Seite | **Nichts.** Korrigiert wird auf der Seite `Reisekorrektur` |
| ✍️ | Reisekorrektur (Seite) | Oben Jahr und Monat als Filter, darunter links die Reisen dieses Zeitraums (nur das Datum), rechts die gewählte Reise als Karte mit denselben Feldern wie im Formular | **Jahr/Monat wählen, Reise anklicken, rechts ändern.** Ohne Jahr gilt das laufende, ohne Monat das ganze Jahr. |
| 🖨️ | Ausdruck (Seite) | Abrechnungszeitraum und die Widgets Reisekostenabrechnung (S1/S2, Vermerke, Ortsverzeichnis), Fahrtenbuch zum Einkleben. Der Zeitraum wird **nur hier** gesetzt | **Pro Abrechnung Zeitraum setzen, aktualisieren, drucken** |
| 🖨️ | Prüfliste (eigene Seite) | Alles aus allen Blättern in einer Zeile je Reise — für die Zeiterfassungsstelle, die den Antrag final bearbeitet | **Nichts.** Getrennt freigebbar, siehe unten |
| ⚙️ | Formularverwaltung (Seite, letzte) | Das Formular-Widget, über das jede Reise in die Tabelle `Reisen` geschrieben wird. Ohne diese Seite gibt es keinen Formularlink: die Veröffentlichung hängt an ihr | **Nur beim Einrichten:** Formular veröffentlichen, Link aufs Handy. Die Seite nicht löschen, sonst funktioniert der Link nicht mehr |

✍️ von Hand pflegen · ✅ läuft automatisch · 🖨️ ausdrucken/unterschreiben · ⚙️ nur beim Einrichten

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

**2. Angefahrene Orte**

Sieben Felder: Ort Reisebeginn, Ort 1 bis Ort 5, Ort Reiseende. Jedes Feld
ist ein **Paar**:

- **Auswahlliste** aus `Stammziele` — für die regelmäßigen Ziele
- **Freitext** daneben — für alles, was nicht in der Liste steht

Je Ort **entweder** aus der Liste wählen **oder** darunter eintragen. Was
eingetragen ist, wird gedruckt: Sind beide Felder gefüllt, erscheinen im
Reiseweg zwei Stopps (`WO > KITA > E26-07 > WO`). Dann in der Reisekorrektur
das falsche Feld leeren.

Im Freitext steht **Bezeichnung, Straße Hausnummer, PLZ Ort**, getrennt durch
Kommas oder Zeilenumbrüche, z. B. `Café Mokka, Bahnhofstr. 7, 12345
Musterstadt`. Der Text wird nicht geprüft: Er steht so, wie er erfasst wurde,
im Ortsverzeichnis — mit Kürzel und Datum (`E26-07`, darunter `03.02.2026`).
Im Reiseweg steht nur das Kürzel (`WO > E26-07 > KV > WO`). Ob die Anschrift vollständig ist, sieht
die Person beim Unterschreiben im Ortsverzeichnis.

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
| Wohnort – Straße, PLZ, Ort | Kopfzeile („Wohnort“) |
| Dienstort – Straße, PLZ, Ort | Kopfzeile („Dienstort“) |
| Abteilung, Buchungsstelle, Behörde (Ort, Name) | S2, Verfügungsteil. Leer bleibt dort die Linie zum Ausfüllen von Hand |

Der Abrechnungszeitraum steht **nicht** hier, sondern nur als Karte oben auf
der Seite `Ausdruck` — dort, wo gedruckt wird.

**Eine Kontoverbindung wird nicht erfasst.** IBAN- und BIC-Kasten bleiben im
S2-Vordruck stehen und werden, falls die Abrechnungsstelle sie überhaupt
braucht, von Hand ausgefüllt.

> **Zu beachten:** Die eigene Anschrift steht hier — und für Reiseweg und
> Routenlink zusätzlich als Zeile `WO` in `Stammziele`. Bei einem Umzug ändert sie
> sich an beiden Stellen.

---

## Stammziele pflegen

Die wiederkehrenden Ziele mit Kürzel und Adresse. Diese Liste ist die
Auswahlliste im Formular und die Legende auf dem Ausdruck. Aufbau wie auf
`Reisekorrektur`: links die Liste (nur Kürzel), rechts die Karte des
gewählten Ziels zum Bearbeiten.

**Neues Ziel anlegen:** in der leeren Zeile ganz unten in der Liste das Kürzel
eintragen, dann rechts Name, Straße, PLZ und Ort ausfüllen. Ohne vollständige
Anschrift bekommt keine Reise über dieses Ziel einen Routenlink.

| Spalte | Inhalt |
|---|---|
| Kürzel | erscheint im Reiseweg (`WO > KV > KITA > WO`) |
| Name der Einrichtung | erscheint im Ortsverzeichnis |
| Straße und Hausnummer, PLZ, Ort | speisen den Routenlink |
| Vollständige Adresse | Formel, wird nicht eingetragen |

`WO` (Wohnung) und `KV` (Dienststelle) sind als Pflichtzeilen schon angelegt —
**ohne Adresse**. Die ist dort einmal nachzutragen, wie bei jedem anderen Ort
auch.

Ein Ziel, das nur einmal vorkommt, gehört **nicht** hierher: dafür ist das
Freitextfeld im Formular da. Es landet mit Kürzel und Datum im Ortsverzeichnis.

---

## Prüfen vor dem Drucken & Einreichung

- **Abrechnungszeitraum** gesetzt? Er entscheidet, welche Reisen erscheinen.
- **Aktualisieren** im Widget gedrückt? Eine neu erfasste Reise erreicht den
  Ausdruck nicht von selbst — siehe [Drucken](#drucken).
- **Anschriften** vollständig? Im Ortsverzeichnis steht jedes Einzelziel
  (`E26-07`, `E26-08` …) mit dem Freitext, wie er erfasst wurde. Fehlt etwas, wird es
  im Freitext der Reise auf der Seite `Reisekorrektur` ergänzt.
- **Keine negativen Werte**: Minuten und Beträge immer positiv eintragen. Ein
  Minus zählt bei den Minuten als 0; ein negativer Betrag steht mit Minus im
  Ausdruck und zieht die Summe herunter.
- **Kilometer** plausibel? Ein Zahlendreher im Tachostand ergibt 0 dienstliche
  Kilometer, keine negative Zahl — er fällt also nicht durch einen Fehlerwert
  auf, sondern durch eine auffällig niedrige Zahl. Eine `0` auf S1 ist nicht
  zwangsläufig ein Fehler: bei einer Fahrt, die vollständig als „Privater
  Umweg“ erfasst wurde (z. B. eine reine Verwaltungsfahrt ohne
  erstattungsfähige Strecke), ist sie das erwartete, gedruckte Ergebnis.
- Eine Korrektur geht auf der Seite `Reisekorrektur`: oben Jahr eintragen
  (mit **Enter** bestätigen) und Monat wählen — die Liste links zeigt dann
  die Reisen dieses Zeitraums, die neueste oben. Ohne Jahr gilt das laufende,
  ohne Monat das ganze Jahr. Der Filter wirkt nur auf diese Liste, nicht auf
  den Ausdruck. Reise anklicken, rechts ändern. Alle Rechenspalten ziehen sofort nach. Ein
  geändertes Datum nummeriert die laufenden Nummern neu.
- Unbekannte Orte dort ins Freitextfeld schreiben, nicht über „+ neu“ in der
  Auswahlliste anlegen — sonst landet das Einzelziel dauerhaft in
  `Stammziele`.

> **Mehrtägige Reisen:** Gefiltert wird über den **Reisebeginn**. Eine Reise,
> die vor dem Zeitraum beginnt und hineinreicht, gehört in die vorige
> Abrechnung und erscheint hier bewusst nicht.

---

## Drucken

Auf der Seite `Ausdruck` liegen zwei Widgets:

| Widget | Inhalt |
|---|---|
| **Reisekostenabrechnung** | S1, S2, Vermerke und Ortsverzeichnis — alle Seiten in einem Druckauftrag |
| **Fahrtenbuch** | das Fahrtenbuch, aber zum Ausschneiden und Einkleben aufgeteilt |

Beide Widgets haben oben eine Leiste mit zwei Knöpfen:

- **Drucken** — öffnet den Druckdialog. Grist versteckt „Widget drucken“ sonst
  im Drei-Punkte-Menü.
- **Aktualisieren** — baut den Ausdruck aus dem aktuellen Tabellenstand neu
  auf.

> **Wichtig:** Der Ausdruck baut sich beim Öffnen und bei jeder Änderung am
> Abrechnungszeitraum neu auf. Eine neu erfasste oder korrigierte **Reise**
> erreicht ihn **nicht** von selbst. Vor dem Drucken einmal **Aktualisieren**
> drücken.

Was auf welchem Blatt landet:

| Blatt | Kopf aus | Zeilen aus |
|---|---|---|
| S1 / S2 | Einstellungen | Reisen im Zeitraum |
| Vermerke | Einstellungen | Reisen mit ausgefülltem Feld „Sonstige Informationen“ |
| Ortsverzeichnis | Einstellungen | Stammziele (je höchstens einmal) + Einzelziele (je Eintrag, mit Kürzel und Datum) |
| Fahrtenbuch | — | Reisen im Zeitraum |

**Spalte „Reiseweg“ auf S1:** Der Vordruck verlangt dort nur die laufende
Nummer, „bei Führung eines Fahrtenbuches“ — genau das steht im Spaltenkopf,
und ein Fahrtenbuch liegt bei dieser Ausgabe ohnehin immer bei. Statt den
Reiseweg dort ein zweites Mal zu zeigen, steht in der Zelle die
Zeitaufschlüsselung zur Tagegeld-Prüfung, z. B.:

> Nr. 67  –  (Ges.: 8:55 | DSt: 0:00 | DO: 0:00 | Rest: 8:55)

Ges. = Abwesenheit insgesamt, DSt = Aufenthalt Dienststätte, DO = Aufenthalt
Dienstort, Priv (nur falls eingetragen) = privater Zeitabzug, Rest = das,
was von der Tagegeld-Staffel übrig bleibt. Der eigentliche Reiseweg
(`WO > KV > WO`) steht stattdessen im Fahrtenbuch.

---

## Prüfliste für die Zeiterfassungsstelle

Die Stelle, die den Antrag final bearbeitet, müsste sonst zwischen fünf
Blättern blättern, um eine einzelne Reise vollständig zu beurteilen. Die
**Prüfliste** legt alles davon in **eine Zeile je Reise**:

Nr. · Reisedatum · Uhrzeit (Beginn/Ende) · Reiseweg · Tagegeldzeiten
(Ges./DSt/DO/Priv/Rest) · Tagegeld-Stufe · Verpflegung · Kilometerstand
(Beginn/Ende) · Wegstrecke (privat/dienstlich) · ÖPNV · Mitnahme ·
Übernachtung · Nebenkosten · Vermerk-Kennung · Routenlink

Darunter steht die **Orte-Legende** — dieselben Zeilen wie auf dem
Ortsverzeichnis, damit die Kürzel im Reiseweg ohne Blattwechsel auflösbar
sind. Die Spaltenbegriffe sind bewusst die aus S1, damit die Ansicht vertraut
ist. A4 quer, mit **Drucken** und **Aktualisieren**.

> **Eigene Seite, mit Absicht:** Die Prüfliste liegt **nicht** auf der Seite
> `Ausdruck`, sondern auf einer eigenen Seite `Prüfliste`. Eine Grist-Freigabe
> geht über Seiten — läge das Widget neben den Druck-Widgets, bekäme die
> Zeiterfassungsstelle bei einer Freigabe zwangsläufig auch S1/S2, Vermerke
> und Fahrtenbuch zu sehen. So lässt sich genau diese eine Seite freigeben.

---

## "Einkleben" und Unterschreiben

- **Fahrtenbuch** bei **100 %** ausdrucken — nicht „an
  Seitengröße anpassen“, sonst stimmen die Spaltenbreiten nicht.
- Je Zeilenblock entstehen zwei Seiten: links die Spalten 1–6, rechts 7–15.
  Die Hinweiszeile über jeder Seite sagt, welche Kante auszuschneiden ist.
- Ausschneiden, ins Fahrtenbuch einkleben, **Unterschrift von Hand** in die
  entsprechende Spalte.
- S1/S2 unterschreiben und wie üblich einreichen.
