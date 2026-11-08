"""
Tests für den Kalender-Service.
Verwendet Mocks für die Google API.
"""

import json
import tempfile
from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.models.event import Event
from src.models.person import Person
from src.services.calendar_service import CalendarService


@pytest.fixture
def persons() -> list:
    """Testpersonen."""
    return [
        Person(key="PERSON_A", display_name="TestA", calendar_label="Kalender A", column_index=1),
        Person(key="PERSON_B", display_name="TestB", calendar_label="Kalender B", column_index=2),
        Person(key="PERSON_C", display_name="TestC", calendar_label="Kalender C", column_index=3),
        Person(key="PERSON_D", display_name="TestD", calendar_label="Kalender D", column_index=4),
    ]


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def service(persons, temp_dir) -> CalendarService:
    """CalendarService mit temporären Dateipfaden."""
    return CalendarService(
        credentials_file=str(temp_dir / "credentials.json"),
        token_file=str(temp_dir / "token.json"),
        cache_file=str(temp_dir / "cache.json"),
        persons=persons,
    )


@pytest.fixture
def sample_events() -> list:
    """Beispiel-Ereignisse für Tests."""
    return [
        Event(
            id="1",
            title="Meeting",
            start=datetime(2026, 11, 2, 9, 0),
            end=datetime(2026, 11, 2, 10, 0),
            all_day=False,
            person="PERSON_A",
            calendar_id="cal-a",
        ),
        Event(
            id="2",
            title="Urlaub Teneriffa",
            start=datetime(2026, 11, 3, 0, 0),
            end=datetime(2026, 11, 7, 0, 0),
            all_day=True,
            person="PERSON_B",
            calendar_id="cal-b",
        ),
        Event(
            id="3",
            title="Elternabend",
            start=datetime(2026, 11, 4, 19, 0),
            end=datetime(2026, 11, 4, 21, 0),
            all_day=False,
            person="general",
            calendar_id="cal-general",
        ),
    ]


class TestGetEventsForWeek:
    """Tests für die Wochenabfrage."""

    def test_gibt_ereignisse_der_woche_zurueck(self, service, sample_events):
        """Ereignisse in der KW45 werden korrekt gefiltert."""
        service._events = sample_events
        week_start = date(2026, 11, 2)  # Montag KW45
        result = service.get_events_for_week(week_start)
        # Meeting am Mo 02.11. und Urlaub 03.–07.11. sind in der Woche
        assert len(result) >= 1

    def test_ereignisse_ausserhalb_der_woche_werden_gefiltert(self, service, sample_events):
        """Ereignisse außerhalb der Woche werden nicht zurückgegeben."""
        service._events = sample_events
        # Eine andere Woche (1. Dezember)
        week_start = date(2026, 11, 30)
        result = service.get_events_for_week(week_start)
        assert len(result) == 0


class TestGetEventsForDate:
    """Tests für die Tagesabfrage."""

    def test_gibt_ereignisse_des_tages_zurueck(self, service, sample_events):
        """Ereignisse am 02.11.2026 werden korrekt zurückgegeben."""
        service._events = sample_events
        result = service.get_events_for_date(date(2026, 11, 2))
        assert any(e.id == "1" for e in result)

    def test_mehrtaegige_ereignisse_werden_erkannt(self, service, sample_events):
        """Mehrtägiger Urlaub 03.–07.11. ist auch am 05.11. sichtbar."""
        service._events = sample_events
        result = service.get_events_for_date(date(2026, 11, 5))
        assert any(e.id == "2" for e in result)


class TestGetEventsForPersonOnDate:
    """Tests für personenbezogene Tagesabfragen."""

    def test_gibt_nur_ereignisse_der_person_zurueck(self, service, sample_events):
        """Nur Ereignisse von PERSON_A am 02.11."""
        service._events = sample_events
        result = service.get_events_for_person_on_date("PERSON_A", date(2026, 11, 2))
        assert all(e.person == "PERSON_A" for e in result)

    def test_keine_ereignisse_fuer_andere_person(self, service, sample_events):
        """PERSON_C hat keine Ereignisse in der Testwoche."""
        service._events = sample_events
        result = service.get_events_for_person_on_date("PERSON_C", date(2026, 11, 2))
        assert len(result) == 0


class TestCacheManagement:
    """Tests für das Cache-Management."""

    def test_cache_speichern_und_laden(self, service, sample_events, temp_dir):
        """Events werden gespeichert und korrekt geladen."""
        service._save_cache(sample_events)

        # Neuen Service mit demselben Cache erstellen
        service2 = CalendarService(
            credentials_file=str(temp_dir / "credentials.json"),
            token_file=str(temp_dir / "token.json"),
            cache_file=str(temp_dir / "cache.json"),
            persons=service._persons,
        )
        assert len(service2._events) == len(sample_events)

    def test_leerer_cache_gibt_leere_liste_zurueck(self, service):
        """Leerer Cache → leere Ereignisliste."""
        events = service._load_cache()
        assert events == []


class TestAssignPerson:
    """Tests für die Personenzuordnung."""

    def test_kalender_label_a_wird_zugeordnet(self, service):
        """Kalender 'Kalender A' wird PERSON_A zugeordnet."""
        item = {"summary": "Test-Termin"}
        result = service._assign_person(item, "Kalender A")
        assert result == "PERSON_A"

    def test_unbekannter_kalender_wird_general(self, service):
        """Unbekannter Kalender → 'general'."""
        item = {"summary": "Test-Termin"}
        result = service._assign_person(item, "Unbekannter Kalender")
        assert result == "general"


class TestEventVacationDetection:
    """Tests für die Urlaubs-Erkennung im Event-Modell."""

    def test_urlaub_im_titel_wird_erkannt(self):
        event = Event(
            id="v1", title="Urlaub Mallorca",
            start=datetime(2026, 8, 1), end=datetime(2026, 8, 14),
            all_day=True, person="PERSON_A", calendar_id="cal",
        )
        assert event.is_vacation is True

    def test_frei_im_titel_wird_erkannt(self):
        event = Event(
            id="v2", title="Frei genommen",
            start=datetime(2026, 5, 2), end=datetime(2026, 5, 2),
            all_day=True, person="PERSON_B", calendar_id="cal",
        )
        assert event.is_vacation is True

    def test_normaler_termin_kein_urlaub(self):
        event = Event(
            id="v3", title="Zahnarzt",
            start=datetime(2026, 5, 2), end=datetime(2026, 5, 2),
            all_day=False, person="PERSON_C", calendar_id="cal",
        )
        assert event.is_vacation is False
