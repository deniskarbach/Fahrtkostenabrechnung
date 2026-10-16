/* Prüft das Ortsverzeichnis in ausdruck.html: Stammziele höchstens einmal,
   Wohnung und Dienststätte vorn, Einzelziele mit Datum und Nummer, der
   Freitext unverändert unter Adresse.

   Das war ein stiller Fehler -- die Liste sammelte einen Eintrag je Reise UND
   je Ortsfeld, zwei Reisen mit Start und Ziel Wohnung ergaben vier Zeilen.
   Falsch, aber plausibel aussehend; genau dafür ist dieser Test da.

       node grist/ausgabe/test_ortsverzeichnis.mjs
*/
import { readFileSync } from "node:fs";
import { strict as assert } from "node:assert";
import vm from "node:vm";

const TAG = 24 * 3600;   // Grist liefert Datumswerte als Sekunden
const d = n => n * TAG;

/* Spaltenweise wie fetchTable, damit der Umbau in zeilen() mitgeprüft wird. */
const spaltig = rows => {
  const keys = [...new Set(rows.flatMap(Object.keys))];
  return Object.fromEntries(keys.map(k => [k, rows.map(r => r[k] ?? null)]));
};

const TABELLEN = {
  // Wohnort_*/Dienstort_* stehen in Einstellungen (source of truth); die
  // Adresse in den WO/KV-Zeilen unten steht nur zum Schein hier -- im echten
  // Dokument liefert sie STAMMZIELE.Adresse per Formel aus genau diesen Feldern.
  Einstellungen: [{ id: 1, Name: "Musterfrau", Vorname: "Erika",
                    Organisationseinheit: "Referat 42", Abteilung: "9-99",
                    Wohnort_Strasse: "Beispielweg 7", Wohnort_PLZ: "00000", Wohnort_Ort: "Musterstadt",
                    Dienstort_Strasse: "Verwaltungsstr. 1", Dienstort_PLZ: "00000", Dienstort_Ort: "Musterstadt",
                    Zeitraum_von: d(20000), Zeitraum_bis: d(20100) }],
  Stammziele: [
    { id: 1, Kuerzel: "WO",   Name: "Wohnung",           Adresse: "Beispielweg 7, 00000 Musterstadt" },
    { id: 2, Kuerzel: "KV",   Name: "Kreisverwaltung",   Adresse: "Verwaltungsstr. 1, 00000 Musterstadt" },
    { id: 3, Kuerzel: "KITA", Name: "Kita Sonnenschein", Adresse: "Lindenweg 3, Musterstadt" },
  ],
  // Zwei Reisen, beide von der Wohnung zur Wohnung -- der gemeldete Fall.
  // Einzelziele: so, wie die Formel Reisen.Einzelziele sie liefert.
  Reisen: [
    { id: 1, Datum: d(20010), Ort_Beginn: 1, Ort_1: 2, Ort_Ende: 1, Lfd_Nr: 1,
      Einzelziele: "E24-01: Beispieldorf, Dorfstr. 2, Beispieldorf" },
    { id: 2, Datum: d(20020), Ort_Beginn: 1, Ort_1: 2, Ort_2: 3, Ort_Ende: 1, Lfd_Nr: 2,
      Einzelziele: "E24-02: Beispieldorf, Dorfstr. 2, Beispieldorf\nE24-03: Hof Lindenau" },
    { id: 3, Datum: d(20500), Ort_Beginn: 1, Ort_Ende: 1,    // ausserhalb des Zeitraums
      Einzelziele: "E25-01: Ausserhalb" },
  ],
};

/* Minimales DOM: sammelt je id, was hineingeschrieben wurde. */
const zellen = {};
const knoten = id => (zellen[id] ??= { html: "", set textContent(v) { this.html = v; },
                                       get textContent() { return this.html; },
                                       innerHTML: "",
                                       insertAdjacentHTML(_, s) { this.innerHTML += s; } });

const quelle = [...readFileSync("grist/ausgabe/ausdruck.html", "utf8")
  .matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join("\n");

const sandbox = {
  // referrer: das Widget leitet daraus die Herkunft der Plugin-API ab und
  // bricht ohne sie ab -- hier egal, onload feuert im Stub ohnehin nie.
  document: { getElementById: knoten, createElement: () => ({}),
              head: { appendChild() {} }, referrer: "https://grist.example/" },
  window: { self: 1, top: 2 },          // != top -> Grist-Zweig, keine Beispieldaten
  grist: { ready() {}, onRecords() {},
           docApi: { fetchTable: async n => spaltig(TABELLEN[n]) } },
  console, URL,
};
vm.createContext(sandbox);
vm.runInContext(quelle, sandbox);
await sandbox.ausGrist();

const zeilen = [...knoten("daten-ov").innerHTML.matchAll(/<tr>([\s\S]*?)<\/tr>/g)]
  .map(m => [...m[1].matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map(z => z[1].trim()));

const spalte = i => zeilen.map(z => z[i]);
console.log(zeilen.map(z => z.slice(0, 4).join(" | ")).join("\n"));

assert.equal(spalte(1).filter(k => k === "WO").length, 1, "Wohnung mehrfach in der Liste");
assert.equal(spalte(1).filter(k => k === "KV").length, 1, "Dienststaette mehrfach in der Liste");
assert.deepEqual(spalte(1).slice(0, 3), ["WO", "KV", "KITA"], "Reihenfolge der Stammziele");
assert.equal(spalte(2)[0], "Wohnung");
// Beide Beispieldorf-Zeilen bleiben stehen, mit Datum und Nummer; die Reise
// ausserhalb des Zeitraums fehlt. Der Freitext steht ganz unter Adresse.
// Kürzel oben, Datum darunter (zweizeilig per pre-line).
const [t1, t2] = spalte(1).slice(3, 5).map(k => k.split("\n")[1]);
assert.ok(t1?.includes(".") && t1 !== t2, "Einzelziel ohne Datum: " + t1);
assert.deepEqual(spalte(1).slice(3).map(k => k.split("\n")[0]), ["E24-01", "E24-02", "E24-03"], "Kürzel");
assert.deepEqual(spalte(2).slice(3), ["", "", ""], "Name bleibt leer");
assert.deepEqual(spalte(3).slice(3),
  ["Beispieldorf, Dorfstr. 2, Beispieldorf", "Beispieldorf, Dorfstr. 2, Beispieldorf", "Hof Lindenau"],
  "Freitext unter Adresse");
assert.equal(zeilen.length, 6, "unerwartete Zeilenzahl: " + zeilen.length);
assert.deepEqual(spalte(0), ["1", "2", "3", "4", "5", "6"], "Nummerierung");

// Kopfzeile: anschrift() setzt Wohnort/Dienstort aus Einstellungen zusammen --
// die Stelle, die beim vorigen Umbau (Ref:Stammziele) versehentlich entfallen war.
assert.equal(knoten("k-ov-wohnort").html, "Beispielweg 7, 00000 Musterstadt", "Wohnort-Kopf");
assert.equal(knoten("k-ov-dienstort").html, "Verwaltungsstr. 1, 00000 Musterstadt", "Dienstort-Kopf");

// S2: Abteilung aus Einstellungen in die Lücke, Buchungsstelle leer -> Linie bleibt.
assert.equal(knoten("s2-abteilung").html, "9-99", "S2 Abteilung");
assert.equal(knoten("s2-buchungsstelle").html, "", "S2 Buchungsstelle ohne Wert");

console.log("\nok");
