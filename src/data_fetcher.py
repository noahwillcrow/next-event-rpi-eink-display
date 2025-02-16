import pytz
import requests
from datetime import date, datetime, timedelta
from icalendar import Calendar


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

        for url in self._config['events']['ics-urls']:
            response = requests.get(url)
            calendar = Calendar.from_ical(response.content)
            events = self._find_events_in_calendar(calendar, now, until)

            for event in events:
                if (
                    next_event is None
                    or event.time_until_event < next_event.time_until_event
                ):
                    next_event = event

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

    def _find_events_in_calendar(
        self, calendar: Calendar, now: datetime, until: datetime
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
