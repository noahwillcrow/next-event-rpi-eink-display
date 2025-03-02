import os
from flask import json
import pytz
import requests
from datetime import date, datetime, timedelta
from icalendar import Calendar as IcsCalendar
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dateutil.parser import parse as parse_date


class Event:
    """This is meant to be a data structure that holds the information of an event."""

    def __init__(self, name, start_time_utc):
        self.name = name
        self.start_time_utc = start_time_utc
        self.time_until_event = start_time_utc - datetime.now().astimezone(pytz.utc)

    def __str__(self):
        return f"{self.name} at {self.start_time_utc}"


class DataFetcher:
    """This module is responsible for reading the config dict, parsing the list of ICS URLs, and fetching the data from the URLs."""

    def __init__(self, config: dict):
        self._config = config

    def fetch_next_event(self) -> Event | None:
        """This function reads the config dict to get the list of ICS URLs, fetches the data from the URLs, and returns the next event coming up within the look-ahead."""
        now = datetime.now().astimezone(pytz.utc)
        until = now + self._get_lookahead_period()

        next_event: Event | None = None

        for calendar in self._config['events']['calendars']:
            next_event_in_calendar = None

            if calendar['type'] == 'google-oauth':
                next_event_in_calendar = (
                    self._fetch_next_event_from_google_oauth_calendar(
                        calendar['client-id'], now, until
                    )
                )
            elif calendar['type'] == 'ics-url':
                next_event_in_calendar = self._fetch_next_event_from_ics_url(
                    calendar['url'], now, until
                )

            if next_event_in_calendar:
                if (
                    next_event is None
                    or next_event_in_calendar.start_time_utc < next_event.start_time_utc
                ):
                    next_event = next_event_in_calendar

        print(next_event)
        return next_event

    def _get_lookahead_period(self) -> timedelta:
        """This function reads the config dict to get the `look-ahead`, which is a string in the format of {days}.{hours}:{minutes}:{seconds}.{milliseconds}, and returns a timedelta object."""
        lookahead = self._config['events']['look-ahead']
        days, times = lookahead.split('.')
        time = times.split(':')
        hours = int(time[0])
        minutes = int(time[1])
        seconds = int(time[2])

        td = timedelta(
            days=int(days),
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )
        return td

    def _load_credentials(self, file_uuid: str) -> Credentials | None:
        """Load OAuth credentials from a file."""
        creds_path = f"../{file_uuid}-credentials.json"
        if os.path.exists(creds_path):
            with open(creds_path, 'r') as file:
                creds_json = file.read()
                return Credentials.from_authorized_user_info(json.loads(creds_json))
        return None

    def _fetch_next_event_from_google_oauth_calendar(
        self, file_uuid: str, now: datetime, until: datetime
    ) -> Event | None:
        creds = self._load_credentials(file_uuid)
        if not creds:
            return None

        service = build('calendar', 'v3', credentials=creds)
        events_result = (
            service.events()
            .list(
                calendarId='primary',
                timeMin=now.isoformat(),
                timeMax=until.isoformat(),
                singleEvents=True,
                orderBy='startTime',
            )
            .execute()
        )
        events = events_result.get('items', [])

        for event in events:
            if event['status'] != 'confirmed':
                continue

            if 'dateTime' not in event['start']:
                continue

            start = parse_date(event['start']['dateTime'])  # assume UTC
            if 'timeZone' in event['start']:
                start = start.astimezone(
                    pytz.timezone(event['start']['timeZone'])
                ).astimezone(pytz.utc)

            if now <= start <= until:
                return Event(
                    name=event['summary'],
                    start_time_utc=start,
                )

        return None

    def _fetch_next_event_from_ics_url(
        self, url: str, now: datetime, until: datetime
    ) -> Event | None:
        response = requests.get(url)
        calendar = IcsCalendar.from_ical(response.content)
        events = self._find_events_in_ics_calendar(calendar, now, until)
        if events:
            return events[0]

        return None

    def _find_events_in_ics_calendar(
        self, calendar: IcsCalendar, now: datetime, until: datetime
    ) -> list[Event]:
        """This function takes a calendar object, a start time, and an end time, and returns a list of events that are starting in the given period of time."""
        events = []
        for component in calendar.walk():
            if component.name == "VEVENT":
                start = self._to_utc_datetime(component.get('dtstart').dt)
                if now <= start <= until:
                    event = Event(
                        name=component.get('summary'),
                        start_time_utc=start,
                    )
                    events.append(event)
        return events

    def _to_utc_datetime(self, dt) -> datetime:
        # Ensure start is a datetime object
        if isinstance(dt, date) and not isinstance(dt, datetime):
            dt = datetime.combine(dt, datetime.min.time(), tzinfo=pytz.utc)

        # Ensure datetime objects are timezone-aware and convert to UTC
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        else:
            dt = dt.astimezone(pytz.utc)

        return dt
