"""
Feiertags-Service für den Familienkalender.
Verwaltet hessische Feiertage und unterscheidet zwischen gesetzlichen
freien Tagen und regionalen Gedenktagen ohne gesetzliche Freiheit.
"""

from datetime import date
from typing import Optional

import holidays


# Feiertage in Hessen, die gesetzlich arbeitsfrei sind
# (alle anderen in der holidays-Bibliothek aufgeführten Tage für HE sind ebenfalls frei,
# aber wir trennen hier explizit, falls in Zukunft Anpassungen nötig sind)
_FREE_HOLIDAYS_HE = {
    "Neujahr",
    "Karfreitag",
    "Ostermontag",
    "Tag der Arbeit",
    "Christi Himmelfahrt",
    "Pfingstmontag",
    "Fronleichnam",
    "Tag der Deutschen Einheit",
    "Reformationstag",
    "Allerheiligen",
    "1. Weihnachtstag",
    "2. Weihnachtstag",
}


class HolidayService:
    """
    Service zur Ermittlung hessischer Feiertage.
    Unterscheidet zwischen gesetzlich freien Feiertagen und sonstigen regionalen Tagen.
    """

    def __init__(self, state: str = "HE") -> None:
        """
        Initialisiert den Service für ein bestimmtes Bundesland.
        Standard: Hessen (HE).
        """
        self._state = state
        # Cache: Jahr → holidays-Objekt
        self._cache: dict[int, holidays.HolidayBase] = {}

    def _get_holidays(self, year: int) -> holidays.HolidayBase:
        """Gibt das holidays-Objekt für ein Jahr zurück (mit Cache)."""
        if year not in self._cache:
            self._cache[year] = holidays.Germany(state=self._state, years=year)
        return self._cache[year]

    def get_holiday_name(self, d: date) -> Optional[str]:
        """
        Gibt den Namen des Feiertags zurück, oder None wenn kein Feiertag.
        Gilt für alle Feiertage – unabhängig davon ob arbeitsfrei oder nicht.
        """
        hols = self._get_holidays(d.year)
        return hols.get(d)

    def is_public_holiday(self, d: date) -> bool:
        """
        Prüft, ob der Tag ein gesetzlich freier Feiertag in Hessen ist.
        Diese Tage werden wie Sonntage in kräftigem Rot dargestellt.
        """
        name = self.get_holiday_name(d)
        if name is None:
            return False
        # Prüfe ob der Feiertagsname einem bekannten freien Feiertag entspricht
        return any(free_name in name for free_name in _FREE_HOLIDAYS_HE)

    def is_regional_holiday(self, d: date) -> bool:
        """
        Prüft, ob der Tag ein regionaler Gedenktag ist, der NICHT arbeitsfrei ist.
        Diese Tage werden nicht farblich hervorgehoben, zeigen aber den Namen in Spalte 1.
        """
        name = self.get_holiday_name(d)
        if name is None:
            return False
        # Ist ein Feiertag, aber kein freier → regionaler Tag
        return not self.is_public_holiday(d)

    def is_any_holiday(self, d: date) -> bool:
        """Prüft, ob der Tag irgendeiner Art von Feiertag ist."""
        return self.get_holiday_name(d) is not None
