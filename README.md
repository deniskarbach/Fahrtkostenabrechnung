# Fahrtkostenabrechnung

- **[Handbuch](manual.md)** – wie man das Formular ausfüllt und die Abrechnung erstellt
- **[Formeln](Formeln.md)** – technische Doku aller Blätter und Formeln

## Projektidee

Das Fahrtkostenformular soll Dienstreisen automatisiert erfassen und abrechnen: Google-Forms-Antworten laufen per IMPORTRANGE in die Tabelle ein und werden im Blatt BERECHNUNG so aufbereitet, dass die Formularblätter S1, Fahrtenbuch-Druck, Vermerke nur noch fertige Werte anzeigen müssen.

## Datenfluss

```
Google-Formular → Setup → IMPORTDATA → BERECHNUNG → S1/S2 · Vermerke · Druck-Fahrtenbuch
```

Details siehe [Formeln.md](Formeln.md#datenfluss).

## Wichtiger rechtlicher Hinweis und Haftungsausschluss

**1. Keine Rechtsberatung, keine Gewähr für Richtigkeit**

Diese Software wurde nach bestem Wissen und Gewissen entwickelt, um bei der
Berechnung und Zusammenstellung von Reisekostenabrechnungen zu unterstützen.
Es handelt sich hierbei ausdrücklich um eine unverbindliche Hilfestellung. Die
Berechnungen basieren auf komplexen Formeln, die Fehler enthalten können.

**2. Alleinige Verantwortung des Nutzers**

Die Nutzung dieses Tools erfolgt auf eigene Gefahr. Der Nutzer bzw. die
Nutzerin ist allein dafür verantwortlich, alle Ergebnisse vor der Einreichung
bei der zuständigen Stelle manuell zu überprüfen. Der Autor/Entwickler
übernimmt keine Verantwortung für:

- abgelehnte Reisekostenabrechnungen,
- falsch berechnete Beträge (zu hohe oder zu niedrige Auszahlungen),
- Rückforderungen seitens der abrechnenden Stelle,
- versäumte Fristen aufgrund technischer Fehler,
- sonstige Schäden oder Nachteile.

**3. Keine Markenrechte**

Die Nutzung von Namen oder Logos in diesem Tool impliziert keine offizielle
Herausgeberschaft durch die jeweilige Institution, sofern dies nicht
ausdrücklich anders ausgewiesen ist.

Mit der Nutzung dieses Tools erkennen Sie diesen Haftungsausschluss
vollumfänglich an.
