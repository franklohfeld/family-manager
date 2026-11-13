# Implementation Plan: Familienkalender auf Raspberry Pi

## Overview

Implementierung einer Touchscreen-Kalenderanwendung für den Raspberry Pi 4 mit rotierender Fotoanzeige und Google-Calendar-basiertem Familienplaner. Die Umsetzung erfolgt in 6 Phasen: Projektstruktur, Services, Datenmodelle, UI-Komponenten, Integration und Deployment.

## Task Dependency Graph

```json
{
  "waves": [
    {
      "wave": 1,
      "tasks": ["1"]
    },
    {
      "wave": 2,
      "tasks": ["2", "3", "4"]
    },
    {
      "wave": 3,
      "tasks": ["5", "7"]
    },
    {
      "wave": 4,
      "tasks": ["6", "8"]
    },
    {
      "wave": 5,
      "tasks": ["9", "10", "11", "12"]
    },
    {
      "wave": 6,
      "tasks": ["13"]
    },
    {
      "wave": 7,
      "tasks": ["14"]
    },
    {
      "wave": 8,
      "tasks": ["15"]
    },
    {
      "wave": 9,
      "tasks": ["16"]
    },
    {
      "wave": 10,
      "tasks": ["17"]
    }
  ]
}
```

## Tasks

- [x] 1. Projektstruktur anlegen
  - Verzeichnisstruktur src/, tests/, docs/, systemd/, assets/ erstellen
  - .gitignore, requirements.txt, setup.py, README.md anlegen
  - config.local.yaml.example als Vorlage für lokale Konfiguration
  - **Abhängigkeiten:** keine

- [x] 2. Konfigurationssystem implementieren
  - src/utils/config.py: lädt config.yaml und mergt mit config.local.yaml
  - Tiefes Merge verschachtelter Dictionaries, Pfad-Expansion für ~
  - Singleton get_config() und reset_config() für Tests
  - **Abhängigkeiten:** Task 1

- [x] 3. Datenmodelle implementieren
  - src/models/event.py: Event-Dataclass mit Urlaubs-Erkennung und JSON-Serialisierung
  - src/models/person.py: Person-Dataclass mit from_config() Fabrikmethode
  - **Abhängigkeiten:** Task 1

- [x] 4. DateUtils implementieren
  - src/utils/date_utils.py: Wochenanfang, KW-Berechnung, Formatierungsfunktionen
  - Sonntag-Mitternacht-Erkennung für Bildwechsel-Scheduler
  - 20 Unit-Tests in tests/test_date_utils.py – alle grün
  - **Abhängigkeiten:** Task 1

- [x] 5. HolidayService implementieren
  - src/services/holiday_service.py: hessische Feiertage via holidays-Bibliothek
  - Unterscheidung gesetzlich frei / regional nicht frei
  - Deutsche Feiertagsnamen über Übersetzungstabelle
  - 11 Unit-Tests in tests/test_holiday_service.py – alle grün
  - **Abhängigkeiten:** Task 2

- [x] 6. ColorLogic implementieren
  - src/utils/color_logic.py: Zeilenfarbe (Samstag/Sonntag/Feiertag) und Zellfarbe (Urlaub/Frei)
  - Farbkonstanten: NORMAL=#FFFFFF, LIGHT_RED=#FFCCCC, DARK_RED=#FF6666, VACATION=#FF9999
  - 10 Unit-Tests in tests/test_color_logic.py – alle grün
  - **Abhängigkeiten:** Task 5

- [x] 7. ImageService implementieren
  - src/services/image_service.py: Bildrotation mit persistentem JSON-State
  - Neustart von vorn nach letztem Bild, Fallback bei leerem Verzeichnis
  - 9 Unit-Tests in tests/test_image_service.py – alle grün
  - **Abhängigkeiten:** Task 2

- [x] 8. CalendarService implementieren
  - src/services/calendar_service.py: Google Calendar API mit OAuth2
  - Graceful Fallback auf lokalen Cache wenn API nicht verfügbar
  - Personenzuordnung via Kalender-Label, Urlaubs-Erkennung im Titel
  - 13 Unit-Tests in tests/test_calendar_service.py – alle grün
  - **Abhängigkeiten:** Task 2, Task 3

- [x] 9. ImageWidget implementieren
  - src/ui/image_widget.py: skalierte Bildanzeige mit QPainter-Overlay
  - Transparentes Datums-Overlay mit Wochentag, Datum und Kalenderwoche
  - Automatische tägliche Datumsaktualisierung via QTimer
  - **Abhängigkeiten:** Task 7

- [x] 10. WeekView implementieren
  - src/ui/week_view.py: 6-Spalten-Tabelle (Datum, 4 Personen, Allgemein)
  - Zeilenfärbung via ColorLogic, Zellfärbung für Urlaubs-Events
  - Touch-freundliche Zeilenhöhe, Navigation vor/zurück/heute
  - **Abhängigkeiten:** Task 6, Task 8

- [x] 11. MonthView implementieren
  - src/ui/month_view.py: Monatsraster 7×6 mit kompakten Ereignis-Chips
  - Feiertags- und Wochenend-Färbung, Personenkürzel als Präfix
  - **Abhängigkeiten:** Task 6, Task 8

- [x] 12. ListView implementieren
  - src/ui/list_view.py: chronologische QTreeWidget-Ansicht mit Tages-Gruppen
  - Urlaubs-Zellfärbung, Personenname als dritte Spalte
  - **Abhängigkeiten:** Task 8

- [x] 13. NavBar und CalendarWidget implementieren
  - src/ui/nav_bar.py: Navigationsleiste mit Qt-Signalen (vor/zurück, Ansichtswechsel)
  - src/ui/calendar_widget.py: QStackedWidget-Container koordiniert alle drei Ansichten
  - **Abhängigkeiten:** Task 10, Task 11, Task 12

- [x] 14. MainWindow implementieren
  - src/ui/main_window.py: QMainWindow mit QSplitter (Foto oben, Kalender unten)
  - Vollbildmodus, konfigurierbare Aufteilung (Standard: 1/3 Foto, 2/3 Kalender)
  - **Abhängigkeiten:** Task 9, Task 13

- [x] 15. App-Integration implementieren
  - src/app.py: initialisiert alle Services, verbindet UI mit Services
  - QTimer für Kalender-Refresh (alle 15 Min) und Bildwechsel-Prüfung (jede Minute)
  - src/main.py: Einstiegspunkt mit Logging und Fehlerbehandlung
  - **Abhängigkeiten:** Task 14

- [x] 16. Deployment-Dateien erstellen
  - systemd/family-calendar.service: Autostart-Service für Raspberry Pi OS
  - docs/installation-raspberry-pi4.md: vollständige Installations-Anleitung (12 Schritte)
  - docs/google-calendar-setup.md: OAuth2-Einrichtung Schritt für Schritt
  - **Abhängigkeiten:** Task 15

- [x] 17. CI/CD und Tests abschließen
  - .github/workflows/ci.yml: GitHub Actions mit Linting (flake8) und pytest
  - tests/test_config.py: 13 Tests für Konfigurationslader
  - Gesamt: 86/86 Tests grün, 0 Linter-Warnings
  - **Abhängigkeiten:** Task 16

## Notes

- Personennamen werden ausschließlich in config.local.yaml gespeichert (nicht versioniert)
- Im Quellcode und allen öffentlichen Dateien werden PERSON_A bis PERSON_D als Platzhalter verwendet
- Google Calendar wird nur lesend abgerufen (Scope: calendar.readonly)
- Bildrotation startet nach dem letzten Bild automatisch von vorn
- Feiertage werden mit deutschen Namen in Spalte 1 angezeigt (auch nicht-freie Feiertage)
- Portrait- und Landscape-Modus werden unterstützt (Konfiguration via config.yaml + /boot/config.txt)
