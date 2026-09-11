/* Prüft ausgabe/routenlinks.html (Gegenstück zum Sheets-Blatt
   GoogleMapsExport): Route-Link wird als echtes <a href> gesetzt, nicht als
   Text; 0 dienstliche km erscheinen als "0" (wie in S1, siehe test_s1_null_km);
   eine Reise ohne Route (Maps_Link leer) bricht nichts; Freitext-Reiseweg mit
   Markup wird nicht ausgeführt.

       node grist/ausgabe/test_routenlinks.mjs
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
    // Normalfall mit Route.
    { id: 1, Datum: d(20010), Lfd_Nr: 1, Beginn: "07:15", Ende: "16:40",
      Reiseweg: "WO > KV > WO", KM_dienstlich: 87,
      Maps_Link: "https://www.google.com/maps/dir/?api=1&origin=A&destination=A&waypoints=B" },
    // Nur in die Verwaltung, komplett privater Umweg -> 0 km, dennoch anzeigen.
    { id: 2, Datum: d(20020), Lfd_Nr: 2, Beginn: "08:00", Ende: "09:00",
      Reiseweg: "WO > KV > WO", KM_dienstlich: 0,
      Maps_Link: "https://www.google.com/maps/dir/?api=1&origin=A&destination=A" },
    // Weniger als zwei Orte -> Maps_Link leer -> keine Route-Zelle, kein Fehler.
    { id: 3, Datum: d(20030), Lfd_Nr: 3, Beginn: "10:00", Ende: "10:30",
      Reiseweg: "WO", KM_dienstlich: 0, Maps_Link: "" },
    // Freitext mit Markup -- darf nicht ausgeführt/eingeschleust werden.
    { id: 4, Datum: d(20040), Lfd_Nr: 4, Beginn: "11:00", Ende: "12:00",
      Reiseweg: '<img src=x onerror=alert(1)> > KV > WO', KM_dienstlich: 5,
      Maps_Link: "https://www.google.com/maps/dir/?api=1&origin=A&destination=A" },
  ],
};

const quelle = [...readFileSync("grist/ausgabe/routenlinks.html", "utf8")
  .matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join("\n");

const zellen = {};
const knoten = id => (zellen[id] ??= { html: "", set textContent(v) { this.html = v; },
                                       get textContent() { return this.html; },
                                       innerHTML: "" });

/* Minimales DOM: reicht fuer tbody.innerHTML = ...; und
   tbody.querySelectorAll("td[data-link]") auf den erzeugten Zeilen.

   unesc(): ein echter Browser decodiert HTML-Entities in Attributwerten beim
   Parsen von innerHTML automatisch -- element.dataset liefert also wieder
   das rohe "&", nicht "&amp;". Das muss das Fake-DOM hier nachbilden, sonst
   prueft der Test nur sich selbst, nicht das echte Verhalten. */
const unesc = s => s.replace(/&amp;/g, "&").replace(/&lt;/g, "<")
                    .replace(/&gt;/g, ">").replace(/&quot;/g, '"');
class FakeTd {
  constructor(attrs) { this.attrs = attrs; this.children = []; }
  get dataset() { return { link: unesc(this.attrs["data-link"] ?? "") }; }
  removeAttribute(n) { delete this.attrs[n]; }
  appendChild(el) { this.children.push(el); }
  get textContent() {
    return this.children.map(c => c.textContent).join("")
      || (this.attrs.class === "weg" ? this.attrs.__text ?? "" : this.attrs.__text ?? "");
  }
}
function parseZeile(html) {
  const tr = { tds: [] };
  const tdRe = /<td([^>]*)>([\s\S]*?)<\/td>/g;
  let m;
  while ((m = tdRe.exec(html))) {
    const attrs = {};
    for (const am of m[1].matchAll(/([\w-]+)="([^"]*)"/g)) attrs[am[1]] = am[2];
    const td = new FakeTd(attrs);
    td.attrs.__text = m[2];
    tr.tds.push(td);
  }
  return tr;
}

const tbody = knoten("daten");
Object.defineProperty(tbody, "innerHTML", {
  get() { return this._html || ""; },
  set(v) {
    this._html = v;
    this._zeilen = [...v.matchAll(/<tr>([\s\S]*?)<\/tr>/g)].map(m => parseZeile(m[1]));
  },
});
tbody.querySelectorAll = sel => {
  assert.equal(sel, 'td[data-link]');
  return tbody._zeilen.flatMap(z => z.tds.filter(td => "data-link" in td.attrs));
};

const sandbox = {
  document: {
    getElementById: knoten, createElement: tag => ({ tag, attrs: {},
      set href(v) { this.attrs.href = v; },
      set target(v) { this.attrs.target = v; },
      set rel(v) { this.attrs.rel = v; },
      set textContent(v) { this.attrs.text = v; },
      get textContent() { return this.attrs.text; } }),
    head: { appendChild() {} }, referrer: "https://grist.example/",
  },
  window: { self: 1, top: 2 },
  grist: { ready() {}, onRecords() {},
           docApi: { fetchTable: async n => spaltig(TABELLEN[n]) } },
  console, URL,
};
vm.createContext(sandbox);
vm.runInContext(quelle, sandbox);
await sandbox.ausGrist();

const zeilen = tbody._zeilen;
assert.equal(zeilen.length, 4, "vier Reisen erwartet");

// Reise 1: Route-Zelle traegt ein <a>-Objekt mit dem richtigen href.
const route1 = zeilen[0].tds[6].children[0];
assert.equal(route1.attrs.href, TABELLEN.Reisen[0].Maps_Link);
assert.equal(route1.attrs.target, "_blank");
assert.equal(route1.attrs.rel, "noopener");
assert.equal(route1.attrs.text, "Route");

// Reise 2: 0 km muss als "0" erscheinen, nicht leer (wie der S1-Fix).
assert.equal(zeilen[1].tds[5].attrs.__text, "0", "0 dienstliche km muessen sichtbar bleiben");

// Reise 3: kein Maps_Link -> keine Route-Zelle, kein Absturz.
assert.equal(zeilen[2].tds[6].children.length, 0, "ohne Route kein <a>");

// Reise 4: Markup im Freitext-Reiseweg darf nicht als Tag ankommen.
const weg4 = zeilen[3].tds[2].attrs.__text;
assert.ok(!weg4.includes("<img"), "Reiseweg-Zelle enthaelt ungeschuetztes <img>: " + weg4);
assert.ok(weg4.includes("&lt;img"), "Markup muss escaped sein: " + weg4);

console.log("ok — Route-Link per DOM-API, 0 km sichtbar, Freitext escaped");
