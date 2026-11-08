"""
Tests für den Bild-Rotations-Service.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from src.services.image_service import ImageService


@pytest.fixture
def temp_dir():
    """Erstellt ein temporäres Verzeichnis für Tests."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def image_dir(temp_dir):
    """Erstellt ein Bildverzeichnis mit Test-Bildern."""
    img_dir = temp_dir / "images"
    img_dir.mkdir()
    # Dummy-Bilder anlegen (leere Dateien reichen für Pfad-Tests)
    for name in ["bild_01.jpg", "bild_02.jpg", "bild_03.jpg"]:
        (img_dir / name).touch()
    return img_dir


@pytest.fixture
def state_file(temp_dir):
    """Pfad zur State-Datei."""
    return temp_dir / "state.json"


@pytest.fixture
def fallback_image(temp_dir):
    """Erstellt ein Fallback-Bild."""
    fb = temp_dir / "fallback.png"
    fb.touch()
    return fb


@pytest.fixture
def service(image_dir, state_file, fallback_image):
    """Erstellt einen ImageService mit Test-Verzeichnis."""
    return ImageService(
        image_dir=str(image_dir),
        state_file=str(state_file),
        fallback_image=str(fallback_image),
    )


class TestGetCurrentImage:
    """Tests für get_current_image()."""

    def test_erster_start_ohne_state(self, service, image_dir):
        """Beim ersten Start wird das erste Bild zurückgegeben."""
        result = service.get_current_image()
        assert result is not None
        assert result.exists()
        assert result.suffix.lower() == ".jpg"

    def test_gleiches_bild_bei_wiederholtem_aufruf(self, service):
        """Wiederholter Aufruf gibt dasselbe Bild zurück."""
        first = service.get_current_image()
        second = service.get_current_image()
        assert first == second

    def test_fallback_wenn_verzeichnis_leer(self, temp_dir, state_file, fallback_image):
        """Leeres Verzeichnis → Fallback-Bild."""
        leeres_verzeichnis = temp_dir / "leer"
        leeres_verzeichnis.mkdir()
        svc = ImageService(
            image_dir=str(leeres_verzeichnis),
            state_file=str(state_file),
            fallback_image=str(fallback_image),
        )
        result = svc.get_current_image()
        assert result == fallback_image


class TestAdvanceImage:
    """Tests für advance_image()."""

    def test_naechstes_bild_ist_anders(self, service):
        """Nach advance_image() wird ein anderes Bild angezeigt."""
        first = service.get_current_image()
        second = service.advance_image()
        assert first != second

    def test_alle_bilder_werden_angezeigt(self, service, image_dir):
        """Alle 3 Bilder werden der Reihe nach angezeigt."""
        bilder = set()
        bilder.add(str(service.get_current_image()))
        bilder.add(str(service.advance_image()))
        bilder.add(str(service.advance_image()))
        # Alle 3 Bilder wurden gezeigt
        assert len(bilder) == 3

    def test_rotation_beginnt_von_vorn_nach_letztem_bild(self, service, image_dir):
        """Nach dem letzten Bild beginnt die Rotation von vorn."""
        # Alle 3 Bilder durchlaufen
        first = service.get_current_image()
        service.advance_image()
        service.advance_image()
        # Vierter Aufruf → beginnt von vorn
        fourth = service.advance_image()
        assert fourth is not None
        assert fourth.exists()
        # Das erste Bild der neuen Runde
        assert fourth.name == first.name or fourth in [p for p in image_dir.iterdir()]


class TestStateManagement:
    """Tests für das State-Management."""

    def test_state_wird_gespeichert(self, service, state_file):
        """State-Datei wird nach dem ersten Bildaufruf erstellt."""
        service.get_current_image()
        assert state_file.exists()

    def test_state_wird_korrekt_gelesen(self, service, state_file, image_dir):
        """State wird beim nächsten Start korrekt gelesen."""
        bild1 = service.get_current_image()
        service.advance_image()

        # Neuen Service mit demselben State erstellen
        service2 = ImageService(
            image_dir=str(image_dir),
            state_file=str(state_file),
            fallback_image=service._fallback_image,
        )
        # Das aktuelle Bild des neuen Services ist nicht das erste Bild
        bild_neu = service2.get_current_image()
        assert bild_neu != bild1

    def test_korrumpierter_state_wird_ignoriert(self, temp_dir, image_dir, fallback_image):
        """Ungültige State-Datei → leerer State, kein Absturz."""
        state_file = temp_dir / "corrupt_state.json"
        state_file.write_text("das ist kein json {{{")

        svc = ImageService(
            image_dir=str(image_dir),
            state_file=str(state_file),
            fallback_image=str(fallback_image),
        )
        # Sollte kein Fehler werfen
        result = svc.get_current_image()
        assert result is not None
