"""
Tests für den Konfigurationslader.
"""

import pytest
import yaml

from src.utils.config import (
    _deep_merge,
    _expand_path,
    get_all_persons,
    get_person_calendar_label,
    get_person_display_name,
    reset_config,
)


@pytest.fixture(autouse=True)
def reset_config_cache():
    """Setzt den Konfigurations-Cache vor jedem Test zurück."""
    reset_config()
    yield
    reset_config()


@pytest.fixture
def temp_config_dir(tmp_path):
    """Erstellt ein temporäres Verzeichnis mit einer Standard-config.yaml."""
    config = {
        "display": {"width": 1920, "height": 1080, "fullscreen": True},
        "holidays": {"state": "HE"},
        "persons": [
            {"key": "PERSON_A", "column": 1},
            {"key": "PERSON_B", "column": 2},
        ],
    }
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config, f)
    return tmp_path


class TestDeepMerge:
    """Tests für die Konfigurations-Zusammenführung."""

    def test_einfaches_merge(self):
        base = {"a": 1, "b": 2}
        override = {"b": 99, "c": 3}
        result = _deep_merge(base, override)
        assert result == {"a": 1, "b": 99, "c": 3}

    def test_verschachteltes_merge(self):
        base = {"display": {"width": 1920, "height": 1080}}
        override = {"display": {"width": 1080}}
        result = _deep_merge(base, override)
        # Höhe bleibt erhalten, Breite wird überschrieben
        assert result["display"]["width"] == 1080
        assert result["display"]["height"] == 1080

    def test_liste_wird_ersetzt(self):
        """Listen werden vollständig ersetzt, nicht zusammengeführt."""
        base = {"persons": [{"key": "A"}]}
        override = {"persons": [{"key": "B"}, {"key": "C"}]}
        result = _deep_merge(base, override)
        assert len(result["persons"]) == 2

    def test_base_wird_nicht_veraendert(self):
        base = {"a": 1}
        override = {"a": 2}
        _deep_merge(base, override)
        assert base["a"] == 1


class TestExpandPath:
    """Tests für die Pfad-Expansion."""

    def test_tilde_wird_expandiert(self):
        result = _expand_path("~/test")
        assert not result.startswith("~")
        assert "test" in result

    def test_normaler_string_unveraendert(self):
        result = _expand_path("kein/pfad")
        assert result == "kein/pfad"

    def test_zahl_unveraendert(self):
        result = _expand_path(42)
        assert result == 42


class TestGetPersonDisplayName:
    """Tests für Personen-Namens-Abfragen."""

    def test_gibt_anzeigenamen_zurueck(self, sample_config):
        name = get_person_display_name(sample_config, "PERSON_A")
        assert name == "TestA"

    def test_fallback_auf_schluessel_wenn_kein_name(self, sample_config):
        name = get_person_display_name(sample_config, "PERSON_X")
        assert name == "PERSON_X"


class TestGetPersonCalendarLabel:
    """Tests für Kalender-Label-Abfragen."""

    def test_gibt_label_zurueck(self, sample_config):
        label = get_person_calendar_label(sample_config, "PERSON_A")
        assert label == "Label A"

    def test_gibt_none_fuer_unbekannte_person(self, sample_config):
        label = get_person_calendar_label(sample_config, "PERSON_X")
        assert label is None


class TestGetAllPersons:
    """Tests für die Personen-Liste."""

    def test_gibt_alle_personen_zurueck(self, sample_config):
        persons = get_all_persons(sample_config)
        assert len(persons) == 4

    def test_personen_sind_nach_spalte_sortiert(self, sample_config):
        persons = get_all_persons(sample_config)
        columns = [p["column"] for p in persons]
        assert columns == sorted(columns)
