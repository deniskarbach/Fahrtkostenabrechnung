/* Prüft die Fahrtenbuch-Schnittversion ohne Reisen im Zeitraum: ein leeres
   Blattpaar mit Spaltenköpfen und ein Hinweis in der Druckleiste.

       node grist/tests/test_fahrtenbuch_leer.mjs
*/
import { readFileSync } from "node:fs";
import { strict as assert } from "node:assert";
import vm from "node:vm";

const TAG = 24 * 3600;
const spaltig = rows => {
  const keys = [...new Set(rows.flatMap(Object.keys))];
  const o = Object.fromEntries(keys.map(k => [k, rows.map(r => r[k] ?? null)]));
  o.id = rows.map(r => r.id);
  return o;
};

const TABELLEN = {
  Einstellungen: [{ id: 1, Zeitraum_von: 20000 * TAG, Zeitraum_bis: 20100 * TAG }],
  // Liegt vor dem Zeitraum -> wird weggefiltert.
  Reisen: [{ id: 1, Datum: 19990 * TAG, Lfd_Nr: 1, Beginn: "08:00", Ende: "09:00" }],
};

const zellen = {};
const knoten = id => (zellen[id] ??= { textContent: "", innerHTML: "", appendChild(k) { this.kinder.push(k); },
                                       kinder: [] });

const quelle = [...readFileSync("grist/ausgabe/fahrtenbuch.html", "utf8")
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

const blaetter = knoten("seiten").kinder.map(k => k.innerHTML);
assert.equal(blaetter.length, 2, "ein Blattpaar");
assert.match(blaetter[0], /Seite 1 von 2/);
assert.match(blaetter[0], /<thead>[\s\S]*Lfd\.&#10;Nr\./);
assert.match(blaetter[1], /<thead>[\s\S]*Vermerke/);
assert.doesNotMatch(blaetter.join(""), /<tbody>\s*<tr>/, "keine Datenzeilen");
assert.match(knoten("hinweis").textContent, /Keine Reisen/);

console.log("ok — leerer Zeitraum zeigt ein Blattpaar mit Spaltenköpfen");
