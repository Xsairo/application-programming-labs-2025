import re


def is_valid_name(value: str) -> bool:
    """
    Проверяет валидность имени или фамилии
    """
    pattern = r'^[A-ZА-ЯЁ][a-zа-яё]+$'
    return bool(re.fullmatch(pattern, value))
