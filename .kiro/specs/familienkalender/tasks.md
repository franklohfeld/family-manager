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
- [x] `.env.example` anlegen (ohne echte Werte)
- [x] `requirements.txt` erstellen
- [x] `setup.py` erstellen

**Ergebnis:** Leeres, aber vollständig strukturiertes Repository

---

### Task 1.2 – Konfigurationssystem implementieren
- [x] `config.yaml` (Standard-Konfiguration, versioniert) anlegen
- [x] `config.local.yaml.example` anlegen
- [x] `src/utils/config.py` implementieren
- [ ] Unit-Test: `tests/test_config.py`

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
- [x] State-Datei laden/speichern, Bildrotation, Fallback
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
- [x] `src/models/event.py` – `Event`-Dataclass
- [x] `src/models/person.py` – `Person`-Dataclass
- [x] Serialisierung/Deserialisierung für Cache (JSON)

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
- [ ] UI-Test: `tests/test_image_widget.py` (pytest-qt, benötigt PyQt5)

**Abhängigkeiten:** Task 2.3, Task 4.1

---

### Task 4.3 – `WeekView` implementieren
- [x] `src/ui/week_view.py` – 6-Spalten-Tabelle mit Farblogik
- [ ] UI-Test: `tests/test_week_view.py` (pytest-qt, benötigt PyQt5)

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
- [x] `src/app.py` – Koordination aller Services und Timer

**Abhängigkeiten:** alle Phase-2- und Phase-4-Tasks

---

## Phase 6: Deployment & Dokumentation

### Task 6.1 – systemd-Service einrichten
- [x] `systemd/family-calendar.service` erstellt

### Task 6.2 – Google Calendar Setup dokumentieren
- [x] `docs/google-calendar-setup.md` erstellt

### Task 6.3 – CI/CD
- [x] `.github/workflows/ci.yml` angelegt (Linting + Tests bei jedem Push)

---

## Offene Punkte

- [ ] PyQt5 UI-Tests (`tests/test_week_view.py`, `tests/test_image_widget.py`) – benötigen PyQt5 auf Testrechner
- [ ] `tests/test_config.py` – Konfigurationslader-Tests
- [ ] Lokaler Test der vollständigen App auf Raspberry Pi
- [ ] Google Calendar OAuth2-Ersteinrichtung auf dem Pi durchführen

**Ergebnis:** Leeres, aber vollständig strukturiertes Repository

---

### Task 1.2 – Konfigurationssystem implementieren
- [ ] `config.yaml` (Standard-Konfiguration, versioniert) anlegen
- [ ] `config.local.yaml.example` anlegen
- [ ] `src/utils/config.py` implementieren:
  - Lädt `config.yaml` und mergt mit `config.local.yaml` (falls vorhanden)
  - Stellt typsichere Zugriffsmethoden bereit
  - Gibt sinnvolle Fehlermeldungen bei fehlenden Pflichtfeldern
- [ ] Unit-Test: `tests/test_config.py`

**Abhängigkeiten:** Task 1.1

---

## Phase 2: Services

### Task 2.1 – `HolidayService` implementieren
- [ ] `src/services/holiday_service.py` implementieren
- [ ] `holidays`-Bibliothek für Hessen (`HE`) einbinden
- [ ] `is_public_holiday(d)` – gesetzlich freier Feiertag in HE
- [ ] `is_regional_holiday(d)` – regional aber nicht frei
- [ ] `get_holiday_name(d)` – Name des Feiertags oder None
- [ ] Unit-Tests: `tests/test_holiday_service.py`
  - Neujahr (frei, Name wird zurückgegeben)
  - Reformationstag (nicht frei in HE, aber Name wird zurückgegeben)
  - Normaler Wochentag (kein Name)
  - Sonntag (kein Feiertag)
  - Pfingstmontag (frei, Name wird zurückgegeben)

**Abhängigkeiten:** Task 1.2

---

### Task 2.2 – `ColorLogic` implementieren
- [ ] `src/utils/color_logic.py` implementieren
- [ ] `get_row_color(d, holiday_service)` – gibt Hex-Farbe für die gesamte Zeile zurück
- [ ] `get_cell_color(event)` – prüft Urlaub/Frei im Titel (case-insensitive)
- [ ] Farbkonstanten definieren (NORMAL, LIGHT_RED, DARK_RED, VACATION)
- [ ] Unit-Tests: `tests/test_color_logic.py`
  - Samstag → `#FFCCCC`
  - Sonntag → `#FF6666`
  - Gesetzlicher Feiertag → `#FF6666`
  - Nicht-freier Feiertag → keine Zeilenfarbe, aber Name sichtbar
  - Normaler Tag → `#FFFFFF`
  - Event mit "Urlaub" im Titel → `#FF9999`
  - Event mit "Frei" im Titel → `#FF9999`
  - Event mit normalem Titel → keine Zellfarbe

**Abhängigkeiten:** Task 2.1

---

### Task 2.3 – `ImageService` implementieren
- [ ] `src/services/image_service.py` implementieren
- [ ] Scan des konfigurierten Bildverzeichnisses (JPG, PNG)
- [ ] State-Datei laden/speichern (`image_state.json`): aktuelles Bild, gezeigte Bilder
- [ ] `get_current_image()` – gibt Pfad zum aktuellen Bild zurück
- [ ] `advance_image()` – wählt nächstes ungesehenes Bild
- [ ] Scheduler: Sonntag 00:00 Uhr → `advance_image()` aufrufen
- [ ] Fallback auf `assets/default_image.png` wenn keine Bilder vorhanden
- [ ] Unit-Tests: `tests/test_image_service.py`
  - Erster Start (leerer State) → erstes Bild aus Verzeichnis
  - `advance_image()` → nächstes Bild
  - Alle Bilder verbraucht → Rotation beginnt von vorn
  - Bilder-Verzeichnis leer → Fallback-Bild
  - State-Datei korrumpiert → sauberes Recovery

**Abhängigkeiten:** Task 1.2

---

### Task 2.4 – `CalendarService` implementieren
- [ ] `src/services/calendar_service.py` implementieren
- [ ] Google Calendar OAuth2-Authentifizierung einrichten
- [ ] `get_events_for_week(week_start)` – Events der Woche abrufen
- [ ] `get_events_for_month(year, month)` – Events des Monats abrufen
- [ ] Personenzuordnung: Google Kalender Label → PERSON_A..D oder "general"
- [ ] `is_vacation_event(event)` – prüft "Urlaub"/"Frei" im Titel
- [ ] Lokalen Cache anlegen/laden/speichern
- [ ] Timer für automatische Aktualisierung (alle X Minuten)
- [ ] Offline-Fallback auf Cache
- [ ] Unit-Tests: `tests/test_calendar_service.py`
  - Personenzuordnung korrekt
  - Urlaub-Erkennung (Groß-/Kleinschreibung)
  - Offline-Cache wird geladen wenn API nicht erreichbar
  - Ereignisse für korrekte Woche gefiltert

**Abhängigkeiten:** Task 1.2

---

### Task 2.5 – `DateUtils` implementieren
- [ ] `src/utils/date_utils.py` implementieren
- [ ] `get_week_start(d)` – Montag der Woche von Datum `d`
- [ ] `get_week_number(d)` – ISO-Kalenderwoche
- [ ] `get_week_dates(week_start)` – Liste der 7 Tage (Mo–So)
- [ ] `is_sunday_midnight(dt)` – prüft ob es Sonntag 00:00 ist (für Bildwechsel)
- [ ] `format_date_display(d)` – `"Montag, 04. November 2026"`
- [ ] `format_week_header(week_start)` – `"KW 45 · 04.–10. Nov 2026"`
- [ ] Unit-Tests: `tests/test_date_utils.py`

**Abhängigkeiten:** Task 1.1

---

## Phase 3: Datenmodelle

### Task 3.1 – Datenmodelle implementieren
- [ ] `src/models/event.py` – `Event`-Dataclass mit allen Feldern
- [ ] `src/models/person.py` – `Person`-Dataclass
- [ ] Serialisierung/Deserialisierung für Cache (JSON)

**Abhängigkeiten:** Task 1.1

---

## Phase 4: UI-Komponenten

### Task 4.1 – Hauptfenster (`MainWindow`) implementieren
- [ ] `src/ui/main_window.py` – QMainWindow-Subklasse
- [ ] Layout: oberes Drittel = `ImageWidget`, unteres Zweidrittel = `CalendarWidget`
- [ ] Vollbildmodus konfigurierbar
- [ ] Korrekte Größenverhältnisse via `QSplitter` oder feste Anteile

**Abhängigkeiten:** Task 1.2

---

### Task 4.2 – `ImageWidget` implementieren
- [ ] `src/ui/image_widget.py` – QWidget-Subklasse
- [ ] Bild laden und skaliert darstellen (Aspect Ratio erhalten)
- [ ] Datums-Overlay mit transparentem Hintergrund (QPainter)
- [ ] Overlay-Inhalt: Wochentag, Datum, Kalenderwoche
- [ ] Lesbare Schrift (weiß mit Schatten)
- [ ] Automatischer Bildwechsel via Signal vom `ImageService`
- [ ] UI-Test: `tests/test_image_widget.py` (pytest-qt)

**Abhängigkeiten:** Task 2.3, Task 4.1

---

### Task 4.3 – `WeekView` implementieren
- [ ] `src/ui/week_view.py` – QTableWidget oder benutzerdefiniertes Widget
- [ ] 6 Spalten: Datum, PERSON_A, PERSON_B, PERSON_C, PERSON_D, Allgemein
- [ ] Spaltenüberschriften mit konfigurierten Anzeigenamen
- [ ] Zeilenfärbung via `ColorLogic`
- [ ] Zellfärbung für Urlaubs-Events
- [ ] Mehrere Events pro Zelle/Tag möglich
- [ ] Touch-freundliche Zeilenhöhe und Schriftgröße
- [ ] UI-Test: `tests/test_week_view.py`

**Abhängigkeiten:** Task 2.2, Task 2.4, Task 3.1, Task 4.1

---

### Task 4.4 – `MonthView` implementieren
- [ ] `src/ui/month_view.py` – Monatsübersicht als Grid (7 Spalten × ~5 Zeilen)
- [ ] Feiertage und Wochenenden farblich hervorgehoben
- [ ] Termine als kompakte Chips in den Tageszellen
- [ ] Konfigurierte Personennamen als Präfix der Chips

**Abhängigkeiten:** Task 2.2, Task 2.4, Task 4.1

---

### Task 4.5 – `ListView` implementieren
- [ ] `src/ui/list_view.py` – chronologische Liste aller Events
- [ ] Sortiert nach Datum/Uhrzeit
- [ ] Gruppenheader pro Tag
- [ ] Person als farbiger Indikator links

**Abhängigkeiten:** Task 2.4, Task 3.1, Task 4.1

---

### Task 4.6 – `NavBar` und `CalendarWidget` implementieren
- [ ] `src/ui/nav_bar.py` – Navigationsleiste
  - Buttons: `< Zurück`, Anzeige des aktuellen Zeitraums, `Vor >`
  - Toggle-Buttons: `W` (Woche), `M` (Monat), `L` (Liste)
- [ ] `src/ui/calendar_widget.py` – Container mit `QStackedWidget`
  - Verwaltet Umschaltung zwischen den drei Ansichten
  - Leitet Navigation an aktive Ansicht weiter

**Abhängigkeiten:** Task 4.3, Task 4.4, Task 4.5

---

## Phase 5: Integration & Hauptprogramm

### Task 5.1 – `main.py` implementieren
- [ ] `src/main.py` – Einstiegspunkt
- [ ] QApplication erstellen
- [ ] Services initialisieren
- [ ] Hauptfenster starten
- [ ] Fehlerbehandlung für fehlende Konfiguration

### Task 5.2 – `app.py` implementieren
- [ ] `src/app.py` – Koordination aller Komponenten
- [ ] Services mit UI-Widgets verbinden (Qt Signals/Slots)
- [ ] Kalender-Refresh-Timer starten
- [ ] Bild-Rotations-Scheduler starten

**Abhängigkeiten:** alle Phase-2- und Phase-4-Tasks

---

## Phase 6: Deployment & Dokumentation

### Task 6.1 – systemd-Service einrichten
- [ ] `systemd/family-calendar.service` erstellen
- [ ] Installations-Skript `install.sh` schreiben
- [ ] Anleitung in `README.md` ergänzen

### Task 6.2 – Google Calendar Setup dokumentieren
- [ ] Schritt-für-Schritt-Anleitung: Google Cloud Projekt, OAuth2-Credentials, Scope
- [ ] Anleitung in `README.md` ergänzen
- [ ] `docs/google-calendar-setup.md` erstellen

### Task 6.3 – CI/CD (optional)
- [ ] GitHub Actions Workflow: Linting (`flake8`/`ruff`) + Tests (`pytest`) bei jedem Push
- [ ] `.github/workflows/ci.yml` anlegen

---

## Zusammenfassung der Phasen

| Phase | Inhalt | Aufwand (geschätzt) |
|-------|--------|---------------------|
| 1 | Projektstruktur + Konfiguration | 1–2h |
| 2 | Services (Holiday, Color, Image, Calendar, Date) | 4–6h |
| 3 | Datenmodelle | 1h |
| 4 | UI-Komponenten | 6–8h |
| 5 | Integration | 2h |
| 6 | Deployment + Dokumentation | 2h |
| **Gesamt** | | **~16–20h** |
