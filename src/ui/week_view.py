"""
Wochenansicht des Familienplaners.
Zeigt eine Woche in 6 Spalten: Datum, vier Personen, Allgemein.
Farbliche Kennzeichnung gemäß Feiertags- und Urlaubslogik.
"""

import logging
from datetime import date, timedelta
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QHeaderView, QAbstractItemView, QSizePolicy
)

from src.models.event import Event
from src.models.person import Person
from src.services.calendar_service import CalendarService
from src.services.holiday_service import HolidayService
from src.utils.color_logic import get_row_color, get_cell_color
from src.utils.date_utils import (
    format_date_short, WEEKDAY_NAMES_SHORT_DE, get_week_dates
)

logger = logging.getLogger(__name__)

# Spaltenindizes
COL_DATE = 0
COL_PERSON_START = 1
COL_GENERAL = 5


class WeekView(QWidget):
    """
    Wochenansicht als Tabelle mit 6 Spalten.
    Zeigt alle 7 Tage einer Woche mit farblicher Kennzeichnung.
    """

    def __init__(
        self,
        persons: list[Person],
        calendar_service: CalendarService,
        holiday_service: HolidayService,
        font_size: int = 12,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._persons = sorted(persons, key=lambda p: p.column_index)
        self._calendar_service = calendar_service
        self._holiday_service = holiday_service
        self._font_size = font_size
        self._current_week_start: date = self._get_current_monday()

        self._setup_ui()
        self.refresh()

    # -------------------------------------------------------------------------
    # Öffentliche Methoden
    # -------------------------------------------------------------------------

    def navigate_previous(self) -> None:
        """Eine Woche zurück navigieren."""
        self._current_week_start -= timedelta(weeks=1)
        self.refresh()

    def navigate_next(self) -> None:
        """Eine Woche vor navigieren."""
        self._current_week_start += timedelta(weeks=1)
        self.refresh()

    def go_to_today(self) -> None:
        """Zur aktuellen Woche springen."""
        self._current_week_start = self._get_current_monday()
        self.refresh()

    def get_current_week_start(self) -> date:
        """Gibt den Montag der aktuell angezeigten Woche zurück."""
        return self._current_week_start

    def refresh(self) -> None:
        """Lädt die Ereignisse neu und aktualisiert die Anzeige."""
        self._populate_table()

    # -------------------------------------------------------------------------
    # Private Methoden
    # -------------------------------------------------------------------------

    def _get_current_monday(self) -> date:
        """Gibt den Montag der aktuellen Woche zurück."""
        today = date.today()
        return today - timedelta(days=today.weekday())

    def _setup_ui(self) -> None:
        """Baut das UI auf."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tabelle erstellen
        self._table = QTableWidget(7, 6)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionMode(QAbstractItemView.NoSelection)
        self._table.setAlternatingRowColors(False)
        self._table.verticalHeader().setVisible(False)
        self._table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Spaltenüberschriften setzen
        headers = ["Datum"] + [p.display_name for p in self._persons] + ["Allgemein"]
        self._table.setHorizontalHeaderLabels(headers)

        # Spaltenbreiten
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(COL_DATE, QHeaderView.ResizeToContents)
        for col in range(1, 6):
            header.setSectionResizeMode(col, QHeaderView.Stretch)

        # Zeilenhöhe (touch-freundlich)
        self._table.verticalHeader().setDefaultSectionSize(60)

        # Schriftgröße
        font = QFont()
        font.setPointSize(self._font_size)
        self._table.setFont(font)

        layout.addWidget(self._table)

    def _populate_table(self) -> None:
        """Befüllt die Tabelle mit den Ereignissen der aktuellen Woche."""
        week_dates = get_week_dates(self._current_week_start)

        for row, day in enumerate(week_dates):
            # Zeilenfarbe bestimmen
            row_color_hex = get_row_color(day, self._holiday_service)
            row_bg = QColor(row_color_hex)

            # Spalte 1: Datum + Wochentag + ggf. Feiertagsname
            date_text = format_date_short(day)
            holiday_name = self._holiday_service.get_holiday_name(day)
            if holiday_name:
                date_text += f"\n{holiday_name}"

            date_item = self._make_item(date_text, row_bg, bold=True)
            self._table.setItem(row, COL_DATE, date_item)

            # Spalten 2–5: Personen-Termine
            for person in self._persons:
                col = person.column_index  # 1–4 → Tabellenspalte 1–4
                events = self._calendar_service.get_events_for_person_on_date(
                    person.key, day
                )
                cell_text = self._format_events(events)

                # Zellfärbung: Urlaub/Frei überschreibt Zeilenfärbung
                cell_bg = row_bg
                for event in events:
                    vacation_color = get_cell_color(event)
                    if vacation_color:
                        cell_bg = QColor(vacation_color)
                        break

                item = self._make_item(cell_text, cell_bg)
                self._table.setItem(row, col, item)

            # Spalte 6: Allgemeine Termine
            general_events = self._calendar_service.get_events_for_person_on_date(
                "general", day
            )
            general_text = self._format_events(general_events)
            general_item = self._make_item(general_text, row_bg)
            self._table.setItem(row, COL_GENERAL, general_item)

    def _make_item(
        self,
        text: str,
        background: QColor,
        bold: bool = False,
    ) -> QTableWidgetItem:
        """Erstellt ein Tabellen-Element mit Hintergrundfarbe und Schriftstil."""
        item = QTableWidgetItem(text)
        item.setBackground(background)
        item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)

        if bold:
            font = item.font()
            font.setBold(True)
            item.setFont(font)

        return item

    def _format_events(self, events: list[Event]) -> str:
        """
        Formatiert eine Liste von Ereignissen als mehrzeiligen Text.
        Ganztägige Ereignisse werden ohne Uhrzeit angezeigt.
        """
        lines = []
        for event in events:
            if event.all_day:
                lines.append(event.title)
            else:
                time_str = event.start.strftime("%H:%M")
                lines.append(f"{time_str} {event.title}")
        return "\n".join(lines)
