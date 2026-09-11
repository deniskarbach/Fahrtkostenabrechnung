/* Prüft die km-Spalte auf S1: 0 dienstliche Kilometer müssen als "0" gedruckt
   werden, nicht als leere Zelle.

   Das war ein stiller Fehler -- S1 nutzte zahl() (für optionale Kostenfelder
   gedacht, 0 -> leer) auch für km. Eine Reise, die vollständig als privater
   Umweg erfasst wurde (z. B. eine reine Verwaltungsfahrt: KM_Ende - KM_Beginn
   als Privater Umweg eingetragen, KM_dienstlich = 0), sah dadurch nach einer
   vergessenen Eingabe aus statt nach einer bewusst erfassten Null. Das
   Fahrtenbuch (f.kmDienstlich ?? "") hatte diese Spalte schon immer richtig.

       node grist/ausgabe/test_s1_null_km.mjs
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
  // Nur in die Verwaltung, vollständig als privater Umweg erfasst.
  Reisen: [
    { id: 1, Datum: d(20010), Ort_Beginn: 1, Ort_1: 2, Ort_Ende: 1, Lfd_Nr: 1,
      Beginn: "08:00", Ende: "09:00", Reiseweg: "WO > KV > WO",
      KM_Beginn: 1000, KM_Ende: 1020, Umweg_privat: 20, KM_dienstlich: 0 },
    // Zweite Reise mit echten dienstlichen Kilometern, damit der Test auch
    // den Normalfall (Zahl bleibt Zahl) und die Summenzeile mitprüft.
    { id: 2, Datum: d(20020), Ort_Beginn: 1, Ort_1: 2, Ort_Ende: 1, Lfd_Nr: 2,
      Beginn: "08:00", Ende: "09:00", Reiseweg: "WO > KV > WO",
      KM_Beginn: 1020, KM_Ende: 1044, Umweg_privat: 0, KM_dienstlich: 24 },
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

const zeilen = [...knoten("daten-s1").innerHTML.matchAll(/<tr(?: class="uebertrag")?>([\s\S]*?)<\/tr>/g)]
  .map(m => [...m[1].matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map(z => z[1].trim()));

const KM_SPALTE = 10;         // Datenzeile: Datum,von,bis,weg,4xKreuz,Verpflegung,ÖPNV,km
const KM_SPALTE_UEBERTRAG = 3; // Übertrag-Zeile: zwei colspan-Zellen ersetzen die ersten neun

assert.equal(zeilen[0][KM_SPALTE], "0", "0 dienstliche km müssen als '0' erscheinen, nicht leer");
assert.equal(zeilen[1][KM_SPALTE], "24", "echte km müssen weiterhin als Zahl erscheinen");
assert.equal(zeilen[2][KM_SPALTE_UEBERTRAG], "24", "Übertrag: Summe (0 + 24) muss als Zahl erscheinen");

console.log("ok — S1 zeigt 0 dienstliche km statt einer leeren Zelle");
