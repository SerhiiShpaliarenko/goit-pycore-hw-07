from collections import UserDict, defaultdict
from datetime import datetime, timedelta

# --- Блок 1: Класи для даних (з валідацією) ---

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not (len(value) == 10 and value.isdigit()):
            raise ValueError("Invalid phone number: must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    
    def __str__(self):
        return self.value.strftime('%d.%m.%Y')

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_str):
        self.phones.append(Phone(phone_str))

    def remove_phone(self, phone_str):
        phone_obj = self.find_phone(phone_str)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError("Phone not found.")

    def edit_phone(self, old_phone_str, new_phone_str):
        old_phone_obj = self.find_phone(old_phone_str)
        if old_phone_obj:
            index = self.phones.index(old_phone_obj)
            self.phones[index] = Phone(new_phone_str)
        else:
            raise ValueError("Old phone not found.")

    def find_phone(self, phone_str):
        for phone in self.phones:
            if phone.value == phone_str:
                return phone
        return None

    def add_birthday(self, birthday_str):
        self.birthday = Birthday(birthday_str)

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str) -> Record:
        return self.data.get(name)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError("Contact not found.")

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                birthday_date = record.birthday.value
                birthday_this_year = birthday_date.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                delta_days = (birthday_this_year - today).days
                if 0 <= delta_days < 7:
                    congrats_date = birthday_this_year
                    if congrats_date.weekday() == 5:
                        congrats_date += timedelta(days=2)
                    elif congrats_date.weekday() == 6:
                        congrats_date += timedelta(days=1)
                    
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": congrats_date.strftime("%d.%m.%Y")
                    })
        return upcoming_birthdays

# --- Блок 2: Декоратор помилок ---

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            # Обробка помилок валідації Phone/Birthday
            if "Invalid date format" in str(e) or "Invalid phone number" in str(e):
                return str(e)
            # Обробка помилок розпакування (недостатньо аргументів)
            return "Give me correct arguments please."
        except KeyError:
            return "Contact not found."
        except IndexError:
            # Обробка помилок, коли не ввели ім'я
            return "Enter user name."
    return inner

# --- Блок 3: Функції-обробники команд ---

def parse_input(user_input):
    # Додаємо перевірку на порожнє введення
    if not user_input:
        raise ValueError
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_contact(args, book: AddressBook):
    # Використовуємо реалізацію з вашого прикладу
    name, phone, *_ = args  # Розпакування підніме ValueError, якщо не вистачає
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        # Валідація телефону відбудеться при створенні Phone
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args # ValueError
    record = book.find(name)
    if record is None:
        raise KeyError # Contact not found
    
    # ValueError (phone format) або ValueError (not found)
    record.edit_phone(old_phone, new_phone) 
    return "Contact updated."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0] # IndexError
    record = book.find(name)
    if record is None:
        raise KeyError # Contact not found
    
    return '; '.join(p.value for p in record.phones)

def show_all(book: AddressBook):
    # Ця функція не може "впасти", тому декоратор не потрібен
    if not book.data:
        return "Address book is empty."
    return '\n'.join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    name, bday_str = args # ValueError
    record = book.find(name)
    if record is None:
        raise KeyError # Contact not found
    
    # ValueError (date format)
    record.add_birthday(bday_str) 
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0] # IndexError
    record = book.find(name)
    if record is None:
        raise KeyError # Contact not found
    
    if record.birthday:
        return str(record.birthday)
    else:
        return "Birthday not set for this contact."

@input_error
def birthdays(args, book: AddressBook):
    # 'args' тут не використовується, але ми його приймаємо
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next week."
    
    return '\n'.join([f"{item['name']} - {item['congratulation_date']}" for item in upcoming])

# --- Блок 4: Головний цикл програми (main) ---

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        
        try:
            command, args = parse_input(user_input)
        except ValueError:
            print("Invalid command. (empty input)")
            continue

        if command in ["close", "exit"]:
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
            print(birthdays(args, book)) # 'args' передається, хоч і не використовується

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
