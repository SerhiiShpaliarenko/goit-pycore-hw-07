from collections import UserDict, defaultdict
from datetime import datetime, timedelta

# --- Блок 1: Класи для даних (з минулого завдання + Birthday) ---

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
            # Перевіряємо формат DD.MM.YYYY та перетворюємо на об'єкт datetime.date
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    
    def __str__(self):
        # Повертаємо дату у гарному форматі
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
            # Знаходимо індекс старого телефону і замінюємо його
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
        """
        Повертає список користувачів, яких треба привітати 
        протягом наступних 7 днів.
        """
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_date = record.birthday.value # Це вже об'єкт date
                
                # Визначаємо дату дня народження в поточному році
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    # Якщо день народження вже пройшов, дивимось на наступний рік
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                # Різниця в днях
                delta_days = (birthday_this_year - today).days

                # Перевіряємо, чи день народження протягом наступних 7 днів
                if 0 <= delta_days < 7:
                    congrats_date = birthday_this_year
                    
                    # Перенос, якщо випадає на вихідний
                    if congrats_date.weekday() == 5: # Субота
                        congrats_date += timedelta(days=2)
                    elif congrats_date.weekday() == 6: # Неділя
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
            # Ловить помилки валідації Phone та Birthday
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            # Ловить помилки, коли не вистачає аргументів
            return "Not enough arguments. Please provide full info."
    return inner

# --- Блок 3: Функції-обробники команд ---

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_contact(args, book: AddressBook):
    if len(args) != 2:
        return "Invalid command. Usage: add [name] [phone(10 digits)]"
    
    name, phone = args
    record = book.find(name)
    
    if not record:
        # Якщо контакту немає, створюємо новий
        record = Record(name)
        book.add_record(record)
    
    # Додаємо телефон (з валідацією всередині)
    record.add_phone(phone)
    return "Contact added."

@input_error
def change_contact(args, book: AddressBook):
    # Змінюємо номер, припускаючи, що користувач знає старий
    # Якщо ви хочете просто перезаписати - логіка буде іншою
    if len(args) != 3:
        return "Invalid command. Usage: change [name] [old phone] [new phone]"
    
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError # "Contact not found."
    
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."

@input_error
def show_phone(args, book: AddressBook):
    if len(args) != 1:
        return "Invalid command. Usage: phone [name]"
    
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError # "Contact not found."
    
    # Показуємо всі телефони
    return '; '.join(p.value for p in record.phones)

def show_all(book: AddressBook):
    if not book.data:
        return "Address book is empty."
    
    return '\n'.join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    if len(args) != 2:
        return "Invalid command. Usage: add-birthday [name] [DD.MM.YYYY]"
    
    name, bday_str = args
    record = book.find(name)
    if not record:
        raise KeyError # "Contact not found."
    
    record.add_birthday(bday_str)
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        return "Invalid command. Usage: show-birthday [name]"
    
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    
    if not record.birthday:
        return "Birthday not set for this contact."
        
    return str(record.birthday)

def get_birthdays(book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next week."
    
    # Форматуємо гарний вивід
    return '\n'.join([f"{item['name']} - {item['congratulation_date']}" for item in upcoming])

# --- Блок 4: Головний цикл програми ---

def main():
    # Замість словника 'contacts' тепер 'book'
    book = AddressBook()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        
        if not user_input:
            print("Invalid command.")
            continue
            
        try:
            command, args = parse_input(user_input)
        except ValueError:
            print("Invalid command.")
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
            print(get_birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
