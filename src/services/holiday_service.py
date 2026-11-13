"""
Feiertags-Service für den Familienkalender.
Verwaltet hessische Feiertage und unterscheidet zwischen gesetzlichen
freien Tagen und regionalen Gedenktagen ohne gesetzliche Freiheit.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

import holidays


# Englische Feiertagsnamen der holidays-Bibliothek, die in Hessen gesetzlich frei sind.
# Quelle: holidays.Germany(subdiv='HE')
_FREE_HOLIDAY_NAMES_EN = {
    "New Year's Day",
    "Good Friday",
    "Easter Monday",
    "Labor Day",
    "Ascension Day",
    "Whit Monday",
    "Corpus Christi",
    "German Unity Day",
    "Christmas Day",
    "Second Day of Christmas",
    # Reformationstag ist in Hessen gesetzlich frei
    "Reformation Day",
    # Allerheiligen ist in Hessen gesetzlich frei
    "All Saints' Day",
}

# Übersetzungstabelle: englischer Name → deutscher Anzeigename
_HOLIDAY_NAMES_DE = {
    "New Year's Day": "Neujahr",
    "Good Friday": "Karfreitag",
    "Easter Sunday": "Ostersonntag",
    "Easter Monday": "Ostermontag",
    "Labor Day": "Tag der Arbeit",
    "Ascension Day": "Christi Himmelfahrt",
    "Whit Sunday": "Pfingstsonntag",
    "Whit Monday": "Pfingstmontag",
    "Corpus Christi": "Fronleichnam",
    "German Unity Day": "Tag der Deutschen Einheit",
    "Reformation Day": "Reformationstag",
    "All Saints' Day": "Allerheiligen",
    "Christmas Day": "1. Weihnachtstag",
    "Second Day of Christmas": "2. Weihnachtstag",
}


class HolidayService:
    """
    Service zur Ermittlung hessischer Feiertage.
    Unterscheidet zwischen gesetzlich freien Feiertagen und sonstigen regionalen Tagen.
    """

    def __init__(self, state: str = "HE") -> None:
        """
        Initialisiert den Service für ein bestimmtes Bundesland.
        Standard: Hessen (HE). Der Parameter heißt weiterhin 'state' für
        Abwärtskompatibilität, wird intern als 'subdiv' übergeben.
        """
        self._subdiv = state
        # Cache: Jahr → holidays-Objekt
        self._cache: dict = {}

    def _get_holidays(self, year: int) -> holidays.HolidayBase:
        """Gibt das holidays-Objekt für ein Jahr zurück (mit Cache)."""
        if year not in self._cache:
            self._cache[year] = holidays.Germany(subdiv=self._subdiv, years=year)
        return self._cache[year]

    def get_holiday_name(self, d: date) -> Optional[str]:
        """
        Gibt den deutschen Namen des Feiertags zurück, oder None wenn kein Feiertag.
        Gilt für alle Feiertage – unabhängig davon ob arbeitsfrei oder nicht.
        """
        hols = self._get_holidays(d.year)
        english_name = hols.get(d)
        if english_name is None:
            return None
        # Deutschen Namen zurückgeben, falls vorhanden
        return _HOLIDAY_NAMES_DE.get(english_name, english_name)

    def _get_holiday_name_en(self, d: date) -> Optional[str]:
        """Gibt den englischen Feiertagsnamen zurück (intern für Prüflogik)."""
        hols = self._get_holidays(d.year)
        return hols.get(d)

    def is_public_holiday(self, d: date) -> bool:
        """
        Prüft, ob der Tag ein gesetzlich freier Feiertag in Hessen ist.
        Diese Tage werden wie Sonntage in kräftigem Rot dargestellt.
        """
        english_name = self._get_holiday_name_en(d)
        if english_name is None:
            return False
        return english_name in _FREE_HOLIDAY_NAMES_EN

    def is_regional_holiday(self, d: date) -> bool:
        """
        Prüft, ob der Tag ein regionaler Gedenktag ist, der NICHT arbeitsfrei ist.
        Diese Tage werden nicht farblich hervorgehoben, zeigen aber den Namen in Spalte 1.
        """
        english_name = self._get_holiday_name_en(d)
        if english_name is None:
            return False
        # Ist ein Feiertag, aber kein freier → regionaler Tag
        return english_name not in _FREE_HOLIDAY_NAMES_EN

    def is_any_holiday(self, d: date) -> bool:
        """Prüft, ob der Tag irgendeiner Art von Feiertag ist."""
        return self._get_holiday_name_en(d) is not None
