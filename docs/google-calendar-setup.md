# Google Calendar Einrichtung

Diese Anleitung beschreibt, wie du die Google Calendar API für den Familienkalender einrichtest.

## Schritt 1: Google Cloud Projekt anlegen

1. Öffne die [Google Cloud Console](https://console.cloud.google.com/)
2. Klick auf "Projekt auswählen" → "Neues Projekt"
3. Vergib einen Namen (z.B. "Familienkalender")
4. Klick auf "Erstellen"

## Schritt 2: Google Calendar API aktivieren

1. Im Projekt auf "APIs und Dienste" → "Bibliothek"
2. Suche nach "Google Calendar API"
3. Klick auf "Aktivieren"

## Schritt 3: OAuth2-Zugangsdaten erstellen

1. Gehe zu "APIs und Dienste" → "Anmeldedaten"
2. Klick auf "+ Anmeldedaten erstellen" → "OAuth-Client-ID"
3. Beim ersten Mal: "Zustimmungsbildschirm konfigurieren"
   - Nutzertyp: "Extern"
   - App-Name: "Familienkalender"
   - Deine E-Mail-Adresse eintragen
   - Unter "Testnutzer": deine Google-Adresse hinzufügen
4. Zurück zu "Anmeldedaten" → "+ Anmeldedaten erstellen" → "OAuth-Client-ID"
   - Anwendungstyp: **Desktop-App**
   - Name: "Familienkalender Desktop"
5. Klick auf "Erstellen"
6. Lade die JSON-Datei herunter

## Schritt 4: Zugangsdaten auf dem Raspberry Pi ablegen

```bash
mkdir -p ~/.family-calendar
# Kopiere die heruntergeladene JSON-Datei:
cp ~/Downloads/client_secret_*.json ~/.family-calendar/credentials.json
chmod 600 ~/.family-calendar/credentials.json
```

## Schritt 5: Erste Authentifizierung

Beim ersten Start der App öffnet sich automatisch ein Browser-Fenster.
Falls du am Raspberry Pi keinen Browser nutzen kannst, starte die App
einmalig auf einem anderen Rechner mit demselben Code, dann kopiere
`~/.family-calendar/token.json` auf den Pi.

```bash
# Einmalig auf einem Rechner mit Browser:
python src/main.py
# Im Browser anmelden und Zugriff erlauben
# Danach:
scp ~/.family-calendar/token.json pi@raspberrypi:~/.family-calendar/
```

## Schritt 6: Kalender-Labels konfigurieren

Für die Personenzuordnung wird der **Name des Kalenders** in Google Calendar verwendet.

1. Öffne [Google Calendar](https://calendar.google.com/)
2. In der linken Seitenleiste siehst du alle Kalender
3. Notiere dir den genauen Namen jedes Kalenders (z.B. "Frank", "Eva")
4. Trage diese Namen in `config.local.yaml` ein:

```yaml
persons:
  - key: "PERSON_A"
    display_name: "VornameA"
    calendar_label: "Kalender-Name-in-Google"
```

> Der `calendar_label` muss mit dem Kalendernamen in Google Calendar übereinstimmen
> (Groß-/Kleinschreibung wird ignoriert).

## Fehlerbehebung

**"credentials.json nicht gefunden"**
→ Prüfe den Pfad in `config.yaml` unter `calendar.credentials_file`

**"Token abgelaufen"**
→ Lösche `~/.family-calendar/token.json` und starte die App neu (neue Authentifizierung)

**"Keine Termine sichtbar"**
→ Prüfe `calendar_label` in `config.local.yaml` – muss dem Kalendernamen in Google entsprechen
