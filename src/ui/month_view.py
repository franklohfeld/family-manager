"""
Monatsansicht des Familienplaners.
Zeigt einen Monat als Raster mit 7 Spalten (Mo–So).
"""

import logging
from calendar import monthrange
from datetime import date

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.services.calendar_service import CalendarService
from src.services.holiday_service import HolidayService
from src.utils.color_logic import get_row_color
from src.utils.date_utils import WEEKDAY_NAMES_SHORT_DE

logger = logging.getLogger(__name__)


class MonthView(QWidget):
    """Monatsansicht als Kalender-Raster."""

    def __init__(
        self,
        persons: list,
        calendar_service: CalendarService,
        holiday_service: HolidayService,
        font_size: int = 12,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._persons = persons
        self._calendar_service = calendar_service
        self._holiday_service = holiday_service
        self._font_size = font_size

        today = date.today()
        self._current_year = today.year
        self._current_month = today.month

        self._setup_ui()
        self.refresh()

    # -------------------------------------------------------------------------
    # Öffentliche Methoden
    # -------------------------------------------------------------------------

    def navigate_previous(self) -> None:
        """Einen Monat zurück navigieren."""
        if self._current_month == 1:
            self._current_month = 12
            self._current_year -= 1
        else:
            self._current_month -= 1
        self.refresh()

    def navigate_next(self) -> None:
        """Einen Monat vor navigieren."""
        if self._current_month == 12:
            self._current_month = 1
            self._current_year += 1
        else:
            self._current_month += 1
        self.refresh()

    def go_to_today(self) -> None:
        """Zum aktuellen Monat springen."""
        today = date.today()
        self._current_year = today.year
        self._current_month = today.month
        self.refresh()

    def get_current_month(self) -> tuple:
        """Gibt (Jahr, Monat) zurück."""
        return self._current_year, self._current_month

    def refresh(self) -> None:
        """Aktualisiert die Monatsansicht."""
        self._populate_table()

    # -------------------------------------------------------------------------
    # Private Methoden
    # -------------------------------------------------------------------------

    def _setup_ui(self) -> None:
        """Baut das UI auf."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Maximal 6 Zeilen (Wochen) pro Monat möglich
        self._table = QTableWidget(6, 7)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionMode(QAbstractItemView.NoSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._table.setHorizontalHeaderLabels(WEEKDAY_NAMES_SHORT_DE)

        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self._table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        font = QFont()
        font.setPointSize(self._font_size)
        self._table.setFont(font)

        layout.addWidget(self._table)

    def _populate_table(self) -> None:
        """Befüllt das Monatsraster mit Tagen und Ereignissen."""
        year = self._current_year
        month = self._current_month

        # Tabelle leeren
        self._table.clearContents()

        first_day = date(year, month, 1)
        _, days_in_month = monthrange(year, month)

        # Wochentag des ersten Tages (0=Mo, 6=So)
        start_col = first_day.weekday()

        for day_num in range(1, days_in_month + 1):
            current_date = date(year, month, day_num)
            cell_index = start_col + day_num - 1
            row = cell_index // 7
            col = cell_index % 7

            if row >= 6:
                break

            # Farbe der Zelle
            row_color = get_row_color(current_date, self._holiday_service)
            holiday_name = self._holiday_service.get_holiday_name(current_date)

            # Tagesnummer + optionaler Feiertagsname
            cell_text = str(day_num)
            if holiday_name:
                cell_text += f"\n{holiday_name}"

            # Ereignisse kompakt anzeigen (max. 3 pro Tag)
            events = self._calendar_service.get_events_for_date(current_date)
            event_lines = []
            for event in events[:3]:
                person_label = ""
                for p in self._persons:
                    if p.key == event.person:
                        # Ersten 3 Buchstaben des Namens als Kürzel
                        person_label = f"[{p.display_name[:3]}] "
                        break
                event_lines.append(f"{person_label}{event.title}")

            if event_lines:
                cell_text += "\n" + "\n".join(event_lines)

            item = QTableWidgetItem(cell_text)
            item.setBackground(QColor(row_color))
            item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
            self._table.setItem(row, col, item)
