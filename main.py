import argparse
import sys
from scraper import scrape_mixkit_audio, save_annotation
from iterator import FilePathIterator


def main() -> None:
    """
    Главная функция
    """
    parser = argparse.ArgumentParser(description="Программа для скачивания музыки с Mixkit")
    parser.add_argument('-l', '--limit', type=int, default=5, help='Количество файлов (50-1000)')
    parser.add_argument('-d', '--dataset_dir', type=str, default='dataset', help='Папка для сохранения файлов')
    parser.add_argument('-a', '--annotation_file', type=str, default='annotation.csv', help='Имя файла аннотации')

    args = parser.parse_args()

    print("Скачивание файлов")
    files_data = scrape_mixkit_audio(
        limit=args.limit,
        save_dir=args.dataset_dir
    )

    if not files_data:
        print("Файлы не были скачаны. Завершение работы.")
        sys.exit(1)

    print("\nСоздание аннотации")
    save_annotation(files_data, args.annotation_file)

    print("\nТестирование итератора")
    try:
        file_iter = FilePathIterator(args.annotation_file)
        print(f"Итератор создан для файла: {args.annotation_file}")

        for i, path in enumerate(file_iter):
            print(f"Файл {i + 1}: {path}")
            if i >= 2:
                print("(остальные файлы скрыты)")
                break

    except Exception as e:
        print(f"Ошибка при работе с итератором: {e}")


if __name__ == '__main__':
    main()
