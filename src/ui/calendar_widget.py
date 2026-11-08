"""
Kalender-Container-Widget.
Verwaltet die Umschaltung zwischen Wochen-, Monats- und Listenansicht
und koordiniert die Navigation.
"""

import logging

from PyQt5.QtWidgets import QStackedWidget, QVBoxLayout, QWidget

from src.models.person import Person
from src.services.calendar_service import CalendarService
from src.services.holiday_service import HolidayService
from src.ui.list_view import ListView
from src.ui.month_view import MonthView
from src.ui.nav_bar import NavBar, VIEW_WEEK, VIEW_MONTH, VIEW_LIST
from src.ui.week_view import WeekView
from src.utils.date_utils import format_week_header, format_month_header

logger = logging.getLogger(__name__)


class CalendarWidget(QWidget):
    """
    Container für alle Kalenderansichten.
    Enthält die NavBar und einen QStackedWidget mit Wochen-, Monats- und Listenansicht.
    """

    def __init__(
        self,
        persons: list,
        calendar_service: CalendarService,
        holiday_service: HolidayService,
        config: dict,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._persons = persons
        self._calendar_service = calendar_service
        self._holiday_service = holiday_service
        self._config = config

        font_size_header = config.get("ui", {}).get("font_size_table_header", 14)
        font_size_cell = config.get("ui", {}).get("font_size_table_cell", 12)

        self._setup_ui(font_size_header, font_size_cell)
        self._connect_signals()
        self._update_period_label()

    # -------------------------------------------------------------------------
    # Öffentliche Methoden
    # -------------------------------------------------------------------------

    def refresh(self) -> None:
        """Aktualisiert die aktive Ansicht nach einem Kalender-Reload."""
        self._week_view.refresh()
        self._month_view.refresh()
        self._list_view.refresh()
        self._update_period_label()

    # -------------------------------------------------------------------------
    # Private Methoden
    # -------------------------------------------------------------------------

    def _setup_ui(self, font_size_header: int, font_size_cell: int) -> None:
        """Baut das Layout auf."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Navigationsleiste
        self._nav_bar = NavBar(font_size=font_size_header)
        layout.addWidget(self._nav_bar)

        # Ansichten in einem Stack
        self._stack = QStackedWidget()

        self._week_view = WeekView(
            persons=self._persons,
            calendar_service=self._calendar_service,
            holiday_service=self._holiday_service,
            font_size=font_size_cell,
        )
        self._month_view = MonthView(
            persons=self._persons,
            calendar_service=self._calendar_service,
            holiday_service=self._holiday_service,
            font_size=font_size_cell,
        )
        self._list_view = ListView(
            persons=self._persons,
            calendar_service=self._calendar_service,
            holiday_service=self._holiday_service,
            font_size=font_size_cell,
        )

        self._stack.addWidget(self._week_view)   # Index 0
        self._stack.addWidget(self._month_view)  # Index 1
        self._stack.addWidget(self._list_view)   # Index 2

        layout.addWidget(self._stack)

    def _connect_signals(self) -> None:
        """Verbindet NavBar-Signale mit den Ansichten."""
        self._nav_bar.navigate_previous.connect(self._on_navigate_previous)
        self._nav_bar.navigate_next.connect(self._on_navigate_next)
        self._nav_bar.view_changed.connect(self._on_view_changed)

    def _on_navigate_previous(self) -> None:
        """Leitet Navigation zurück an die aktive Ansicht weiter."""
        view = self._nav_bar.get_current_view()
        if view == VIEW_WEEK:
            self._week_view.navigate_previous()
        elif view == VIEW_MONTH:
            self._month_view.navigate_previous()
        else:
            self._list_view.navigate_previous()
        self._update_period_label()

    def _on_navigate_next(self) -> None:
        """Leitet Navigation vor an die aktive Ansicht weiter."""
        view = self._nav_bar.get_current_view()
        if view == VIEW_WEEK:
            self._week_view.navigate_next()
        elif view == VIEW_MONTH:
            self._month_view.navigate_next()
        else:
            self._list_view.navigate_next()
        self._update_period_label()

    def _on_view_changed(self, view: str) -> None:
        """Schaltet auf die gewählte Ansicht um."""
        if view == VIEW_WEEK:
            self._stack.setCurrentIndex(0)
        elif view == VIEW_MONTH:
            self._stack.setCurrentIndex(1)
        else:
            self._stack.setCurrentIndex(2)
        self._update_period_label()

    def _update_period_label(self) -> None:
        """Aktualisiert die Zeitraum-Anzeige in der NavBar."""
        view = self._nav_bar.get_current_view()
        if view == VIEW_WEEK:
            week_start = self._week_view.get_current_week_start()
            label = format_week_header(week_start)
        elif view == VIEW_MONTH:
            year, month = self._month_view.get_current_month()
            label = format_month_header(year, month)
        else:
            label = "Nächste 60 Tage"
        self._nav_bar.set_period_label(label)
