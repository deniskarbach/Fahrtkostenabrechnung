/* Prüft die Seitenzuordnung im Druck von ausdruck.html.

   Vier Dokumente mit gemischter Ausrichtung (hoch/hoch/hoch/hoch/quer) in
   einem Druckjob hängen an zwei Dingen: jedes Blatt muss eine @page-Regel
   bekommen, und kein erzwungener Umbruch darf eine Seite erzeugen, zu der
   kein Blatt gehört. Genau das war der Fehler: "break-after: page" auf dem
   letzten Blatt (Fahrtenbuch, quer) erzeugte eine Seite ohne Blatt, die auf
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
assert.equal(doks.length, 5, `erwartet 5 Dokumente, gefunden ${doks.length}`);
for (const [, dok, regeln] of doks) {
  const seite = /page:\s*([a-z0-9-]+)/i.exec(regeln)?.[1];
  assert.ok(seite, `${dok}: kein page: gesetzt`);
  assert.ok(seite === "auto" || benannt.has(seite), `${dok}: @page ${seite} fehlt`);
}

// 3. Das Fahrtenbuch ist das einzige Querformat -- der Grund für die ganze
//    Konstruktion. Faellt es auf die Standardregel zurueck, ist es hoch.
const fb = /@page\s+fahrtenbuch\s*\{([^}]*)\}/i.exec(css)?.[1] ?? "";
assert.ok(/landscape/.test(fb), "@page fahrtenbuch ist nicht landscape");
assert.ok(/@page\s*\{[^}]*portrait/.test(css), "namenlose @page ist nicht portrait");

console.log(`ok — ${doks.length} Blätter mit @page-Zuordnung, Umbruch vor dem Blatt, `
            + `keine Seite ohne Blatt`);
