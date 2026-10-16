/* Prüft Spalte 11 der Fahrtenbuch-Schnittversion: sie zeigt nur DSt und DO,
   immer beide (auch 0:00), einzeilig. Die volle Aufschlüsselung steht auf S1.

       node grist/tests/test_fahrtenbuch_zeit.mjs
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
  Einstellungen: [{ id: 1, Zeitraum_von: d(20000), Zeitraum_bis: d(20100) }],
  Reisen: [
    // Ohne Aufenthalt -> DSt und DO stehen trotzdem da, als 0:00.
    { id: 1, Datum: d(20010), Lfd_Nr: 67, Beginn: "08:00", Ende: "16:55",
      Abwesenheit_min: 535, Min_Dienststaette: 0, Min_Dienstort: 0,
      Min_privat_Abzug: 0, Rest_min: 535 },
    { id: 2, Datum: d(20020), Lfd_Nr: 68, Beginn: "08:00", Ende: "18:00",
      Abwesenheit_min: 600, Min_Dienststaette: 60, Min_Dienstort: 30,
      Min_privat_Abzug: 45, Rest_min: 465 },
  ],
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

const zeit = [...knoten("seiten").kinder.map(k => k.innerHTML).join("")
  .matchAll(/<td class="zeit">([\s\S]*?)<\/td>/g)].map(m => m[1]);

assert.deepEqual(zeit, [
  "DSt 0:00 | DO 0:00",
  "DSt 1:00 | DO 0:30",
]);

console.log("ok — Schnittversion zeigt DSt | DO einzeilig in Spalte 11");
