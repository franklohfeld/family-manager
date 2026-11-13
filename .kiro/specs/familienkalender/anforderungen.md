# Anforderungsspezifikation – Familienkalender auf Raspberry Pi

## Projektübersicht

Eine Touchscreen-Kalenderanwendung für den Raspberry Pi, die als digitales Familien-Dashboard dient. Die Anwendung zeigt rotierende Familienfotos im oberen Bildschirmbereich und einen Google-Calendar-basierten Familienplaner im unteren Bereich.

---

## 1. Funktionale Anforderungen

### 1.1 Bildanzeige (oberes Drittel)

| ID | Anforderung |
|----|-------------|
| FA-01 | Im oberen Drittel des Bildschirms wird dauerhaft ein Foto angezeigt. |
| FA-02 | Die Bilder werden aus einem konfigurierbaren lokalen Verzeichnis geladen. |
| FA-03 | Jedes Bild wird genau eine Woche lang angezeigt. |
| FA-04 | Jedes Bild wird nur einmal angezeigt (keine Wiederholung). |
| FA-05 | Der Bildwechsel erfolgt automatisch jeden Sonntag um Mitternacht (00:00 Uhr). |
| FA-06 | Sind alle Bilder einmal gezeigt worden, beginnt die Rotation von vorn – alle Bilder gelten wieder als „neu". |
| FA-07 | Über dem Bild wird – mit transparentem Hintergrund – das heutige Datum, der Wochentag und die Kalenderwoche angezeigt. |
| FA-08 | Die Datums-/Wochenanzeige ist jederzeit gut lesbar (Schriftfarbe mit Kontrast, ggf. leichter Schatten). |

### 1.2 Familienplaner (unteres Drittel)

| ID | Anforderung |
|----|-------------|
| FA-10 | Im unteren Bereich wird ein Familienplaner angezeigt. |
| FA-11 | Die Standardansicht ist die **Wochenansicht**. |
| FA-12 | Umschaltbar auf **Monatsansicht** und **Listenansicht**. |
| FA-13 | Navigation zwischen Wochen (Wochenansicht) bzw. Monaten (Monatsansicht) per Touch möglich. |
| FA-14 | Termine werden aus einem **Google Kalender** synchronisiert. |
| FA-15 | Die Synchronisierung erfolgt automatisch in regelmäßigen Abständen (konfigurierbar, Standard: alle 15 Minuten). |

### 1.3 Wochenansicht – Spaltenstruktur

Die Wochenansicht zeigt 6 Spalten:

| Spalte | Inhalt |
|--------|--------|
| 1 | Datum und Wochentag |
| 2 | Termine von **Person A** (Kategorie/Label konfigurierbar) |
| 3 | Termine von **Person B** |
| 4 | Termine von **Person C** |
| 5 | Termine von **Person D** |
| 6 | Allgemeine Termine (ohne Kategorie) |

> **Hinweis zur Konfiguration:** Die echten Personennamen werden ausschließlich in einer lokalen Konfigurationsdatei (`.env` oder `config.local.yaml`) gespeichert, die **nicht** in das Git-Repository eingecheckt wird. Im Quellcode und in allen öffentlichen Dateien werden die Platzhalter `PERSON_A`, `PERSON_B`, `PERSON_C`, `PERSON_D` verwendet.

### 1.4 Farbliche Darstellung in der Wochenansicht

| ID | Bedingung | Darstellung |
|----|-----------|-------------|
| FA-20 | Samstag | Gesamte Zeile in hellem Rot (`#FFCCCC`) |
| FA-21 | Hessischer Feiertag – kein gesetzlicher freier Tag | Keine farbliche Kennzeichnung der Zeile; in Spalte 1 wird zusätzlich zum Datum der Name des Feiertags angezeigt. |
| FA-22 | Sonntag | Gesamte Zeile in kräftigem Rot (`#FF6666`) |
| FA-23 | Hessischer Feiertag – gesetzlich frei | Gesamte Zeile in kräftigem Rot (`#FF6666`); in Spalte 1 wird zusätzlich zum Datum der Name des Feiertags angezeigt. |
| FA-24 | Ein Termin einer Person enthält „Urlaub" oder „Frei" im Namen | Nur die Zelle dieser Person wird rot markiert (nicht die gesamte Zeile) |
| FA-25 | FA-24 gilt unabhängig vom Wochentag | Überschreibung durch FA-22/FA-23 nur auf Zeilenebene, nicht auf Zellebene |

### 1.5 Konfiguration

| ID | Anforderung |
|----|-------------|
| FA-30 | Bildverzeichnis ist konfigurierbar. |
| FA-31 | Google Calendar API-Zugangsdaten werden aus einer lokalen, nicht versionierten Datei geladen. |
| FA-32 | Personennamen/-kategorien sind konfigurierbar (Mapping von Kalender-Label zu Spalte). |
| FA-33 | Aktualisierungsintervall für Kalender ist konfigurierbar. |
| FA-34 | Feiertags-Bundesland ist konfigurierbar (Standard: Hessen). |
| FA-35 | Bildschirmauflösung und UI-Skalierung sind konfigurierbar (für verschiedene Touchscreen-Größen). |
| FA-36 | Der Bildschirm kann im **Hochformat (Portrait)** oder **Querformat (Landscape)** betrieben werden. Die Ausrichtung ist konfigurierbar. |
| FA-37 | Im Hochformat bleibt die Aufteilung (Foto oben, Kalender unten) erhalten. Schriftgrößen und Spaltenbreiten passen sich automatisch an die Bildschirmbreite an. |

---

## 2. Nicht-funktionale Anforderungen

| ID | Anforderung |
|----|-------------|
| NFA-01 | Die Anwendung läuft stabil auf einem Raspberry Pi 4 (mind. 2 GB RAM). |
| NFA-02 | Die Anwendung startet automatisch beim Systemstart (systemd-Service). |
| NFA-03 | Touch-Interaktion muss reaktionsschnell sein (< 200 ms Reaktionszeit). |
| NFA-04 | Die Anwendung läuft im Vollbildmodus ohne Fensterrahmen. |
| NFA-05 | Keine Internet-Verbindung darf zum Absturz führen – Fallback auf gecachte Daten. |
| NFA-06 | Alle sensiblen Daten (API-Keys, Personennamen) bleiben lokal und werden nicht eingecheckt. |
| NFA-07 | Der Quellcode ist sauber dokumentiert und auf **Deutsch** kommentiert. |
| NFA-08 | Unit-Tests decken mindestens die Kernlogik ab (Bildrotation, Feiertage, Farblogik, Kalender-Parsing). |

---

## 3. Technologie-Stack

| Komponente | Technologie | Begründung |
|------------|-------------|------------|
| Programmiersprache | Python 3.11+ | Beste Raspberry Pi Unterstützung |
| UI-Framework | PyQt5 | Stabil, Touch-freundlich, gute Performance auf ARM |
| Google Calendar | `google-api-python-client` | Offizielle Google-Bibliothek |
| Feiertage | `holidays` (Python) | Unterstützt Hessen direkt |
| Konfiguration | `python-dotenv` + YAML | Trennung von lokalen und versionierten Einstellungen |
| Tests | `pytest` + `pytest-qt` | Standard für Python-Projekte |
| Autostart | `systemd` | Zuverlässigster Autostart auf Raspberry Pi OS |

---

## 4. Systemgrenzen und Abgrenzungen

- Die App läuft **lokal** auf dem Raspberry Pi; es gibt kein Backend oder Web-Interface.
- Die App **liest** den Google Kalender nur; es werden keine Termine über die App erstellt oder geändert.
- Es gibt keine Benutzerverwaltung oder Authentifizierung in der App selbst.
- Die App ist für den **Dauerbetrieb** (24/7) ausgelegt.

---

## 5. Offene Punkte / Annahmen

- Der Google Kalender verwendet Labels/Farben zur Personenzuordnung (Konfiguration erforderlich).
- Die Feiertags-Logik unterscheidet zwischen „frei" und „nicht frei" gemäß Hessischem Kalender.
- Bildformat: JPG und PNG werden unterstützt.
- Maximale Bildanzahl im Verzeichnis: unbegrenzt.

---

## 6. Hardware-Kompatibilität und Display-Ausrichtung

### Unterstützte Hardware

| Hardware | Unterstützt | Hinweis |
|----------|-------------|---------|
| Raspberry Pi 4 (2/4/8 GB) | ✅ | Empfohlen, gut getestet |
| Raspberry Pi 5 (2/4/8 GB) | ✅ | Ebenfalls unterstützt – bessere Performance |
| Raspberry Pi 3B+ | ⚠️ | Eingeschränkt – kann bei großen Bildern träge sein |

### Display-Ausrichtung

Die App unterstützt beide Ausrichtungen. Die Konfiguration erfolgt in `config.yaml`:

```yaml
display:
  orientation: "landscape"   # oder "portrait"
  width: 1920
  height: 1080
```

**Querformat (Landscape)** – Standard  
Typische Auflösung: 1920×1080 oder 1280×800

**Hochformat (Portrait)** – Empfohlen für Bilderrahmen-Optik  
Typische Auflösung: 1080×1920 oder 800×1280

- Das Foto wirkt im Hochformat natürlicher (wie ein digitaler Bilderrahmen)
- Die Wochenansicht gewinnt mehr vertikalen Platz für Termine
- Breite und Höhe in `config.yaml` einfach tauschen
- Betriebssystem-Rotation: in `/boot/config.txt` `display_rotate=1` (90°) oder `display_rotate=3` (270°) eintragen
- PyQt5 bekommt die gedrehten Dimensionen automatisch – keine Code-Änderung nötig
