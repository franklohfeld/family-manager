"""
Farbzuweisungslogik für den Familienkalender.
Bestimmt die Hintergrundfarbe von Tabellenzeilen und -zellen
basierend auf Wochentag, Feiertag und Termintyp.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from src.models.event import Event
from src.services.holiday_service import HolidayService


# Farbkonstanten (Hex-Werte)
COLOR_ROW_NORMAL = "#FFFFFF"       # Normaler Werktag – weiß
COLOR_ROW_LIGHT_RED = "#FFCCCC"    # Samstag – hell-rot
COLOR_ROW_DARK_RED = "#FF6666"     # Sonntag / gesetzlicher Feiertag – kräftig-rot
COLOR_CELL_VACATION = "#FF9999"    # Urlaub / Frei bei einer Person – Zellfarbe


def get_row_color(d: date, holiday_service: HolidayService) -> str:
    """
    Gibt die Hintergrundfarbe für eine komplette Tabellenzeile zurück.

    Regeln (in Priorität):
    1. Sonntag → kräftig-rot
    2. Gesetzlicher freier Feiertag → kräftig-rot
    3. Samstag → hell-rot
    4. Regionaler nicht-freier Feiertag → keine Färbung (weiß)
    5. Normaler Werktag → weiß
    """
    # Sonntag (weekday() == 6)
    if d.weekday() == 6:
        return COLOR_ROW_DARK_RED

    # Gesetzlich freier Feiertag
    if holiday_service.is_public_holiday(d):
        return COLOR_ROW_DARK_RED

    # Samstag (weekday() == 5)
    if d.weekday() == 5:
        return COLOR_ROW_LIGHT_RED

    # Normaler Tag (inkl. regionaler Feiertage ohne Freiheit)
    return COLOR_ROW_NORMAL


def get_cell_color(event: Event) -> Optional[str]:
    """
    Gibt die Hintergrundfarbe für eine einzelne Zelle zurück.
    Wird verwendet, wenn ein Termin "Urlaub" oder "Frei" im Namen enthält.
    Gibt None zurück, wenn keine besondere Zellfärbung notwendig ist.
    """
    if event.is_vacation:
        return COLOR_CELL_VACATION
    return None


def should_highlight_row(d: date, holiday_service: HolidayService) -> bool:
    """
    Gibt True zurück, wenn die Zeile farblich hervorgehoben werden soll
    (Samstag, Sonntag oder gesetzlicher Feiertag).
    """
    return get_row_color(d, holiday_service) != COLOR_ROW_NORMAL
