"""
Bildrotations-Service für den Familienkalender.
Verwaltet die wöchentliche Rotation der Fotos aus einem konfigurierten Verzeichnis.
Jedes Bild wird einmal gezeigt; nach dem letzten beginnt die Rotation von vorn.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.utils.date_utils import get_next_sunday_midnight

logger = logging.getLogger(__name__)


class ImageService:
    """
    Verwaltet die Bildrotation für die Fotoanzeige im oberen Bildschirmbereich.
    Der Zustand (aktuelles Bild, bereits gezeigte Bilder) wird in einer
    JSON-Datei persistent gespeichert.
    """

    def __init__(
        self,
        image_dir: str,
        state_file: str,
        fallback_image: str,
        supported_formats: Optional[List[str]] = None,
    ) -> None:
        """
        Initialisiert den Service.

        Args:
            image_dir: Verzeichnis mit den Fotos.
            state_file: Pfad zur JSON-State-Datei.
            fallback_image: Bild, das angezeigt wird wenn das Verzeichnis leer ist.
            supported_formats: Unterstützte Dateiendungen (Standard: .jpg, .jpeg, .png).
        """
        self._image_dir = Path(image_dir).expanduser()
        self._state_file = Path(state_file).expanduser()
        self._fallback_image = Path(fallback_image)
        self._supported_formats = supported_formats or [".jpg", ".jpeg", ".png"]
        self._state: dict = {}

        # State-Verzeichnis anlegen falls nötig
        self._state_file.parent.mkdir(parents=True, exist_ok=True)

        # State laden
        self._state = self._load_state()

    # -------------------------------------------------------------------------
    # Öffentliche Methoden
    # -------------------------------------------------------------------------

    def get_current_image(self) -> Optional[Path]:
        """
        Gibt den Pfad zum aktuell anzuzeigenden Bild zurück.
        Falls kein Bild verfügbar ist, wird das Fallback-Bild zurückgegeben.
        """
        current = self._state.get("current_image")

        if current:
            path = Path(current)
            if path.exists():
                return path
            else:
                logger.warning(f"Aktuelles Bild nicht gefunden: {path}. Wähle neues Bild.")
                self._state.pop("current_image", None)
                return self._select_next_image()

        return self._select_next_image()

    def advance_image(self) -> Optional[Path]:
        """
        Wechselt zum nächsten ungesehenen Bild.
        Werden alle Bilder einmal gezeigt, beginnt die Rotation von vorn.
        Gibt den Pfad zum neuen Bild zurück.
        """
        # Aktuelles Bild als gesehen markieren
        current = self._state.get("current_image")
        if current:
            seen = set(self._state.get("seen_images", []))
            seen.add(current)
            self._state["seen_images"] = list(seen)
            self._state.pop("current_image", None)

        return self._select_next_image()

    def schedule_weekly_rotation(self, callback=None) -> None:
        """
        Plant den nächsten Bildwechsel (Sonntag 00:00 Uhr).
        Verwendet Qt-Timer; callback wird aufgerufen wenn der Wechsel erfolgt.
        Diese Methode wird von der App aufgerufen und verwaltet den Timer extern.
        """
        next_rotation = get_next_sunday_midnight(datetime.now())
        logger.info(f"Nächster Bildwechsel geplant für: {next_rotation}")
        return next_rotation

    def get_next_rotation_time(self) -> datetime:
        """Gibt den Zeitpunkt des nächsten Bildwechsels zurück."""
        return get_next_sunday_midnight(datetime.now())

    # -------------------------------------------------------------------------
    # Private Methoden
    # -------------------------------------------------------------------------

    def _get_all_images(self) -> List[Path]:
        """
        Gibt alle unterstützten Bilder aus dem konfigurierten Verzeichnis zurück,
        sortiert nach Dateiname.
        """
        if not self._image_dir.exists():
            logger.warning(f"Bildverzeichnis nicht gefunden: {self._image_dir}")
            return []

        images = []
        for file in sorted(self._image_dir.iterdir()):
            if file.suffix.lower() in self._supported_formats:
                images.append(file)

        return images

    def _select_next_image(self) -> Optional[Path]:
        """
        Wählt das nächste ungesehene Bild aus.
        Sind alle Bilder verbraucht, werden die Seen-Bilder zurückgesetzt
        und die Rotation beginnt von vorn.
        """
        all_images = self._get_all_images()

        if not all_images:
            logger.warning("Keine Bilder im Verzeichnis gefunden – verwende Fallback.")
            return self._fallback_image if self._fallback_image.exists() else None

        seen = set(self._state.get("seen_images", []))
        # Ungesehene Bilder ermitteln
        unseen = [img for img in all_images if str(img) not in seen]

        if not unseen:
            # Alle Bilder wurden gezeigt – von vorn beginnen
            logger.info("Alle Bilder wurden gezeigt. Rotation beginnt von vorn.")
            self._state["seen_images"] = []
            unseen = all_images

        # Erstes ungesehenes Bild auswählen
        selected = unseen[0]
        self._state["current_image"] = str(selected)
        self._save_state(self._state)

        logger.info(f"Neues Bild ausgewählt: {selected.name}")
        return selected

    def _load_state(self) -> dict:
        """
        Lädt den State aus der JSON-Datei.
        Bei einem Fehler wird ein leerer State zurückgegeben.
        """
        if not self._state_file.exists():
            return {}

        try:
            with open(self._state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("State-Datei hat ungültiges Format.")
                return data
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"State-Datei konnte nicht gelesen werden: {e}. Starte mit leerem State.")
            return {}

    def _save_state(self, state: dict) -> None:
        """Speichert den aktuellen State in der JSON-Datei."""
        try:
            with open(self._state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.error(f"State-Datei konnte nicht gespeichert werden: {e}")
