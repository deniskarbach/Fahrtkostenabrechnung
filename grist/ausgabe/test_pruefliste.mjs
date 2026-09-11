/* Prüft ausgabe/pruefliste.html -- das Blatt für die Zeiterfassungsstelle,
   auf dem alles aus S1, Vermerken, Dienstorten, Fahrtenbuch und Routenlinks
   in einer Zeile je Reise zusammenläuft.

   Geprüft wird:
   1. Zeilenbreite -- 22 Zellen, gleich der Spaltenzahl im Kopf (das ist
      schon einmal auseinandergelaufen, siehe S1-Übertragszeile).
   2. Die Werte landen in der richtigen Spalte (Tagegeldzeiten, km, Kosten).
   3. Mehrtägige Reise erscheint als Datumsspanne, wie auf S1.
   4. Freitext mit Markup bleibt inert.
   5. DRIFT-WÄCHTER: die Orte-Legende muss Zeile für Zeile dasselbe liefern
      wie das Dienstorte-Blatt in ausdruck.html -- die Sortierlogik steht
      in beiden Dateien (eigenständige Widgets ohne gemeinsame Datei) und
      darf nicht auseinanderlaufen.

       node grist/ausgabe/test_pruefliste.mjs
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
                    Organisationseinheit: "Referat 42",
                    Wohnort_Strasse: "Beispielweg 7", Wohnort_PLZ: "00000", Wohnort_Ort: "Musterstadt",
                    Dienstort_Strasse: "Amtsstr. 1", Dienstort_PLZ: "00000", Dienstort_Ort: "Musterstadt",
                    Zeitraum_von: d(20000), Zeitraum_bis: d(20100) }],
  Orte: [
    { id: 1, Kuerzel: "WO",   Name: "Wohnung",        Adresse: "Beispielweg 7, 00000 Musterstadt" },
    { id: 2, Kuerzel: "KV",   Name: "Kreisverwaltung", Adresse: "Amtsstr. 1, 00000 Musterstadt" },
    { id: 3, Kuerzel: "KITA", Name: "Kita Sonnenschein", Adresse: "Lindenweg 3, 00000 Musterstadt" },
  ],
  Reisen: [
    { id: 1, Datum: d(20010), Datum_bis: d(20010), Lfd_Nr: 1,
      Beginn: "07:15", Ende: "16:40", Reiseweg: "WO > KV > WO",
      Abwesenheit_min: 565, Min_Dienststaette: 60, Min_Dienstort: 270,
      Min_privat_Abzug: 0, Rest_min: 235, Tagegeld_Stufe: "anteilig",
      Verpflegung: "Nein", KM_Beginn: 12000, KM_Ende: 12087,
      Umweg_privat: 0, KM_dienstlich: 87,
      OePNV: 0, Mitnahme_Personen: 0, Uebernachtung: 0, Nebenkosten: 0,
      Vermerk_Label: "V24-01", Ort_Beginn: 1, Ort_1: 2, Ort_Ende: 1,
      Maps_Link: "https://www.google.com/maps/dir/?api=1&origin=A&destination=A" },
    // Mehrtaegig -> Datumsspanne; ausserdem KITA als dritter Stammort.
    { id: 2, Datum: d(20020), Datum_bis: d(20021), Lfd_Nr: 2,
      Beginn: "06:30", Ende: "18:05", Reiseweg: "WO > KITA > WO",
      Abwesenheit_min: 2135, Min_Dienststaette: 0, Min_Dienstort: 0,
      Min_privat_Abzug: 45, Rest_min: 2090, Tagegeld_Stufe: "24h",
      Verpflegung: "Ja", KM_Beginn: 12087, KM_Ende: 12087,
      Umweg_privat: 0, KM_dienstlich: 0,
      OePNV: 42.8, Mitnahme_Personen: 2, Uebernachtung: 89, Nebenkosten: 6,
      Vermerk_Label: "", Ort_Beginn: 1, Ort_1: 3, Ort_Ende: 1,
      Maps_Link: "" },
    // Freitext-Ziel mit Markup.
    { id: 3, Datum: d(20030), Datum_bis: d(20030), Lfd_Nr: 3,
      Beginn: "09:00", Ende: "12:00", Reiseweg: '<img src=x onerror=alert(1)> > WO',
      Abwesenheit_min: 180, Min_Dienststaette: 0, Min_Dienstort: 0,
      Min_privat_Abzug: 0, Rest_min: 180, Tagegeld_Stufe: "",
      Verpflegung: "Nein", KM_Beginn: 12087, KM_Ende: 12100,
      Umweg_privat: 3, KM_dienstlich: 10,
      OePNV: 0, Mitnahme_Personen: 0, Uebernachtung: 0, Nebenkosten: 0,
      Vermerk_Label: "", Ort_Ende: 1, Maps_Link: "" },
  ],
  Adressen: [
    { id: 1, Datum: d(20030), Label: "Hof Lindenau", Adresse: "Dorfstr. 2, 00000 Beispieldorf" },
  ],
};

/* ------------------------------------------------- Fake-DOM (wie test_routenlinks) */
const unesc = s => s.replace(/&amp;/g, "&").replace(/&lt;/g, "<")
                    .replace(/&gt;/g, ">").replace(/&quot;/g, '"');

function sandboxFuer(datei, tbodyIds) {
  const zellen = {};
  const tbodies = {};
  /* Die Widgets fuellen ihre tbodys unterschiedlich: pruefliste.html und
     routenlinks.html setzen innerHTML in einem Rutsch, ausdruck.html haengt
     Zeile fuer Zeile per insertAdjacentHTML an. Das Fake-DOM muss beides
     koennen, sonst prueft der Drift-Waechter nur eine der beiden Dateien. */
  const knoten = id => {
    if (tbodyIds.includes(id)) {
      return tbodies[id] ??= {
        _html: "", _zeilen: [],
        _parse() {
          this._zeilen = [...this._html.matchAll(/<tr[^>]*>([\s\S]*?)<\/tr>/g)].map(m =>
            [...m[1].matchAll(/<td([^>]*)>([\s\S]*?)<\/td>/g)].map(z => {
              const attrs = {};
              for (const am of z[1].matchAll(/([\w-]+)="([^"]*)"/g)) attrs[am[1]] = am[2];
              return { attrs, text: z[2], children: [],
                       get dataset() { return { link: unesc(attrs["data-link"] ?? "") }; },
                       removeAttribute(n) { delete attrs[n]; },
                       appendChild(el) { this.children.push(el); } };
            }));
        },
        set innerHTML(v) { this._html = v; this._parse(); },
        get innerHTML() { return this._html; },
        insertAdjacentHTML(_, s) { this._html += s; this._parse(); },
        querySelectorAll() {
          return this._zeilen.flat().filter(td => "data-link" in td.attrs);
        },
      };
    }
    return zellen[id] ??= { html: "", set textContent(v) { this.html = v; },
                            get textContent() { return this.html; }, innerHTML: "",
                            insertAdjacentHTML(_, s) { this.innerHTML += s; } };
  };

  const quelle = [...readFileSync(datei, "utf8")
    .matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join("\n");

  const sandbox = {
    document: { getElementById: knoten, createElement: () => ({ attrs: {},
                  set href(v) { this.attrs.href = v; }, set target(v) { this.attrs.target = v; },
                  set rel(v) { this.attrs.rel = v; }, set textContent(v) { this.attrs.text = v; } }),
                head: { appendChild() {} }, referrer: "https://grist.example/" },
    window: { self: 1, top: 2 },
    grist: { ready() {}, onRecords() {},
             docApi: { fetchTable: async n => spaltig(TABELLEN[n]) } },
    console, URL,
  };
  vm.createContext(sandbox);
  vm.runInContext(quelle, sandbox);
  return { sandbox, knoten, tbodies };
}

/* ------------------------------------------------- Prüfliste rendern */
const p = sandboxFuer("grist/ausgabe/pruefliste.html", ["daten", "daten-orte"]);
await p.sandbox.ausGrist();

const zeilen = p.tbodies["daten"]._zeilen;
assert.equal(zeilen.length, 3, "drei Reisen erwartet");

// 1. Zeilenbreite = Spaltenzahl im Kopf.
const kopfSpalten = (() => {
  const t = readFileSync("grist/ausgabe/pruefliste.html", "utf8");
  const raster = t.slice(t.indexOf('<table class="raster">'), t.indexOf('<table class="legende">'));
  return [...raster.matchAll(/<col style="width:[\d.]+mm">/g)].length;
})();
for (const [i, z] of zeilen.entries())
  assert.equal(z.length, kopfSpalten,
    `Zeile ${i + 1} hat ${z.length} Zellen, der Kopf ${kopfSpalten}`);

// 2. Werte in der richtigen Spalte (Reihenfolge laut thead).
const S = { nr:0, datum:1, von:2, bis:3, weg:4, ges:5, dst:6, dort:7, priv:8, rest:9,
            stufe:10, verpflegung:11, kmBeginn:12, kmEnde:13, kmPrivat:14, kmDienst:15,
            oepnv:16, mitnahme:17, uebernachtung:18, neben:19, vermerk:20, route:21 };
const r1 = zeilen[0];
assert.equal(r1[S.nr].text, "1");
assert.equal(r1[S.von].text, "07:15");
assert.equal(r1[S.bis].text, "16:40");
assert.equal(r1[S.ges].text, "9:25",  "Ges. = Abwesenheit_min als H:MM");
assert.equal(r1[S.dst].text, "1:00",  "DSt = Min_Dienststaette");
assert.equal(r1[S.dort].text, "4:30", "DO = Min_Dienstort");
assert.equal(r1[S.rest].text, "3:55", "Rest = Rest_min");
assert.equal(r1[S.stufe].text, "anteilig");
assert.equal(r1[S.kmDienst].text, "87");
assert.equal(r1[S.vermerk].text, "V24-01");
assert.equal(r1[S.route].children[0].attrs.text, "Route", "Route als <a>, nicht als Text");

const r2 = zeilen[1];
// 3. Mehrtaegige Reise als Spanne, wie auf S1.
assert.ok(r2[S.datum].text.includes(" - "), "mehrtägig muss Spanne sein: " + r2[S.datum].text);
assert.equal(r2[S.priv].text, "0:45", "privater Zeitabzug eigene Spalte");
assert.equal(r2[S.oepnv].text, "42,80", "EUR deutsch formatiert");
assert.equal(r2[S.uebernachtung].text, "89,00");
assert.equal(r2[S.kmDienst].text, "0", "0 dienstliche km bleiben sichtbar");
assert.equal(r2[S.route].children.length, 0, "ohne Maps_Link kein <a>");

// 4. Markup im Freitext bleibt inert.
const weg3 = zeilen[2][S.weg].text;
assert.ok(!weg3.includes("<img"), "ungeschütztes <img> in der Weg-Zelle: " + weg3);
assert.ok(weg3.includes("&lt;img"), "Markup muss escaped sein: " + weg3);

// Kopfblock
assert.equal(p.knoten("k-antragsteller").html, "Musterfrau Erika, Referat 42");
assert.equal(p.knoten("k-wohnort").html, "Beispielweg 7, 00000 Musterstadt");

/* ------------------------------------------------- 5. Drift-Wächter gegen ausdruck.html */
const a = sandboxFuer("grist/ausgabe/ausdruck.html", ["daten-dien"]);
await a.sandbox.ausGrist();

const spalten = tb => tb._zeilen.map(z => z.map(td => td.text.trim()).slice(1));  // ohne lfd. Nr.
const ausPruefliste = spalten(p.tbodies["daten-orte"]);
const ausAusdruck   = spalten(a.tbodies["daten-dien"]);

assert.deepEqual(ausPruefliste, ausAusdruck,
  "Orte-Legende der Prüfliste weicht vom Dienstorte-Blatt ab -- die Sortierlogik "
  + "steht in beiden Dateien und ist auseinandergelaufen");
assert.ok(ausPruefliste.length >= 4, "zu wenige Orte im Vergleich: " + ausPruefliste.length);

console.log(`ok — ${kopfSpalten} Spalten je Zeile, Werte in der richtigen Spalte, `
          + `Orte-Legende deckungsgleich mit dem Dienstorte-Blatt (${ausPruefliste.length} Zeilen)`);
