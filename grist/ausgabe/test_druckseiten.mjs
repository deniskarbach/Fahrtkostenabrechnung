/* Prüft die Seitenzuordnung im Druck von ausdruck.html.

   Mehrere Dokumente mit eigenen Seitenrändern in einem Druckjob hängen an zwei Dingen: jedes Blatt muss eine @page-Regel
   bekommen, und kein erzwungener Umbruch darf eine Seite erzeugen, zu der
   kein Blatt gehört. Genau das war der Fehler: "break-after: page" auf dem
   letzten Blatt (damals das Fahrtenbuch, quer) erzeugte eine Seite ohne Blatt, die auf
   die namenlose Standardregel fiel -- A4 hoch. Chrome unterschlug sie, Edge
   druckte sie.

       node grist/ausgabe/test_druckseiten.mjs
*/
import { readFileSync } from "node:fs";
import { strict as assert } from "node:assert";

const css = readFileSync("grist/ausgabe/ausdruck.html", "utf8")
  .split("<style>")[1].split("</style>")[0]
  .replace(/\/\*[\s\S]*?\*\//g, "");        // Kommentare raus, sonst Treffer darin

// 1. Der Umbruch geht nach vorn. Nach hinten liesse hinter dem letzten Blatt
//    eine Seite ohne @page-Zuordnung entstehen.
assert.ok(/\.blatt\s*\{[^}]*break-before:\s*page/.test(css), "kein break-before: page auf .blatt");
assert.ok(!/break-after:\s*page/.test(css), "break-after: page erzeugt eine Seite ohne Blatt");

// 2. Jedes Dokument weist seinem Blatt eine Seite zu, und jede benannte Seite
//    ist auch definiert. 'auto' ist die namenlose @page-Regel.
const benannt = new Set([...css.matchAll(/@page\s+([a-z0-9-]+)\s*\{/gi)].map(m => m[1]));
const doks = [...css.matchAll(/\.(dok-[a-z0-9-]+)\s+\.blatt\s*\{([^}]*)\}/gi)];
assert.equal(doks.length, 4, `erwartet 4 Dokumente, gefunden ${doks.length}`);
for (const [, dok, regeln] of doks) {
  const seite = /page:\s*([a-z0-9-]+)/i.exec(regeln)?.[1];
  assert.ok(seite, `${dok}: kein page: gesetzt`);
  assert.ok(seite === "auto" || benannt.has(seite), `${dok}: @page ${seite} fehlt`);
}

// 3. Alle Blätter sind hoch -- das Fahrtenbuch (quer) steht in fahrtenbuch.html.
assert.ok(!/landscape/.test(css), "Querformat im Ausdruck, obwohl alle Blätter hoch sind");
assert.ok(/@page\s*\{[^}]*portrait/.test(css), "namenlose @page ist nicht portrait");

// 4. Gedruckt wird aus einem eigenen Fenster, nicht aus dem Grist-Iframe:
//    dort greifen die @page-Regeln unter Windows/Edge nicht und der ganze
//    Job fiel auf A4 hoch zurueck. Gleiche Loesung wie in pruefliste.html.
const html = readFileSync("grist/ausgabe/ausdruck.html", "utf8");
assert.ok(!/onclick="window\.print\(\)"/.test(html),
          "druckt noch direkt aus dem Widget-Iframe");
assert.ok(/window\.open\(/.test(html) && /\bw\.print\(\)/.test(html),
          "kein Druckfenster-Pfad gefunden");

// 5. Das Druckfenster muss alle .dok-*-Huellen mitnehmen, nicht nur die
//    .blatt darin -- das CSS ist je Dokument unter .dok-XXX gekapselt.
const huellen = [...html.matchAll(/<div class="(dok-[a-z0-9-]+)">/gi)].map(m => m[1]);
assert.equal(huellen.length, doks.length,
             `${huellen.length} Huellen im HTML, aber ${doks.length} im CSS`);
assert.ok(/querySelectorAll\("body > \[class\^='dok-'\]"\)/.test(html),
          "Druckfenster kopiert nicht alle .dok-*-Huellen");

console.log(`ok — ${doks.length} Blätter mit @page-Zuordnung, Umbruch vor dem Blatt, `
            + `keine Seite ohne Blatt, Druck aus eigenem Fenster`);
