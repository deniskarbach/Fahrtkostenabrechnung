#!/bin/sh
# Alle Offline-Tests: kein Grist, kein API-Kontingent. Aus jedem Verzeichnis
# aufrufbar:   sh grist/tests/alle.sh
# Der Abnahmetest (tests/abnahme/) läuft gegen eine Grist-Testkopie und gehört
# bewusst nicht hierher.
cd "$(dirname "$0")/../.." || exit 1

fehler=0
lauf() {   # lauf <Name> <Befehl …> -- still bei Erfolg, volle Ausgabe bei Fehler
  name=$1; shift
  if ausgabe=$("$@" 2>&1); then
    echo "ok      $name"
  else
    echo "FEHLER  $name"; echo "$ausgabe" | sed 's/^/        /'; fehler=1
  fi
}

lauf "setup.py --selbsttest" python3 -W error::SyntaxWarning grist/setup.py --selbsttest
for t in grist/tests/test_*.mjs; do lauf "$(basename "$t")" node "$t"; done
for t in grist/tests/test_*.py;  do lauf "$(basename "$t")" python3 "$t"; done

[ $fehler = 0 ] && echo "Alle Tests bestanden." || echo "Mindestens ein Test fehlgeschlagen."
exit $fehler
