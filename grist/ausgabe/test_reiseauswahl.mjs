/* Prüft die Auswahllogik von reiseauswahl.html: welche Reisen an einem Tag
   erscheinen (mehrtägige auch an Folgetagen, nach Uhrzeit sortiert) und
   wohin "vorige/nächste Reise" springt. Datum kommt mal als Sekunden, mal
   als Date -- beides muss gleich behandelt werden.

       node grist/ausgabe/test_reiseauswahl.mjs
*/
import { readFileSync } from "node:fs";
import { strict as assert } from "node:assert";
import vm from "node:vm";

const quelle = readFileSync("grist/ausgabe/reiseauswahl.html", "utf8")
  .split("// LOGIK-ANFANG")[1].split("// LOGIK-ENDE")[0].replace(/^.*\n/, "");
const s = {};
vm.createContext(s);
vm.runInContext(quelle + "; this.amTag = amTag; this.nachbar = nachbar; this.iso = iso;", s);

const sek = t => Date.parse(t + "T00:00:00Z") / 1000;
const reisen = [
  { id: 1, Datum: sek("2026-10-06"), Beginn: "13:00" },
  { id: 2, Datum: new Date("2026-10-06T00:00:00Z"), Beginn: "08:01" },
  { id: 3, Datum: sek("2026-10-08"), Datum_Ende: sek("2026-10-09"), Beginn: "07:00" },
  { id: 4, Datum: null },                                   // unvollständig erfasst
];
const ids = tag => s.amTag(reisen, tag).map(r => r.id);

assert.deepEqual(ids("2026-10-06"), [2, 1], "Sekunden und Date gleich, nach Beginn sortiert");
assert.deepEqual(ids("2026-10-09"), [3], "mehrtägige Reise auch am Folgetag");
assert.deepEqual(ids("2026-10-07"), [], "leerer Tag");
assert.equal(s.nachbar(reisen, "2026-10-07", +1), "2026-10-08");
assert.equal(s.nachbar(reisen, "2026-10-07", -1), "2026-10-06");
assert.equal(s.nachbar(reisen, "2026-10-08", +1), "", "keine spätere Reise");
assert.equal(s.nachbar(reisen, "9999-12-31", -1), "2026-10-08", "Start auf der jüngsten Reise");

console.log("ok — Reisen je Tag inkl. mehrtägiger, vorige/nächste Reise");
