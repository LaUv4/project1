import sqlite3
import os

class HospitalSystem:
    def __init__(self):
        self.db_path = "database/hospital.db"
        self.medications_list = [
            "Парацетамол - Обезболивающее, жаропонижающее",
            "Ибупрофен - Противовоспалительное",
            "Аспирин - Антибиотик",
            "Анальгин - Обезболивающий",
            "Снупп - Капли в нос",
            "Отривин - Капли в нос",
            "Терафлю - Жаропонижающее",
            "Стрепсилс - Таблетки от кашля"
        ]

    def get_connection(self):
        print(f"Trying to connect to: {self.db_path}")
        print(f"File exists: {os.path.exists(self.db_path)}")


        if not os.path.exists(self.db_path):
            print(f"Current directory: {os.getcwd()}")

        return sqlite3.connect(self.db_path)

    def add_doctor_1(self):
        print("\nДОБАВЛЕНИЕ ВРАЧА ТИП 1")
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO Doctor_1 (Surname, Name, Patronymic, Password) 
            VALUES ("Андрей", "Антибиотиков", "Андреевич", "111222")
        ''')

        conn.commit()
        print("Врач типа 1 добавлен!")
        conn.close()

    def add_doctor_2(self):
        print("\nДОБАВЛЕНИЕ ВРАЧА ТИП 2")
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO Doctor_2 (Surname, Name, Patronymic, Password)
            VALUES ("Виталий", "Вируснов", "Витальевич", "222111")
        ''')

        conn.commit()
        print("Врач типа 2 добавлен!")
        conn.close()

    def show_doctors(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        print("\nВРАЧИ ТИП 1:")
        cursor.execute("SELECT * FROM Doctor_1")
        doctors = cursor.fetchall()
        for doctor in doctors:
            print(f"ID: {doctor[0]}, {doctor[1]} {doctor[2]} {doctor[3]}")

        print("\nВРАЧИ ТИП 2:")
        cursor.execute("SELECT * FROM Doctor_2")
        doctors = cursor.fetchall()
        for doctor in doctors:
            print(f"ID: {doctor[0]}, {doctor[1]} {doctor[2]} {doctor[3]}")

        conn.close()

    def add_patient(self):
        print("\nДОБАВЛЕНИЕ ПАЦИЕНТА")
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO Patient (Surname, Name, Patronymic)
            VALUES 
            ("Белкин", "Дмитрий", "Дмитриевич"),
            ("Волков", "Андрей", "Владимирович"),
            ("Котов", "Владислав", "Владиславович"),
            ("Медведев", "Михаил", "Михайлович"),
            ("Стрелкин", "Николай", "Николаевич"),
            ("Петров", "Антон", "Антонович"),
            ("Соколов", "Олег", "Олегович")
        ''')

        conn.commit()
        print("Пациенты добавлены!")
        conn.close()

    def show_patients(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        print("\nПАЦИЕНТЫ:")
        cursor.execute("SELECT * FROM Patient")
        patients = cursor.fetchall()
        for patient in patients:
            print(f"ID: {patient[0]}, {patient[1]} {patient[2]} {patient[3]}")

        conn.close()

    def add_medical_card(self):
        print("\nДОБАВЛЕНИЕ МЕДИЦИНСКОЙ КАРТЫ")
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO Medical_card (Patient_ID, Health_complaints, Medical_history)
            VALUES 
            (1, "Головная боль, кашель, температура", "Ранее болел ОРВ и простой простудой"),
            (2, "Кашель, высокая температура", "Ранее болел простой простудой"),
            (3, "Озноб, головная боль, головокружение", "Ранее болел ОРВ"),
            (4, "Насморк, красное горло, кашель", "Ранее болел ангиной"),
            (5, "Насморк, головная боль, головокружение", "Ранее ничем не болел"),
            (6, "Кашель, озноб", "Ранее болел простой простудой"),
            (7, "Кашель, насморк, головная боль, красное горло", "Ранее болел ОРВ и простой простудой")
        ''')

        conn.commit()
        print("Медицинские карты добавлены!")
        conn.close()

    def show_medical_cards(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        print("\nМЕДИЦИНСКИЕ КАРТЫ:")
        cursor.execute('''
            SELECT p.Patient_ID, p.Surname, p.Name, p.Patronymic, 
                   m.Health_complaints, m.Medical_history
            FROM Patient p
            JOIN Medical_card m ON p.Patient_ID = m.Patient_ID
        ''')
        cards = cursor.fetchall()

        for card in cards:
            print(f"\nПациент: {card[1]} {card[2]} {card[3]} (ID: {card[0]})")
            print(f"Жалобы: {card[4]}")
            print(f"История: {card[5]}")

        conn.close()

    def show_medications_menu(self):
        print("\nВЫБЕРИТЕ ЛЕКАРСТВО ИЗ СПИСКА:")
        print("=" * 50)
        for i, med in enumerate(self.medications_list, 1):
            print(f"{i}. {med}")
        print("=" * 50)

    def add_medication(self):
        print("\nДОБАВЛЕНИЕ ЛЕКАРСТВА")
        self.show_medications_menu()

        choice = input("Выберите номер лекарства: ")

        try:
            index = int(choice) - 1
            if 0 <= index < len(self.medications_list):
                med_info = self.medications_list[index].split(" - ")
                name = med_info[0]
                default_usage = med_info[1] if len(med_info) > 1 else "Стандартное применение"

                usage = input(f"Способ применения для {name} (Enter для '{default_usage}'): ")
                if not usage:
                    usage = default_usage

                conn = self.get_connection()
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO Medication (Name_of_the_drug, Usage_record)
                    VALUES (?, ?)
                ''', (name, usage))

                drug_id = cursor.lastrowid
                conn.commit()
                print(f"Лекарство '{name}' добавлено! ID: {drug_id}")
                conn.close()
            else:
                print("Неверный номер!")
        except ValueError:
            print("Введите число!")

    def show_medications(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        print("\nЛЕКАРСТВА В БАЗЕ:")
        cursor.execute("SELECT * FROM Medication")
        meds = cursor.fetchall()

        if not meds:
            print("Лекарств пока нет")
            return

        for med in meds:
            print(f"ID: {med[0]}, {med[1]} - {med[2]}")

        conn.close()

def main_menu():
    system = HospitalSystem()

    while True:
        print("\n" + "=" * 50)
        print("СИСТЕМА УПРАВЛЕНИЯ БОЛЬНИЦЕЙ")
        print("=" * 50)
        print("ДОКТОРА:")
        print("1. Добавить врача типа 1")
        print("2. Добавить врача типа 2")
        print("3. Показать всех врачей")
        print("ПАЦИЕНТЫ:")
        print("4. Добавить пациента")
        print("5. Показать всех пациентов")
        print("МЕДКАРТЫ:")
        print("6. Добавить медицинскую карту")
        print("7. Показать все медицинские карты")
        print("ЛЕКАРСТВА:")
        print("8. Добавить лекарство (выбор из списка)")
        print("9. Показать все лекарства в базе")
        print("10. Показать список доступных лекарств")
        print("0. Выход")
        print("=" * 50)

        choice = input("Выберите действие: ")

        actions = {
            '1': system.add_doctor_1,
            '2': system.add_doctor_2,
            '3': system.show_doctors,
            '4': system.add_patient,
            '5': system.show_patients,
            '6': system.add_medical_card,
            '7': system.show_medical_cards,
            '8': system.add_medication,
            '9': system.show_medications,
            '10': system.show_medications_menu
        }

        if choice == '0':
            print("Выход из системы...")
            break
        elif choice in actions:
            actions[choice]()
        else:
            print("Неверный выбор!")

if __name__ == "__main__":
    main_menu()