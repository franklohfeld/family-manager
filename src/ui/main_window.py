"""
Hauptfenster der Familienkalender-Anwendung.
Teilt den Bildschirm in oberes Drittel (Fotoanzeige) und
unteres Zweidrittel (Familienplaner).
"""

import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QSplitter, QVBoxLayout, QWidget

from src.services.calendar_service import CalendarService
from src.services.holiday_service import HolidayService
from src.services.image_service import ImageService
from src.ui.calendar_widget import CalendarWidget
from src.ui.image_widget import ImageWidget

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Hauptfenster der Anwendung.
    Layout: ImageWidget (oben) + CalendarWidget (unten).
    """

    def __init__(
        self,
        config: dict,
        image_service: ImageService,
        calendar_service: CalendarService,
        holiday_service: HolidayService,
        persons: list,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._config = config
        self._image_service = image_service
        self._calendar_service = calendar_service
        self._holiday_service = holiday_service
        self._persons = persons

        self._setup_window()
        self._setup_ui()
        self._load_initial_image()

    # -------------------------------------------------------------------------
    # Öffentliche Methoden
    # -------------------------------------------------------------------------

    def update_image(self) -> None:
        """Lädt das nächste Bild und zeigt es an."""
        image_path = self._image_service.advance_image()
        self._image_widget.set_image(image_path)
        logger.info(f"Bild gewechselt: {image_path}")

    def refresh_calendar(self) -> None:
        """Aktualisiert den Kalender nach einem Reload."""
        self._calendar_widget.refresh()

    # -------------------------------------------------------------------------
    # Private Methoden
    # -------------------------------------------------------------------------

    def _setup_window(self) -> None:
        """Konfiguriert das Hauptfenster."""
        self.setWindowTitle("Familienkalender")

        display_cfg = self._config.get("display", {})
        width = display_cfg.get("width", 1920)
        height = display_cfg.get("height", 1080)
        fullscreen = display_cfg.get("fullscreen", True)

        if fullscreen:
            self.showFullScreen()
        else:
            self.resize(width, height)

        # Kein Fensterrahmen im Vollbildmodus
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

    def _setup_ui(self) -> None:
        """Baut das UI-Layout auf."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Vertikaler Splitter: oben Foto, unten Kalender
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(2)

        # Bild-Widget
        img_cfg = self._config.get("ui", {})
        font_size_overlay = img_cfg.get("font_size_date_overlay", 24)
        self._image_widget = ImageWidget(font_size=font_size_overlay)

        # Kalender-Widget
        self._calendar_widget = CalendarWidget(
            persons=self._persons,
            calendar_service=self._calendar_service,
            holiday_service=self._holiday_service,
            config=self._config,
        )

        splitter.addWidget(self._image_widget)
        splitter.addWidget(self._calendar_widget)

        # Verhältnis: oberes Drittel / untere zwei Drittel
        ratio = self._config.get("display", {}).get("image_area_ratio", 0.33)
        total = 1000
        image_part = int(total * ratio)
        calendar_part = total - image_part
        splitter.setSizes([image_part, calendar_part])

        layout.addWidget(splitter)

    def _load_initial_image(self) -> None:
        """Lädt das aktuelle Bild beim Start."""
        image_path = self._image_service.get_current_image()
        self._image_widget.set_image(image_path)
