import os
import csv
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple, Optional


def create_directory(path: str) -> None:
    """
    Создает директорию, если она не существует.
    """
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            print(f"Ошибка при создании директории {path}: {e}")


def save_annotation(data: List[Tuple[str, str]], filepath: str) -> None:
    """
    Сохраняет список путей в CSV файл.
    """
    header = ["Absolute Path", "Relative Path"]
    try:
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(data)
        print(f"Аннотация успешно сохранена в: {filepath}")
    except IOError as e:
        print(f"Ошибка при записи аннотации: {e}")


def download_file(url: str, save_folder: str, filename: str) -> Optional[str]:
    """
    Скачивает файл по URL.
    """
    try:
        response = requests.get(url, timeout=15)

        path = os.path.join(save_folder, filename)
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return path
    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети при скачивании {filename}: {e}")
    except IOError as e:
        print(f"Ошибка записи файла {filename}: {e}")
    return None


def scrape_mixkit_audio(
        limit: int,
        save_dir: str
) -> List[Tuple[str, str]]:
    """
    Основная функция парсинга аудио.
    """
    base_url = "https://mixkit.co/free-stock-music/instrument/piano/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36'
    }

    create_directory(save_dir)
    downloaded_files: List[Tuple[str, str]] = []
    count = 0
    page = 1

    print(f"Запуск загрузки {limit} файлов в '{save_dir}'...")

    while count < limit:
        current_url = f"{base_url}?page={page}"
        print(f"Обработка страницы: {page}")

        try:
            response = requests.get(current_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print("Страница недоступна")
                break
            if page > 1 and response.url == base_url:
                print(f" Страница {page} привела к перенаправлению на базовый URL ({base_url}).")
                break
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find_all(attrs={"data-test-id": "audio-player"})

            for item in items:
                if count >= limit:
                    break

                audio_url = item.get('data-audio-player-preview-url-value')
                print(audio_url)
                if audio_url:
                    filename = f"track_{count + 1}.mp3"
                    full_path = download_file(audio_url, save_dir, filename)

                    if full_path:
                        abs_path = os.path.abspath(full_path)
                        rel_path = os.path.relpath(full_path, start=os.getcwd())
                        downloaded_files.append((abs_path, rel_path))
                        print(f"[{count + 1}/{limit}] Скачано: {filename}")
                        count += 1

            page += 1

        except Exception as e:
            print(f"Критическая ошибка при парсинге: {e}")
            break

    return downloaded_files
