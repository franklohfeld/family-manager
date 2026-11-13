"""
Konfigurationslader für den Familienkalender.
Lädt config.yaml (Standardwerte) und mergt mit config.local.yaml (lokale Überschreibungen).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


# Basis-Verzeichnis des Projekts (zwei Ebenen über diesem Modul)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _expand_path(value: Any) -> Any:
    """Erweitert ~ in Pfadangaben zu absoluten Pfaden."""
    if isinstance(value, str) and value.startswith("~"):
        return str(Path(value).expanduser())
    return value


def _expand_paths_recursive(data: Any) -> Any:
    """Rekursiv alle Pfade in einem verschachtelten Dict/List erweitern."""
    if isinstance(data, dict):
        return {k: _expand_paths_recursive(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_expand_paths_recursive(item) for item in data]
    return _expand_path(data)


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Führt zwei Dictionaries tief zusammen.
    Werte aus 'override' überschreiben Werte aus 'base'.
    Listen werden vollständig ersetzt (nicht zusammengeführt).
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config() -> dict:
    """
    Lädt die Konfiguration aus config.yaml und config.local.yaml.
    config.local.yaml überschreibt Werte aus config.yaml.
    Gibt das zusammengeführte Konfigurations-Dictionary zurück.
    """
    # Standardkonfiguration laden
    default_config_path = BASE_DIR / "config.yaml"
    if not default_config_path.exists():
        raise FileNotFoundError(
            f"Standardkonfiguration nicht gefunden: {default_config_path}"
        )

    with open(default_config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    # Lokale Konfiguration laden und zusammenführen (falls vorhanden)
    local_config_path = BASE_DIR / "config.local.yaml"
    if local_config_path.exists():
        with open(local_config_path, "r", encoding="utf-8") as f:
            local_config = yaml.safe_load(f) or {}
        config = _deep_merge(config, local_config)

    # Pfade expandieren (~ → absoluter Pfad)
    config = _expand_paths_recursive(config)

    return config


def get_person_display_name(config: dict, person_key: str) -> str:
    """
    Gibt den Anzeigenamen einer Person zurück.
    Falls kein lokaler Name konfiguriert ist, wird der Schlüssel zurückgegeben.
    """
    for person in config.get("persons", []):
        if person.get("key") == person_key:
            return person.get("display_name", person_key)
    return person_key


def get_person_calendar_label(config: dict, person_key: str) -> str | None:
    """
    Gibt das Google-Kalender-Label einer Person zurück.
    """
    for person in config.get("persons", []):
        if person.get("key") == person_key:
            return person.get("calendar_label")
    return None


def get_all_persons(config: dict) -> list[dict]:
    """
    Gibt alle Personen sortiert nach ihrer Spalte zurück.
    """
    return sorted(config.get("persons", []), key=lambda p: p.get("column", 99))


# Singleton-Instanz
_config: dict | None = None


def get_config() -> dict:
    """
    Gibt die geladene Konfiguration zurück (Singleton – wird nur einmal geladen).
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reset_config() -> None:
    """
    Setzt den Konfigurations-Cache zurück (nützlich für Tests).
    """
    global _config
    _config = None
