"""
Google Calendar Service für den Familienkalender.
Verwaltet die Anbindung an die Google Calendar API, das lokale Caching
und die Zuordnung von Terminen zu Personen.
"""

import json
import logging
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.models.event import Event
from src.models.person import Person

logger = logging.getLogger(__name__)

# Minimal notwendiger Scope – nur lesend
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class CalendarService:
    """
    Service zur Anbindung an Google Calendar.
    Lädt Termine, ordnet sie Personen zu und cached die Daten lokal
    für den Offline-Betrieb.
    """

    def __init__(
        self,
        credentials_file: str,
        token_file: str,
        cache_file: str,
        persons: list[Person],
        lookahead_weeks: int = 4,
        lookbehind_weeks: int = 1,
    ) -> None:
        """
        Initialisiert den Service.

        Args:
            credentials_file: Pfad zu den Google OAuth2-Zugangsdaten (credentials.json).
            token_file: Pfad zur gespeicherten OAuth2-Token-Datei.
            cache_file: Pfad zur lokalen Cache-Datei.
            persons: Liste der konfigurierten Personen.
            lookahead_weeks: Wie viele Wochen voraus geladen werden.
            lookbehind_weeks: Wie viele Wochen zurück geladen werden.
        """
        self._credentials_file = Path(credentials_file).expanduser()
        self._token_file = Path(token_file).expanduser()
        self._cache_file = Path(cache_file).expanduser()
        self._persons = persons
        self._lookahead_weeks = lookahead_weeks
        self._lookbehind_weeks = lookbehind_weeks
        self._events: list[Event] = []
        self._service = None

        # Cache-Verzeichnis anlegen
        self._cache_file.parent.mkdir(parents=True, exist_ok=True)

        # Gespeicherte Ereignisse aus Cache laden
        self._events = self._load_cache()

    # -------------------------------------------------------------------------
    # Öffentliche Methoden
    # -------------------------------------------------------------------------

    def get_events_for_week(self, week_start: date) -> list[Event]:
        """
        Gibt alle Ereignisse der angegebenen Woche zurück (Montag bis Sonntag).
        """
        week_end = week_start + timedelta(days=6)
        return [
            event for event in self._events
            if event.start_date <= week_end and event.end_date >= week_start
        ]

    def get_events_for_month(self, year: int, month: int) -> list[Event]:
        """
        Gibt alle Ereignisse des angegebenen Monats zurück.
        """
        month_start = date(year, month, 1)
        # Letzter Tag des Monats
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)

        return [
            event for event in self._events
            if event.start_date <= month_end and event.end_date >= month_start
        ]

    def get_events_for_date(self, d: date) -> list[Event]:
        """Gibt alle Ereignisse eines bestimmten Tages zurück."""
        return [
            event for event in self._events
            if event.start_date <= d <= event.end_date
        ]

    def get_events_for_person_on_date(self, person_key: str, d: date) -> list[Event]:
        """Gibt alle Ereignisse einer Person an einem bestimmten Tag zurück."""
        return [
            event for event in self.get_events_for_date(d)
            if event.person == person_key
        ]

    def refresh(self) -> bool:
        """
        Aktualisiert die Ereignisse von der Google Calendar API.
        Bei Fehler wird der lokale Cache verwendet.
        Gibt True zurück bei Erfolg, False bei Fehler.
        """
        try:
            creds = self._get_credentials()
            if creds is None:
                logger.warning("Keine gültigen Zugangsdaten – verwende Cache.")
                return False

            self._service = build("calendar", "v3", credentials=creds)
            self._events = self._fetch_events()
            self._save_cache(self._events)
            logger.info(f"{len(self._events)} Ereignisse geladen.")
            return True

        except HttpError as e:
            logger.error(f"Google Calendar API Fehler: {e}")
            return False
        except Exception as e:
            logger.error(f"Unerwarteter Fehler beim Laden der Ereignisse: {e}")
            return False

    # -------------------------------------------------------------------------
    # Private Methoden
    # -------------------------------------------------------------------------

    def _get_credentials(self) -> Optional[Credentials]:
        """
        Gibt gültige OAuth2-Zugangsdaten zurück.
        Lädt gespeichertes Token oder startet OAuth2-Flow falls nötig.
        """
        creds = None

        # Gespeichertes Token laden
        if self._token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    str(self._token_file), SCOPES
                )
            except Exception as e:
                logger.warning(f"Token konnte nicht geladen werden: {e}")

        # Token erneuern oder neu authentifizieren
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self._save_token(creds)
                    return creds
                except Exception as e:
                    logger.warning(f"Token-Erneuerung fehlgeschlagen: {e}")
                    creds = None

            # Neue Authentifizierung erforderlich
            if not self._credentials_file.exists():
                logger.error(
                    f"credentials.json nicht gefunden: {self._credentials_file}"
                )
                return None

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self._credentials_file), SCOPES
                )
                creds = flow.run_local_server(port=0)
                self._save_token(creds)
            except Exception as e:
                logger.error(f"OAuth2-Authentifizierung fehlgeschlagen: {e}")
                return None

        return creds

    def _save_token(self, creds: Credentials) -> None:
        """Speichert das OAuth2-Token für künftige Sitzungen."""
        try:
            with open(self._token_file, "w") as f:
                f.write(creds.to_json())
        except OSError as e:
            logger.error(f"Token konnte nicht gespeichert werden: {e}")

    def _fetch_events(self) -> list[Event]:
        """
        Ruft Ereignisse von der Google Calendar API ab.
        Lädt alle Kalender und ordnet Termine den konfigurierten Personen zu.
        """
        now = datetime.utcnow()
        time_min = (now - timedelta(weeks=self._lookbehind_weeks)).isoformat() + "Z"
        time_max = (now + timedelta(weeks=self._lookahead_weeks)).isoformat() + "Z"

        all_events = []

        # Alle Kalender des Nutzers abrufen
        calendars_result = self._service.calendarList().list().execute()
        calendars = calendars_result.get("items", [])

        for calendar in calendars:
            cal_id = calendar["id"]
            cal_summary = calendar.get("summary", "")

            try:
                events_result = (
                    self._service.events()
                    .list(
                        calendarId=cal_id,
                        timeMin=time_min,
                        timeMax=time_max,
                        singleEvents=True,
                        orderBy="startTime",
                    )
                    .execute()
                )

                for item in events_result.get("items", []):
                    event = self._parse_event(item, cal_id, cal_summary)
                    if event:
                        all_events.append(event)

            except HttpError as e:
                logger.warning(f"Fehler beim Laden von Kalender '{cal_summary}': {e}")

        return all_events

    def _parse_event(
        self, item: dict, calendar_id: str, calendar_summary: str
    ) -> Optional[Event]:
        """
        Parst ein Google Calendar API-Ereignis in ein Event-Objekt.
        """
        try:
            title = item.get("summary", "(Kein Titel)")
            event_id = item.get("id", "")

            # Ganztägiges Ereignis oder mit Uhrzeit?
            start_raw = item["start"]
            end_raw = item["end"]

            if "date" in start_raw:
                # Ganztägig
                all_day = True
                start_dt = datetime.fromisoformat(start_raw["date"])
                end_dt = datetime.fromisoformat(end_raw["date"])
            else:
                # Mit Uhrzeit
                all_day = False
                start_str = start_raw["dateTime"]
                end_str = end_raw["dateTime"]
                # Zeitzone entfernen für einheitliche Verarbeitung
                start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00"))

            # Person zuordnen
            person_key = self._assign_person(item, calendar_summary)

            return Event(
                id=event_id,
                title=title,
                start=start_dt,
                end=end_dt,
                all_day=all_day,
                person=person_key,
                calendar_id=calendar_id,
            )

        except (KeyError, ValueError) as e:
            logger.warning(f"Ereignis konnte nicht geparst werden: {e} | {item}")
            return None

    def _assign_person(self, item: dict, calendar_summary: str) -> str:
        """
        Ordnet ein Ereignis einer Person zu.
        Vergleicht den Kalendernamen mit den konfigurierten Kalender-Labels.
        Gibt "general" zurück wenn keine Zuordnung gefunden wird.
        """
        for person in self._persons:
            if person.calendar_label and (
                person.calendar_label.lower() in calendar_summary.lower()
                or person.calendar_label.lower() in item.get("summary", "").lower()
            ):
                return person.key

        # Fallback: "general" für nicht zugeordnete Termine
        return "general"

    def _load_cache(self) -> list[Event]:
        """
        Lädt den Ereignis-Cache aus der lokalen JSON-Datei.
        """
        if not self._cache_file.exists():
            return []

        try:
            with open(self._cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Event.from_dict(e) for e in data]
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Cache konnte nicht gelesen werden: {e}")
            return []

    def _save_cache(self, events: list[Event]) -> None:
        """Speichert Ereignisse als lokalen Cache."""
        try:
            with open(self._cache_file, "w", encoding="utf-8") as f:
                json.dump([e.to_dict() for e in events], f, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.error(f"Cache konnte nicht gespeichert werden: {e}")
