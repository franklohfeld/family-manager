"""
Datenmodell für eine Person / Kategorie im Familienkalender.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Person:
    """Repräsentiert eine Person mit einer Spalte im Familienplaner."""

    # Interner Schlüssel (z.B. "PERSON_A") – verwendet im Quellcode
    key: str
    # Anzeigename (aus lokaler Konfiguration, z.B. echter Vorname)
    display_name: str
    # Google-Kalender-Label oder Farbe zur Termins-Zuordnung
    calendar_label: Optional[str]
    # Spaltenindex in der Wochenansicht (1–4)
    column_index: int

    @classmethod
    def from_config(cls, person_dict: dict) -> "Person":
        """Erstellt eine Person aus einem Konfigurations-Dictionary."""
        return cls(
            key=person_dict.get("key", ""),
            display_name=person_dict.get("display_name", person_dict.get("key", "")),
            calendar_label=person_dict.get("calendar_label"),
            column_index=person_dict.get("column", 0),
        )

    def __str__(self) -> str:
        return self.display_name or self.key
