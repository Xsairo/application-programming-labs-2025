from functions import process_data, save_file_content, read_file_content, parse_arguments


def main() -> None:
    """
    Главная функция программы
    """
    args = parse_arguments()

    print(f"Чтение из {args.input_file}...")
    profiles = read_file_content(args.input_file)

    if not profiles:
        print("Нет данных для обработки.")
        return

    print("Валидация и сортировка...")
    sorted_profiles = process_data(profiles)

    print(f"Сохранение {len(sorted_profiles)} записей...")
    save_file_content(sorted_profiles, args.output)


if __name__ == '__main__':
    main()
