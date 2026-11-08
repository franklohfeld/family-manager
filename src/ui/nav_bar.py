"""
Navigationsleiste des Familienplaners.
Enthält Vor/Zurück-Buttons, die Anzeige des aktuellen Zeitraums
und die Umschaltung zwischen den Ansichten.
"""

import logging

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)

logger = logging.getLogger(__name__)

# Ansichtskonstanten
VIEW_WEEK = "week"
VIEW_MONTH = "month"
VIEW_LIST = "list"


class NavBar(QWidget):
    """
    Navigationsleiste mit Zeitraum-Anzeige und Ansichtsumschaltung.
    Sendet Signale an das CalendarWidget.
    """

    # Signale
    navigate_previous = pyqtSignal()
    navigate_next = pyqtSignal()
    view_changed = pyqtSignal(str)  # Übergabe: VIEW_WEEK, VIEW_MONTH oder VIEW_LIST

    def __init__(self, font_size: int = 14, parent=None) -> None:
        super().__init__(parent)
        self._font_size = font_size
        self._current_view = VIEW_WEEK
        self._setup_ui()

    # -------------------------------------------------------------------------
    # Öffentliche Methoden
    # -------------------------------------------------------------------------

    def set_period_label(self, text: str) -> None:
        """Setzt den angezeigten Zeitraumtext (z.B. 'KW 45 · 04.–10. Nov 2026')."""
        self._period_label.setText(text)

    def get_current_view(self) -> str:
        """Gibt die aktuell aktive Ansicht zurück."""
        return self._current_view

    # -------------------------------------------------------------------------
    # Private Methoden
    # -------------------------------------------------------------------------

    def _setup_ui(self) -> None:
        """Baut die Navigationsleiste auf."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        btn_font = QFont()
        btn_font.setPointSize(self._font_size)

        # Zurück-Button
        self._btn_prev = QPushButton("◀")
        self._btn_prev.setFont(btn_font)
        self._btn_prev.setFixedWidth(48)
        self._btn_prev.setToolTip("Vorherige Woche / Vorheriger Monat")
        self._btn_prev.clicked.connect(self.navigate_previous)

        # Zeitraum-Label (mittig, dehnbar)
        self._period_label = QLabel("")
        period_font = QFont()
        period_font.setPointSize(self._font_size)
        period_font.setBold(True)
        self._period_label.setFont(period_font)
        self._period_label.setAlignment(Qt.AlignCenter)
        self._period_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Vor-Button
        self._btn_next = QPushButton("▶")
        self._btn_next.setFont(btn_font)
        self._btn_next.setFixedWidth(48)
        self._btn_next.setToolTip("Nächste Woche / Nächster Monat")
        self._btn_next.clicked.connect(self.navigate_next)

        # Ansicht-Toggle-Buttons
        self._btn_week = self._make_view_button("W", VIEW_WEEK, "Wochenansicht")
        self._btn_month = self._make_view_button("M", VIEW_MONTH, "Monatsansicht")
        self._btn_list = self._make_view_button("L", VIEW_LIST, "Listenansicht")

        # Aktive Ansicht hervorheben
        self._update_view_buttons()

        # Layout zusammenbauen
        layout.addWidget(self._btn_prev)
        layout.addWidget(self._period_label)
        layout.addWidget(self._btn_next)
        layout.addSpacing(16)
        layout.addWidget(self._btn_week)
        layout.addWidget(self._btn_month)
        layout.addWidget(self._btn_list)

    def _make_view_button(self, label: str, view: str, tooltip: str) -> QPushButton:
        """Erstellt einen Ansichts-Toggle-Button."""
        btn = QPushButton(label)
        font = QFont()
        font.setPointSize(self._font_size)
        btn.setFont(font)
        btn.setFixedWidth(40)
        btn.setToolTip(tooltip)
        btn.clicked.connect(lambda: self._on_view_button_clicked(view))
        return btn

    def _on_view_button_clicked(self, view: str) -> None:
        """Verarbeitet einen Klick auf einen Ansichts-Button."""
        self._current_view = view
        self._update_view_buttons()
        self.view_changed.emit(view)

    def _update_view_buttons(self) -> None:
        """Hebt den aktiven Ansichts-Button optisch hervor."""
        buttons = {
            VIEW_WEEK: self._btn_week,
            VIEW_MONTH: self._btn_month,
            VIEW_LIST: self._btn_list,
        }
        for view, btn in buttons.items():
            if view == self._current_view:
                btn.setStyleSheet("QPushButton { font-weight: bold; background-color: #4A90D9; color: white; }")
            else:
                btn.setStyleSheet("")
