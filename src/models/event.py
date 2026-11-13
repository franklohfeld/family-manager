"""
Datenmodell für einen Kalender-Termin.
"""

from dataclasses import dataclass, field
from datetime import datetime, date


# Schlüsselwörter im Termintitel, die auf Urlaub oder freien Tag hinweisen
VACATION_KEYWORDS = ("urlaub", "frei")


@dataclass
class Event:
    """Repräsentiert einen einzelnen Kalender-Termin."""

    id: str
    title: str
    start: datetime
    end: datetime
    all_day: bool
    # Personenschlüssel: "PERSON_A", "PERSON_B", "PERSON_C", "PERSON_D" oder "general"
    person: str
    calendar_id: str
    is_vacation: bool = field(init=False)

    def __post_init__(self) -> None:
        """Erkennt automatisch Urlaubs-/Frei-Termine anhand des Titels."""
        title_lower = self.title.lower()
        self.is_vacation = any(keyword in title_lower for keyword in VACATION_KEYWORDS)

    @property
    def start_date(self) -> date:
        """Gibt das Startdatum ohne Uhrzeit zurück."""
        return self.start.date() if isinstance(self.start, datetime) else self.start

    @property
    def end_date(self) -> date:
        """Gibt das Enddatum ohne Uhrzeit zurück."""
        return self.end.date() if isinstance(self.end, datetime) else self.end

    def to_dict(self) -> dict:
        """Serialisiert das Event als Dictionary (für den Cache)."""
        return {
            "id": self.id,
            "title": self.title,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "all_day": self.all_day,
            "person": self.person,
            "calendar_id": self.calendar_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        """Erstellt ein Event aus einem Dictionary (aus dem Cache)."""
        return cls(
            id=data["id"],
            title=data["title"],
            start=datetime.fromisoformat(data["start"]),
            end=datetime.fromisoformat(data["end"]),
            all_day=data.get("all_day", False),
            person=data.get("person", "general"),
            calendar_id=data.get("calendar_id", ""),
        )
