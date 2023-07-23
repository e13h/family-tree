import json
from dataclasses import dataclass
from datetime import datetime

from ics import Calendar, Event


@dataclass
class Person:
    first_name: str
    last_name: str
    birthday: datetime
    anniversary: datetime = None

    def __init__(
        self, first_name: str, last_name: str, birthday: str, anniversary: str = None
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = datetime.strptime(birthday, "%Y-%m-%d")
        self.anniversary = (
            datetime.strptime(anniversary, "%Y-%m-%d") if anniversary else None
        )


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
    for i in range(num_years):
        tag = f"{ordinal(i)} " if i > 0 else ""
        title = f"{person.first_name}'s {tag}Birthday"
        date = f"{year + i}-{person.birthday.month}-{person.birthday.day}"
        e = Event(name=title, begin=date)
        e.make_all_day()
        events.append(e)
    return events


def main():
    people = load_from_file("small_family.json")
    print(people)
    events = []
    for person in people:
        events.extend(generate_birthday_events(person))
    cal = Calendar(events=events)
    with open("test.ics", "w", encoding="utf-8") as f:
        f.writelines(cal.serialize_iter())


if __name__ == "__main__":
    main()
