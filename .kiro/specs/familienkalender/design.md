# Designdokument – Familienkalender auf Raspberry Pi

## 1. Systemarchitektur

Die Anwendung ist in drei Schichten aufgeteilt:

```
┌─────────────────────────────────────────────────────┐
│                  UI-Schicht (PyQt5)                 │
│  ┌────────────────┐  ┌──────────────────────────┐   │
│  │  ImageWidget   │  │   CalendarWidget          │   │
│  │  (oberes 1/3)  │  │   (unteres 2/3)           │   │
│  └────────────────┘  └──────────────────────────┘   │
├─────────────────────────────────────────────────────┤
│               Logik-Schicht (Services)              │
│  ┌──────────────┐ ┌───────────────┐ ┌────────────┐  │
│  │ ImageService │ │CalendarService│ │HolidaySvc  │  │
│  └──────────────┘ └───────────────┘ └────────────┘  │
├─────────────────────────────────────────────────────┤
│               Daten-Schicht                         │
│  ┌──────────────┐ ┌───────────────┐ ┌────────────┐  │
│  │ Bilderordner │ │ Google Cal API│ │ holidays   │  │
│  │ (lokal)      │ │ (OAuth2)      │ │ (Bibliothek│  │
│  └──────────────┘ └───────────────┘ └────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 2. Projektstruktur

```
family-manager/
├── README.md
├── requirements.txt
├── config.yaml                    # Versionierte Standardkonfiguration (ohne Secrets)
├── config.local.yaml              # Lokale Konfiguration mit echten Namen (in .gitignore)
├── .env.example                   # Vorlage für Umgebungsvariablen
├── .gitignore
├── setup.py
│
├── src/
│   ├── main.py                    # Einstiegspunkt
│   ├── app.py                     # Hauptfenster (QMainWindow)
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py         # Layout-Koordination (oberes/unteres Drittel)
│   │   ├── image_widget.py        # Bildanzeige mit Datumsoverlay
│   │   ├── calendar_widget.py     # Kalender-Container (Ansichtsumschaltung)
│   │   ├── week_view.py           # Wochenansicht (6 Spalten)
│   │   ├── month_view.py          # Monatsansicht
│   │   ├── list_view.py           # Listenansicht
│   │   └── nav_bar.py             # Navigationsleiste (Vor/Zurück + Ansichtswahl)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── image_service.py       # Bildrotationslogik
│   │   ├── calendar_service.py    # Google Calendar API Anbindung + Cache
│   │   └── holiday_service.py     # Feiertags-Logik für Hessen
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── event.py               # Datenmodell: Kalender-Ereignis
│   │   └── person.py              # Datenmodell: Person/Kategorie
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config.py              # Konfigurationslader
│       ├── color_logic.py         # Farbzuweisungslogik für Zellen/Zeilen
│       └── date_utils.py          # Datums-Hilfsfunktionen
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_image_service.py
│   ├── test_calendar_service.py
│   ├── test_holiday_service.py
│   ├── test_color_logic.py
│   ├── test_date_utils.py
│   └── test_week_view.py          # UI-Tests mit pytest-qt
│
├── assets/
│   └── default_image.png          # Fallback-Bild
│
└── systemd/
    └── family-calendar.service    # systemd Unit-Datei für Autostart
```

---

## 3. Komponentenbeschreibung

### 3.1 `ImageService`

**Verantwortung:** Verwaltung der Bildrotation.

**Kernlogik:**
- Liest alle `.jpg`/`.png`-Dateien aus dem konfigurierten Verzeichnis.
- Hält einen persistenten Index in einer lokalen State-Datei (`image_state.json`), um zu tracken, welche Bilder bereits gezeigt wurden.
- Gibt beim Aufruf von `get_current_image()` das aktuelle Bild zurück.
- `advance_image()` wird jeden Sonntag um 00:00 Uhr aufgerufen und wählt das nächste ungesehene Bild.
- Sind alle Bilder verbraucht, beginnt die Rotation von vorn (State wird zurückgesetzt).

```python
class ImageService:
    def get_current_image(self) -> Path | None
    def advance_image(self) -> None
    def schedule_weekly_rotation(self) -> None
    def _load_state(self) -> dict
    def _save_state(self, state: dict) -> None
```

### 3.2 `CalendarService`

**Verantwortung:** Google Calendar API Anbindung, Datencaching, Ereignis-Parsing.

**Kernlogik:**
- OAuth2-Authentifizierung mit `token.json` (lokal, nicht versioniert).
- Lädt Ereignisse für einen konfigurierten Zeitraum (Standard: ±4 Wochen).
- Cached Ergebnisse lokal als JSON für Offline-Betrieb.
- Parst Ereignisse und ordnet sie anhand von Kalender-Labels den Personen zu.
- Aktualisiert sich alle X Minuten (konfigurierbar via Timer).

```python
class CalendarService:
    def get_events_for_week(self, week_start: date) -> list[Event]
    def get_events_for_month(self, year: int, month: int) -> list[Event]
    def refresh(self) -> None
    def _assign_person(self, event: dict) -> str  # gibt PERSON_A..D oder 'general' zurück
    def _load_cache(self) -> list[dict]
    def _save_cache(self, events: list[dict]) -> None
```

### 3.3 `HolidayService`

**Verantwortung:** Bestimmung von Feiertagen in Hessen.

**Kernlogik:**
- Nutzt die `holidays`-Bibliothek für Hessen (`HE`).
- Unterscheidet zwischen gesetzlichen Feiertagen (= Sonntag-Farbe, Name in Spalte 1) und sonstigen regionalen Tagen (= keine Farbe, aber Name in Spalte 1).
- Methoden werden von der Farblogik und den UI-Komponenten aufgerufen.

```python
class HolidayService:
    def is_public_holiday(self, d: date) -> bool       # gesetzlich frei
    def is_regional_holiday(self, d: date) -> bool     # regional, nicht frei
    def get_holiday_name(self, d: date) -> str | None
```

### 3.4 `ColorLogic`

**Verantwortung:** Zentrale Farbzuweisungslogik für Zeilen und Zellen.

```python
ROW_COLOR_NORMAL    = "#FFFFFF"
ROW_COLOR_LIGHT_RED = "#FFCCCC"   # Samstag, nicht-freier Feiertag
ROW_COLOR_DARK_RED  = "#FF6666"   # Sonntag, freier Feiertag
CELL_COLOR_VACATION = "#FF9999"   # Urlaub/Frei bei einer Person

def get_row_color(d: date, holiday_service: HolidayService) -> str
def get_cell_color(event: Event) -> str  # prüft "Urlaub"/"Frei" im Titel
```

### 3.5 `WeekView`

**Verantwortung:** Darstellung der Wochenansicht als 6-Spalten-Tabelle.

- Zeigt Mo–So der aktuellen Woche.
- Jede Zeile entspricht einem Tag.
- Spalte 1: Datum + Wochentag (formatiert: `Mo, 04.11.`), bei Feiertagen zusätzlich der Feiertagsname
- Spalten 2–5: Ereignisse der vier Personen (PERSON_A bis PERSON_D)
- Spalte 6: Allgemeine Termine
- Farbgebung gemäß `ColorLogic`.

### 3.6 `ImageWidget`

**Verantwortung:** Anzeige des Fotos mit Datums-Overlay.

- Zeigt das aktuelle Bild skaliert (Aspect Ratio erhalten, kein Zuschnitt).
- Overlay oben links (oder konfigurierbar): transparenter dunkler Hintergrund mit weißer Schrift.
- Inhalt des Overlays: `Montag, 04. November 2026 · KW 45`

---

## 4. Datenmodell

### `Event`

```python
@dataclass
class Event:
    id: str
    title: str
    start: datetime
    end: datetime
    all_day: bool
    person: str          # "PERSON_A", "PERSON_B", "PERSON_C", "PERSON_D", "general"
    calendar_id: str
    is_vacation: bool    # True wenn "Urlaub" oder "Frei" im Titel
```

### `Person`

```python
@dataclass
class Person:
    key: str             # z.B. "PERSON_A"
    display_name: str    # wird aus lokaler Config geladen, nicht versioniert
    calendar_label: str  # Google Calendar Label/Farbe zur Zuordnung
    column_index: int    # 1-4
```

---

## 5. Konfigurationsstruktur

### `config.yaml` (versioniert)

```yaml
display:
  width: 1920
  height: 1080
  fullscreen: true
  image_area_ratio: 0.33       # oberes Drittel

images:
  directory: "~/Bilder/familienkalender"
  state_file: "~/.family-calendar/image_state.json"
  fallback_image: "assets/default_image.png"

calendar:
  refresh_interval_minutes: 15
  cache_file: "~/.family-calendar/calendar_cache.json"
  credentials_file: "~/.family-calendar/credentials.json"
  token_file: "~/.family-calendar/token.json"
  lookahead_weeks: 4

holidays:
  state: "HE"    # Hessen

persons:
  - key: "PERSON_A"
    column: 1
  - key: "PERSON_B"
    column: 2
  - key: "PERSON_C"
    column: 3
  - key: "PERSON_D"
    column: 4
```

### `config.local.yaml` (NICHT versioniert – `.gitignore`)

```yaml
persons:
  - key: "PERSON_A"
    display_name: "<echter Vorname>"
    calendar_label: "<Google Kalender Label>"
  - key: "PERSON_B"
    display_name: "<echter Vorname>"
    calendar_label: "<Google Kalender Label>"
  - key: "PERSON_C"
    display_name: "<echter Vorname>"
    calendar_label: "<Google Kalender Label>"
  - key: "PERSON_D"
    display_name: "<echter Vorname>"
    calendar_label: "<Google Kalender Label>"
```

---

## 6. UI-Layout

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   [ Foto des Monats – skaliert, Bildformat beliebig ]   │ ~33%
│                                                         │
│  ┌─ Overlay (transparent) ──────────────────────────┐   │
│  │  Montag, 04. November 2026  ·  KW 45              │   │
│  └───────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│ [< Zurück]  KW 45 · 04.–10. Nov 2026  [Vor >]  [W M L] │ Navbar
├──────┬────────┬────────┬────────┬────────┬──────────────┤
│Datum │PERSON_A│PERSON_B│PERSON_C│PERSON_D│  Allgemein   │
├──────┼────────┼────────┼────────┼────────┼──────────────┤
│Mo 04.│        │        │ Zahnarzt│       │ Elternabend  │ ~67%
│Di 05.│ Meeting│        │        │        │              │
│Mi 06.│        │ Urlaub ←rot nur diese Zelle             │
│Do 07.│        │        │        │        │              │
│Fr 08.│        │        │        │        │              │
│Sa 09.│←──────── gesamte Zeile hell-rot ─────────────────│
│So 10.│←──────── gesamte Zeile kräftig-rot ──────────────│
└──────┴────────┴────────┴────────┴────────┴──────────────┘
```

---

## 7. Testplan

| Testklasse | Getestete Komponente | Testfälle |
|------------|---------------------|-----------|
| `test_image_service.py` | `ImageService` | Erster Start (kein State), nächstes Bild, alle Bilder verbraucht → Neustart von vorn, Bilder-Verzeichnis leer → Fallback |
| `test_holiday_service.py` | `HolidayService` | Gesetzlicher Feiertag HE (Name korrekt + Farbe), nicht-freier Feiertag (Name korrekt, keine Farbe), Wochentag, Sonntag |
| `test_color_logic.py` | `ColorLogic` | Samstag→hellrot, Sonntag→dunkelrot, Feiertag→dunkelrot, Urlaub→Zelle rot, normaler Tag→weiß |
| `test_calendar_service.py` | `CalendarService` | Personenzuordnung, Urlaub-Erkennung, Offline-Cache, Wochenabruf |
| `test_date_utils.py` | `DateUtils` | Wochenanfang, KW-Berechnung, Sonntag-Mitternacht-Prüfung |
| `test_week_view.py` | `WeekView` (UI) | Spaltenstruktur, Farben, Touch-Navigation (pytest-qt) |

---

## 8. Deployment

### systemd Service (`/etc/systemd/system/family-calendar.service`)

```ini
[Unit]
Description=Family Calendar Display
After=graphical.target network-online.target
Wants=network-online.target

[Service]
User=pi
Environment=DISPLAY=:0
WorkingDirectory=/home/pi/family-manager
ExecStart=/home/pi/family-manager/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
```

### Installation auf dem Raspberry Pi

```bash
# Abhängigkeiten
sudo apt install python3-pyqt5 python3-pip
pip install -r requirements.txt

# Autostart aktivieren
sudo systemctl enable family-calendar
sudo systemctl start family-calendar
```

---

## 9. Sicherheit & Datenschutz

- `config.local.yaml`, `token.json`, `credentials.json` sind in `.gitignore` eingetragen.
- Keine Personennamen im versionierten Code.
- Google API läuft mit minimalem Scope: `https://www.googleapis.com/auth/calendar.readonly`.
- Kein Netzwerkzugriff außer Google Calendar API.
