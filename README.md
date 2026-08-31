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
