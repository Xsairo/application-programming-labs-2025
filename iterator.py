import csv
from typing import Iterator, List


class FilePathIterator:
    """
    Итератор для перебора путей к файлам из CSV-аннотации.
    """
    def __init__(self, annotation_file: str) -> None:
        """
        Инициализирует итератор.
        """
        self.data: List[str] = []
        self.index: int = 0
        self._load_data(annotation_file)
        self.limit: int = len(self.data)

    def _load_data(self, filepath: str) -> None:
        """
        Загружает данные из CSV файла в память.
        """
        try:
            with open(filepath, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader, None)
                for row in reader:
                    if row:
                        self.data.append(row[0])
        except FileNotFoundError:
            print(f"Ошибка: Файл аннотации '{filepath}' не найден.")
            self.data = []
        except Exception as e:
            print(f"Ошибка чтения аннотации: {e}")
            self.data = []

    def __iter__(self) -> Iterator[str]:
        """Возвращает экземпляр итератора."""
        return self

    def __next__(self) -> str:
        """
        Возвращает следующий путь из списка.
        """
        if self.index < self.limit:
            path = self.data[self.index]
            self.index += 1
            return path
        else:
            raise StopIteration
