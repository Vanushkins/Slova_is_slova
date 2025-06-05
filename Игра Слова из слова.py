import os
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia

class GameSave:
    SAVE_FILE = "game_save.txt"
    @classmethod
    def save_progress(cls, level, guessed_words):
        with open(cls.SAVE_FILE, 'w', encoding='utf-8') as f:
            f.write(f"current_level:{level}\nguessed_words:\n")
            for lvl, words in guessed_words.items():
                f.write(f"{lvl}:{','.join(words)}\n")
    @classmethod
    def load_progress(cls):
        if not os.path.exists(cls.SAVE_FILE):
            return 0, {}
        with open(cls.SAVE_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        current_level = 0
        guessed_words = {}
        reading_words = False
        for line in lines:
            line = line.strip()
            if line.startswith("current_level:"):
                current_level = int(line.split(":")[1])
            elif line == "guessed_words:":
                reading_words = True
            elif reading_words and ":" in line:
                lvl, words = line.split(":")
                guessed_words[lvl] = words.split(",") if words else []  
        return current_level, guessed_words
    @classmethod
    def reset_progress(cls):
        if os.path.exists(cls.SAVE_FILE):
            os.remove(cls.SAVE_FILE)

class AudioManager:
    def __init__(self):
        self.music_player = QtMultimedia.QMediaPlayer()
        self.sound_player = QtMultimedia.QMediaPlayer()
        self.music_enabled = True
        self.sounds_enabled = True
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.cleanup)
        self.timer.start(1000)
    
    def cleanup(self):
        if self.sound_player.state() == QtMultimedia.QMediaPlayer.StoppedState:
            self.sound_player.setPosition(0)

    def play_music(self, path):
        if self.music_enabled and os.path.exists(path):
            self.music_player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path)))
            self.music_player.play()
    
    def play_sound(self, path):
        if self.sounds_enabled and os.path.exists(path):
            self.sound_player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path)))
            self.sound_player.play()
    
    def stop_music(self):
        self.music_player.stop()
    
    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        return self.music_enabled
    
    def toggle_sounds(self):
        self.sounds_enabled = not self.sounds_enabled
        return self.sounds_enabled

class SettingsManager:
    SETTINGS_FILE = "game_settings.txt"
    BACKGROUNDS = [
        r"C:\Users\1\OneDrive\Рабочий стол\Игра\Музыка, звуки, фон\Фон 1.jpg",
        r"C:\Users\1\OneDrive\Рабочий стол\Игра\Музыка, звуки, фон\Фон 2.jpg",
        r"C:\Users\1\OneDrive\Рабочий стол\Игра\Музыка, звуки, фон\Фон 3.jpg",
        r"C:\Users\1\OneDrive\Рабочий стол\Игра\Музыка, звуки, фон\Фон 4.jpg"
    ]
    @classmethod
    def load_settings(cls):
        defaults = {
            "background_index": 0,
            "music_enabled": True,
            "sounds_enabled": True,
            "background_path": cls.BACKGROUNDS[0]
        }
        if not os.path.exists(cls.SETTINGS_FILE):
            return defaults 
        try:
            with open(cls.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    key, val = line.strip().split(":")
                    if key in defaults:
                        if key == "background_index":
                            idx = int(val)
                            if 0 <= idx < len(cls.BACKGROUNDS):
                                defaults[key] = idx
                                defaults["background_path"] = cls.BACKGROUNDS[idx]
                        else:
                            defaults[key] = eval(val)
            return defaults
        except:
            return defaults
    @classmethod
    def save_settings(cls, bg_index, music, sounds):
        with open(cls.SETTINGS_FILE, 'w', encoding='utf-8') as f:
            f.write(f"background_index:{bg_index}\n")
            f.write(f"music_enabled:{music}\n")
            f.write(f"sounds_enabled:{sounds}\n")
# ==================== Игровые окна ====================
class MainMenu(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_audio()
        self.connect_buttons()
        
    def setup_ui(self):
        self.setWindowTitle("Игра Слова из слова")
        self.setFixedSize(800, 600)
        self.central = QtWidgets.QWidget()
        self.setCentralWidget(self.central)
        self.settings = SettingsManager.load_settings()
        self.set_background(self.settings["background_path"])
        self.title = QtWidgets.QLabel("Слова из слова", self.central)
        self.title.setGeometry(200, 80, 400, 80)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setStyleSheet("""
            font-size: 36px; 
            font-family: 'Times New Roman';
            background: rgba(240,240,240,0.8); 
            border-radius: 10px;
            padding: 10px;
            color: #333;
        """)
        self.start_btn = self.create_button("Начать игру", 250, 200)
        self.settings_btn = self.create_button("Настройки", 250, 300)
        self.exit_btn = self.create_button("Выход", 250, 400)
        self.rules_btn = self.create_button("Правила игры", 600, 20, 150, 40, 14)
    
    def create_button(self, text, x, y, w=300, h=80, font_size=24):
        btn = QtWidgets.QPushButton(text, self.central)
        btn.setGeometry(x, y, w, h)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(230,230,230,0.8);
                border-radius: {10 if h==80 else 5}px;
                font-size: {font_size}px;
                border: 1px solid #aaa;
                padding: 5px;
            }}
            QPushButton:hover {{
                background: rgba(210,230,250,0.9);
            }}
        """)
        return btn
    
    def setup_audio(self):
        self.audio = AudioManager()
        self.audio.music_enabled = self.settings["music_enabled"]
        self.audio.sounds_enabled = self.settings["sounds_enabled"]
        self.music_path = r"C:\Users\1\OneDrive\Рабочий стол\Игра\Музыка, звуки, фон\Фоновая музыка.mp3"
        self.click_sound = r"C:\Users\1\OneDrive\Рабочий стол\Игра\Музыка, звуки, фон\звук клика.mp3"
        if self.settings["music_enabled"]:
            self.audio.play_music(self.music_path)
    
    def connect_buttons(self):
        self.rules_btn.clicked.connect(self.show_rules)
        self.start_btn.clicked.connect(self.start_game)
        self.settings_btn.clicked.connect(self.show_settings)
        self.exit_btn.clicked.connect(self.close)
    
    def set_background(self, path):
        if os.path.exists(path):
            self.central.setAutoFillBackground(True)
            palette = self.central.palette()
            palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(QtGui.QPixmap(path)))
            self.central.setPalette(palette)
     #окно с правилами игры   
    def show_rules(self):
        self.audio.play_sound(self.click_sound)
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Правила")
        dialog.setFixedSize(600, 500)
        title = QtWidgets.QLabel("Правила игры", dialog)
        title.setGeometry(200, 20, 200, 50)
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-family: 'Times New Roman';")
        rules_text = QtWidgets.QTextBrowser(dialog)
        rules_text.setGeometry(20, 80, 560, 350)
        rules_text.setHtml("""
            <h2>Правила игры:</h2>
            <ol>
                <li>Создавать можно только нарицательные существительные в единственном числе</li>
                <li>Вводите слова с клавиатуры в поле ввода</li>
                <li>Нажмите кнопку 'Проверить' для проверки слова</li>
                <li>Для перехода на следующий уровень нужно отгадать указанное количество слов</li>
                <li>Буквы «Е» и «Ё» взаимозаменяемы</li>
            </ol>
        """)
        close_btn = QtWidgets.QPushButton("Понятно", dialog)
        close_btn.setGeometry(235, 440, 130, 40)
        close_btn.clicked.connect(dialog.close)
        dialog.exec_()
    
    def show_settings(self):
        self.audio.play_sound(self.click_sound)
        dialog = SettingsDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.settings = SettingsManager.load_settings()
            self.set_background(self.settings["background_path"])
            self.audio.music_enabled = self.settings["music_enabled"]
            self.audio.sounds_enabled = self.settings["sounds_enabled"]
            if not self.settings["music_enabled"]:
                self.audio.stop_music()
        
    def start_game(self):
        self.audio.play_sound(self.click_sound)
        dialog = StartDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.game_window = GameWindow(self, dialog.start_level)
            self.game_window.show()
            self.hide()
    
    def closeEvent(self, event):
        self.audio.stop_music()
        event.accept()

class StartDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Начать игру")
        self.setFixedSize(300, 150)
        layout = QtWidgets.QVBoxLayout()
        self.new_game_btn = QtWidgets.QPushButton("Новая игра")
        self.continue_btn = QtWidgets.QPushButton("Продолжить")
        self.cancel_btn = QtWidgets.QPushButton("Отмена")
        for btn in [self.new_game_btn, self.continue_btn, self.cancel_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(230,230,230,0.8);
                    border-radius: 5px;
                    padding: 10px;
                    border: 1px solid #aaa;
                }
                QPushButton:hover {
                    background: rgba(210,230,250,0.9);
                }
            """)
            layout.addWidget(btn)
        self.setLayout(layout)
        # Проверка сохраненной игры
        saved_level, guessed_words = GameSave.load_progress()
        has_progress = saved_level > 0 or bool(guessed_words)
        self.continue_btn.setEnabled(has_progress)
        self.new_game_btn.clicked.connect(self.start_new)
        self.continue_btn.clicked.connect(self.continue_game)
        self.cancel_btn.clicked.connect(self.reject)
        self.start_level = 0
    
    def start_new(self):
        self.start_level = 0
        GameSave.reset_progress()
        self.accept()
    
    def continue_game(self):
        self.start_level, _ = GameSave.load_progress()
        self.accept()

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        self.setWindowTitle("Настройки")
        self.setFixedSize(600, 500)
        layout = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("Настройки игры")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 24px;
            font-family: 'Times New Roman';
            padding: 10px;
        """)
        layout.addWidget(title)
        bg_group = QtWidgets.QGroupBox("Смена фона")
        bg_layout = QtWidgets.QVBoxLayout()
        preview_layout = QtWidgets.QHBoxLayout()
        self.prev_btn = QtWidgets.QPushButton("<")
        self.prev_btn.setFixedSize(50, 50)
        self.preview = QtWidgets.QLabel()
        self.preview.setFixedSize(400, 200)
        self.preview.setAlignment(QtCore.Qt.AlignCenter)
        self.preview.setStyleSheet("""
            background: #f5f5f5;
            border: 2px solid #ccc;
            border-radius: 5px;
        """)
        self.next_btn = QtWidgets.QPushButton(">")
        self.next_btn.setFixedSize(50, 50)
        preview_layout.addWidget(self.prev_btn)
        preview_layout.addWidget(self.preview)
        preview_layout.addWidget(self.next_btn)
        bg_layout.addLayout(preview_layout)
        bg_group.setLayout(bg_layout)
        layout.addWidget(bg_group)
        sound_group = QtWidgets.QGroupBox("Настройки звука")
        sound_layout = QtWidgets.QVBoxLayout()
        self.music_btn = QtWidgets.QPushButton()
        self.music_btn.setFixedHeight(50)
        self.sounds_btn = QtWidgets.QPushButton()
        self.sounds_btn.setFixedHeight(50)
        sound_layout.addWidget(self.music_btn)
        sound_layout.addWidget(self.sounds_btn)
        sound_group.setLayout(sound_layout)
        layout.addWidget(sound_group)
        btn_layout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("Сохранить")
        self.save_btn.setFixedHeight(40)
        self.cancel_btn = QtWidgets.QPushButton("Отмена")
        self.cancel_btn.setFixedHeight(40)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        for btn in [self.prev_btn, self.next_btn, self.music_btn, self.sounds_btn, 
                   self.save_btn, self.cancel_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(230,230,230,0.8);
                    border-radius: 5px;
                    border: 1px solid #aaa;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background: rgba(210,230,250,0.9);
                }
            """)
        for group in [bg_group, sound_group]:
            group.setStyleSheet("""
                QGroupBox {
                    background: rgba(240,240,240,0.7);
                    border-radius: 5px;
                    padding: 10px;
                    border: 1px solid #ccc;
                    font-size: 18px;
                }
            """)
        self.prev_btn.clicked.connect(self.prev_bg)
        self.next_btn.clicked.connect(self.next_bg)
        self.music_btn.clicked.connect(self.toggle_music)
        self.sounds_btn.clicked.connect(self.toggle_sounds)
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn.clicked.connect(self.reject)
    
    def load_settings(self):
        self.settings = SettingsManager.load_settings()
        self.bg_index = self.settings["background_index"]
        self.music_enabled = self.settings["music_enabled"]
        self.sounds_enabled = self.settings["sounds_enabled"]
        self.update_preview()
        self.update_buttons()
    
    def update_preview(self):
        if 0 <= self.bg_index < len(SettingsManager.BACKGROUNDS):
            path = SettingsManager.BACKGROUNDS[self.bg_index]
            if os.path.exists(path):
                pixmap = QtGui.QPixmap(path)
                pixmap = pixmap.scaled(400, 200, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.preview.setPixmap(pixmap)
                return
        self.preview.setText("Фон не найден")
        self.preview.setPixmap(QtGui.QPixmap())
    
    def update_buttons(self):
        self.music_btn.setText(f"Музыка: {'ВКЛ' if self.music_enabled else 'ВЫКЛ'}")
        self.sounds_btn.setText(f"Звуки: {'ВКЛ' if self.sounds_enabled else 'ВЫКЛ'}")
    
    def prev_bg(self):
        self.parent.audio.play_sound(self.parent.click_sound)
        self.bg_index = (self.bg_index - 1) % len(SettingsManager.BACKGROUNDS)
        self.update_preview()
    
    def next_bg(self):
        self.parent.audio.play_sound(self.parent.click_sound)
        self.bg_index = (self.bg_index + 1) % len(SettingsManager.BACKGROUNDS)
        self.update_preview()
    
    def toggle_music(self):
        self.parent.audio.play_sound(self.parent.click_sound)
        self.music_enabled = not self.music_enabled
        self.update_buttons()
    
    def toggle_sounds(self):
        self.parent.audio.play_sound(self.parent.click_sound)
        self.sounds_enabled = not self.sounds_enabled
        self.update_buttons()
    
    def save_settings(self):
        self.parent.audio.play_sound(self.parent.click_sound)
        SettingsManager.save_settings(
            self.bg_index,
            self.music_enabled,
            self.sounds_enabled
        )
        self.accept()

class GameWindow(QtWidgets.QMainWindow):
    def __init__(self, parent, start_level=0):
        super().__init__()
        self.parent = parent
        self.current_level = start_level
        self.guessed_words = {}
        self.setup_ui()
        self.load_levels()
        self.setup_level()
        
    def setup_ui(self):
        self.setWindowTitle("Игра Слова из слова")
        self.setFixedSize(800, 600)
        self.central = QtWidgets.QWidget()
        self.setCentralWidget(self.central)
        self.set_background(self.parent.settings["background_path"])
        self.menu_btn = QtWidgets.QPushButton("Выход в меню", self.central)
        self.menu_btn.setGeometry(20, 20, 150, 40)
        self.level_label = QtWidgets.QLabel(self.central)
        self.level_label.setGeometry(300, 20, 200, 40)
        self.level_label.setAlignment(QtCore.Qt.AlignCenter)
        self.source_frame = QtWidgets.QFrame(self.central)
        self.source_frame.setGeometry(50, 80, 700, 60)
        self.source_label = QtWidgets.QLabel("Исходное слово:", self.source_frame)
        self.source_label.setGeometry(20, 15, 150, 30)
        self.source_word = QtWidgets.QLabel(self.source_frame)
        self.source_word.setGeometry(180, 10, 500, 40)
        self.source_word.setAlignment(QtCore.Qt.AlignCenter)
        self.word_frame = QtWidgets.QFrame(self.central)
        self.word_frame.setGeometry(50, 160, 700, 80)
        self.word_label = QtWidgets.QLabel("Введённое слово:", self.word_frame)
        self.word_label.setGeometry(20, 25, 150, 30)
        self.word_input = QtWidgets.QLineEdit(self.word_frame)
        self.word_input.setGeometry(180, 20, 400, 40)
        self.word_input.setAlignment(QtCore.Qt.AlignCenter)
        self.check_btn = QtWidgets.QPushButton("Проверить", self.word_frame)
        self.check_btn.setGeometry(590, 20, 80, 40)
        #список слов
        self.words_list = QtWidgets.QTextBrowser(self.central)
        self.words_list.setGeometry(50, 260, 700, 250)
        self.prev_btn = QtWidgets.QPushButton("Предыдущий уровень", self.central)
        self.prev_btn.setGeometry(50, 530, 180, 40)
        self.next_btn = QtWidgets.QPushButton("Следующий уровень", self.central)
        self.next_btn.setGeometry(570, 530, 180, 40)
        for widget in [self.menu_btn, self.check_btn, self.prev_btn, self.next_btn]:
            widget.setStyleSheet("""
                QPushButton {
                    background: rgba(230,230,230,0.8);
                    border-radius: 5px;
                    padding: 5px;
                    border: 1px solid #aaa;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: rgba(210,230,250,0.9);
                }
            """)
        for frame in [self.source_frame, self.word_frame, self.words_list]:
            frame.setStyleSheet("""
                background: rgba(245,245,245,0.85);
                border-radius: 5px;
                border: 1px solid #bbb;
            """)
        self.level_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            background: rgba(245,245,245,0.85);
            border-radius: 5px;
            border: 1px solid #bbb;
        """)
        self.source_label.setStyleSheet("font-size: 18px;")
        self.word_label.setStyleSheet("font-size: 18px;")
        self.source_word.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.word_input.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            border: none;
            background: transparent;
        """)
        self.words_list.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.menu_btn.clicked.connect(self.return_to_menu)
        self.check_btn.clicked.connect(self.check_word)
        self.prev_btn.clicked.connect(self.prev_level)
        self.next_btn.clicked.connect(self.next_level)
    
    def set_background(self, path):
        if os.path.exists(path):
            self.central.setAutoFillBackground(True)
            palette = self.central.palette()
            palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(QtGui.QPixmap(path)))
            self.central.setPalette(palette)
    
    def load_levels(self):
        self.levels = [
            {
                "name": "Уровень 1",
                "letters": ["к", "о", "р", "з", "и", "н", "а"],
                "words": self.load_words(r"C:\Users\1\OneDrive\Рабочий стол\Игра\Возможные слова\1 уровень ответы к слову Корзина.txt"),
                "required": 5
            },
            {
                "name": "Уровень 2", 
                "letters": ["п", "а", "р", "о", "в", "о", "з"],
                "words": self.load_words(r"C:\Users\1\OneDrive\Рабочий стол\Игра\Возможные слова\2 уровень ответы к слову Паровоз.txt"),
                "required": 5
            },
            {
                "name": "Уровень 3",
                "letters": ["к", "а", "р", "т", "и", "н", "а"],
                "words": self.load_words(r"C:\Users\1\OneDrive\Рабочий стол\Игра\Возможные слова\3 уровень ответы к слову Картина.txt"),
                "required": 5
            }
        ]
        # Загрузка сохранений
        saved_level, self.guessed_words = GameSave.load_progress()
        if self.current_level == 0:
            self.current_level = saved_level
    
    def load_words(self, path):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return [line.strip().lower() for line in f if line.strip()]
        return []
    
    def setup_level(self):
        if self.current_level >= len(self.levels):
            self.current_level = len(self.levels) - 1 
        level = self.levels[self.current_level]
        self.level_label.setText(level["name"])
        self.source_word.setText("".join(level["letters"]).upper())
        self.current_words = level["words"]
        self.required_words = level["required"]
        self.guessed_words_list = self.guessed_words.get(str(self.current_level), [])
        # Показываем кнопку "Завершить игру" только на последнем уровне
        if self.current_level == len(self.levels) - 1:
            self.next_btn.setText("Завершить игру")
        else:
            self.next_btn.setText("Следующий уровень")
        self.update_words_list()
        self.word_input.setFocus()
    
    def update_words_list(self):
        words_html = "<br>".join([word.upper() for word in self.guessed_words_list])
        self.words_list.setHtml(f"""
            <p style='font-size:18px; font-weight:bold;'>
                Список отгаданных слов ({len(self.guessed_words_list)} из {self.required_words}):<br>
                {words_html}
            </p>
        """)
    
    def check_word(self):
        word = self.word_input.text().strip().lower()
        if not word:
            return
        # Проверка букв
        level = self.levels[self.current_level]
        temp_letters = level["letters"].copy()
        valid = True
        for letter in word:
            if letter in temp_letters:
                temp_letters.remove(letter)
            else:
                valid = False
                break
        if not valid:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Используйте только доступные буквы!")
            return
        if word not in self.current_words:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Такого слова нет в списке!")
            return
        if word in self.guessed_words_list:
            self.word_input.clear()
            return
        self.guessed_words_list.append(word)
        self.guessed_words[str(self.current_level)] = self.guessed_words_list
        GameSave.save_progress(self.current_level, self.guessed_words)
        self.update_words_list()
        self.word_input.clear()
        self.parent.audio.play_sound(self.parent.click_sound)
    
    def prev_level(self):
        self.parent.audio.play_sound(self.parent.click_sound)
        if self.current_level > 0:
            self.current_level -= 1
            GameSave.save_progress(self.current_level, self.guessed_words)
            self.setup_level()
    
    def next_level(self):
        self.parent.audio.play_sound(self.parent.click_sound)
        if len(self.guessed_words_list) >= self.required_words:
            if self.current_level < len(self.levels) - 1:
                self.current_level += 1
                GameSave.save_progress(self.current_level, self.guessed_words)
                self.setup_level()
            else:
                # Действия при завершении игры
                QtWidgets.QMessageBox.information(
                    self, 
                    "Поздравляем!", 
                    "Вы прошли все уровни игры!"
                )
                GameSave.reset_progress()
                self.return_to_menu()
        else:
            QtWidgets.QMessageBox.warning(
                self,
                "Недостаточно слов",
                f"Нужно отгадать {self.required_words} слов для перехода!"
            )
        
    def return_to_menu(self):
        GameSave.save_progress(self.current_level, self.guessed_words)
        self.parent.show()
        self.close()
    
    def closeEvent(self, event):
        GameSave.save_progress(self.current_level, self.guessed_words)
        event.accept()

# Запуск приложения
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    print("Проверка доступности файлов:")
    for i, path in enumerate(SettingsManager.BACKGROUNDS):
        print(f"{i+1}. {'✓' if os.path.exists(path) else '✗'} {path}")
    music_path = r"C:\Users\1\OneDrive\Рабочий стол\Игра\Музыка, звуки, фон\Фоновая музыка.mp3"
    click_path = r"C:\Users\1\OneDrive\Рабочий стол\Игра\Музыка, звуки, фон\звук клика.mp3"
    print(f"\nМузыка: {'✓' if os.path.exists(music_path) else '✗'} {music_path}")
    print(f"Звук: {'✓' if os.path.exists(click_path) else '✗'} {click_path}")
    window = MainMenu()
    window.show()
    app.exec_()