"""
Bild-Widget mit Datums-Overlay für den oberen Bildschirmbereich.
Zeigt das aktuelle Foto skaliert an und überlagert es mit Datum,
Wochentag und Kalenderwoche.
"""

import logging
from datetime import date
from pathlib import Path
from typing import Optional

from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QPen
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy

from src.utils.date_utils import format_date_display, format_kw_overlay

logger = logging.getLogger(__name__)


class ImageWidget(QWidget):
    """
    Widget für die Fotoanzeige im oberen Bildschirmbereich.
    Skaliert das Bild proportional und zeigt ein transparentes Datums-Overlay.
    """

    def __init__(
        self,
        font_size: int = 24,
        overlay_bg_alpha: int = 160,
        parent=None,
    ) -> None:
        """
        Initialisiert das Widget.

        Args:
            font_size: Schriftgröße für das Overlay.
            overlay_bg_alpha: Transparenz des Overlay-Hintergrunds (0–255).
            parent: Eltern-Widget.
        """
        super().__init__(parent)
        self._font_size = font_size
        self._overlay_bg_alpha = overlay_bg_alpha
        self._pixmap: Optional[QPixmap] = None
        self._current_date = date.today()

        # Timer für tägliche Datumsaktualisierung (prüft jede Minute)
        self._date_timer = QTimer(self)
        self._date_timer.timeout.connect(self._check_date_update)
        self._date_timer.start(60_000)  # Jede Minute prüfen

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(100)

    def set_image(self, image_path: Optional[Path]) -> None:
        """
        Lädt und zeigt ein neues Bild an.

        Args:
            image_path: Pfad zum Bild oder None für leere Anzeige.
        """
        if image_path and image_path.exists():
            self._pixmap = QPixmap(str(image_path))
            if self._pixmap.isNull():
                logger.warning(f"Bild konnte nicht geladen werden: {image_path}")
                self._pixmap = None
        else:
            self._pixmap = None
        self.update()

    def paintEvent(self, event) -> None:
        """Zeichnet Bild und Datums-Overlay."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        widget_rect = self.rect()

        # Hintergrund
        painter.fillRect(widget_rect, QColor(30, 30, 30))

        # Bild skaliert zeichnen
        if self._pixmap and not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                widget_rect.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            # Zentriert einfügen
            x = (widget_rect.width() - scaled.width()) // 2
            y = (widget_rect.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

        # Datums-Overlay zeichnen
        self._draw_overlay(painter, widget_rect)
        painter.end()

    def _draw_overlay(self, painter: QPainter, rect) -> None:
        """
        Zeichnet das transparente Datums-Overlay oben links.
        """
        today = self._current_date
        line1 = format_date_display(today)
        line2 = format_kw_overlay(today)
        text = f"{line1}  ·  {line2}"

        # Schrift einrichten
        font = QFont("Sans Serif", self._font_size, QFont.Bold)
        painter.setFont(font)
        fm = painter.fontMetrics()

        padding = 12
        text_width = fm.horizontalAdvance(text)
        text_height = fm.height()

        bg_rect_x = padding
        bg_rect_y = padding
        bg_rect_w = text_width + padding * 2
        bg_rect_h = text_height + padding

        # Transparenter dunkler Hintergrund
        painter.setBrush(QColor(0, 0, 0, self._overlay_bg_alpha))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(
            bg_rect_x, bg_rect_y, bg_rect_w, bg_rect_h, 6, 6
        )

        # Weißer Text mit leichtem Schatten
        # Schatten
        painter.setPen(QColor(0, 0, 0, 180))
        painter.drawText(
            bg_rect_x + padding + 1,
            bg_rect_y + padding // 2 + text_height - fm.descent() + 1,
            text,
        )
        # Text
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(
            bg_rect_x + padding,
            bg_rect_y + padding // 2 + text_height - fm.descent(),
            text,
        )

    def _check_date_update(self) -> None:
        """Aktualisiert das Datum wenn ein neuer Tag begonnen hat."""
        today = date.today()
        if today != self._current_date:
            self._current_date = today
            self.update()
