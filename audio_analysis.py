import pandas as pd
import matplotlib.pyplot as plt
import soundfile as sf
import numpy as np
import os
from typing import Optional


def create_dataframe_from_annotation(annotation_file: str) -> pd.DataFrame:
    """
    Создает DataFrame из CSV аннотации.
    """
    try:
        df = pd.read_csv(annotation_file)

        if 'Absolute Path' in df.columns and 'Relative Path' in df.columns:
            df = df.rename(columns={
                'Absolute Path': 'absolute_path',
                'Relative Path': 'relative_path'
            })
        elif 'absolute_path' not in df.columns or 'relative_path' not in df.columns:
            if len(df.columns) >= 2:
                df.columns = ['absolute_path', 'relative_path'] + list(df.columns[2:])
            else:
                raise ValueError(f"Файл аннотации должен содержать как минимум 2 колонки")

        print(f"DataFrame создан из {annotation_file}")
        print(f"Загружено {len(df)} записей")
        return df

    except FileNotFoundError:
        print(f"Ошибка: Файл аннотации '{annotation_file}' не найден")
        return pd.DataFrame()
    except Exception as e:
        print(f"Ошибка при создании DataFrame: {e}")
        return pd.DataFrame()


def calculate_amplitude_range(audio_file: str) -> Optional[float]:
    """
    Вычисляет диапазон амплитуды (max - min) для аудиофайла.
    """
    try:
        data, samplerate = sf.read(audio_file)

        if len(data.shape) > 1:
            data = np.mean(data, axis=1)

        amp_range = np.max(data) - np.min(data)

        return float(amp_range)

    except Exception as e:
        print(f"Ошибка при обработке файла {audio_file}: {e}")
        return None


def add_amplitude_range_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Добавляет колонку с диапазоном амплитуды для каждого аудиофайла.
    """
    amplitude_ranges = []

    print("Вычисление диапазона амплитуды для аудиофайлов...")

    for idx, row in df.iterrows():
        audio_path = row['absolute_path']

        if os.path.exists(audio_path):
            amp_range = calculate_amplitude_range(audio_path)
            amplitude_ranges.append(amp_range)
        else:
            print(f"Предупреждение: Файл {audio_path} не найден")
            amplitude_ranges.append(None)

    df['amplitude_range'] = amplitude_ranges

    initial_count = len(df)
    df = df.dropna(subset=['amplitude_range'])
    removed_count = initial_count - len(df)

    if removed_count > 0:
        print(f"Удалено {removed_count} файлов с отсутствующими данными амплитуды")

    print(f"Колонка 'amplitude_range' успешно добавлена. Осталось {len(df)} записей")

    return df


def sort_by_amplitude(df: pd.DataFrame, ascending: bool = True) -> pd.DataFrame:
    """
    Сортирует DataFrame по колонке amplitude_range.
    """
    sorted_df = df.sort_values(by='amplitude_range', ascending=ascending)

    direction = "возрастанию" if ascending else "убыванию"
    print(f"DataFrame отсортирован по {direction} амплитуды")

    return sorted_df


def filter_by_amplitude(df: pd.DataFrame, min_value: float = 0, max_value: float = None) -> pd.DataFrame:
    """
    Фильтрует DataFrame по диапазону амплитуды.
    """
    filtered_df = df.copy()

    filtered_df = filtered_df[filtered_df['amplitude_range'] >= min_value]

    if max_value is not None:
        filtered_df = filtered_df[filtered_df['amplitude_range'] <= max_value]

    print(f"Фильтрация: амплитуда от {min_value}" +
          (f" до {max_value}" if max_value is not None else "") +
          f". Осталось {len(filtered_df)} записей из {len(df)}")

    return filtered_df


def plot_amplitude_ranges(df: pd.DataFrame, output_image: str = "amplitude_plot.png") -> None:
    """
    Строит график диапазонов амплитуды.
    """
    if len(df) == 0:
        print("Ошибка: Нет данных для построения графика")
        return

    plt.figure(figsize=(12, 6))

    file_numbers = range(1, len(df) + 1)

    amplitude_ranges = df['amplitude_range'].values

    plt.plot(file_numbers, amplitude_ranges,
             marker='o', linestyle='-', linewidth=1, markersize=4)

    plt.title('Диапазон амплитуды аудиофайлов', fontsize=14, fontweight='bold')
    plt.xlabel('Номер аудиофайла в отсортированном списке', fontsize=12)
    plt.ylabel('Диапазон амплитуды', fontsize=12)

    plt.grid(True, alpha=0.3)

    plt.xlim(0, len(df) + 1)

    stats_text = f"Всего файлов: {len(df)}\n" \
                 f"Мин. амплитуда: {amplitude_ranges.min():.4f}\n" \
                 f"Макс. амплитуда: {amplitude_ranges.max():.4f}\n" \
                 f"Средняя амплитуда: {amplitude_ranges.mean():.4f}"

    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
             verticalalignment='top', horizontalalignment='left',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
             fontsize=10)

    plt.tight_layout()
    plt.savefig(output_image, dpi=150, bbox_inches='tight')
    print(f"График сохранен в файл: {output_image}")

    plt.show()


def save_dataframe(df: pd.DataFrame, output_file: str = "audio_analysis.csv") -> None:
    """
    Сохраняет DataFrame в CSV файл.
    """
    try:
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"DataFrame сохранен в файл: {output_file}")
    except Exception as e:
        print(f"Ошибка при сохранении DataFrame: {e}")


def analyze_audio_data(annotation_file: str,
                       output_csv: str = "audio_analysis.csv",
                       output_plot: str = "amplitude_plot.png",
                       min_amplitude: float = 0,
                       max_amplitude: Optional[float] = None,
                       sort_descending: bool = False) -> None:
    """
    Основная функция анализа аудиоданных.
    """
    print("АНАЛИЗ АУДИОДАННЫХ...")

    df = create_dataframe_from_annotation(annotation_file)

    if df.empty:
        print("Не удалось создать DataFrame. Завершение работы.")
        return

    print("\nПервоначальные данные:")
    print(df.head())
    print(f"\nКолонки: {list(df.columns)}")

    df = add_amplitude_range_column(df)

    if df.empty:
        print("Нет данных для анализа. Завершение работы.")
        return

    df = sort_by_amplitude(df, ascending=not sort_descending)

    if min_amplitude > 0 or max_amplitude is not None:
        df = filter_by_amplitude(df, min_amplitude, max_amplitude)

    print("\nОбработанные данные (первые 5 строк):")
    print(df.head())

    print("\nСтатистика по амплитуде:")
    print(df['amplitude_range'].describe())

    save_dataframe(df, output_csv)

    plot_amplitude_ranges(df, output_plot)

    print("\nАнализ завершен успешно")
