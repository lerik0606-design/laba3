import random
import time
import tkinter as tk
from tkinter import messagebox


class MinesweeperGame:
    def __init__(self, rows=9, cols=9, mines=10):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.cell_size = 35

        # Игровое поле
        self.board = []  # -1 = мина, 0-8 = количество мин вокруг
        self.visible = []  # False = скрыто, True = открыто
        self.flags = []  # True = флаг

        # Состояние игры
        self.game_over = False
        self.game_started = False
        self.first_click = True
        self.start_time = 0
        self.revealed_count = 0

        # Цвета
        self.colors = {
            "hidden": "#CCCCCC",
            "revealed": "#cfa5a5",
            "grid": "#808080",
            "1": "blue",
            "2": "green",
            "3": "red",
            "4": "darkblue",
            "5": "darkred",
            "6": "cyan",
            "7": "black",
            "8": "gray",
            "mine": "black",
            "flag": "red",
            "exploded": "red"
        }

        # Дополнительные функции
        self.hint_available = True
        self.auto_flag_enabled = False

    def new_game(self):
        """Новая игра"""
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.visible = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flags = [[False for _ in range(self.cols)] for _ in range(self.rows)]

        self.game_over = False
        self.game_started = False
        self.first_click = True
        self.revealed_count = 0
        self.hint_available = True

        # Пока не размещаем мины - это сделаем после первого клика

    def place_mines(self, safe_row, safe_col):
        """Размещение мин после первого клика"""
        # Безопасная зона 3x3 вокруг первого клика
        safe_zone = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                r, c = safe_row + dr, safe_col + dc
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    safe_zone.append((r, c))

        # Размещаем мины
        mines_placed = 0
        while mines_placed < self.mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)

            # Не ставим мину в безопасной зоне и не повторяем
            if (r, c) not in safe_zone and self.board[r][c] != -1:
                self.board[r][c] = -1
                mines_placed += 1

                # Обновляем счетчики вокруг мины
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols and self.board[nr][nc] != -1:
                            self.board[nr][nc] += 1

        self.game_started = True
        self.start_time = time.time()

    def reveal(self, row, col):
        """Открыть клетку"""
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return

        if self.visible[row][col] or self.flags[row][col]:
            return

        # Первый клик - размещаем мины
        if self.first_click:
            self.place_mines(row, col)
            self.first_click = False

        self.visible[row][col] = True
        self.revealed_count += 1

        # Если пустая клетка, открываем соседей рекурсивно
        if self.board[row][col] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr != 0 or dc != 0:
                        self.reveal(row + dr, col + dc)

    def toggle_flag(self, row, col):
        """Поставить/снять флаг"""
        if self.visible[row][col]:
            return

        self.flags[row][col] = not self.flags[row][col]

    def check_win(self):
        """Проверка победы"""
        # Все не-минные клетки открыты
        non_mine_cells = self.rows * self.cols - self.mines
        return self.revealed_count == non_mine_cells

    def check_game_over(self):
        """Проверка проигрыша"""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.visible[r][c] and self.board[r][c] == -1:
                    return True
        return False

    def get_hint(self):
        """Получить подсказку (безопасную клетку)"""
        safe_cells = []
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.visible[r][c] and not self.flags[r][c] and self.board[r][c] != -1:
                    safe_cells.append((r, c))

        if safe_cells:
            return random.choice(safe_cells)
        return None

    def auto_flag(self):
        """Автоматическая расстановка флагов"""
        changed = True
        while changed:
            changed = False
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.visible[r][c] and self.board[r][c] > 0:
                        # Считаем скрытых соседей
                        hidden_neighbors = []
                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                if dr == 0 and dc == 0:
                                    continue
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                    if not self.visible[nr][nc] and not self.flags[nr][nc]:
                                        hidden_neighbors.append((nr, nc))

                        # Если число равно количеству скрытых соседей, ставим флаги
                        if self.board[r][c] == len(hidden_neighbors):
                            for nr, nc in hidden_neighbors:
                                if not self.flags[nr][nc]:
                                    self.flags[nr][nc] = True
                                    changed = True


class MinesweeperGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Сапер")

        # Начальные параметры
        self.rows = 9
        self.cols = 9
        self.mines = 10

        # Создаем игру
        self.game = MinesweeperGame(self.rows, self.cols, self.mines)

        # Создаем интерфейс
        self.create_widgets()

        # Запускаем новую игру
        self.new_game()

        # Запускаем таймер обновления
        self.update_timer()

    def create_widgets(self):
        """Создание интерфейса"""
        # Панель управления
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=5)

        # Кнопка новой игры
        self.new_game_btn = tk.Button(
            self.control_frame,
            text="Новая игра",
            command=self.new_game,
            font=("Arial", 12),
            width=12
        )
        self.new_game_btn.pack(side=tk.LEFT, padx=5)

        # Счетчик мин
        self.mines_label = tk.Label(
            self.control_frame,
            text=f"Мин: {self.mines}",
            font=("Arial", 12),
            width=10
        )
        self.mines_label.pack(side=tk.LEFT, padx=5)

        # Таймер
        self.timer_label = tk.Label(
            self.control_frame,
            text="Время: 00:00",
            font=("Arial", 12),
            width=12
        )
        self.timer_label.pack(side=tk.LEFT, padx=5)

        # Кнопка подсказки
        self.hint_btn = tk.Button(
            self.control_frame,
            text="Подсказка (H)",
            command=self.give_hint,
            font=("Arial", 12),
            width=12
        )
        self.hint_btn.pack(side=tk.LEFT, padx=5)

        # Кнопка авто-флагов
        self.auto_flag_btn = tk.Button(
            self.control_frame,
            text="Авто-флаги (F)",
            command=self.auto_flag,
            font=("Arial", 12),
            width=12
        )
        self.auto_flag_btn.pack(side=tk.LEFT, padx=5)

        # Игровое поле
        self.canvas = tk.Canvas(
            self.root,
            width=self.cols * self.game.cell_size,
            height=self.rows * self.game.cell_size,
            bg=self.game.colors["hidden"]
        )
        self.canvas.pack(padx=10, pady=10)

        # Привязка событий
        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<Button-3>", self.right_click)
        self.root.bind("<h>", lambda e: self.give_hint())
        self.root.bind("<H>", lambda e: self.give_hint())
        self.root.bind("<f>", lambda e: self.auto_flag())
        self.root.bind("<F>", lambda e: self.auto_flag())

        # Создаем меню
        self.create_menu()

    def create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню "Игра"
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Игра", menu=game_menu)
        game_menu.add_command(label="Новая игра", command=self.new_game, accelerator="F2")
        game_menu.add_separator()
        game_menu.add_command(label="Выход", command=self.root.quit)

        # Меню "Сложность" - ВАЖНО: исправлены команды!
        difficulty_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Сложность", menu=difficulty_menu)

        # Добавляем команды с правильными вызовами
        difficulty_menu.add_command(
            label="Новичок (9x9, 10 мин)",
            command=self.set_beginner
        )
        difficulty_menu.add_command(
            label="Средний (16x16, 40 мин)",
            command=self.set_intermediate
        )
        difficulty_menu.add_command(
            label="Эксперт (16x30, 99 мин)",
            command=self.set_expert
        )
        difficulty_menu.add_command(
            label="Своя сложность...",
            command=self.set_custom
        )

        # Меню "Функции"
        features_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Функции", menu=features_menu)
        features_menu.add_command(label="Подсказка", command=self.give_hint, accelerator="H")
        features_menu.add_command(label="Авто-флаги", command=self.auto_flag, accelerator="F")

        # Привязка горячих клавиш
        self.root.bind("<F2>", lambda e: self.new_game())

    def set_beginner(self):
        """Установить уровень новичка"""
        self.rows = 9
        self.cols = 9
        self.mines = 10
        self.apply_difficulty()

    def set_intermediate(self):
        """Установить средний уровень"""
        self.rows = 16
        self.cols = 16
        self.mines = 40
        self.apply_difficulty()

    def set_expert(self):
        """Установить экспертный уровень"""
        self.rows = 16
        self.cols = 30
        self.mines = 99
        self.apply_difficulty()

    def set_custom(self):
        """Установить пользовательскую сложность"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Своя сложность")
        dialog.transient(self.root)
        dialog.grab_set()

        # Поля ввода
        tk.Label(dialog, text="Строки (5-30):").grid(row=0, column=0, padx=5, pady=5)
        rows_entry = tk.Entry(dialog)
        rows_entry.grid(row=0, column=1, padx=5, pady=5)
        rows_entry.insert(0, str(self.rows))

        tk.Label(dialog, text="Колонки (5-30):").grid(row=1, column=0, padx=5, pady=5)
        cols_entry = tk.Entry(dialog)
        cols_entry.grid(row=1, column=1, padx=5, pady=5)
        cols_entry.insert(0, str(self.cols))

        tk.Label(dialog, text="Мины:").grid(row=2, column=0, padx=5, pady=5)
        mines_entry = tk.Entry(dialog)
        mines_entry.grid(row=2, column=1, padx=5, pady=5)
        mines_entry.insert(0, str(self.mines))

        def apply():
            try:
                rows = int(rows_entry.get())
                cols = int(cols_entry.get())
                mines = int(mines_entry.get())

                max_mines = rows * cols // 2

                if 5 <= rows <= 30 and 5 <= cols <= 30 and 1 <= mines <= max_mines:
                    self.rows = rows
                    self.cols = cols
                    self.mines = mines
                    dialog.destroy()
                    self.apply_difficulty()
                else:
                    messagebox.showerror("Ошибка",
                                         f"Некорректные значения!\n"
                                         f"Максимум мин: {max_mines}")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите числа!")

        tk.Button(dialog, text="OK", command=apply).grid(row=3, column=0, columnspan=2, pady=10)

    def apply_difficulty(self):
        """Применить выбранную сложность"""
        # Обновляем размеры canvas
        self.canvas.config(
            width=self.cols * self.game.cell_size,
            height=self.rows * self.game.cell_size
        )

        # Создаем новую игру с новыми параметрами
        self.game = MinesweeperGame(self.rows, self.cols, self.mines)

        # Запускаем новую игру
        self.new_game()

        # Обновляем счетчик мин
        self.mines_label.config(text=f"Мин: {self.mines}")

    def new_game(self):
        """Начать новую игру"""
        self.game.new_game()
        self.draw_board()
        self.mines_label.config(text=f"Мин: {self.mines}")
        self.hint_btn.config(state=tk.NORMAL)

    def draw_board(self):
        """Отрисовка игрового поля"""
        self.canvas.delete("all")

        for r in range(self.game.rows):
            for c in range(self.game.cols):
                x1 = c * self.game.cell_size
                y1 = r * self.game.cell_size
                x2 = x1 + self.game.cell_size
                y2 = y1 + self.game.cell_size

                # Рисуем клетку
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline=self.game.colors["grid"]
                )

                if self.game.visible[r][c]:  # Открытая клетка
                    # Фон открытой клетки
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=self.game.colors["revealed"],
                        outline=self.game.colors["grid"]
                    )

                    if self.game.board[r][c] == -1:  # Мина
                        if self.game.game_over:  # Проигрыш - красная мина
                            self.canvas.create_oval(
                                x1 + 5, y1 + 5, x2 - 5, y2 - 5,
                                fill=self.game.colors["exploded"]
                            )
                        else:  # Просто мина (например, при показе всех мин)
                            self.canvas.create_oval(
                                x1 + 5, y1 + 5, x2 - 5, y2 - 5,
                                fill=self.game.colors["mine"]
                            )
                    elif self.game.board[r][c] > 0:  # Число
                        self.canvas.create_text(
                            x1 + self.game.cell_size // 2,
                            y1 + self.game.cell_size // 2,
                            text=str(self.game.board[r][c]),
                            font=("Arial", 12, "bold"),
                            fill=self.game.colors.get(str(self.game.board[r][c]), "black")
                        )

                elif self.game.flags[r][c]:  # Флаг
                    # Фон скрытой клетки с флагом
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=self.game.colors["hidden"],
                        outline=self.game.colors["grid"]
                    )

                    # Рисуем флаг
                    flag_color = self.game.colors["flag"]
                    # Древко флага
                    self.canvas.create_line(
                        x1 + 10, y2 - 10, x1 + 10, y1 + 10,
                        width=2, fill="black"
                    )
                    # Треугольник флага
                    self.canvas.create_polygon(
                        x1 + 10, y1 + 10,
                        x1 + 10, y1 + 20,
                        x1 + 25, y1 + 15,
                        fill=flag_color
                    )

                else:  # Скрытая клетка
                    # Фон скрытой клетки с 3D эффектом
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=self.game.colors["hidden"],
                        outline=self.game.colors["grid"]
                    )

                    # 3D эффект (выпуклая кнопка)
                    self.canvas.create_line(x1, y1, x2, y1, fill="white", width=2)
                    self.canvas.create_line(x1, y1, x1, y2, fill="white", width=2)
                    self.canvas.create_line(x2, y1, x2, y2, fill="gray", width=2)
                    self.canvas.create_line(x1, y2, x2, y2, fill="gray", width=2)

    def left_click(self, event):
        """Обработка левого клика"""
        if self.game.game_over:
            return

        col = event.x // self.game.cell_size
        row = event.y // self.game.cell_size

        if 0 <= row < self.game.rows and 0 <= col < self.game.cols:
            self.game.reveal(row, col)

            # Проверяем состояние игры
            if self.game.check_game_over():
                self.game.game_over = True
                self.show_all_mines()
                self.draw_board()
                messagebox.showinfo("Игра окончена", "Вы наступили на мину!")
            elif self.game.check_win():
                self.game.game_over = True
                self.draw_board()
                elapsed = int(time.time() - self.game.start_time)
                messagebox.showinfo("Победа!", f"Поздравляем! Вы выиграли!\nВремя: {elapsed} сек")
            else:
                self.draw_board()

    def right_click(self, event):
        """Обработка правого клика"""
        if self.game.game_over:
            return

        col = event.x // self.game.cell_size
        row = event.y // self.game.cell_size

        if 0 <= row < self.game.rows and 0 <= col < self.game.cols:
            self.game.toggle_flag(row, col)

            # Проверяем победу
            if self.game.check_win():
                self.game.game_over = True
                self.draw_board()
                elapsed = int(time.time() - self.game.start_time)
                messagebox.showinfo("Победа!", f"Поздравляем! Вы выиграли!\nВремя: {elapsed} сек")
            else:
                self.draw_board()

    def show_all_mines(self):
        """Показать все мины после проигрыша"""
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                if self.game.board[r][c] == -1:
                    self.game.visible[r][c] = True

    def give_hint(self):
        """Дать подсказку"""
        if not self.game.game_started or self.game.game_over or not self.game.hint_available:
            return

        hint = self.game.get_hint()
        if hint:
            row, col = hint
            self.game.hint_available = False
            self.hint_btn.config(state=tk.DISABLED)

            # Подсвечиваем клетку
            x1 = col * self.game.cell_size
            y1 = row * self.game.cell_size
            x2 = x1 + self.game.cell_size
            y2 = y1 + self.game.cell_size

            self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=3)

            # Снимаем подсветку через 2 секунды
            self.root.after(2000, self.draw_board)

    def auto_flag(self):
        """Автоматическая расстановка флагов"""
        if not self.game.game_started or self.game.game_over:
            return

        self.game.auto_flag()
        self.draw_board()

    def update_timer(self):
        """Обновление таймера"""
        if self.game.game_started and not self.game.game_over:
            elapsed = int(time.time() - self.game.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.timer_label.config(text=f"Время: {minutes:02d}:{seconds:02d}")

        # Повторяем каждую секунду
        self.root.after(1000, self.update_timer)

    def run(self):
        """Запуск игры"""
        self.root.mainloop()


# Запуск игры
if __name__ == "__main__":
    print("=" * 50)
    print("ИГРА 'САПЕР'")
    print("=" * 50)
    print("Управление:")
    print("• Левый клик - открыть клетку")
    print("• Правый клик - поставить/снять флаг")
    print("• H - подсказка (показать безопасную клетку)")
    print("• F - авто-флаги (расставить очевидные флаги)")
    print("• F2 - новая игра")
    print("• В меню 'Сложность' - выбор уровня сложности")
    print("=" * 50)

    app = MinesweeperGUI()
    app.run()