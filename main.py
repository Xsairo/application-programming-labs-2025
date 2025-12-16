import argparse
import sys
from scraper import scrape_mixkit_audio, save_annotation
from iterator import FilePathIterator
from audio_processor import process_audio_file


def main() -> None:
    """
    Главная функция
    """
    parser = argparse.ArgumentParser(description="Программа для скачивания музыки с Mixkit")
    parser.add_argument(
        'mode',
        choices=['download', 'process'],
        help='Режим работы: download - скачивание файлов, process - обработка аудио',
    )
    parser.add_argument('-l', '--limit',
                        type=int,
                        help='Количество файлов (50-1000)')
    parser.add_argument('-d', '--dataset_dir',
                        type=str,
                        help='Папка для сохранения файлов')
    parser.add_argument('-a', '--annotation_file',
                        type=str,
                        help='Имя файла аннотации')
    parser.add_argument(
        '-i', '--input',
        type=str,
        help='Путь к исходному аудиофайлу (требуется для режима process)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Путь для сохранения результата (требуется для режима process)'
    )

    parser.add_argument(
        '-s', '--speed',
        type=float,
        default=2.0,
        help='Коэффициент ускорения аудио (по умолчанию: 2.0)'
    )

    args = parser.parse_args()


    if args.mode == 'download':
        print("РЕЖИМ СКАЧИВАНИЯ ФАЙЛОВ")
        print("Скачивание файлов")
        files_data = scrape_mixkit_audio(
            limit=args.limit,
            save_dir=args.dataset_dir
        )

        if not files_data:
            print("Файлы не были скачаны. Завершение работы.")
            sys.exit(1)

        print("\nСоздание аннотации...")
        save_annotation(files_data, args.annotation_file)

        print("\nТестирование итератора...")
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

    elif args.mode == 'process':
        if not args.input or not args.output:
            print("Ошибка: для режима 'process' необходимо указать --input и --output")
            parser.print_help()
            sys.exit(1)

        process_audio_file(args.input, args.output, args.speed)


if __name__ == '__main__':
    main()
