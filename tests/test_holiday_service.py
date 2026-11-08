"""
Tests für den Feiertags-Service.
"""

from datetime import date

import pytest

from src.services.holiday_service import HolidayService


@pytest.fixture
def holiday_service() -> HolidayService:
    """HolidayService für Hessen."""
    return HolidayService(state="HE")


class TestIsPublicHoliday:
    """Tests für gesetzlich freie Feiertage in Hessen."""

    def test_neujahr_ist_frei(self, holiday_service):
        """01.01. ist gesetzlich frei."""
        assert holiday_service.is_public_holiday(date(2026, 1, 1)) is True

    def test_karfreitag_ist_frei(self, holiday_service):
        """Karfreitag 2026 ist gesetzlich frei."""
        assert holiday_service.is_public_holiday(date(2026, 4, 3)) is True

    def test_tag_der_arbeit_ist_frei(self, holiday_service):
        """01.05. ist gesetzlich frei."""
        assert holiday_service.is_public_holiday(date(2026, 5, 1)) is True

    def test_tag_der_deutschen_einheit_ist_frei(self, holiday_service):
        """03.10. ist gesetzlich frei."""
        assert holiday_service.is_public_holiday(date(2026, 10, 3)) is True

    def test_weihnachten_erster_tag_ist_frei(self, holiday_service):
        """25.12. ist gesetzlich frei."""
        assert holiday_service.is_public_holiday(date(2026, 12, 25)) is True

    def test_weihnachten_zweiter_tag_ist_frei(self, holiday_service):
        """26.12. ist gesetzlich frei."""
        assert holiday_service.is_public_holiday(date(2026, 12, 26)) is True

    def test_normaler_werktag_ist_kein_feiertag(self, holiday_service):
        """Normaler Dienstag ist kein Feiertag."""
        assert holiday_service.is_public_holiday(date(2026, 6, 2)) is False

    def test_sonntag_ist_kein_feiertag(self, holiday_service):
        """Sonntag ist kein Feiertag im Sinne des Services."""
        assert holiday_service.is_public_holiday(date(2026, 11, 8)) is False


class TestGetHolidayName:
    """Tests für die Feiertagsnamen-Rückgabe."""

    def test_neujahr_hat_namen(self, holiday_service):
        """Neujahr hat einen Namen."""
        name = holiday_service.get_holiday_name(date(2026, 1, 1))
        assert name is not None
        assert len(name) > 0

    def test_normaler_tag_hat_keinen_namen(self, holiday_service):
        """Normaler Werktag hat keinen Feiertagsnamen."""
        name = holiday_service.get_holiday_name(date(2026, 6, 2))
        assert name is None

    def test_fronleichnam_hessen_hat_namen(self, holiday_service):
        """Fronleichnam ist in Hessen ein Feiertag."""
        # Fronleichnam 2026: 4. Juni
        name = holiday_service.get_holiday_name(date(2026, 6, 4))
        assert name is not None


class TestIsRegionalHoliday:
    """Tests für regionale Feiertage ohne Freiheit."""

    def test_freier_feiertag_ist_kein_regionaler(self, holiday_service):
        """Neujahr ist frei, also kein 'regionaler' Feiertag."""
        assert holiday_service.is_regional_holiday(date(2026, 1, 1)) is False

    def test_normaler_tag_ist_kein_regionaler(self, holiday_service):
        """Normaler Tag ist auch kein regionaler Feiertag."""
        assert holiday_service.is_regional_holiday(date(2026, 6, 2)) is False


class TestIsAnyHoliday:
    """Tests für die allgemeine Feiertags-Prüfung."""

    def test_neujahr_ist_irgendein_feiertag(self, holiday_service):
        assert holiday_service.is_any_holiday(date(2026, 1, 1)) is True

    def test_werktag_ist_kein_feiertag(self, holiday_service):
        assert holiday_service.is_any_holiday(date(2026, 6, 2)) is False
