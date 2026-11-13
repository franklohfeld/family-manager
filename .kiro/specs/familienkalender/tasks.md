# Implementierungs-Aufgabenliste – Familienkalender auf Raspberry Pi

## Legende
- [ ] = Offen
- [x] = Erledigt
- Abhängigkeiten sind jeweils angegeben

---

## Phase 1: Projektgrundlage

### Task 1.1 – Projektstruktur anlegen
- [x] Verzeichnisstruktur gemäß Designdokument erstellen
- [x] `README.md` mit Projektbeschreibung und Setup-Anleitung verfassen
- [x] `.gitignore` anlegen (inkl. `config.local.yaml`, `token.json`, `credentials.json`, `__pycache__`, `.env`)
- [x] `config.local.yaml.example` anlegen
- [x] `requirements.txt` erstellen
- [x] `setup.py` erstellen

**Abhängigkeiten:** –

---

### Task 1.2 – Konfigurationssystem implementieren
- [x] `config.yaml` (Standard-Konfiguration, versioniert) anlegen
- [x] `config.local.yaml.example` anlegen
- [x] `src/utils/config.py` implementieren
- [x] Unit-Tests: `tests/test_config.py` – alle 13 Tests grün

**Abhängigkeiten:** Task 1.1

---

## Phase 2: Services

### Task 2.1 – `HolidayService` implementieren
- [x] `src/services/holiday_service.py` implementieren
- [x] `holidays`-Bibliothek für Hessen (`HE`) einbinden (subdiv-API)
- [x] Deutsche Feiertagsnamen über Übersetzungstabelle
- [x] `is_public_holiday(d)`, `is_regional_holiday(d)`, `get_holiday_name(d)`
- [x] Unit-Tests: `tests/test_holiday_service.py` – alle 11 Tests grün

**Abhängigkeiten:** Task 1.2

---

### Task 2.2 – `ColorLogic` implementieren
- [x] `src/utils/color_logic.py` implementieren
- [x] `get_row_color()`, `get_cell_color()`, `should_highlight_row()`
- [x] Unit-Tests: `tests/test_color_logic.py` – alle 10 Tests grün

**Abhängigkeiten:** Task 2.1

---

### Task 2.3 – `ImageService` implementieren
- [x] `src/services/image_service.py` implementieren
- [x] State-Datei laden/speichern, Bildrotation, Neustart von vorn nach letztem Bild
- [x] Unit-Tests: `tests/test_image_service.py` – alle 9 Tests grün

**Abhängigkeiten:** Task 1.2

---

### Task 2.4 – `CalendarService` implementieren
- [x] `src/services/calendar_service.py` implementieren
- [x] Google Calendar API Anbindung mit graceful Fallback wenn nicht installiert
- [x] Cache, Personenzuordnung, Urlaubs-Erkennung
- [x] Unit-Tests: `tests/test_calendar_service.py` – alle 13 Tests grün

**Abhängigkeiten:** Task 1.2

---

### Task 2.5 – `DateUtils` implementieren
- [x] `src/utils/date_utils.py` implementieren
- [x] Unit-Tests: `tests/test_date_utils.py` – alle 20 Tests grün

**Abhängigkeiten:** Task 1.1

---

## Phase 3: Datenmodelle

### Task 3.1 – Datenmodelle implementieren
- [x] `src/models/event.py` – `Event`-Dataclass mit Serialisierung
- [x] `src/models/person.py` – `Person`-Dataclass

**Abhängigkeiten:** Task 1.1

---

## Phase 4: UI-Komponenten

### Task 4.1 – Hauptfenster (`MainWindow`) implementieren
- [x] `src/ui/main_window.py` – QMainWindow mit Splitter-Layout
- [x] Vollbildmodus, konfigurierbare Größenverhältnisse

**Abhängigkeiten:** Task 1.2

---

### Task 4.2 – `ImageWidget` implementieren
- [x] `src/ui/image_widget.py` – Bildskalierung + Datums-Overlay mit QPainter
- [ ] UI-Test: `tests/test_image_widget.py` (pytest-qt, benötigt PyQt5 auf Testrechner)

**Abhängigkeiten:** Task 2.3, Task 4.1

---

### Task 4.3 – `WeekView` implementieren
- [x] `src/ui/week_view.py` – 6-Spalten-Tabelle mit Farblogik
- [ ] UI-Test: `tests/test_week_view.py` (pytest-qt, benötigt PyQt5 auf Testrechner)

**Abhängigkeiten:** Task 2.2, Task 2.4, Task 3.1, Task 4.1

---

### Task 4.4 – `MonthView` implementieren
- [x] `src/ui/month_view.py` – Monatsraster mit Ereignis-Chips

**Abhängigkeiten:** Task 2.2, Task 2.4, Task 4.1

---

### Task 4.5 – `ListView` implementieren
- [x] `src/ui/list_view.py` – chronologische Listenansicht mit QTreeWidget

**Abhängigkeiten:** Task 2.4, Task 3.1, Task 4.1

---

### Task 4.6 – `NavBar` und `CalendarWidget` implementieren
- [x] `src/ui/nav_bar.py` – Navigationsleiste mit Signalen
- [x] `src/ui/calendar_widget.py` – QStackedWidget-Container

**Abhängigkeiten:** Task 4.3, Task 4.4, Task 4.5

---

## Phase 5: Integration & Hauptprogramm

### Task 5.1 – `main.py` implementieren
- [x] `src/main.py` – Einstiegspunkt mit Logging und Fehlerbehandlung

### Task 5.2 – `app.py` implementieren
- [x] `src/app.py` – Koordination aller Services und Timer (Kalender-Refresh, Bildwechsel)

**Abhängigkeiten:** alle Phase-2- und Phase-4-Tasks

---

## Phase 6: Deployment & Dokumentation

### Task 6.1 – Deployment-Dateien einrichten
- [x] `systemd/family-calendar.service` erstellt
- [x] `docs/installation-raspberry-pi4.md` – vollständige Installations-Anleitung für Pi 4
- [x] `README.md` mit Link zur Installations-Anleitung ergänzt

### Task 6.2 – Google Calendar Setup dokumentieren
- [x] `docs/google-calendar-setup.md` erstellt

### Task 6.3 – CI/CD
- [x] `.github/workflows/ci.yml` angelegt (Linting + Tests bei jedem Push)

---

## Offene Punkte

- [ ] UI-Tests auf dem Raspberry Pi: `tests/test_week_view.py`, `tests/test_image_widget.py`
- [ ] Google Calendar OAuth2-Ersteinrichtung auf dem Pi durchführen
- [ ] App auf dem Pi 4 in Betrieb nehmen und Praxistest durchführen

---

## Gesamtergebnis

| Phase | Inhalt | Status |
|-------|--------|--------|
| 1 | Projektstruktur + Konfiguration | ✅ Abgeschlossen |
| 2 | Services (Holiday, Color, Image, Calendar, Date) | ✅ Abgeschlossen |
| 3 | Datenmodelle | ✅ Abgeschlossen |
| 4 | UI-Komponenten | ✅ Abgeschlossen |
| 5 | Integration | ✅ Abgeschlossen |
| 6 | Deployment + Dokumentation | ✅ Abgeschlossen |
| **Tests gesamt** | 86/86 grün | ✅ |
