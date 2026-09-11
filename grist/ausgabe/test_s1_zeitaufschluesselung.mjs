/* Prüft die Spalte "Reiseweg" auf S1: sie muss die Zeitaufschlüsselung
   zeigen (Ges./DSt/DO/Priv/Rest), nicht den Reiseweg -- der steht bereits im
   Fahrtenbuch, und der amtliche Vordruck verlangt an dieser Stelle ohnehin
   nur die laufende Nummer, wenn ein Fahrtenbuch geführt wird.

   Das war ein stiller Fehler -- S1 zeigte "Nr. X – WO > KV > WO", identisch
   zur Fahrtenbuch-Spalte und ohne Bezug zur Tagegeld-Prüfung. Format und
   Rundungsbeispiel sind aus der Sheets-Version übernommen.

       node grist/ausgabe/test_s1_zeitaufschluesselung.mjs
*/
import { readFileSync } from "node:fs";
import { strict as assert } from "node:assert";
import vm from "node:vm";

const TAG = 24 * 3600;
const d = n => n * TAG;

const spaltig = rows => {
  const keys = [...new Set(rows.flatMap(Object.keys))];
  const o = Object.fromEntries(keys.map(k => [k, rows.map(r => r[k] ?? null)]));
  o.id = rows.map(r => r.id);
  return o;
};

const TABELLEN = {
  Einstellungen: [{ id: 1, Name: "Musterfrau", Vorname: "Erika",
                    Zeitraum_von: d(20000), Zeitraum_bis: d(20100) }],
  Orte: [
    { id: 1, Kuerzel: "WO", Name: "Wohnung",    Adresse: "Beispielweg 7" },
    { id: 2, Kuerzel: "KV", Name: "Verwaltung", Adresse: "Amtsstr. 1" },
  ],
  Reisen: [
    // Genau das gemeldete Beispiel: kein privater Zeitabzug -> kein Priv-Teil.
    { id: 1, Datum: d(20010), Ort_Beginn: 1, Ort_1: 2, Ort_Ende: 1, Lfd_Nr: 67,
      Beginn: "08:00", Ende: "16:55", Reiseweg: "WO > KV > WO",
      Abwesenheit_min: 535, Min_Dienststaette: 0, Min_Dienstort: 0,
      Min_privat_Abzug: 0, Rest_min: 535 },
    // Mit privatem Zeitabzug -> Priv-Teil muss erscheinen, Rest entsprechend kleiner.
    { id: 2, Datum: d(20020), Ort_Beginn: 1, Ort_1: 2, Ort_Ende: 1, Lfd_Nr: 68,
      Beginn: "08:00", Ende: "18:00", Reiseweg: "WO > KV > WO",
      Abwesenheit_min: 600, Min_Dienststaette: 60, Min_Dienstort: 30,
      Min_privat_Abzug: 45, Rest_min: 465 },
  ],
  Adressen: [],
};

const zellen = {};
const knoten = id => (zellen[id] ??= { html: "", set textContent(v) { this.html = v; },
                                       get textContent() { return this.html; },
                                       innerHTML: "",
                                       insertAdjacentHTML(_, s) { this.innerHTML += s; } });

const quelle = [...readFileSync("grist/ausgabe/ausdruck.html", "utf8")
  .matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join("\n");

const sandbox = {
  document: { getElementById: knoten, createElement: () => ({}),
              head: { appendChild() {} }, referrer: "https://grist.example/" },
  window: { self: 1, top: 2 },
  grist: { ready() {}, onRecords() {},
           docApi: { fetchTable: async n => spaltig(TABELLEN[n]) } },
  console, URL,
};
vm.createContext(sandbox);
vm.runInContext(quelle, sandbox);
await sandbox.ausGrist();

const zeilen = [...knoten("daten-s1").innerHTML.matchAll(/<tr>([\s\S]*?)<\/tr>/g)]
  .map(m => [...m[1].matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map(z => z[1].trim()));
const WEG_SPALTE = 3;

assert.equal(zeilen[0][WEG_SPALTE],
  "Nr. 67  –  (Ges.: 8:55 | DSt: 0:00 | DO: 0:00 | Rest: 8:55)",
  "S1 muss die Zeitaufschlüsselung zeigen, nicht den Reiseweg");
assert.equal(zeilen[1][WEG_SPALTE],
  "Nr. 68  –  (Ges.: 10:00 | DSt: 1:00 | DO: 0:30 | Priv: 0:45 | Rest: 7:45)",
  "Priv-Teil muss bei privatem Zeitabzug erscheinen");

// Der echte Reiseweg bleibt exklusiv Sache des Fahrtenbuchs.
const fbWeg = [...knoten("daten-fb").innerHTML.matchAll(/<td class="weg">([\s\S]*?)<\/td>/g)]
  .map(m => m[1]);
assert.equal(fbWeg[0], "WO &gt; KV &gt; WO", "Fahrtenbuch muss weiterhin den Reiseweg zeigen");

console.log("ok — S1 zeigt Ges./DSt/DO/Priv/Rest, Fahrtenbuch weiterhin den Reiseweg");
