# Family Manager – Familienkalender auf dem Raspberry Pi

Ein digitales Familien-Dashboard für den Raspberry Pi mit Touchscreen. Die Anwendung kombiniert eine rotierende Fotoanzeige mit einem Google-Calendar-basierten Familienplaner.

---

## Funktionsübersicht

**Oberes Drittel – Fotoanzeige**
- Zeigt Fotos aus einem lokalen Verzeichnis an
- Jedes Foto wird genau eine Woche lang angezeigt, danach automatischer Wechsel (Sonntag 00:00 Uhr)
- Jedes Foto wird einmalig gezeigt; nach dem letzten Bild beginnt die Rotation von vorn
- Über dem Foto: Datum, Wochentag und Kalenderwoche mit transparentem Hintergrund

**Unteres Zweidrittel – Familienplaner**
- Datenquelle: Google Kalender (read-only)
- Drei Ansichten: Woche, Monat, Liste – per Touch umschaltbar
- Navigation zwischen Wochen bzw. Monaten per Touch
- Automatische Aktualisierung alle 15 Minuten (konfigurierbar)
- Offline-Betrieb durch lokalen Cache

**Wochenansicht – 6 Spalten**

| Spalte | Inhalt |
|--------|--------|
| 1 | Datum, Wochentag, ggf. Feiertagsname |
| 2–5 | Termine der vier Familienmitglieder (konfigurierbar) |
| 6 | Allgemeine Termine ohne Kategorie |

**Farbliche Kennzeichnung**

| Tag | Farbe |
|-----|-------|
| Samstag | Zeile hell-rot (`#FFCCCC`) |
| Sonntag | Zeile kräftig-rot (`#FF6666`) |
| Gesetzlicher Feiertag (Hessen) | Zeile kräftig-rot + Feiertagsname in Spalte 1 |
| Nicht-freier Feiertag | Keine Zeilenfarbe, aber Feiertagsname in Spalte 1 |
| Termin mit „Urlaub" / „Frei" im Namen | Nur die Zelle der betreffenden Person rot |

---

## Voraussetzungen

- Raspberry Pi 4 (mind. 2 GB RAM, 4 GB empfohlen)
- Raspberry Pi OS (64-bit empfohlen)
- Touchscreen-Monitor (Quer- oder **Hochformat**)
- Python 3.11+
- Google-Konto mit Kalender-Zugriff

---

## Installation

Eine ausführliche Schritt-für-Schritt-Anleitung speziell für den Raspberry Pi 4 findest du hier:

**[→ docs/installation-raspberry-pi4.md](docs/installation-raspberry-pi4.md)**

Kurzfassung:

```bash
git clone https://github.com/franklohfeld/family-manager.git
cd family-manager
```

### 2. Python-Abhängigkeiten installieren

```bash
sudo apt install python3-pyqt5 python3-pip
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Konfiguration anlegen

```bash
cp config.local.yaml.example config.local.yaml
```

Die Datei `config.local.yaml` enthält die echten Personennamen und Google-Kalender-Labels. Sie wird **nicht** ins Repository eingecheckt.

### 4. Google Calendar einrichten

Eine ausführliche Schritt-für-Schritt-Anleitung findest du unter [`docs/google-calendar-setup.md`](docs/google-calendar-setup.md).

Kurzfassung:
1. Google Cloud Projekt anlegen
2. Google Calendar API aktivieren
3. OAuth2-Zugangsdaten (Desktop-App) erstellen und als `credentials.json` speichern unter `~/.family-calendar/credentials.json`
4. Beim ersten Start öffnet sich ein Browser-Fenster zur Authentifizierung – danach wird `token.json` lokal gespeichert

### 5. Bilder vorbereiten

Fotos (JPG oder PNG) in das konfigurierte Bildverzeichnis legen (Standard: `~/Bilder/familienkalender`). Das Verzeichnis kann in `config.yaml` angepasst werden.

### 6. Anwendung starten

```bash
source venv/bin/activate
python src/main.py
```

---

## Display-Ausrichtung (Hoch- oder Querformat)

Die App unterstützt beide Ausrichtungen. Das Hochformat eignet sich besonders gut – das Foto wirkt wie ein digitaler Bilderrahmen, und die Wochenansicht bekommt mehr Platz.

**Querformat (Standard):** `width: 1920, height: 1080`

**Hochformat:** Werte tauschen und Rotation im Betriebssystem aktivieren:

1. In `config.yaml` anpassen:
```yaml
display:
  orientation: "portrait"
  width: 1080
  height: 1920
  font_size_date_overlay: 28   # optional größer
```

2. In `/boot/config.txt` (einmalig, Raspberry Pi OS):
```
display_rotate=1   # 90° im Uhrzeigersinn
# oder
display_rotate=3   # 270° (je nach Montagerichtung)
```

3. Pi neu starten – PyQt5 übernimmt die gedrehten Dimensionen automatisch.

---

Damit die Anwendung automatisch beim Systemstart läuft:

```bash
sudo cp systemd/family-calendar.service /etc/systemd/system/
sudo systemctl enable family-calendar
sudo systemctl start family-calendar
```

Status prüfen:

```bash
sudo systemctl status family-calendar
```

---

## Konfiguration

### `config.yaml` (versioniert – Standardwerte)

Enthält allgemeine Einstellungen wie Bildschirmauflösung, Bildverzeichnis, Aktualisierungsintervall und Bundesland für Feiertage.

### `config.local.yaml` (lokal – **nicht** versioniert)

Enthält die echten Personennamen und Google-Kalender-Labels. Vorlage: `config.local.yaml.example`.

### Sensible Dateien (niemals einchecken)

| Datei | Inhalt |
|-------|--------|
| `config.local.yaml` | Personennamen, Kalender-Labels |
| `~/.family-calendar/credentials.json` | Google OAuth2-Zugangsdaten |
| `~/.family-calendar/token.json` | Google OAuth2-Token |

---

## Projektstruktur

```
family-manager/
├── src/
│   ├── main.py              # Einstiegspunkt
│   ├── app.py               # Hauptkoordination
│   ├── ui/                  # UI-Komponenten (PyQt5)
│   ├── services/            # Geschäftslogik (Bilder, Kalender, Feiertage)
│   ├── models/              # Datenmodelle
│   └── utils/               # Hilfsfunktionen, Konfiguration, Farblogik
├── tests/                   # Unit-Tests (pytest)
├── assets/                  # Fallback-Bild
├── systemd/                 # systemd Service-Datei
├── docs/                    # Zusätzliche Dokumentation
├── config.yaml              # Standardkonfiguration
└── config.local.yaml.example
```

---

## Tests ausführen

```bash
source venv/bin/activate
pytest tests/
```

---

## Spezifikation & Design

Die vollständige Spezifikation, das Designdokument und die Aufgabenliste liegen unter:

- [Anforderungen](.kiro/specs/familienkalender/anforderungen.md)
- [Design](.kiro/specs/familienkalender/design.md)
- [Aufgaben](.kiro/specs/familienkalender/tasks.md)

---

## Datenschutz & Sicherheit

Die Namen der Familienmitglieder sind **nicht** im Quellcode oder in versionierten Dateien enthalten. Sie werden ausschließlich lokal in `config.local.yaml` gespeichert. Der Google-Kalender wird nur lesend abgerufen (Scope: `calendar.readonly`).

---

## Lizenz

Privates Projekt – kein öffentliches Release vorgesehen.
