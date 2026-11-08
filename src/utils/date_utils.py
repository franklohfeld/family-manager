"""
Datums-Hilfsfunktionen für den Familienkalender.
"""

from datetime import date, datetime, timedelta
from typing import List


# Deutsche Wochentagsnamen
WEEKDAY_NAMES_DE = [
    "Montag", "Dienstag", "Mittwoch", "Donnerstag",
    "Freitag", "Samstag", "Sonntag"
]

# Kurze Wochentagsnamen
WEEKDAY_NAMES_SHORT_DE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

# Deutsche Monatsnamen
MONTH_NAMES_DE = [
    "", "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember"
]

MONTH_NAMES_SHORT_DE = [
    "", "Jan", "Feb", "Mär", "Apr", "Mai", "Jun",
    "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"
]


def get_week_start(d: date) -> date:
    """
    Gibt den Montag der Woche zurück, in der das Datum liegt.
    Beispiel: Mittwoch 06.11. → Montag 04.11.
    """
    return d - timedelta(days=d.weekday())


def get_week_number(d: date) -> int:
    """Gibt die ISO-Kalenderwoche des Datums zurück."""
    return d.isocalendar()[1]


def get_week_year(d: date) -> int:
    """Gibt das ISO-Jahr der Kalenderwoche zurück (kann vom Kalenderjahr abweichen)."""
    return d.isocalendar()[0]


def get_week_dates(week_start: date) -> List[date]:
    """
    Gibt eine Liste mit den 7 Tagen einer Woche zurück (Montag bis Sonntag).
    """
    return [week_start + timedelta(days=i) for i in range(7)]


def is_sunday_midnight(dt: datetime) -> bool:
    """
    Prüft, ob der gegebene Zeitpunkt Sonntag um Mitternacht (00:00:00) ist.
    Wird für den wöchentlichen Bildwechsel verwendet.
    """
    return dt.weekday() == 6 and dt.hour == 0 and dt.minute == 0 and dt.second == 0


def format_date_display(d: date) -> str:
    """
    Formatiert ein Datum für die Overlay-Anzeige.
    Beispiel: "Montag, 04. November 2026"
    """
    weekday = WEEKDAY_NAMES_DE[d.weekday()]
    month = MONTH_NAMES_DE[d.month]
    return f"{weekday}, {d.day:02d}. {month} {d.year}"


def format_date_short(d: date) -> str:
    """
    Kurze Datumsformatierung für Tabellenzellen.
    Beispiel: "Mo, 04.11."
    """
    weekday = WEEKDAY_NAMES_SHORT_DE[d.weekday()]
    return f"{weekday}, {d.day:02d}.{d.month:02d}."


def format_week_header(week_start: date) -> str:
    """
    Formatiert die Wochenüberschrift für die Navigationsleiste.
    Beispiel: "KW 45 · 04.–10. Nov 2026"
    """
    week_end = week_start + timedelta(days=6)
    kw = get_week_number(week_start)

    # Unterscheide ob Start und Ende im selben Monat liegen
    if week_start.month == week_end.month:
        date_range = (
            f"{week_start.day:02d}.–{week_end.day:02d}. "
            f"{MONTH_NAMES_SHORT_DE[week_start.month]} {week_start.year}"
        )
    else:
        date_range = (
            f"{week_start.day:02d}. {MONTH_NAMES_SHORT_DE[week_start.month]} – "
            f"{week_end.day:02d}. {MONTH_NAMES_SHORT_DE[week_end.month]} {week_end.year}"
        )

    return f"KW {kw} · {date_range}"


def format_month_header(year: int, month: int) -> str:
    """
    Formatiert die Monatsüberschrift.
    Beispiel: "November 2026"
    """
    return f"{MONTH_NAMES_DE[month]} {year}"


def format_kw_overlay(d: date) -> str:
    """
    Formatiert die Kalenderwochen-Anzeige für das Bild-Overlay.
    Beispiel: "KW 45"
    """
    return f"KW {get_week_number(d)}"


def get_next_sunday_midnight(from_dt: datetime) -> datetime:
    """
    Gibt den nächsten Sonntag um 00:00 Uhr zurück, der nach 'from_dt' liegt.
    Wird für die Planung des Bildwechsels verwendet.
    """
    days_until_sunday = (6 - from_dt.weekday()) % 7
    if days_until_sunday == 0:
        # Heute ist Sonntag – nächste Woche
        days_until_sunday = 7
    next_sunday = from_dt.date() + timedelta(days=days_until_sunday)
    return datetime(next_sunday.year, next_sunday.month, next_sunday.day, 0, 0, 0)
