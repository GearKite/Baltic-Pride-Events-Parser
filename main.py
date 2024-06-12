from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import ics
from bs4 import BeautifulSoup
from dataclasses_json import DataClassJsonMixin

TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo


@dataclass
class Event(DataClassJsonMixin):
    title: str
    location: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    link: Optional[str] = None


def is_date_div(block):
    return block.select_one("div > div.e-con-inner") is None


def parse_date_div(block):
    text = block.select_one("h2").text
    text = text.split("-")[0].strip()

    try:
        date = datetime.strptime(text, "%d %B")
    except ValueError:
        date = datetime.strptime(text, "%d.%m.")

    date = date.replace(year=datetime.now().year)

    return date


def parse_events_block(block, date: datetime):
    block_events = block.select("div.e-con-inner > div")
    events = []
    for event_block in block_events:
        try:
            event = parse_event(event_block, date)
        except Exception as e:
            print(f"Unable to parse event: {event_block}")
            print(f"Error: {e}")
        if event is None:
            continue
        events.append(event)

    return events


def parse_event(event, date: datetime):
    title_html = event.select_one("h2")
    content_html = event.select('div[data-widget_type="text-editor.default"]')
    if title_html is None or content_html is None:
        return

    title = title_html.text.strip()
    location = content_html[0].text.strip()
    time_str = content_html[1].text.strip()
    try:
        description = content_html[2].text.strip()
    except IndexError:
        description = ""
    try:
        link = event.select_one("a")["href"]
    except TypeError:
        link = ""

    start_time, end_time = parse_time(time_str, date)
    print(start_time, time_str)

    return Event(title, location, start_time, end_time, description, link)


def parse_time(time_str: str, date: datetime):
    time_split = time_str.split("-")
    start_time = datetime.strptime(time_split[0], "%H:%M")

    if len(time_split) > 1:
        end_time = datetime.strptime(time_split[1], "%H:%M")
    else:
        # Make event 1 hour long by default
        end_time = start_time + timedelta(hours=1)

    start_time = datetime.combine(date, start_time.time(), TIMEZONE)
    end_time = datetime.combine(date, end_time.time(), TIMEZONE)

    # Fix events that go past midnight
    if end_time < start_time:
        end_time += timedelta(days=1)

    return start_time, end_time


def parse_events(page) -> list[Event]:
    events = []
    current_date = None
    for block in page.select(
        'div[data-elementor-type="wp-page"] > div > div.e-con-inner'
    ):
        if is_date_div(block):
            current_date = parse_date_div(block)
            continue

        events += parse_events_block(block, current_date)

    return events


def main():
    with open("events.html", encoding="utf-8") as fp:
        soup = BeautifulSoup(fp, features="html5lib")

    events = parse_events(soup)

    c = ics.Calendar()

    for event in events:
        e = ics.Event(
            name=event.title,
            begin=event.start_time,
            end=event.end_time,
            description=event.description + "\n" + event.link,
            location=event.location,
        )
        c.events.add(e)

    with open("events.ics", "w+", encoding="utf-8") as fp:
        fp.writelines(c.serialize_iter())


main()
