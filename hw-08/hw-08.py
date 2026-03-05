from collections import UserDict
from datetime import datetime, timedelta
import pickle

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

# --------- МОДЕЛІ ---------
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            birthday = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(birthday)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError(f"Phone {old_phone} not found")

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else ""
        return f"{self.name.value}: phones [{phones}]" + (f", birthday: {birthday}" if birthday else "")


# --------- АДРЕСНА КНИГА ---------
class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []
        for record in self.data.values():
            if not record.birthday:
                continue
            bday = record.birthday.value.date()
            bday_this_year = bday.replace(year=today.year)
            if bday_this_year < today:
                bday_this_year = bday_this_year.replace(year=today.year + 1)
            delta = (bday_this_year - today).days
            if 0 <= delta <= 7:
                congrat_date = bday_this_year
                if congrat_date.weekday() == 5:
                    congrat_date += timedelta(days=2)
                elif congrat_date.weekday() == 6:
                    congrat_date += timedelta(days=1)
                upcoming.append({
                    "name": record.name.value,
                    "congratulation_date": congrat_date.strftime("%d.%m.%Y")
                })
        return upcoming


# --------- ДЕКОРАТОР ---------
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError) as e:
            return f"Error: {e}"
        except Exception:
            return "Something went wrong"
    return wrapper


# --------- ФУНКЦІЇ ---------
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if not record:
        return f"Contact {name} not found."
    record.edit_phone(old_phone, new_phone)
    return f"Phone updated for {name}."


@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if not record:
        return f"Contact {name} not found."
    if not record.phones:
        return f"No phones for {name}."
    return "; ".join(p.value for p in record.phones)


@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "Address book is empty."
    return "\n".join(str(r) for r in book.data.values())


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_str, *_ = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = f"Contact {name} added and birthday set."
    else:
        message = f"Birthday updated for {name}."
    record.add_birthday(birthday_str)
    return message


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if not record:
        return f"Contact {name} not found."
    if not record.birthday:
        return f"{name} has no birthday set."
    return f"{name}'s birthday is {record.birthday.value.strftime('%d.%m.%Y')}"


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next week."
    return "\n".join(f"{item['name']} — {item['congratulation_date']}" for item in upcoming)


# --------- MAIN ---------
def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            continue
        parts = user_input.strip().split()
        command, *args = parts

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()