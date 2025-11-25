import sqlite3
import os


def create_hospital_database():
    """Создает и заполняет базу данных больницы"""
    db_path = "../database/hospital.db"

    # Создаем папку если её нет
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    try:
        conn = sqlite3.connect(db_path)
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

        # Очистка и добавление пациентов
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

        # Очистка и добавление препаратов
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

        conn.commit()
        conn.close()
        print(f"База данных успешно создана: {db_path}")
        print("Добавлены врачи, пациенты, медкарты, назначения и лекарства")

    except sqlite3.Error as e:
        print(f"Ошибка создания базы данных: {e}")


if __name__ == "__main__":
    create_hospital_database()