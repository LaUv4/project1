import json
import csv
import xml.etree.ElementTree as ET
import os
import sqlite3


class HospitalDataExporter:
    def __init__(self, db_path):
        self.db_path = db_path
        self.ensure_out_directory()

    def ensure_out_directory(self):
        """Создает папку out, если её нет"""
        if not os.path.exists('out'):
            os.makedirs('out')
        print("Папка 'out' создана или уже существует")

    def get_connection(self):
        """Создает соединение с базой данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            # Проверяем, что база данных работает
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Найдено таблиц в базе: {len(tables)}")
            return conn
        except Exception as e:
            print(f"Ошибка подключения к базе: {e}")
            return None

    def fetch_patient_data(self):
        """Извлекает данные пациентов с их назначениями"""
        conn = self.get_connection()
        if not conn:
            return []

        cursor = conn.cursor()

        try:
            # Получаем данные пациентов с их медкартами, назначениями и лекарствами
            query = """
            SELECT 
                p.patient_id,
                p.surname,
                p.name,
                p.patronymic,
                p.doctor_id,
                d.surname as doctor_surname,
                d.name as doctor_name,
                d.patronymic as doctor_patronymic,
                mc.health_complaints,
                mc.medical_history,
                mc.treatment_plan,
                a.appointment_id,
                a.appointment_date,
                a.appointment_time,
                a.confirmed,
                m.medication_id,
                m.medication_name,
                m.usage_description,
                m.is_taken
            FROM patients p
            LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
            LEFT JOIN medical_cards mc ON p.patient_id = mc.patient_id
            LEFT JOIN appointments a ON p.patient_id = a.patient_id
            LEFT JOIN medications m ON p.patient_id = m.patient_id
            ORDER BY p.patient_id
            """

            cursor.execute(query)
            rows = cursor.fetchall()
            print(f"Получено строк из базы: {len(rows)}")

        except sqlite3.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return []
        finally:
            conn.close()

        # Группируем данные по пациентам
        patients = {}
        for row in rows:
            patient_id = row[0]
            if patient_id not in patients:
                patients[patient_id] = {
                    'patient_id': patient_id,
                    'surname': row[1],
                    'name': row[2],
                    'patronymic': row[3],
                    'doctor_id': row[4],
                    'doctor': {
                        'surname': row[5],
                        'name': row[6],
                        'patronymic': row[7]
                    } if row[5] else None,
                    'medical_card': {
                        'health_complaints': row[8],
                        'medical_history': row[9],
                        'treatment_plan': row[10]
                    } if row[8] else None,
                    'appointments': [],
                    'medications': []
                }

            # Добавляем назначение, если оно есть
            if row[11]:  # appointment_id
                appointment = {
                    'appointment_id': row[11],
                    'appointment_date': row[12],
                    'appointment_time': row[13],
                    'confirmed': bool(row[14])
                }
                # Проверяем дубликаты
                if not any(a['appointment_id'] == appointment['appointment_id'] for a in
                           patients[patient_id]['appointments']):
                    patients[patient_id]['appointments'].append(appointment)

            # Добавляем лекарство, если оно есть
            if row[15]:  # medication_id
                medication = {
                    'medication_id': row[15],
                    'medication_name': row[16],
                    'usage_description': row[17],
                    'is_taken': bool(row[18])
                }
                # Проверяем дубликаты
                if not any(
                        m['medication_id'] == medication['medication_id'] for m in patients[patient_id]['medications']):
                    patients[patient_id]['medications'].append(medication)

        result = list(patients.values())
        print(f"Сгруппировано пациентов: {len(result)}")
        return result

    def export_to_json(self, data):
        """Экспорт данных в JSON"""
        try:
            with open('out/data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("Данные успешно экспортированы в JSON")
        except Exception as e:
            print(f"Ошибка при экспорте в JSON: {e}")

    def export_to_csv(self, data):
        """Экспорт данных в CSV"""
        try:
            with open('out/data.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Заголовки
                writer.writerow([
                    'patient_id', 'surname', 'name', 'patronymic', 'doctor_id',
                    'doctor_info', 'health_complaints', 'medical_history', 'treatment_plan',
                    'appointments_info', 'medications_info'
                ])

                # Данные
                for patient in data:
                    # Формируем информацию о враче
                    doctor_info = ""
                    if patient['doctor']:
                        doctor_info = f"{patient['doctor']['surname']} {patient['doctor']['name']} {patient['doctor']['patronymic']}"

                    # Формируем информацию о медкарте
                    health_complaints = patient['medical_card']['health_complaints'] if patient['medical_card'] else ""
                    medical_history = patient['medical_card']['medical_history'] if patient['medical_card'] else ""
                    treatment_plan = patient['medical_card']['treatment_plan'] if patient['medical_card'] else ""

                    # Формируем информацию о назначениях
                    appointments_info = ""
                    if patient['appointments']:
                        appointments_list = []
                        for app in patient['appointments']:
                            app_str = f"{app['appointment_date']} {app['appointment_time']} ({'Подтверждена' if app['confirmed'] else 'Ожидает'})"
                            appointments_list.append(app_str)
                        appointments_info = "; ".join(appointments_list)

                    # Формируем информацию о лекарствах
                    medications_info = ""
                    if patient['medications']:
                        medications_list = []
                        for med in patient['medications']:
                            med_str = f"{med['medication_name']}: {med['usage_description']} ({'Принято' if med['is_taken'] else 'Не принято'})"
                            medications_list.append(med_str)
                        medications_info = "; ".join(medications_list)

                    writer.writerow([
                        patient['patient_id'],
                        patient['surname'],
                        patient['name'],
                        patient['patronymic'],
                        patient['doctor_id'],
                        doctor_info,
                        health_complaints,
                        medical_history,
                        treatment_plan,
                        appointments_info,
                        medications_info
                    ])

            print("Данные успешно экспортированы в CSV")
        except Exception as e:
            print(f"Ошибка при экспорте в CSV: {e}")

    def export_to_xml(self, data):
        """Экспорт данных в XML"""
        try:
            root = ET.Element('patients')

            for patient in data:
                patient_elem = ET.SubElement(root, 'patient')

                ET.SubElement(patient_elem, 'patient_id').text = str(patient['patient_id'])
                ET.SubElement(patient_elem, 'surname').text = patient['surname']
                ET.SubElement(patient_elem, 'name').text = patient['name']
                ET.SubElement(patient_elem, 'patronymic').text = patient['patronymic']
                ET.SubElement(patient_elem, 'doctor_id').text = str(patient['doctor_id'])

                # Информация о враче
                if patient['doctor']:
                    doctor_elem = ET.SubElement(patient_elem, 'doctor')
                    ET.SubElement(doctor_elem, 'surname').text = patient['doctor']['surname']
                    ET.SubElement(doctor_elem, 'name').text = patient['doctor']['name']
                    ET.SubElement(doctor_elem, 'patronymic').text = patient['doctor']['patronymic']

                # Медицинская карта
                if patient['medical_card']:
                    medical_card_elem = ET.SubElement(patient_elem, 'medical_card')
                    ET.SubElement(medical_card_elem, 'health_complaints').text = patient['medical_card'][
                                                                                     'health_complaints'] or ''
                    ET.SubElement(medical_card_elem, 'medical_history').text = patient['medical_card'][
                                                                                   'medical_history'] or ''
                    ET.SubElement(medical_card_elem, 'treatment_plan').text = patient['medical_card'][
                                                                                  'treatment_plan'] or ''

                # Назначения
                appointments_elem = ET.SubElement(patient_elem, 'appointments')
                for appointment in patient['appointments']:
                    app_elem = ET.SubElement(appointments_elem, 'appointment')
                    ET.SubElement(app_elem, 'appointment_id').text = str(appointment['appointment_id'])
                    ET.SubElement(app_elem, 'appointment_date').text = appointment['appointment_date']
                    ET.SubElement(app_elem, 'appointment_time').text = appointment['appointment_time']
                    ET.SubElement(app_elem, 'confirmed').text = str(appointment['confirmed'])

                # Лекарства
                medications_elem = ET.SubElement(patient_elem, 'medications')
                for medication in patient['medications']:
                    med_elem = ET.SubElement(medications_elem, 'medication')
                    ET.SubElement(med_elem, 'medication_id').text = str(medication['medication_id'])
                    ET.SubElement(med_elem, 'medication_name').text = medication['medication_name']
                    ET.SubElement(med_elem, 'usage_description').text = medication['usage_description']
                    ET.SubElement(med_elem, 'is_taken').text = str(medication['is_taken'])

            tree = ET.ElementTree(root)
            tree.write('out/data.xml', encoding='utf-8', xml_declaration=True)
            print("Данные успешно экспортированы в XML")
        except Exception as e:
            print(f"Ошибка при экспорте в XML: {e}")

    def export_to_yaml(self, data):
        """Экспорт данных в YAML (без внешних библиотек)"""
        try:
            with open('out/data.yaml', 'w', encoding='utf-8') as f:
                self._write_yaml(data, f)
            print("Данные успешно экспортированы в YAML")
        except Exception as e:
            print(f"Ошибка при экспорте в YAML: {e}")

    def _write_yaml(self, data, f, indent=0):
        """Ручная реализация YAML записи"""
        indent_str = '  ' * indent

        if isinstance(data, list):
            for item in data:
                f.write(f'{indent_str}- ')
                if isinstance(item, (dict, list)):
                    f.write('\n')
                    self._write_yaml(item, f, indent + 1)
                else:
                    f.write(f'{self._yaml_value(item)}\n')
        elif isinstance(data, dict):
            first = True
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    if not first:
                        f.write('\n')
                    f.write(f'{indent_str}{key}:\n')
                    self._write_yaml(value, f, indent + 1)
                else:
                    f.write(f'{indent_str}{key}: {self._yaml_value(value)}\n')
                first = False
        else:
            f.write(f'{indent_str}{self._yaml_value(data)}\n')

    def _yaml_value(self, value):
        """Форматирование значения для YAML"""
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            # Экранирование специальных символов
            str_value = str(value)
            if any(char in str_value for char in ':[]{}#&*!|>\"\'%@`'):
                return f'"{str_value}"'
            return str_value

    def run_export(self):
        """Основной метод для выполнения экспорта"""
        print("=" * 50)
        print("НАЧАЛО ЭКСПОРТА ДАННЫХ")
        print("=" * 50)

        # Получаем данные
        data = self.fetch_patient_data()

        if not data:
            print("Не удалось получить данные из базы")
            return

        print(f"Найдено пациентов: {len(data)}")

        # Экспортируем во все форматы
        print("\nЭкспорт в форматы:")
        print("-" * 20)
        self.export_to_json(data)
        self.export_to_csv(data)
        self.export_to_xml(data)
        self.export_to_yaml(data)

        print("\n" + "=" * 50)
        print("ЭКСПОРТ ЗАВЕРШЕН!")
        print("Файлы сохранены в папке 'out/':")
        print("  - data.json")
        print("  - data.csv")
        print("  - data.xml")
        print("  - data.yaml")
        print("=" * 50)


def main():
    """Главная функция"""
    # Пробуем разные возможные пути к базе данных
    possible_paths = [
        "hospital.db",  # В текущей папке
        "../database/hospital.db",  # В папке database на уровень выше
        "../src/main/database/hospital.db",  # В папке src/main/database
    ]

    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            print(f"Найдена база данных: {path}")
            break

    if not db_path:
        print("База данных не найдена!")
        print("Сначала создайте базу данных:")
        print("1. Запустите create_database.py")
        return

    # Создаем экземпляр класса и запускаем экспорт
    exporter = HospitalDataExporter(db_path)
    exporter.run_export()


if __name__ == "__main__":
    main()