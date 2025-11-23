import sqlite3
import os


def create_tables():
    """Создает все таблицы заново"""

    # Создаем папку database если ее нет
    os.makedirs("database", exist_ok=True)

    # Подключаемся к базе данных
    conn = sqlite3.connect("database/hospital.db")
    cursor = conn.cursor()

    # Список всех таблиц в правильном порядке
    tables_sql = [
        # Doctor_1
        '''CREATE TABLE IF NOT EXISTS Doctor_1
           (
               Doctor_1_id INTEGER PRIMARY KEY AUTOINCREMENT,
               Surname TEXT NOT NULL,
               Name TEXT NOT NULL,
               Patronymic TEXT NOT NULL,
               Password TEXT NOT NULL
           )''',

        # Doctor_2
        '''CREATE TABLE IF NOT EXISTS Doctor_2
           (
               Doctor_2_id INTEGER PRIMARY KEY AUTOINCREMENT,
               Surname TEXT NOT NULL,
               Name TEXT NOT NULL,
               Patronymic TEXT NOT NULL,
               Password TEXT NOT NULL
           )''',

        # Patient
        '''CREATE TABLE IF NOT EXISTS Patient
           (
               Patient_ID INTEGER PRIMARY KEY AUTOINCREMENT,
               Surname TEXT NOT NULL,
               Name TEXT NOT NULL,
               Patronymic TEXT NOT NULL
           )''',

        # Medical_card
        '''CREATE TABLE IF NOT EXISTS Medical_card
        (
            Patient_ID INTEGER PRIMARY KEY,
            Health_complaints TEXT NOT NULL,
            Medical_history TEXT NOT NULL,
            FOREIGN KEY
           (
            Patient_ID
           ) REFERENCES Patient
           (
               Patient_ID
           )
            )''',

        # Medication
        '''CREATE TABLE IF NOT EXISTS Medication
           (
               Drug_id INTEGER PRIMARY KEY AUTOINCREMENT,
               Name_of_the_drug TEXT NOT NULL,
               Usage_record TEXT NOT NULL
           )''',

        # Make_an_appointment
        '''CREATE TABLE IF NOT EXISTS Make_an_appointment
        (
            Appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            Doctor_id INTEGER NOT NULL,
            Patient_ID INTEGER NOT NULL,
            Date_time_of_reception TEXT NOT NULL,
            FOREIGN KEY
           (
            Patient_ID
           ) REFERENCES Patient
           (
               Patient_ID
           )
            )''',

        # Drug_intake
        '''CREATE TABLE IF NOT EXISTS Drug_intake
        (
            Drug_intake_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Appointment_id INTEGER NOT NULL,
            Drug_id INTEGER NOT NULL,
            FOREIGN KEY
           (
            Appointment_id
           ) REFERENCES Make_an_appointment
           (
               Appointment_id
           ),
            FOREIGN KEY
           (
               Drug_id
           ) REFERENCES Medication
           (
               Drug_id
           )
            )'''
    ]

    # Создаем все таблицы
    for i, sql in enumerate(tables_sql, 1):
        try:
            cursor.execute(sql)
            print(f"Таблица {i} создана успешно")
        except Exception as e:
            print(f"Ошибка при создании таблицы {i}: {e}")

    conn.commit()
    conn.close()
    print("\nВсе таблицы созданы!")


def show_tables():
    """Показывает все таблицы"""
    conn = sqlite3.connect("database/hospital.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print("\nТаблицы в базе данных:")
    for table in tables:
        print(f"- {table[0]}")

    conn.close()


if __name__ == "__main__":
    create_tables()
    show_tables()