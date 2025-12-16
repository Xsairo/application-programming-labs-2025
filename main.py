import argparse
import sys
from scraper import scrape_mixkit_audio, save_annotation
from iterator import FilePathIterator
from audio_analysis import analyze_audio_data

def main() -> None:
    """
    Главная функция
    """
    parser = argparse.ArgumentParser(description="Программа для скачивания музыки с Mixkit")
    parser.add_argument(
        'mode',
        choices=['download', 'analysis'],
        help='Режим работы: download - скачивание файлов, analysis - обработка аудио',
    )
    parser.add_argument('-l', '--limit', type=int, default=5, help='Количество файлов (50-1000)')
    parser.add_argument('-d', '--dataset_dir', type=str, default='dataset', help='Папка для сохранения файлов')
    parser.add_argument('-a', '--annotation_file', type=str, default='annotation.csv', help='Имя файла аннотации')
    parser.add_argument('--analysis_csv', type=str, default='audio_analysis.csv', help='Файл для результатов анализа')
    parser.add_argument('--analysis_plot', type=str, default='amplitude_plot.png', help='Файл для графика анализа')
    parser.add_argument('--min', type=float, default=0,
                        help='Минимальное значение амплитуды для фильтрации (по умолчанию: 0)')
    parser.add_argument('--max', type=float, default=None,
                        help='Максимальное значение амплитуды для фильтрации (по умолчанию: нет)')
    parser.add_argument('--descending', action='store_true',
                        help='Сортировать по убыванию амплитуды (по умолчанию: по возрастанию)')
    args = parser.parse_args()

    if args.mode == 'analysis':
        print("АНАЛИЗ АУДИОДАННЫХ...")

        analyze_audio_data(
            annotation_file=args.annotation_file,
            output_csv=args.analysis_csv,
            output_plot=args.analysis_plot,
            min_amplitude=args.min,
            max_amplitude=args.max,
            sort_descending=args.descending
        )
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


if __name__ == '__main__':
    main()
