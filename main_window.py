import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from iterator import FilePathIterator


class AudioPlayerWindow(QMainWindow):
    """
    Главное окно приложения
    """

    def __init__(self):
        super().__init__()
        self.current_index = 0
        self.file_paths = []
        self.iterator = None
        self.init_ui()
        self.init_audio_player()

    def init_ui(self):
        """
        Инициализация интерфейса
        """
        self.setWindowTitle("Аудио Плеер")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)

        file_panel = self.create_file_panel()
        main_layout.addWidget(file_panel)

        info_panel = self.create_info_panel()
        main_layout.addWidget(info_panel)

        audio_controls = self.create_audio_controls()
        main_layout.addWidget(audio_controls)

        nav_panel = self.create_navigation_panel()
        main_layout.addWidget(nav_panel)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово")

    def create_file_panel(self):
        """
        Создание панели для выбора файла аннотации
        """
        panel = QGroupBox("Файл аннотации")
        layout = QHBoxLayout()

        self.file_path_label = QLabel("Файл не выбран")
        self.file_path_label.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        self.file_path_label.setMinimumHeight(30)

        browse_btn = QPushButton("Выбрать файл...")
        browse_btn.clicked.connect(self.browse_annotation_file)
        browse_btn.setMinimumHeight(30)

        layout.addWidget(self.file_path_label, 1)
        layout.addWidget(browse_btn)

        panel.setLayout(layout)
        return panel

    def create_info_panel(self):
        """
        Создание панели с информацией о треке
        """
        panel = QGroupBox("Информация о треке")
        layout = QVBoxLayout()
        name_layout = QHBoxLayout()
        name_label = QLabel("Название:")
        name_label.setMinimumWidth(80)
        self.track_name = QLabel("Нет данных")
        self.track_name.setStyleSheet("font-weight: bold; font-size: 12px;")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.track_name, 1)

        duration_layout = QHBoxLayout()
        duration_label = QLabel("Длительность:")
        duration_label.setMinimumWidth(80)
        self.track_duration = QLabel("00:00")
        self.track_duration.setStyleSheet("font-size: 12px;")
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.track_duration, 1)

        path_layout = QHBoxLayout()
        path_label = QLabel("Путь:")
        path_label.setMinimumWidth(80)
        self.track_path = QLabel("Нет данных")
        self.track_path.setWordWrap(True)
        self.track_path.setStyleSheet("color: #666; font-size: 12px;")
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.track_path, 1)

        layout.addLayout(name_layout)
        layout.addLayout(duration_layout)
        layout.addLayout(path_layout)
        panel.setLayout(layout)
        panel.setMinimumHeight(120)
        return panel

    def create_audio_controls(self):
        """
        Создание панели управления аудио
        """
        panel = QGroupBox("Управление воспроизведением")
        layout = QHBoxLayout()

        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.clicked.connect(self.toggle_play_pause)
        self.play_btn.setEnabled(False)
        self.play_btn.setMinimumSize(50, 50)

        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_btn.clicked.connect(self.stop_audio)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumSize(50, 50)


        layout.addStretch(1)
        layout.addWidget(self.play_btn)
        layout.addWidget(self.stop_btn)
        layout.addStretch(1)

        panel.setLayout(layout)
        return panel

    def create_navigation_panel(self):
        """
        Создание панели навигации по трекам
        """
        panel = QGroupBox("Навигация по датасету")
        layout = QHBoxLayout()

        self.position_label = QLabel("0 / 0")
        self.position_label.setAlignment(Qt.AlignCenter)

        self.prev_btn = QPushButton("Предыдущий")
        self.prev_btn.clicked.connect(self.prev_track)
        self.prev_btn.setEnabled(False)

        self.next_btn = QPushButton("Следующий")
        self.next_btn.clicked.connect(self.next_track)
        self.next_btn.setEnabled(False)

        layout.addWidget(self.prev_btn)
        layout.addStretch(1)
        layout.addWidget(self.position_label)
        layout.addStretch(1)
        layout.addWidget(self.next_btn)

        panel.setLayout(layout)
        return panel

    def init_audio_player(self):
        """
        Инициализация аудио-плеера
        """
        self.player = QMediaPlayer()

        self.player.durationChanged.connect(self.update_duration)
        self.player.stateChanged.connect(self.update_play_button)

    def browse_annotation_file(self):
        """
        Выбор файла аннотации
        """
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл аннотации",
            "",
            "CSV файлы (*.csv)"
        )

        if file_name:
            self.file_path_label.setText(file_name)
            self.load_annotation_file(file_name)

    def load_annotation_file(self, file_path):
        """
        Загрузка файла аннотации и создание итератора
        """
        try:
            self.iterator = FilePathIterator(file_path)
            self.file_paths = list(self.iterator.data)
            self.current_index = 0

            if self.file_paths:
                self.prev_btn.setEnabled(False)
                self.next_btn.setEnabled(len(self.file_paths) > 1)
                self.position_label.setText(f"1 / {len(self.file_paths)}")
                self.load_track(self.file_paths[0])
                self.status_bar.showMessage(f"Загружено {len(self.file_paths)} треков")
            else:
                self.clear_track_info()
                self.status_bar.showMessage("Файл аннотации пуст")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл аннотации: {str(e)}")
            self.status_bar.showMessage("Ошибка загрузки файла")

    def load_track(self, file_path):
        """
        Загрузка трека по указанному пути
        """
        if os.path.exists(file_path):
            self.stop_audio()

            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))

            file_name = os.path.basename(file_path)
            self.track_name.setText(file_name)
            self.track_path.setText(file_path)
            self.track_duration.setText("00:00")

            self.play_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)

            self.status_bar.showMessage(f"Загружен: {file_name}")
        else:
            self.status_bar.showMessage(f"Файл не найден: {file_path}")

    def clear_track_info(self):
        """
        Очистка информации о треке
        """
        self.track_name.setText("Нет данных")
        self.track_duration.setText("00:00")
        self.track_path.setText("Нет данных")
        self.play_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.position_label.setText("0 / 0")

    def toggle_play_pause(self):
        """
        Переключение между воспроизведением и паузой
        """
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def stop_audio(self):
        """
        Остановка воспроизведения
        """
        self.player.stop()

    def update_duration(self, duration):
        """
        Обновление информации о длительности трека
        """
        if duration > 0:
            minutes = duration // 60000
            seconds = (duration % 60000) // 1000
            self.track_duration.setText(f"{minutes:02d}:{seconds:02d}")


    def update_play_button(self, state):
        """
        Обновление иконки кнопки воспроизведения/паузы
        """
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def next_track(self):
        """
        Переход к следующему треку
        """
        if self.file_paths and self.current_index < len(self.file_paths) - 1:
            self.current_index += 1
            self.load_track(self.file_paths[self.current_index])
            self.update_navigation_buttons()
            self.position_label.setText(f"{self.current_index + 1} / {len(self.file_paths)}")

    def prev_track(self):
        """
        Переход к предыдущему треку
        """
        if self.file_paths and self.current_index > 0:
            self.current_index -= 1
            self.load_track(self.file_paths[self.current_index])
            self.update_navigation_buttons()
            self.position_label.setText(f"{self.current_index + 1} / {len(self.file_paths)}")

    def update_navigation_buttons(self):
        """
        Обновление состояния кнопок навигации
        """
        self.prev_btn.setEnabled(self.current_index > 0)
        self.next_btn.setEnabled(self.current_index < len(self.file_paths) - 1)


def appstart():
    """
    Запуск приложения
    """
    app = QApplication(sys.argv)

    window = AudioPlayerWindow()
    window.show()

    sys.exit(app.exec_())
