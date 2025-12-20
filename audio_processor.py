import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import os
import sys
from typing import Tuple


class AudioProcessor:
    """Класс для обработки аудиофайлов"""

    def __init__(self):
        self.audio_data = None
        self.original_samplerate = None
        self.processed_samplerate = None

    def load_audio(self, filepath: str) -> Tuple[np.ndarray, int]:
        """
        Загружает аудиофайл с помощью soundfile.
        """
        print(f"Загрузка аудиофайла: {filepath}")

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Файл '{filepath}' не найден")

        self.audio_data, self.original_samplerate = sf.read(filepath)
        print(f"Аудио загружено. Размер массива: {self.audio_data.shape}")

        return self.audio_data, self.original_samplerate

    def get_audio_info(self) -> dict:
        """
        Возвращает информацию об аудиофайле.
        """
        if self.audio_data is None:
            raise ValueError("Аудиофайл не загружен")

        shape = self.audio_data.shape

        if len(shape) == 1:
            samples = shape[0]
            channels = 1
            audio_type = "Моно (1 канал)"
        else:
            samples = shape[0]
            channels = shape[1]
            audio_type = f"Стерео ({channels} канала)"

        duration = samples / self.original_samplerate

        info = {
            "samples": samples,
            "samplerate": self.original_samplerate,
            "duration": duration,
            "channels": channels,
            "type": audio_type,
            "shape": shape,
            "dtype": self.audio_data.dtype,
            "min_amplitude": np.min(self.audio_data),
            "max_amplitude": np.max(self.audio_data)
        }

        return info

    def visualize_audio(self, speed_factor: float):
        """
        Визуализирует исходное и обработанное аудио с помощью matplotlib.
        Графики показываются на экране.
        """
        if self.audio_data is None:
            raise ValueError("Аудиофайл не загружен")
        time_original = np.arange(len(self.audio_data)) / self.original_samplerate
        time_processed = np.arange(len(self.audio_data)) / (self.original_samplerate * speed_factor)

        if len(self.audio_data.shape) == 1:
            channels = 1
            audio_data_2d = self.audio_data.reshape(-1, 1)
        else:
            channels = self.audio_data.shape[1]
            audio_data_2d = self.audio_data

        fig, axes = plt.subplots(2, channels, figsize=(10, 5))

        if channels == 1:
            axes = axes.reshape(-1, 1)

        for channel in range(channels):
            channel_data = audio_data_2d[:, channel]

            axes[0, channel].plot(time_original, channel_data, color='blue', linewidth=0.5)
            axes[0, channel].set_title(f'Исходное аудио (канал {channel + 1})')
            axes[0, channel].set_xlabel('Время (сек)')
            axes[0, channel].set_ylabel('Амплитуда')
            axes[0, channel].grid(True, alpha=0.3)
            axes[0, channel].set_xlim([0, time_original[-1]])

            axes[1, channel].plot(time_processed, channel_data, color='red', linewidth=0.5)
            axes[1, channel].set_title(f'Ускоренное аудио (x{speed_factor}, канал {channel + 1})')
            axes[1, channel].set_xlabel('Время (сек)')
            axes[1, channel].set_ylabel('Амплитуда')
            axes[1, channel].grid(True, alpha=0.3)
            axes[1, channel].set_xlim([0, time_processed[-1]])

        plt.suptitle(f'Сравнение исходного и ускоренного аудио (коэффициент: {speed_factor}x)', fontsize=16)
        plt.tight_layout()
        print("\nОтображение графиков... (закройте окно для продолжения)")
        plt.show()
        plt.close()

    def save_and_speedup_audio(self, filepath: str, speed_factor: float):
        """
        Сохраняет обработанное аудио в файл.
        Для ускорения аудио используется изменение частоты дискретизации.
        """
        if self.audio_data is None:
            raise ValueError("Аудиоданные не загружены")

        new_samplerate = int(self.original_samplerate * speed_factor)

        print(f"Сохранение аудио с частотой дискретизации: {new_samplerate} Гц")
        sf.write(filepath, self.audio_data, new_samplerate)
        print(f"Обработанное аудио сохранено в: {filepath}")


def process_audio_file(input_path: str, output_path: str, speed_factor: float = 2.0):
    """
    Основная функция обработки аудиофайла.
    """
    print("АУДИО ПРОЦЕССОР - Увеличение скорости аудиофайла")

    processor = AudioProcessor()

    try:
        processor.load_audio(input_path)
        info = processor.get_audio_info()
        print("ИНФОРМАЦИЯ ОБ АУДИОФАЙЛЕ")
        print(f"Файл: {os.path.basename(input_path)}")
        print(f"Тип: {info['type']}")
        print(f"Размер массива: {info['shape']}")
        print(f"Тип данных: {info['dtype']}")
        print(f"Частота дискретизации: {info['samplerate']} Гц")
        print(f"Количество сэмплов: {info['samples']:,}")
        print(f"Длительность: {info['duration']:.2f} секунд")
        print(f"Диапазон амплитуд: от {info['min_amplitude']:.3f} до {info['max_amplitude']:.3f}")

        print("ОБРАБОТКА АУДИО...")

        processed_duration = info['duration'] / speed_factor
        new_samplerate = info['samplerate'] * speed_factor

        print("СОХРАНЕНИЕ РЕЗУЛЬТАТА...")

        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        processor.save_and_speedup_audio(output_path, speed_factor)
        print(f"Новая частота дискретизации: {new_samplerate} Гц")
        print(f"Длительность после обработки: {processed_duration:.2f} секунд")
        print(f"Коэффициент сжатия времени: {speed_factor:.2f}")

        print("ВИЗУАЛИЗАЦИЯ...")
        processor.visualize_audio(speed_factor)

        print("ОБРАБОТКА УСПЕШНО ЗАВЕРШЕНА!")

    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
