# Installationsanleitung – Raspberry Pi 4

Diese Anleitung führt dich Schritt für Schritt durch die vollständige Einrichtung des Familienkalenders auf einem Raspberry Pi 4.

---

## Voraussetzungen

- Raspberry Pi 4 (mind. 2 GB RAM, 4 GB empfohlen)
- microSD-Karte (mind. 16 GB, Class 10)
- Touchscreen-Monitor mit HDMI-Anschluss
- Tastatur und Maus (nur für die Einrichtung)
- Internetverbindung

---

## Schritt 1: Raspberry Pi OS installieren

1. Lade den **Raspberry Pi Imager** herunter: [raspberrypi.com/software](https://www.raspberrypi.com/software/)
2. Stecke die microSD-Karte in deinen Mac
3. Starte den Imager und wähle:
   - **Gerät:** Raspberry Pi 4
   - **Betriebssystem:** Raspberry Pi OS (64-bit) – die Desktop-Version
   - **Speichermedium:** deine microSD-Karte
4. Klick auf das Zahnrad-Symbol (⚙️) und konfiguriere vorab:
   - Hostname: `familienkalender`
   - Benutzername: `pi`, Passwort deiner Wahl
   - WLAN: Netzwerkname und Passwort eintragen
   - SSH aktivieren
   - Spracheinstellungen: Zeitzone `Europe/Berlin`, Tastatur `de`
5. Schreibe das Image auf die Karte und stecke sie in den Pi

---

## Schritt 2: Erststart und System aktualisieren

Verbinde den Pi mit dem Monitor, starte ihn und öffne ein Terminal (oder verbinde dich per SSH):

```bash
ssh pi@familienkalender.local
```

System aktualisieren:

```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

---

## Schritt 3: Bildschirm-Ausrichtung einstellen

### Querformat (Standard)
Keine Änderung nötig.

### Hochformat (Portrait)
Öffne die Boot-Konfiguration:

```bash
sudo nano /boot/config.txt
```

Folgende Zeile am Ende einfügen:

```
# Bildschirm 90° drehen (Portrait-Modus)
display_rotate=1
```

> `display_rotate=1` dreht 90° im Uhrzeigersinn.  
> `display_rotate=3` dreht 270° (je nach Montagerichtung des Monitors).

Datei speichern (`Strg+O`, `Enter`, `Strg+X`) und neu starten:

```bash
sudo reboot
```

Passe danach `config.yaml` im Projekt entsprechend an:

```yaml
display:
  orientation: "portrait"
  width: 1080    # Breite und Höhe tauschen
  height: 1920
```

---

## Schritt 4: Abhängigkeiten installieren

```bash
# System-Pakete (PyQt5 und Grafikbibliotheken)
sudo apt install -y python3-pyqt5 python3-pip python3-venv git

# Prüfen ob PyQt5 korrekt installiert ist
python3 -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
```

---

## Schritt 5: Projekt klonen

```bash
cd ~
git clone https://github.com/franklohfeld/family-manager.git
cd family-manager
```

---

## Schritt 6: Python Virtual Environment einrichten

```bash
python3 -m venv venv
source venv/bin/activate

# Abhängigkeiten installieren
pip install --upgrade pip
pip install -r requirements.txt
```

> **Hinweis:** PyQt5 ist bereits als System-Paket installiert. Falls es im venv nicht gefunden wird:
> ```bash
> pip install PyQt5
> ```

---

## Schritt 7: Lokale Konfiguration anlegen

```bash
cp config.local.yaml.example config.local.yaml
nano config.local.yaml
```

Trage die echten Personennamen und Google-Kalender-Labels ein:

```yaml
persons:
  - key: "PERSON_A"
    display_name: "Vorname1"
    calendar_label: "Name des Google-Kalenders für Person 1"
  - key: "PERSON_B"
    display_name: "Vorname2"
    calendar_label: "Name des Google-Kalenders für Person 2"
  - key: "PERSON_C"
    display_name: "Vorname3"
    calendar_label: "Name des Google-Kalenders für Person 3"
  - key: "PERSON_D"
    display_name: "Vorname4"
    calendar_label: "Name des Google-Kalenders für Person 4"
```

Datei speichern (`Strg+O`, `Enter`, `Strg+X`).

---

## Schritt 8: Bildverzeichnis anlegen

```bash
mkdir -p ~/Bilder/familienkalender
```

Kopiere Fotos (JPG oder PNG) in dieses Verzeichnis, zum Beispiel per `scp` vom Mac:

```bash
# Auf dem Mac ausführen:
scp ~/Fotos/*.jpg pi@familienkalender.local:~/Bilder/familienkalender/
```

---

## Schritt 9: Google Calendar einrichten

Folge der ausführlichen Anleitung in [`docs/google-calendar-setup.md`](google-calendar-setup.md).

Kurzfassung:
1. Google Cloud Konsole: Projekt anlegen, Calendar API aktivieren, OAuth2-Zugangsdaten erstellen
2. `credentials.json` herunterladen und auf den Pi übertragen:

```bash
# Auf dem Mac:
scp ~/Downloads/client_secret_*.json pi@familienkalender.local:~/.family-calendar/credentials.json
```

3. Verzeichnis anlegen:

```bash
mkdir -p ~/.family-calendar
chmod 700 ~/.family-calendar
chmod 600 ~/.family-calendar/credentials.json
```

4. Erste Authentifizierung – einmalig mit angeschlossenem Browser-fähigem Gerät oder direkt auf dem Pi:

```bash
source ~/family-manager/venv/bin/activate
cd ~/family-manager
python3 src/main.py
```

Ein Browser-Fenster öffnet sich auf dem Pi-Desktop. Nach der Anmeldung bei Google wird `token.json` automatisch gespeichert. Die App kann danach beendet werden.

---

## Schritt 10: App manuell testen

```bash
cd ~/family-manager
source venv/bin/activate
python3 src/main.py
```

Die App sollte im Vollbildmodus starten. Prüfe:
- Foto wird angezeigt (oder dunkler Hintergrund wenn noch keine Fotos vorhanden)
- Datum und Kalenderwoche im Overlay sichtbar
- Kalenderbereich lädt (ggf. kurz warten oder 15 Minuten auf automatischen Refresh)

Beenden mit `Strg+C` im Terminal.

---

## Schritt 11: Autostart mit systemd einrichten

```bash
sudo cp ~/family-manager/systemd/family-calendar.service /etc/systemd/system/

# Service aktivieren und starten
sudo systemctl daemon-reload
sudo systemctl enable family-calendar
sudo systemctl start family-calendar
```

Status prüfen:

```bash
sudo systemctl status family-calendar
```

Logs anzeigen:

```bash
# Systemd-Log
sudo journalctl -u family-calendar -f

# App-eigenes Log
tail -f ~/.family-calendar/app.log
```

---

## Schritt 12: Bildschirmschoner und Energiesparmodus deaktivieren

Damit der Bildschirm dauerhaft an bleibt:

```bash
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

Folgende Zeilen am Ende einfügen:

```
@xset s off
@xset -dpms
@xset s noblank
```

Speichern und neu starten:

```bash
sudo reboot
```

---

## Troubleshooting

### App startet nicht / kein Bild
```bash
sudo journalctl -u family-calendar --no-pager | tail -30
```

### PyQt5 Fehler: "cannot connect to X server"
Der systemd-Service startet möglicherweise bevor der Desktop bereit ist:
```bash
sudo nano /etc/systemd/system/family-calendar.service
# After=graphical.target prüfen – sollte bereits gesetzt sein
```

### Google Calendar lädt nicht
- Prüfe ob `~/.family-calendar/credentials.json` vorhanden ist
- Prüfe ob `~/.family-calendar/token.json` vorhanden ist (nach erster Authentifizierung)
- Token erneuern: `token.json` löschen und App neu starten

### Kein WLAN nach Neustart
```bash
sudo raspi-config
# Network Options → WLAN
```

### App aktualisieren
```bash
cd ~/family-manager
git pull origin main
sudo systemctl restart family-calendar
```

---

## Nützliche Befehle

| Befehl | Beschreibung |
|--------|-------------|
| `sudo systemctl start family-calendar` | App starten |
| `sudo systemctl stop family-calendar` | App stoppen |
| `sudo systemctl restart family-calendar` | App neu starten |
| `sudo systemctl status family-calendar` | Status anzeigen |
| `tail -f ~/.family-calendar/app.log` | Live-Log anzeigen |
| `git pull && sudo systemctl restart family-calendar` | Update einspielen |
