import json
from datetime import datetime
from textwrap import indent

import matplotlib.pyplot as plt
import networkx as nx
import phonenumbers
from attrs import define, field
from ics import Calendar, Event


def normalize_phone_number(phone: str, region: str = "US") -> str:
    if phone is None:
        return None
    return phonenumbers.format_number(
        phonenumbers.parse(phone, region), phonenumbers.PhoneNumberFormat.NATIONAL
    )


def convert_date(date: str) -> datetime | None:
    if date is None:
        return None
    return datetime.strptime(date, "%Y-%m-%d")


@define(frozen=True)
class Person:
    id: str
    first_name: str
    last_name: str
    birthday: datetime = field(converter=convert_date)
    anniversary: datetime = field(default=None, converter=convert_date)
    phone: str = field(default=None, converter=normalize_phone_number)
    email: str = None
    nickname: str = field()
    parents: tuple[str] = field(default=tuple(), converter=tuple)

    @nickname.default
    def _first_name_is_nickname(self) -> str:
        return self.first_name

    def __repr__(self) -> str:
        return self.nickname


def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix


def load_from_file(filepath: str) -> dict[str, Person]:
    with open(filepath, "rb") as file:
        people = json.load(file)
    assert isinstance(people, list)
    return {person["id"]: Person(**person) for person in people}


def create_contact_info(person: Person) -> str:
    phone_contact = f"\n📱 {person.phone}" if person.phone else ""
    email_contact = f"\n📧 {person.email}" if person.email else ""
    if phone_contact or email_contact:
        contact_info = f"{person.nickname}:{phone_contact}{email_contact}"
        return contact_info
    return ""


def generate_birthday_events(
    person: Person, graph: nx.DiGraph = None, num_years: int = 110
) -> list[Event]:
    events = []
    year = person.birthday.year
    contact_info = create_contact_info(person)
    if contact_info == "" and graph is not None:
        contact_info = "\n".join(
            [create_contact_info(parent) for _, parent in graph.out_edges(person)]
        ).strip()
    if contact_info != "":
        contact_info = "\n\nContact info:\n" + indent(contact_info, "    ")
    bday_formatted = person.birthday.strftime("%B %d, %Y")
    description = (
        f"{person.first_name} {person.last_name} was born on {bday_formatted}."
        + contact_info
    )
    for i in range(num_years):
        tag = f"{ordinal(i)} " if i > 0 else ""
        title = f"{person.nickname}'s {tag}Birthday"
        date = f"{year + i}-{person.birthday.month}-{person.birthday.day}"
        e = Event(name=title, begin=date, description=description)
        e.make_all_day()
        events.append(e)
    return events


def main():
    people = load_from_file("small_family.json")
    graph = nx.DiGraph()
    graph.add_nodes_from(people.values())
    for person in people.values():
        for parent_id in person.parents:
            if parent_id in people:
                graph.add_edge(person, people[parent_id])
    nx.draw(graph, with_labels=True)
    plt.show()
    events = []
    for person in graph:
        events.extend(generate_birthday_events(person, graph))
    cal = Calendar(events=events)
    with open("test.ics", "w", encoding="utf-8") as f:
        f.writelines(cal.serialize_iter())


if __name__ == "__main__":
    main()
