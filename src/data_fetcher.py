import pytz
import requests
import yaml
from datetime import date, datetime, timedelta
from icalendar import Calendar


class Event:
    """This is meant to be a data structure that holds the information of an event."""

    def __init__(self, name, start_time_utc):
        self.name = name
        self.start_time_utc = start_time_utc

    def __str__(self):
        return f"{self.name} at {self.start_time_utc}"


class DataFetcher:
    """This module is responsible for reading the config yaml file, parsing the list of ICS URLs, and fetching the data from the URLs."""

    def __init__(self, config_path: str):
        self._config_path = config_path

    def fetch_upcoming_events(self) -> list[Event]:
        """This function reads the config yaml file to get the list of ICS URLs, fetches the data from the URLs, and returns a list of events that are happening in the next given period of time."""
        with open(self._config_path, 'r') as file:
            config = yaml.safe_load(file)

        events = []
        now = datetime.now().astimezone(pytz.utc)
        until = now + self._get_lookahead_period()

        for url in config['ics-urls']:
            response = requests.get(url)
            calendar = Calendar.from_ical(response.content)
            events.extend(self._find_events_in_calendar(calendar, now, until))

        return events

    def _get_lookahead_period(self) -> timedelta:
        """This function reads the config yamle file to get the `look-ahead`, which is a string in the format of {days}.{hours}:{minutes}:{seconds}.{milliseconds}, and returns a timedelta object."""
        config = self._load_config_yaml()
        lookahead = config['look-ahead']
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

    def _load_config_yaml(self) -> dict:
        """This function reads the config yaml file and returns the content as a dictionary."""
        with open(self._config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config

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
