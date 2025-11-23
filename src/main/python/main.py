import sqlite3
import os
from datetime import datetime, time


class HospitalSystem:
    def __init__(self):
        self.db_path = "../database/hospital.db"
        self.current_doctor_id = None
        self.current_patient_id = None
        self.current_admin_id = None
        self.initialize_database()

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

    def initialize_database(self):
        """Инициализация базы данных с распределением пациентов"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Создание таблицы врачей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS doctors (
                    doctor_id INTEGER PRIMARY KEY,
                    surname TEXT NOT NULL,
                    name TEXT NOT NULL,
                    patronymic TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            ''')

            # Создание таблицы пациентов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id INTEGER PRIMARY KEY,
                    surname TEXT NOT NULL,
                    name TEXT NOT NULL,
                    patronymic TEXT NOT NULL,
                    doctor_id INTEGER,
                    FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
                )
            ''')

            # Создание таблицы медицинских карт
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS medical_cards (
                    patient_id INTEGER PRIMARY KEY,
                    health_complaints TEXT,
                    medical_history TEXT,
                    treatment_plan TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
                )
            ''')

            # Создание таблицы приемов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS appointments (
                    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    appointment_date TEXT NOT NULL,
                    appointment_time TEXT NOT NULL,
                    confirmed INTEGER DEFAULT 0,
                    FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
                )
            ''')

            # Создание таблицы лекарств
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS medications (
                    medication_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    medication_name TEXT NOT NULL,
                    usage_description TEXT,
                    is_taken INTEGER DEFAULT 0,
                    FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
                )
            ''')

            # Создание таблицы администраторов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS administrators (
                    admin_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            ''')

            # Очистка и добавление врачей
            cursor.execute('DELETE FROM doctors')
            doctors = [
                (111, 'Антибиотиков', 'Андрей', 'Андреевич', '111222'),
                (222, 'Вируснов', 'Виталий', 'Витальевич', '222111')
            ]
            cursor.executemany('''
                INSERT INTO doctors (doctor_id, surname, name, patronymic, password)
                VALUES (?, ?, ?, ?, ?)
            ''', doctors)

            # Очистка и добавление пациентов с распределением
            cursor.execute('DELETE FROM patients')
            patients = [
                (1, 'Белкин', 'Дмитрий', 'Дмитриевич', 111),
                (2, 'Волков', 'Андрей', 'Владимирович', 111),
                (3, 'Котов', 'Владислав', 'Владиславович', 111),
                (4, 'Медведев', 'Михаил', 'Михайлович', 222),
                (5, 'Стрелкин', 'Николай', 'Николаевич', 222),
                (6, 'Петров', 'Антон', 'Антонович', 222),
                (7, 'Соколов', 'Олег', 'Олегович', 222)
            ]
            cursor.executemany('''
                INSERT INTO patients (patient_id, surname, name, patronymic, doctor_id)
                VALUES (?, ?, ?, ?, ?)
            ''', patients)

            # Очистка и добавление медицинских карт
            cursor.execute('DELETE FROM medical_cards')
            medical_cards = [
                (1, 'Головная боль, кашель, температура', 'Ранее болел ОРВИ и простой простудой', ''),
                (2, 'Кашель, высокая температура', 'Ранее болел простой простудой', ''),
                (3, 'Озноб, головная боль, головокружение', 'Ранее болел ОРВИ', ''),
                (4, 'Насморк, красное горло, кашель', 'Ранее болел ангиной', ''),
                (5, 'Насморк, головная боль, головокружение', 'Ранее ничем не болел', ''),
                (6, 'Кашель, озноб', 'Ранее болел простой простудой', ''),
                (7, 'Кашель, насморк, головная боль, красное горло', 'Ранее болел ОРВИ и простой простудой', '')
            ]
            cursor.executemany('''
                INSERT INTO medical_cards (patient_id, health_complaints, medical_history, treatment_plan)
                VALUES (?, ?, ?, ?)
            ''', medical_cards)

            # Очистка и добавление приемов
            cursor.execute('DELETE FROM appointments')
            appointments = [
                (1, '2025-01-15', '10:00', 1),
                (2, '2025-01-16', '11:30', 1),
                (4, '2025-01-18', '09:00', 1),
                (6, '2025-01-20', '16:45', 1)
            ]
            cursor.executemany('''
                INSERT INTO appointments (patient_id, appointment_date, appointment_time, confirmed)
                VALUES (?, ?, ?, ?)
            ''', appointments)

            # Очистка и добавление препаратов (по одному на каждого пациента)
            cursor.execute('DELETE FROM medications')
            medications = [
                (1, 'Парацетамол', 'По 1 таблетке 3 раза в день после еды', 1),
                (2, 'Амоксиклав', 'По 1 таблетке 2 раза в день 7 дней', 0),
                (3, 'Ибупрофен', 'По 1 таблетке при температуре', 0),
                (4, 'Тантум Верде', 'По 1 впрыскиванию 3 раза в день', 1),
                (5, 'Називин', 'По 1 впрыскиванию в каждую ноздрю 2 раза в день', 0),
                (6, 'Арбидол', 'По 2 капсулы 4 раза в день', 0),
                (7, 'Стрепсилс', 'По 1 таблетке каждые 2-3 часа', 0)
            ]
            cursor.executemany('''
                INSERT INTO medications (patient_id, medication_name, usage_description, is_taken)
                VALUES (?, ?, ?, ?)
            ''', medications)

            # Очистка и добавление администраторов
            cursor.execute('DELETE FROM administrators')
            admins = [
                (1, 'admin', '123123')
            ]
            cursor.executemany('''
                INSERT INTO administrators (admin_id, username, password)
                VALUES (?, ?, ?)
            ''', admins)

            conn.commit()
            conn.close()
            print("База данных инициализирована с распределением пациентов!")

        except sqlite3.Error as e:
            print(f"Ошибка инициализации базы данных: {e}")

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
                return True
            else:
                print("Неверный пароль!")
                return False

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
            return False

    def show_doctor_menu(self):
        """Меню врача"""
        while True:
            print("\n" + "=" * 40)
            print("МЕНЮ ВРАЧА")
            print("=" * 40)
            print("1. Посмотреть моих пациентов")
            print("2. Выбрать пациента для работы")
            print("3. Выход")

            choice = input("Выберите действие: ")

            if choice == '1':
                self.show_doctor_patients()
            elif choice == '2':
                self.work_with_patient()
            elif choice == '3':
                self.current_doctor_id = None
                break
            else:
                print("Неверный выбор!")

    def show_doctor_patients(self):
        """Показывает пациентов текущего врача"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT p.patient_id, p.surname, p.name, p.patronymic, 
                       a.appointment_date, a.appointment_time, a.confirmed
                FROM patients p
                LEFT JOIN appointments a ON p.patient_id = a.patient_id
                WHERE p.doctor_id = ?
                ORDER BY p.patient_id
            ''', (self.current_doctor_id,))

            patients = cursor.fetchall()

            print("\n" + "=" * 50)
            print("ВАШИ ПАЦИЕНТЫ:")
            print("=" * 50)
            if patients:
                for patient in patients:
                    status = "Подтверждена" if patient[6] else "Не подтверждена"
                    appointment_info = f" - Запись: {patient[4]} {patient[5]} ({status})" if patient[
                        4] else " - Нет записи"
                    print(f"ID: {patient[0]}, {patient[1]} {patient[2]} {patient[3]}{appointment_info}")
            else:
                print("У вас пока нет пациентов")

            conn.close()
            return patients

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
            return []

    def work_with_patient(self):
        """Работа с конкретным пациентом"""
        patients = self.show_doctor_patients()
        if not patients:
            return

        try:
            patient_id = input("\nВведите ID пациента для работы: ")

            # Проверка, что пациент принадлежит врачу
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT doctor_id FROM patients WHERE patient_id = ?', (patient_id,))
            patient = cursor.fetchone()

            if not patient or str(patient[0]) != str(self.current_doctor_id):
                print("Это не ваш пациент!")
                conn.close()
                return

            conn.close()

            while True:
                print(f"\nРАБОТА С ПАЦИЕНТОМ ID: {patient_id}")
                print("1. Записать жалобы на здоровье")
                print("2. Назначить план лечения")
                print("3. Заполнить историю болезни")
                print("4. Просмотреть отмеченные препараты")
                print("5. Просмотреть медкарту пациента")
                print("6. Управление препаратами пациента")
                print("7. Назад")

                choice = input("Выберите действие: ")

                if choice == '1':
                    self.record_health_complaints(patient_id)
                elif choice == '2':
                    self.set_treatment_plan(patient_id)
                elif choice == '3':
                    self.record_medical_history(patient_id)
                elif choice == '4':
                    self.view_patient_medications(patient_id)
                elif choice == '5':
                    self.view_patient_medical_card(patient_id)
                elif choice == '6':
                    self.manage_patient_medications(patient_id)
                elif choice == '7':
                    break
                else:
                    print("Неверный выбор!")

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def manage_patient_medications(self, patient_id):
        """Управление препаратами пациента"""
        try:
            while True:
                print(f"\nУПРАВЛЕНИЕ ПРЕПАРАТАМИ ПАЦИЕНТА ID: {patient_id}")
                print("1. Добавить препарат")
                print("2. Изменить препарат")
                print("3. Удалить препарат")
                print("4. Назад")

                choice = input("Выберите действие: ")

                if choice == '1':
                    self.add_medication(patient_id)
                elif choice == '2':
                    self.edit_medication(patient_id)
                elif choice == '3':
                    self.delete_medication(patient_id)
                elif choice == '4':
                    break
                else:
                    print("Неверный выбор!")

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def add_medication(self, patient_id):
        """Добавление препарата пациенту"""
        try:
            medication_name = input("Введите название препарата: ")
            usage_description = input("Введите способ применения: ")

            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO medications (patient_id, medication_name, usage_description)
                VALUES (?, ?, ?)
            ''', (patient_id, medication_name, usage_description))
            conn.commit()
            conn.close()

            print("Препарат успешно добавлен!")

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def edit_medication(self, patient_id):
        """Изменение препарата пациента"""
        try:
            # Показываем текущие препараты
            self.view_patient_medications(patient_id)

            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT medication_id FROM medications WHERE patient_id = ?', (patient_id,))
            medications = cursor.fetchall()

            if not medications:
                print("У пациента нет препаратов для изменения!")
                conn.close()
                return

            try:
                medication_id = int(input("Введите ID препарата для изменения: "))

                # Проверяем, что препарат принадлежит пациенту
                cursor.execute('SELECT * FROM medications WHERE medication_id = ? AND patient_id = ?',
                               (medication_id, patient_id))
                medication = cursor.fetchone()

                if not medication:
                    print("Препарат не найден или не принадлежит пациенту!")
                    conn.close()
                    return

                new_name = input("Введите новое название препарата: ")
                new_usage = input("Введите новый способ применения: ")

                cursor.execute('''
                    UPDATE medications 
                    SET medication_name = ?, usage_description = ?
                    WHERE medication_id = ?
                ''', (new_name, new_usage, medication_id))

                conn.commit()
                print("Препарат успешно изменен!")

            except ValueError:
                print("Неверный ID препарата!")

            conn.close()

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def delete_medication(self, patient_id):
        """Удаление препарата пациента"""
        try:
            # Показываем текущие препараты
            self.view_patient_medications(patient_id)

            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT medication_id FROM medications WHERE patient_id = ?', (patient_id,))
            medications = cursor.fetchall()

            if not medications:
                print("У пациента нет препаратов для удаления!")
                conn.close()
                return

            try:
                medication_id = int(input("Введите ID препарата для удаления: "))

                # Проверяем, что препарат принадлежит пациенту
                cursor.execute('SELECT * FROM medications WHERE medication_id = ? AND patient_id = ?',
                               (medication_id, patient_id))
                medication = cursor.fetchone()

                if not medication:
                    print("Препарат не найден или не принадлежит пациенту!")
                    conn.close()
                    return

                cursor.execute('DELETE FROM medications WHERE medication_id = ?', (medication_id,))

                conn.commit()
                print("Препарат успешно удален!")

            except ValueError:
                print("Неверный ID препарата!")

            conn.close()

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def record_health_complaints(self, patient_id):
        """Запись жалоб на здоровье"""
        try:
            complaints = input("Введите жалобы пациента: ")

            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE medical_cards 
                SET health_complaints = ?
                WHERE patient_id = ?
            ''', (complaints, patient_id))
            conn.commit()
            conn.close()

            print("Жалобы успешно записаны!")

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def set_treatment_plan(self, patient_id):
        """Назначение плана лечения"""
        try:
            treatment_plan = input("Введите план лечения: ")

            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE medical_cards 
                SET treatment_plan = ?
                WHERE patient_id = ?
            ''', (treatment_plan, patient_id))

            conn.commit()
            conn.close()
            print("План лечения успешно назначен!")

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def record_medical_history(self, patient_id):
        """Запись истории болезни"""
        try:
            medical_history = input("Введите историю болезни: ")

            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE medical_cards 
                SET medical_history = ?
                WHERE patient_id = ?
            ''', (medical_history, patient_id))
            conn.commit()
            conn.close()

            print("История болезни успешно записана!")

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def view_patient_medications(self, patient_id):
        """Просмотр лекарств пациента"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT medication_id, medication_name, usage_description, is_taken
                FROM medications 
                WHERE patient_id = ?
            ''', (patient_id,))

            medications = cursor.fetchall()

            print("\n" + "=" * 40)
            print("ЛЕКАРСТВА ПАЦИЕНТА:")
            print("=" * 40)

            if medications:
                for med in medications:
                    status = "Принято" if med[3] else "Не принято"
                    print(f"ID препарата: {med[0]}")
                    print(f"Лекарство: {med[1]}")
                    print(f"Способ применения: {med[2]}")
                    print(f"Статус: {status}")
                    print("-" * 20)
            else:
                print("Лекарства не назначены")

            conn.close()

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def view_patient_medical_card(self, patient_id):
        """Просмотр медкарты пациента"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT p.surname, p.name, p.patronymic,
                       mc.health_complaints, mc.medical_history, mc.treatment_plan
                FROM patients p
                JOIN medical_cards mc ON p.patient_id = mc.patient_id
                WHERE p.patient_id = ?
            ''', (patient_id,))

            patient_info = cursor.fetchone()

            if not patient_info:
                print("Медкарта пациента не найдена!")
                return

            print("\n" + "=" * 50)
            print("МЕДИЦИНСКАЯ КАРТА ПАЦИЕНТА:")
            print("=" * 50)
            print(f"Пациент: {patient_info[0]} {patient_info[1]} {patient_info[2]}")
            print(f"Жалобы: {patient_info[3]}")
            print(f"История болезни: {patient_info[4]}")
            print(f"План лечения: {patient_info[5]}")

            # Получаем препараты пациента
            cursor.execute('''
                SELECT medication_name, usage_description, is_taken
                FROM medications 
                WHERE patient_id = ?
            ''', (patient_id,))

            medications = cursor.fetchall()

            if medications:
                print(f"\nНазначенные препараты:")
                for med in medications:
                    status = "Принят" if med[2] else "Не принят"
                    print(f"  - {med[0]} - {med[1]} [{status}]")

            # Получаем информацию о приемах
            cursor.execute('''
                SELECT appointment_date, appointment_time, confirmed
                FROM appointments 
                WHERE patient_id = ?
            ''', (patient_id,))

            appointments = cursor.fetchall()

            if appointments:
                print(f"\nЗаписи на прием:")
                for app in appointments:
                    status = "Подтверждена" if app[2] else "Ожидает подтверждения"
                    print(f"  - {app[0]} {app[1]} - {status}")

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
            self.show_patient_menu()
            return True

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
            return False

    def show_patient_menu(self):
        """Меню пациента"""
        while True:
            print("\n" + "=" * 40)
            print("МЕНЮ ПАЦИЕНТА")
            print("=" * 40)
            print("1. Посмотреть свои назначения")
            print("2. Отметить прием препарата")
            print("3. Посмотреть информацию о приеме")
            print("4. Выход")

            choice = input("Выберите действие: ")

            if choice == '1':
                self.view_patient_medications(self.current_patient_id)
            elif choice == '2':
                self.mark_medication_taken()
            elif choice == '3':
                self.view_appointment_info()
            elif choice == '4':
                self.current_patient_id = None
                break
            else:
                print("Неверный выбор!")

    def mark_medication_taken(self):
        """Отметка приема препарата"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT medication_id, medication_name 
                FROM medications 
                WHERE patient_id = ? AND is_taken = 0
            ''', (self.current_patient_id,))

            medications = cursor.fetchall()

            if not medications:
                print("Нет препаратов для отметки!")
                conn.close()
                return

            print("\nДоступные препараты для отметки:")
            for med in medications:
                print(f"ID: {med[0]} - {med[1]}")

            try:
                med_id = int(input("Введите ID препарата для отметки: "))

                cursor.execute('''
                    UPDATE medications 
                    SET is_taken = 1 
                    WHERE medication_id = ? AND patient_id = ?
                ''', (med_id, self.current_patient_id))

                if cursor.rowcount > 0:
                    print("Препарат отмечен как принятый!")
                else:
                    print("Препарат не найден!")

                conn.commit()

            except ValueError:
                print("Неверный ID препарата!")

            conn.close()

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def view_appointment_info(self):
        """Просмотр информации о приеме"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT appointment_date, appointment_time, confirmed
                FROM appointments 
                WHERE patient_id = ?
            ''', (self.current_patient_id,))

            appointments = cursor.fetchall()

            print("\n" + "=" * 40)
            print("ИНФОРМАЦИЯ О ПРИЕМЕ:")
            print("=" * 40)

            if appointments:
                for app in appointments:
                    status = "Подтверждена" if app[2] else "Ожидает подтверждения"
                    print(f"Дата приема: {app[0]}")
                    print(f"Время приема: {app[1]}")
                    print(f"Статус: {status}")
                    print("-" * 20)
            else:
                print("Запись на прием не найдена")

            conn.close()

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def admin_login(self):
        """Авторизация администратора"""
        try:
            username = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")

            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM administrators WHERE username = ? AND password = ?', (username, password))
            admin = cursor.fetchone()
            conn.close()

            if not admin:
                print("Неверные учетные данные!")
                return False

            self.current_admin_id = admin[0]
            print(f"Добро пожаловать, администратор {username}!")
            self.show_admin_menu()
            return True

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
            return False

    def show_admin_menu(self):
        """Меню администратора"""
        while True:
            print("\n" + "=" * 40)
            print("МЕНЮ АДМИНИСТРАТОРА")
            print("=" * 40)
            print("1. Показать всех пациентов")
            print("2. Записать пациента на прием")
            print("3. Подтвердить запись пациента")
            print("4. Выход")

            choice = input("Выберите действие: ")

            if choice == '1':
                self.show_all_patients()
            elif choice == '2':
                self.schedule_appointment()
            elif choice == '3':
                self.confirm_appointment()
            elif choice == '4':
                self.current_admin_id = None
                break
            else:
                print("Неверный выбор!")

    def show_all_patients(self):
        """Показать всех пациентов"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT p.patient_id, p.surname, p.name, p.patronymic,
                       d.surname, d.name, d.patronymic
                FROM patients p
                LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
                ORDER BY p.patient_id
            ''')

            patients = cursor.fetchall()

            print("\n" + "=" * 60)
            print("ВСЕ ПАЦИЕНТЫ:")
            print("=" * 60)

            for patient in patients:
                doctor_info = f"{patient[4]} {patient[5]} {patient[6]}" if patient[4] else "Не назначен"
                print(f"ID: {patient[0]}, {patient[1]} {patient[2]} {patient[3]} - Врач: {doctor_info}")

            conn.close()

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def schedule_appointment(self):
        """Запись пациента на прием"""
        try:
            self.show_all_patients()
            patient_id = input("\nВведите ID пациента для записи: ")

            # Проверка существования пациента
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT patient_id FROM patients WHERE patient_id = ?', (patient_id,))
            if not cursor.fetchone():
                print("Пациент не найден!")
                conn.close()
                return

            # Ввод даты
            print("\nВведите дату приема (формат: ГГГГ-ММ-ДД, например: 2025-01-15):")
            date = input("Дата: ")

            try:
                # Проверка корректности даты
                appointment_date = datetime.strptime(date, '%Y-%m-%d')
                if appointment_date.year != 2025:
                    print("Год должен быть 2025!")
                    conn.close()
                    return
            except ValueError:
                print("Неверный формат даты!")
                conn.close()
                return

            # Ввод времени
            print("\nВведите время приема (формат: ЧЧ:ММ, например: 14:30):")
            time_str = input("Время: ")

            try:
                # Проверка корректности времени
                appointment_time = datetime.strptime(time_str, '%H:%M').time()
                if appointment_time < time(8, 0) or appointment_time > time(20, 0):
                    print("Время приема должно быть с 8:00 до 20:00!")
                    conn.close()
                    return
            except ValueError:
                print("Неверный формат времени!")
                conn.close()
                return

            # Проверка занятости времени
            cursor.execute('''
                SELECT patient_id FROM appointments 
                WHERE appointment_date = ? AND appointment_time = ?
            ''', (date, time_str))

            if cursor.fetchone():
                print("Это время уже занято! Выберите другое время.")
                conn.close()
                return

            # Создание записи
            cursor.execute('''
                INSERT INTO appointments (patient_id, appointment_date, appointment_time)
                VALUES (?, ?, ?)
            ''', (patient_id, date, time_str))

            conn.commit()
            conn.close()

            print(f"Пациент ID:{patient_id} успешно записан на {date} в {time_str}")

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")

    def confirm_appointment(self):
        """Подтверждение записи пациента"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Показать неподтвержденные записи
            cursor.execute('''
                SELECT a.appointment_id, p.patient_id, a.appointment_date, a.appointment_time
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                WHERE a.confirmed = 0
                ORDER BY a.appointment_date, a.appointment_time
            ''')

            appointments = cursor.fetchall()

            if not appointments:
                print("Нет неподтвержденных записей!")
                conn.close()
                return

            print("\nНеподтвержденные записи:")
            for app in appointments:
                print(f"ID записи: {app[0]}, Пациент ID: {app[1]}, Дата: {app[2]}, Время: {app[3]}")

            try:
                appointment_id = int(input("\nВведите ID записи для подтверждения: "))

                cursor.execute('''
                    UPDATE appointments 
                    SET confirmed = 1 
                    WHERE appointment_id = ?
                ''', (appointment_id,))

                if cursor.rowcount > 0:
                    print("Запись подтверждена!")
                else:
                    print("Запись не найдена!")

                conn.commit()

            except ValueError:
                print("Неверный ID записи!")

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
        print("3. Вход администратора")
        print("4. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            if system.doctor_login():
                system.show_doctor_menu()
        elif choice == '2':
            system.patient_login()
        elif choice == '3':
            system.admin_login()
        elif choice == '4':
            print("Выход из системы")
            break
        else:
            print("Неверный выбор!")


if __name__ == "__main__":
    main()