"""
Listenansicht des Familienplaners.
Zeigt alle Ereignisse chronologisch sortiert mit Gruppenheadern pro Tag.
"""

import logging
from datetime import date, timedelta

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QSizePolicy,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.models.event import Event
from src.models.person import Person
from src.services.calendar_service import CalendarService
from src.services.holiday_service import HolidayService
from src.utils.color_logic import get_row_color, get_cell_color
from src.utils.date_utils import format_date_short, get_week_start

logger = logging.getLogger(__name__)

# Anzahl der anzuzeigenden Tage ab heute
DAYS_TO_SHOW = 60


class ListView(QWidget):
    """
    Listenansicht: chronologisch sortierte Ereignisse mit Tages-Gruppen.
    """

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

        self._setup_ui()
        self.refresh()

    # -------------------------------------------------------------------------
    # Öffentliche Methoden
    # -------------------------------------------------------------------------

    def navigate_previous(self) -> None:
        """In der Listenansicht nicht anwendbar – kein Effekt."""
        pass

    def navigate_next(self) -> None:
        """In der Listenansicht nicht anwendbar – kein Effekt."""
        pass

    def go_to_today(self) -> None:
        """Springt zum heutigen Tag in der Liste."""
        self.refresh()
        # Ersten Eintrag auswählen (= heute)
        if self._tree.topLevelItemCount() > 0:
            self._tree.scrollToItem(self._tree.topLevelItem(0))

    def refresh(self) -> None:
        """Lädt alle Ereignisse neu und baut die Liste auf."""
        self._populate_list()

    # -------------------------------------------------------------------------
    # Private Methoden
    # -------------------------------------------------------------------------

    def _setup_ui(self) -> None:
        """Baut das UI auf."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._tree = QTreeWidget()
        self._tree.setColumnCount(3)
        self._tree.setHeaderLabels(["Zeit", "Titel", "Person"])
        self._tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._tree.setSelectionMode(QAbstractItemView.NoSelection)
        self._tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._tree.setAlternatingRowColors(True)

        # Spaltenbreiten
        self._tree.setColumnWidth(0, 80)
        self._tree.setColumnWidth(1, 300)
        self._tree.setColumnWidth(2, 100)

        font = QFont()
        font.setPointSize(self._font_size)
        self._tree.setFont(font)

        layout.addWidget(self._tree)

    def _populate_list(self) -> None:
        """Befüllt die Liste mit Ereignissen der nächsten DAYS_TO_SHOW Tage."""
        self._tree.clear()

        today = date.today()
        for offset in range(DAYS_TO_SHOW):
            current_date = today + timedelta(days=offset)
            events = self._calendar_service.get_events_for_date(current_date)

            if not events:
                continue

            # Tages-Gruppenheader
            row_color_hex = get_row_color(current_date, self._holiday_service)
            holiday_name = self._holiday_service.get_holiday_name(current_date)

            header_text = format_date_short(current_date)
            if holiday_name:
                header_text += f"  –  {holiday_name}"

            day_item = QTreeWidgetItem([header_text, "", ""])
            day_item.setBackground(0, QColor(row_color_hex))
            day_item.setBackground(1, QColor(row_color_hex))
            day_item.setBackground(2, QColor(row_color_hex))

            header_font = QFont()
            header_font.setPointSize(self._font_size)
            header_font.setBold(True)
            day_item.setFont(0, header_font)

            self._tree.addTopLevelItem(day_item)

            # Ereignisse des Tages als Kindelemente
            for event in sorted(events, key=lambda e: e.start):
                time_str = "" if event.all_day else event.start.strftime("%H:%M")
                person_name = self._get_person_name(event.person)

                event_item = QTreeWidgetItem([time_str, event.title, person_name])

                # Zellfärbung für Urlaub/Frei
                cell_color = get_cell_color(event)
                if cell_color:
                    for col in range(3):
                        event_item.setBackground(col, QColor(cell_color))

                day_item.addChild(event_item)

            day_item.setExpanded(True)

    def _get_person_name(self, person_key: str) -> str:
        """Gibt den Anzeigenamen einer Person zurück."""
        if person_key == "general":
            return "Allgemein"
        for person in self._persons:
            if person.key == person_key:
                return person.display_name
        return person_key
