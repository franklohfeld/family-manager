"""
Tests für Datums-Hilfsfunktionen.
"""

from datetime import date, datetime, timedelta

from src.utils.date_utils import (
    format_date_display,
    format_date_short,
    format_kw_overlay,
    format_month_header,
    format_week_header,
    get_next_sunday_midnight,
    get_week_dates,
    get_week_number,
    get_week_start,
    is_sunday_midnight,
)


class TestGetWeekStart:
    """Tests für get_week_start()."""

    def test_montag_bleibt_montag(self):
        """Montag ist sein eigener Wochenanfang."""
        montag = date(2026, 11, 2)
        assert get_week_start(montag) == montag

    def test_mittwoch_ergibt_montag(self):
        """Mittwoch 04.11. → Montag 02.11."""
        mittwoch = date(2026, 11, 4)
        erwartet = date(2026, 11, 2)
        assert get_week_start(mittwoch) == erwartet

    def test_sonntag_ergibt_montag_der_woche(self):
        """Sonntag 08.11. → Montag 02.11."""
        sonntag = date(2026, 11, 8)
        erwartet = date(2026, 11, 2)
        assert get_week_start(sonntag) == erwartet

    def test_jahreswechsel(self):
        """Silvesterwoche: Do 31.12.2026 → Mo 28.12.2026."""
        silvester = date(2026, 12, 31)
        erwartet = date(2026, 12, 28)
        assert get_week_start(silvester) == erwartet


class TestGetWeekDates:
    """Tests für get_week_dates()."""

    def test_gibt_sieben_tage_zurueck(self):
        montag = date(2026, 11, 2)
        tage = get_week_dates(montag)
        assert len(tage) == 7

    def test_erster_tag_ist_montag(self):
        montag = date(2026, 11, 2)
        tage = get_week_dates(montag)
        assert tage[0].weekday() == 0  # Montag

    def test_letzter_tag_ist_sonntag(self):
        montag = date(2026, 11, 2)
        tage = get_week_dates(montag)
        assert tage[-1].weekday() == 6  # Sonntag

    def test_tage_sind_aufeinanderfolgend(self):
        montag = date(2026, 11, 2)
        tage = get_week_dates(montag)
        for i in range(1, 7):
            assert tage[i] == tage[i - 1] + timedelta(days=1)


class TestGetWeekNumber:
    """Tests für get_week_number()."""

    def test_kw_45_november_2026(self):
        """02.11.2026 liegt in KW 45."""
        assert get_week_number(date(2026, 11, 2)) == 45

    def test_kw_1_januar(self):
        """01.01.2026 liegt in KW 1."""
        assert get_week_number(date(2026, 1, 1)) == 1


class TestIsSundayMidnight:
    """Tests für is_sunday_midnight()."""

    def test_sonntag_mitternacht(self):
        sonntag_mitternacht = datetime(2026, 11, 8, 0, 0, 0)
        assert is_sunday_midnight(sonntag_mitternacht) is True

    def test_sonntag_nicht_mitternacht(self):
        sonntag_abend = datetime(2026, 11, 8, 23, 59, 0)
        assert is_sunday_midnight(sonntag_abend) is False

    def test_montag_mitternacht(self):
        montag_mitternacht = datetime(2026, 11, 9, 0, 0, 0)
        assert is_sunday_midnight(montag_mitternacht) is False


class TestFormatFunctions:
    """Tests für Formatierungsfunktionen."""

    def test_format_date_display(self):
        """Montag 02.11.2026 → 'Montag, 02. November 2026'."""
        d = date(2026, 11, 2)
        result = format_date_display(d)
        assert "Montag" in result
        assert "November" in result
        assert "2026" in result

    def test_format_date_short(self):
        """Montag 02.11.2026 → 'Mo, 02.11.'"""
        d = date(2026, 11, 2)
        result = format_date_short(d)
        assert result.startswith("Mo")
        assert "02.11." in result

    def test_format_week_header_gleicher_monat(self):
        """KW innerhalb eines Monats."""
        montag = date(2026, 11, 2)
        result = format_week_header(montag)
        assert "KW 45" in result
        assert "Nov" in result

    def test_format_month_header(self):
        result = format_month_header(2026, 11)
        assert result == "November 2026"

    def test_format_kw_overlay(self):
        d = date(2026, 11, 2)
        result = format_kw_overlay(d)
        assert result == "KW 45"


class TestGetNextSundayMidnight:
    """Tests für get_next_sunday_midnight()."""

    def test_von_montag_aus(self):
        """Von Montag aus ist der nächste Sonntag in 6 Tagen."""
        montag = datetime(2026, 11, 2, 10, 0, 0)
        result = get_next_sunday_midnight(montag)
        assert result.weekday() == 6
        assert result.hour == 0
        assert result.minute == 0
        assert result > montag

    def test_von_sonntag_mittag_aus(self):
        """Von Sonntag Mittag aus ist der nächste Sonntag in 7 Tagen."""
        sonntag_mittag = datetime(2026, 11, 8, 12, 0, 0)
        result = get_next_sunday_midnight(sonntag_mittag)
        # Muss NACH dem aktuellen Sonntag liegen
        assert result > sonntag_mittag
        assert result.weekday() == 6
