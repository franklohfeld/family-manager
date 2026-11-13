"""
Haupt-Koordinationsklasse der Familienkalender-Anwendung.
Initialisiert alle Services, verbindet sie mit der UI
und verwaltet die automatischen Timer.
"""

import logging
from datetime import datetime

from PyQt5.QtCore import QTimer

from src.models.person import Person
from src.services.calendar_service import CalendarService
from src.services.holiday_service import HolidayService
from src.services.image_service import ImageService
from src.ui.main_window import MainWindow
from src.utils.config import get_all_persons

logger = logging.getLogger(__name__)


class FamilyCalendarApp:
    """
    Zentrale Anwendungsklasse.
    Erstellt und verbindet alle Komponenten.
    """

    def __init__(self, config: dict) -> None:
        self._config = config

        # Services initialisieren
        self._holiday_service = self._create_holiday_service()
        self._image_service = self._create_image_service()
        self._persons = self._create_persons()
        self._calendar_service = self._create_calendar_service()

        # Hauptfenster erstellen
        self._main_window = MainWindow(
            config=config,
            image_service=self._image_service,
            calendar_service=self._calendar_service,
            holiday_service=self._holiday_service,
            persons=self._persons,
        )

        # Timer einrichten
        self._setup_timers()

    # -------------------------------------------------------------------------
    # Öffentliche Methoden
    # -------------------------------------------------------------------------

    def show(self) -> None:
        """Zeigt das Hauptfenster an."""
        self._main_window.show()

    def initial_calendar_refresh(self) -> None:
        """Führt den ersten Kalender-Refresh beim Start durch."""
        logger.info("Initialer Kalender-Refresh...")
        success = self._calendar_service.refresh()
        if success:
            self._main_window.refresh_calendar()
            logger.info("Kalender erfolgreich geladen.")
        else:
            logger.warning("Kalender konnte nicht geladen werden – Cache wird verwendet.")

    # -------------------------------------------------------------------------
    # Private Methoden
    # -------------------------------------------------------------------------

    def _create_holiday_service(self) -> HolidayService:
        """Erstellt den Feiertags-Service."""
        state = self._config.get("holidays", {}).get("state", "HE")
        return HolidayService(state=state)

    def _create_image_service(self) -> ImageService:
        """Erstellt den Bild-Service."""
        img_cfg = self._config.get("images", {})
        return ImageService(
            image_dir=img_cfg.get("directory", "~/Bilder/familienkalender"),
            state_file=img_cfg.get("state_file", "~/.family-calendar/image_state.json"),
            fallback_image=img_cfg.get("fallback_image", "assets/default_image.png"),
            supported_formats=img_cfg.get("supported_formats", [".jpg", ".jpeg", ".png"]),
        )

    def _create_persons(self) -> list:
        """Erstellt die Personen-Objekte aus der Konfiguration."""
        persons_cfg = get_all_persons(self._config)
        return [Person.from_config(p) for p in persons_cfg]

    def _create_calendar_service(self) -> CalendarService:
        """Erstellt den Kalender-Service."""
        cal_cfg = self._config.get("calendar", {})
        return CalendarService(
            credentials_file=cal_cfg.get("credentials_file", "~/.family-calendar/credentials.json"),
            token_file=cal_cfg.get("token_file", "~/.family-calendar/token.json"),
            cache_file=cal_cfg.get("cache_file", "~/.family-calendar/calendar_cache.json"),
            persons=self._persons,
            lookahead_weeks=cal_cfg.get("lookahead_weeks", 4),
            lookbehind_weeks=cal_cfg.get("lookbehind_weeks", 1),
        )

    def _setup_timers(self) -> None:
        """Richtet die automatischen Timer für Kalender-Refresh und Bildwechsel ein."""
        # Kalender-Refresh-Timer
        refresh_minutes = self._config.get("calendar", {}).get("refresh_interval_minutes", 15)
        self._refresh_timer = QTimer()
        self._refresh_timer.timeout.connect(self._on_calendar_refresh)
        self._refresh_timer.start(refresh_minutes * 60 * 1000)
        logger.info(f"Kalender-Refresh alle {refresh_minutes} Minuten.")

        # Bildwechsel-Timer: prüft jede Minute ob Sonntag Mitternacht
        self._image_timer = QTimer()
        self._image_timer.timeout.connect(self._on_image_rotation_check)
        self._image_timer.start(60 * 1000)
        logger.info("Bildwechsel-Timer gestartet (Prüfung jede Minute).")

    def _on_calendar_refresh(self) -> None:
        """Wird vom Timer aufgerufen – aktualisiert den Kalender."""
        logger.info("Automatischer Kalender-Refresh...")
        success = self._calendar_service.refresh()
        if success:
            self._main_window.refresh_calendar()

    def _on_image_rotation_check(self) -> None:
        """
        Wird jede Minute aufgerufen.
        Prüft ob Sonntag Mitternacht ist und wechselt ggf. das Bild.
        """
        now = datetime.now()
        # Sonntag (weekday=6), Stunde 0, Minute 0
        if now.weekday() == 6 and now.hour == 0 and now.minute == 0:
            logger.info("Sonntag Mitternacht – Bildwechsel wird durchgeführt.")
            self._main_window.update_image()
