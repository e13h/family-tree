import json
from datetime import datetime
from attrs import define, field

from ics import Calendar, Event
import phonenumbers
import networkx as nx


def normalize_phone_number(input: str, region: str = "US") -> str:
    if input is None:
        return None
    return phonenumbers.format_number(
        phonenumbers.parse(input, region),
        phonenumbers.PhoneNumberFormat.NATIONAL)

def convert_date(input: str) -> datetime | None:
    if input is None:
        return None
    return datetime.strptime(input, "%Y-%m-%d")


@define(frozen=True)
class Person:
    first_name: str
    last_name: str
    birthday: datetime = field(converter=convert_date)
    anniversary: datetime = field(default=None, converter=convert_date)
    phone: str = field(default=None, converter=lambda phone: normalize_phone_number(phone))
    email: str = None
    nickname: str = None


def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix


def load_from_file(filepath: str) -> list[Person]:
    with open(filepath, "rb") as file:
        people = json.load(file)
    return [Person(**person) for person in people]


def generate_birthday_events(person: Person, num_years: int = 110) -> list[Event]:
    events = []
    year = person.birthday.year
    description = f"""
{person.first_name} {person.last_name} was born on {person.birthday.strftime("%B %d, %Y")}.

Contact info:
    {person.nickname if person.nickname else person.first_name}:
    📱 {person.phone}
    📧 {person.email}
    """.strip()
    print(description)
    for i in range(num_years):
        tag = f"{ordinal(i)} " if i > 0 else ""
        title = f"{person.nickname if person.nickname else person.first_name}'s {tag}Birthday"
        date = f"{year + i}-{person.birthday.month}-{person.birthday.day}"
        e = Event(name=title, begin=date, description=description)
        e.make_all_day()
        events.append(e)
    return events


def main():
    people = load_from_file("small_family.json")
    graph = nx.Graph()
    graph.add_nodes_from(people)
    print(people)
    events = []
    for person in people:
        events.extend(generate_birthday_events(person))
    cal = Calendar(events=events)
    with open("test.ics", "w", encoding="utf-8") as f:
        f.writelines(cal.serialize_iter())


if __name__ == "__main__":
    main()
