from typing import List, Dict, Any
from validator import is_valid_name
import sys
import re
import argparse

ProfileDict = Dict[str, Any]


def parse_arguments() -> argparse.Namespace:
    """
    Парсинг аргументов командной строки
    """
    parser = argparse.ArgumentParser(description='Сортировка анкет пользователей.')
    parser.add_argument('input_file', type=str, help='Путь к входному файлу')
    parser.add_argument('-o', '--output', type=str, default='sorted_data_new.txt', help='Путь к выходному файлу')
    return parser.parse_args()


def read_file_content(filename: str) -> List[ProfileDict]:
    """
    Читает файл, используя регулярное выражение
    """
    profiles: List[ProfileDict] = []

    try:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError as error:
        print(f"Ошибка: Файл '{filename}' не найден. ({error})")
        sys.exit(1)
    except PermissionError as error:
        print(f"Ошибка: Нет доступа к файлу. ({error})")
        sys.exit(1)

    profile_pattern = re.compile(
        r'\d+\)\n'
        r'Фамилия:\s*(.+?)\n'
        r'Имя:\s*(.+?)\n'
        r'Пол:\s*(.+?)\n'
        r'Дата рождения:\s*(.+?)\n'
        r'Номер телефона или email:\s*(.+?)\n'
        r'Город:\s*(.+?)(?=\n|\Z)',
    )

    matches = profile_pattern.finditer(content)

    for match in matches:
        raw_record = match.group(0).strip().split('\n')
        if raw_record:
            raw_record.pop(0)
        surname = match.group(1).strip()
        name = match.group(2).strip()

        profile_dict = {
            "surname": surname,
            "name": name,
            "raw_lines": raw_record
        }
        profiles.append(profile_dict)

    return profiles


def get_sort_key(profile: ProfileDict) -> tuple:
    """
    Возвращает ключ для сортировки: (Фамилия, Имя).
    """
    return profile['surname'], profile['name']


def process_data(profiles: List[ProfileDict]) -> List[ProfileDict]:
    """
    Валидирует и сортирует список профилей
    """
    valid_profiles: List[ProfileDict] = []

    for profile in profiles:
        if is_valid_name(profile['surname']) and is_valid_name(profile['name']):
            valid_profiles.append(profile)
        else:
            print(f"Исключена запись из-за невалидного формата (строчная буква): {profile['surname']} "
                  f"{profile['name']}")

    valid_profiles.sort(key=get_sort_key)

    return valid_profiles


def save_file_content(profiles: List[ProfileDict], filename: str) -> None:
    """
    Сохраняет данные в файл
    """
    try:
        with open(filename, "w", encoding="utf-8") as file:
            last_index = len(profiles)
            for index, profile in enumerate(profiles, 1):
                file.write(f"{index})\n")
                if index < last_index:
                    for line in profile['raw_lines']:
                        file.write(line + "\n")
                    file.write("\n")
                else:
                    for i in range(len(profile['raw_lines']) - 1):
                        file.write(profile['raw_lines'][i] + "\n")
                    file.write(profile['raw_lines'][i+1])

        print(f"Успешно сохранено {len(profiles)} отсортированных и валидных анкет в '{filename}'.")
    except IOError as error:
        print(f"Ошибка записи: {error}")
