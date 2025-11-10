import sqlite3
import os


class HospitalSystem:
    def __init__(self):
        self.db_path = "database/hospital.db"
        self.current_doctor_id = None
        self.current_patient_id = None
        self.create_doctors_if_not_exist()

    def get_connection(self):
        """Создает соединение с базой данных"""
        try:
            db_dir = os.path.dirname(self.db_path)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            return sqlite3.connect(self.db_path)
        except Exception as e:
            print(f"Ошибка подключения к базе: {e}")
            return None

    def create_doctors_if_not_exist(self):
        """Создает врачей если они не существуют"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS doctors
                           (
                               doctor_id
                               INTEGER
                               PRIMARY
                               KEY,
                               surname
                               TEXT
                               NOT
                               NULL,
                               name
                               TEXT
                               NOT
                               NULL,
                               patronymic
                               TEXT
                               NOT
                               NULL,
                               password
                               TEXT
                               NOT
                               NULL
                           )
                           ''')

            # Удаляем врачей с ID 5 и 6 если они существуют
            cursor.execute('DELETE FROM doctors WHERE doctor_id IN (5, 6)')

            # Добавляем только врачей с ID 111 и 222
            doctors = [
                ('111', 'Антибиотиков', 'Андрей', 'Андреевич', 'doctor111'),
                ('222', 'Вируснов', 'Виталий', 'Витальевич', 'doctor222')
            ]

            for doctor in doctors:
                cursor.execute('SELECT * FROM doctors WHERE doctor_id = ?', (doctor[0],))
                if not cursor.fetchone():
                    cursor.execute('''
                                   INSERT INTO doctors (doctor_id, surname, name, patronymic, password)
                                   VALUES (?, ?, ?, ?, ?)
                                   ''', doctor)

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            print(f"Ошибка создания врачей: {e}")

    def fix_all_doctors_patients(self):
        """Полностью исправляет привязку пациентов ко всем врачам"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS patients
                           (
                               patient_id
                               INTEGER
                               PRIMARY
                               KEY,
                               surname
                               TEXT
                               NOT
                               NULL,
                               name
                               TEXT
                               NOT
                               NULL,
                               patronymic
                               TEXT
                               NOT
                               NULL,
                               doctor_id
                               INTEGER,
                               FOREIGN
                               KEY
                           (
                               doctor_id
                           ) REFERENCES doctors
                           (
                               doctor_id
                           )
                               )
                           ''')

            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS medical_cards
                           (
                               patient_id
                               INTEGER
                               PRIMARY
                               KEY,
                               health_complaints
                               TEXT,
                               medical_history
                               TEXT,
                               FOREIGN
                               KEY
                           (
                               patient_id
                           ) REFERENCES patients
                           (
                               patient_id
                           )
                               )
                           ''')

            cursor.execute("DELETE FROM patients")
            cursor.execute("DELETE FROM medical_cards")

            # Теперь привязываем пациентов к врачам с ID 111 и 222
            patients = [
                ('1', 'Белкин', 'Дмитрий', 'Дмитриевич', '111'),
                ('2', 'Волков', 'Андрей', 'Владимирович', '111'),
                ('3', 'Котов', 'Владислав', 'Владиславович', '111'),
                ('7', 'Соколов', 'Олег', 'Олегович', '111'),
                ('4', 'Медведев', 'Михаил', 'Михайлович', '222'),
                ('5', 'Стрелкин', 'Николай', 'Николаевич', '222'),
                ('6', 'Петров', 'Антон', 'Антонович', '222')
            ]

            cursor.executemany('''
                               INSERT INTO patients (patient_id, surname, name, patronymic, doctor_id)
                               VALUES (?, ?, ?, ?, ?)
                               ''', patients)

            medical_cards = [
                ('1', 'Головная боль, кашель, температура', 'Ранее болел ОРВИ и простой простудой'),
                ('2', 'Кашель, высокая температура', 'Ранее болел простой простудой'),
                ('3', 'Озноб, головная боль, головокружение', 'Ранее болел ОРВИ'),
                ('4', 'Насморк, красное горло, кашель', 'Ранее болел ангиной'),
                ('5', 'Насморк, головная боль, головокружение', 'Ранее ничем не болел'),
                ('6', 'Кашель, озноб', 'Ранее болел простой простудой'),
                ('7', 'Кашель, насморк, головная боль, красное горло', 'Ранее болел ОРВИ и простой простудой')
            ]

            cursor.executemany('''
                               INSERT INTO medical_cards (patient_id, health_complaints, medical_history)
                               VALUES (?, ?, ?)
                               ''', medical_cards)

            conn.commit()

            cursor.execute('''
                           SELECT p.patient_id, p.surname, p.name, p.doctor_id, d.surname, d.name, d.patronymic
                           FROM patients p
                                    LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
                           ORDER BY p.patient_id
                           ''')
            patients_check = cursor.fetchall()

            print("Распределение пациентов после исправления:")
            for patient in patients_check:
                if patient[4]:
                    print(
                        f"Пациент ID:{patient[0]} {patient[1]} {patient[2]} -> Врач ID:{patient[3]} {patient[4]} {patient[5]} {patient[6]}")
                else:
                    print(f"Пациент ID:{patient[0]} {patient[1]} {patient[2]} -> Врач ID:{patient[3]} (врач не найден)")

            conn.close()
            print("Все пациенты распределены между врачами!")

        except sqlite3.Error as e:
            print(f"Ошибка исправления пациентов: {e}")

    def doctor_login(self):
        """Авторизация врача"""
        try:
            print("\nДоступные врачи:")
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT doctor_id, surname, name, patronymic FROM doctors')
            doctors = cursor.fetchall()
            for doctor in doctors:
                print(f"ID: {doctor[0]}, {doctor[1]} {doctor[2]} {doctor[3]}")
            conn.close()

            doctor_id = input("\nВведите ID врача: ")
            password = input("Введите пароль: ")

            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM doctors WHERE doctor_id = ?', (doctor_id,))
            doctor = cursor.fetchone()
            conn.close()

            if not doctor:
                print("Врач с таким ID не найден!")
                return False

            if password == doctor[4]:
                self.current_doctor_id = doctor[0]
                print(f"Добро пожаловать, {doctor[1]} {doctor[2]} {doctor[3]}!")
                self.show_doctor_patients()
                return True
            else:
                print("Неверный пароль!")
                return False

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
            return False

    def show_doctor_patients(self):
        """Показывает пациентов текущего врача"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                           SELECT patient_id, surname, name, patronymic
                           FROM patients
                           WHERE doctor_id = ?
                           ORDER BY patient_id
                           ''', (self.current_doctor_id,))

            patients = cursor.fetchall()

            print("\n" + "=" * 40)
            print("ВАШИ ПАЦИЕНТЫ:")
            print("=" * 40)
            if patients:
                for patient in patients:
                    print(f"ID: {patient[0]}, {patient[1]} {patient[2]} {patient[3]}")
            else:
                print("У вас пока нет пациентов")

            conn.close()
            return patients

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
            return []

    def get_patient_medical_info_by_id(self, patient_id):
        """Просмотр медкарты пациента по ID (для врачей)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT doctor_id FROM patients WHERE patient_id = ?', (patient_id,))
            patient_doctor = cursor.fetchone()

            if not patient_doctor:
                print("Пациент не найден!")
                conn.close()
                return

            if str(patient_doctor[0]) != str(self.current_doctor_id):
                print("Это не ваш пациент!")
                conn.close()
                return

            cursor.execute('''
                           SELECT p.surname,
                                  p.name,
                                  p.patronymic,
                                  mc.health_complaints,
                                  mc.medical_history
                           FROM patients p
                                    LEFT JOIN medical_cards mc ON p.patient_id = mc.patient_id
                           WHERE p.patient_id = ?
                           ''', (patient_id,))

            patient_info = cursor.fetchone()

            if not patient_info:
                print("Медкарта пациента не найдена!")
                return

            print(f"\n" + "=" * 50)
            print("МЕДИЦИНСКАЯ КАРТА ПАЦИЕНТА:")
            print("=" * 50)
            print(f"Пациент: {patient_info[0]} {patient_info[1]} {patient_info[2]}")
            print(f"Жалобы: {patient_info[3]}")
            print(f"История болезни: {patient_info[4]}")

            cursor.execute('''
                           SELECT m.medication_name, m.usage_description
                           FROM medications m
                                    JOIN medication_intake mi ON m.medication_id = mi.medication_id
                                    JOIN appointments a ON mi.appointment_id = a.appointment_id
                           WHERE a.patient_id = ?
                           ''', (patient_id,))

            medications = cursor.fetchall()
            if medications:
                print("\nНазначенные лекарства:")
                for med in medications:
                    print(f"  - {med[0]} ({med[1]})")

            print("=" * 50)
            conn.close()

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def patient_login(self):
        """Авторизация пациента"""
        try:
            patient_id = input("Введите ID пациента: ")

            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
            patient = cursor.fetchone()
            conn.close()

            if not patient:
                print("Пациент с таким ID не найден!")
                return False

            self.current_patient_id = patient[0]
            print(f"Добро пожаловать, {patient[1]} {patient[2]} {patient[3]}!")
            self.show_patient_medical_info()
            return True

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
            return False

    def show_patient_medical_info(self):
        """Показывает медицинскую карту пациента"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                           SELECT p.surname,
                                  p.name,
                                  p.patronymic,
                                  mc.health_complaints,
                                  mc.medical_history
                           FROM patients p
                                    LEFT JOIN medical_cards mc ON p.patient_id = mc.patient_id
                           WHERE p.patient_id = ?
                           ''', (self.current_patient_id,))

            patient_info = cursor.fetchone()

            print("\n" + "=" * 50)
            print("ВАША МЕДИЦИНСКАЯ КАРТА")
            print("=" * 50)
            print(f"Пациент: {patient_info[0]} {patient_info[1]} {patient_info[2]}")
            print(f"Жалобы: {patient_info[3]}")
            print(f"История болезни: {patient_info[4]}")

            cursor.execute('''
                           SELECT d.surname, d.name, d.patronymic
                           FROM doctors d
                                    JOIN patients p ON d.doctor_id = p.doctor_id
                           WHERE p.patient_id = ?
                           ''', (self.current_patient_id,))

            doctor = cursor.fetchone()
            if doctor:
                print(f"Лечащий врач: {doctor[0]} {doctor[1]} {doctor[2]}")

            cursor.execute('''
                           SELECT m.medication_name, m.usage_description
                           FROM medications m
                                    JOIN medication_intake mi ON m.medication_id = mi.medication_id
                                    JOIN appointments a ON mi.appointment_id = a.appointment_id
                           WHERE a.patient_id = ?
                           ''', (self.current_patient_id,))

            medications = cursor.fetchall()
            if medications:
                print("\nНазначенные лекарства:")
                for med in medications:
                    print(f"  - {med[0]} ({med[1]})")

            print("=" * 50)
            conn.close()

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")


def main():
    system = HospitalSystem()

    while True:
        print("\n" + "=" * 40)
        print("СИСТЕМА БОЛЬНИЦЫ")
        print("=" * 40)
        print("1. Вход врача")
        print("2. Вход пациента")
        print("3. Просмотр медкарты пациента")
        print("4. РАСПРЕДЕЛИТЬ пациентов между всеми врачами")
        print("5. Выход")

        if system.current_doctor_id:
            conn = system.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT surname, name FROM doctors WHERE doctor_id = ?', (system.current_doctor_id,))
            doctor = cursor.fetchone()
            conn.close()
            if doctor:
                print(f"Врач: {doctor[0]} {doctor[1]}")
        elif system.current_patient_id:
            print(f"Пациент: ID {system.current_patient_id}")

        choice = input("Выберите действие: ")

        if choice == '1':
            system.doctor_login()
        elif choice == '2':
            system.patient_login()
        elif choice == '3':
            if system.current_doctor_id:
                patient_id = input("Введите ID пациента для просмотра медкарты: ")
                system.get_patient_medical_info_by_id(patient_id)
            else:
                print("Доступно только врачам!")
        elif choice == '4':
            system.fix_all_doctors_patients()
        elif choice == '5':
            print("Выход из системы")
            break
        else:
            print("Неверный выбор!")


if __name__ == "__main__":
    main()