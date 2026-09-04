[← Formeln-Übersicht](README.md)

# Orte

Stammdaten der Reiseziele, Daten beginnen ab Zeile 6. Keine Formeln — reine
Nachschlagetabelle, die GoogleMapsExport!G3 pro Kürzel abfragt.

| Spalte | Inhalt |
|---|---|
| A | Nr. |
| B | Kürzel (= Formularwert, außer WO/KV — siehe unten) |
| C:D | Vollständiger Name der Einrichtung |
| E:M | Vollständige Adresse (Straße Hausnummer, PLZ Ort) |

WO (Wohnort) und KV (Kreisverwaltung) stehen als normale Zeilen in diesem Blatt
— Kürzel "WO"/"KV" in Spalte B, Adresse wie bei jedem anderen Ort in E:M. Das
Formular liefert bei Start/Ziel den Langtext "Wohnort"/"Kreisverwaltung", bei
Wegpunkten das Kürzel "WO"/"KV"; GoogleMapsExport!G3 gleicht das per SUBSTITUTE
an, wie bereits BERECHNUNG!L3, und schlägt beides hier nach.

Setup C26/C28/C30/C32 (Wohnort) bzw. C48/C50/C52/C54 (Kreisverwaltung) sind eine
ZWEITE, unabhängige Pflegestelle derselben Adressen — sie speisen
S1 E3/J3. GoogleMapsExport!G3 nutzt sie nicht mehr.
Adressänderungen müssen daher an beiden Stellen gepflegt werden.
