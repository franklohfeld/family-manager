"""
Einstiegspunkt der Familienkalender-Anwendung.
Initialisiert Qt, lädt die Konfiguration und startet die App.
"""

import logging
import sys
from pathlib import Path

# Projekt-Root zum Python-Pfad hinzufügen (für Imports aus src/)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt5.QtWidgets import QApplication  # noqa: E402

from src.app import FamilyCalendarApp  # noqa: E402
from src.utils.config import get_config  # noqa: E402

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            Path.home() / ".family-calendar" / "app.log",
            mode="a",
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Startet die Anwendung und gibt den Exit-Code zurück."""
    logger.info("Familienkalender wird gestartet...")

    # Log-Verzeichnis anlegen
    log_dir = Path.home() / ".family-calendar"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Qt-Anwendung erstellen
    app = QApplication(sys.argv)
    app.setApplicationName("Familienkalender")
    app.setOrganizationName("Familie")

    # Konfiguration laden
    try:
        config = get_config()
    except FileNotFoundError as e:
        logger.error(f"Konfigurationsfehler: {e}")
        print(f"Fehler: {e}", file=sys.stderr)
        return 1

    # Anwendung starten
    try:
        family_app = FamilyCalendarApp(config=config)
        family_app.show()
        # Kalender im Hintergrund laden (nach dem ersten Rendern)
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(500, family_app.initial_calendar_refresh)

        logger.info("Anwendung gestartet.")
        return app.exec_()

    except Exception as e:
        logger.exception(f"Unerwarteter Fehler beim Start: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
