import tkinter as tk
from tkinter import messagebox
import random
from database import DBManager

WIDTH = 600
HEIGHT = 400
BODY_SIZE = 20


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Игра Змейка")

        self.db = DBManager()
        self.user_id = None
        self.username = None
        self.mode = "medium"

        # НАСТРОЙКИ КАСТОМИЗАЦИИ
        self.snake_color = "#48bb78"
        self.snake_outline = "#38a169"
        self.eye_color = "black"

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#2d3748")
        self.canvas.pack()

        self.root.bind_all("<KeyPress>", self.change_direction)
        self.root.bind_all("<Escape>", self.toggle_pause)

        self.bombs = []
        self.is_paused = False
        self.pause_elements = []

        self.show_menu()

    # --- ЭКРАН 1: ГЛАВНОЕ МЕНЮ ---
    def show_menu(self):
        self.canvas.delete("all")
        self.bombs = []
        self.is_paused = False
        self.pause_elements = []

        auth_text = self.username if self.user_id else "Войти в аккаунт"
        auth_color = "#48bb78" if self.user_id else "#4299e1"
        login_btn = self.canvas.create_text(
            90, 25, text=auth_text, fill=auth_color, font=("Arial", 12, "bold", "underline")
        )
        if not self.user_id:
            self.canvas.tag_bind(login_btn, "<Button-1>", lambda event: self.show_auth_screen())

        self.canvas.create_text(
            WIDTH // 2 - 80, HEIGHT // 2 - 100,
            text="ЗМЕЙКА", fill="#48bb78", font=("Arial", 36, "bold")
        )

        btn_play = tk.Button(
            self.root, text="ИГРАТЬ", font=("Arial", 14, "bold"), bg="#48bb78", fg="white",
            command=self.show_modes_screen
        )
        self.canvas.create_window(WIDTH // 2 - 80, HEIGHT // 2 - 20, window=btn_play, width=160, height=45)

        # МИНИ-ПОЛЕ КАСТОМИЗАЦИИ
        preview_bg = self.canvas.create_rectangle(
            WIDTH // 2 - 150, HEIGHT // 2 + 30, WIDTH // 2 - 10, HEIGHT // 2 + 130,
            fill="#1a202c", outline="#4a5568", width=2
        )
        preview_body = self.canvas.create_rectangle(
            WIDTH // 2 - 110, HEIGHT // 2 + 65, WIDTH // 2 - 70, HEIGHT // 2 + 95,
            fill=self.snake_color, outline=self.snake_outline
        )
        preview_eye1 = self.canvas.create_oval(
            WIDTH // 2 - 85, HEIGHT // 2 + 73, WIDTH // 2 - 80, HEIGHT // 2 + 78, fill=self.eye_color
        )
        preview_eye2 = self.canvas.create_oval(
            WIDTH // 2 - 85, HEIGHT // 2 + 82, WIDTH // 2 - 80, HEIGHT // 2 + 87, fill=self.eye_color
        )
        preview_text = self.canvas.create_text(
            WIDTH // 2 - 80, HEIGHT // 2 + 115, text="Кастомизация", fill="#cbd5e0", font=("Arial", 9)
        )

        for item in [preview_bg, preview_body, preview_eye1, preview_eye2, preview_text]:
            self.canvas.tag_bind(item, "<Button-1>", lambda event: self.show_customization_screen())

        # ТАБЛИЦА ЛИДЕРОВ
        self.canvas.create_text(480, 50, text=f"Топ-3 ({self.mode.upper()}):", fill="#ecc94b",
                                font=("Arial", 12, "bold"))

        top_3 = self.db.get_leaderboard(self.mode, limit=3)
        y_offset = 80
        for i, row in enumerate(top_3, 1):
            text_line = f"{i}. {row[0]:<12} — {row[1]}"
            self.canvas.create_text(480, y_offset, text=text_line, fill="white", font=("Courier", 11, "bold"))
            y_offset += 25

        all_leaders_btn = self.canvas.create_text(
            480, y_offset + 10, text="Посмотреть весь ТОП-100", fill="#4299e1", font=("Arial", 10, "underline")
        )
        self.canvas.tag_bind(all_leaders_btn, "<Button-1>", lambda event: self.show_leaderboard_window())

        self.canvas.create_text(480, y_offset + 40, text="Сменить режим топа:", fill="#cbd5e0", font=("Arial", 9))
        btn_ch_easy = tk.Button(self.root, text="Обыч.", font=("Arial", 8),
                                command=lambda: self.change_menu_top_mode("easy"))
        self.canvas.create_window(410, y_offset + 65, window=btn_ch_easy, width=50)
        btn_ch_med = tk.Button(self.root, text="Сред.", font=("Arial", 8),
                               command=lambda: self.change_menu_top_mode("medium"))
        self.canvas.create_window(480, y_offset + 65, window=btn_ch_med, width=50)
        btn_ch_hard = tk.Button(self.root, text="Слож.", font=("Arial", 8),
                                command=lambda: self.change_menu_top_mode("hard"))
        self.canvas.create_window(550, y_offset + 65, window=btn_ch_hard, width=50)

    def change_menu_top_mode(self, mode):
        self.mode = mode
        self.show_menu()

    # --- ЭКРАН 2: КАСТОМИЗАЦИЯ ---
    def show_customization_screen(self):
        self.canvas.delete("all")
        self.canvas.create_text(WIDTH // 2, 50, text="КАСТОМИЗАЦИЯ ЗМЕЙКИ", fill="#ecc94b", font=("Arial", 20, "bold"))

        self.canvas.create_rectangle(WIDTH // 2 - 40, 100, WIDTH // 2 + 40, 180, fill=self.snake_color,
                                     outline=self.snake_outline, width=2)
        self.canvas.create_oval(WIDTH // 2 + 15, 120, WIDTH // 2 + 25, 130, fill=self.eye_color)
        self.canvas.create_oval(WIDTH // 2 + 15, 150, WIDTH // 2 + 25, 160, fill=self.eye_color)

        self.canvas.create_text(WIDTH // 2 - 150, 230, text="Цвет чешуи:", fill="white", font=("Arial", 12, "bold"))
        colors_skin = [("#48bb78", "#38a169", "Зеленый"), ("#3182ce", "#2b6cb0", "Синий"),
                       ("#e53e3e", "#9b2c2c", "Красный"), ("#d69e2e", "#975a16", "Желтый")]

        x_btn = WIDTH // 2 - 40
        for skin, outline, name in colors_skin:
            btn = tk.Button(self.root, text=name, bg=skin, fg="white" if name != "Желтый" else "black",
                            command=lambda s=skin, o=outline: self.set_snake_color(s, o))
            self.canvas.create_window(x_btn, 230, window=btn, width=75)
            x_btn += 85

        self.canvas.create_text(WIDTH // 2 - 150, 290, text="Цвет глаз:", fill="white", font=("Arial", 12, "bold"))
        colors_eyes = ["black", "white", "yellow", "cyan"]

        x_btn = WIDTH // 2 - 40
        for color in colors_eyes:
            btn = tk.Button(self.root, text=color.upper(), bg=color,
                            fg="white" if color in ["black", "blue"] else "black",
                            command=lambda c=color: self.set_eye_color(c))
            self.canvas.create_window(x_btn, 290, window=btn, width=75)
            x_btn += 85

        btn_back = tk.Button(self.root, text="Сохранить и выйти", font=("Arial", 12, "bold"), bg="#48bb78", fg="white",
                             command=self.show_menu)
        self.canvas.create_window(WIDTH // 2, 360, window=btn_back, width=180, height=35)

    def set_snake_color(self, skin, outline):
        self.snake_color = skin
        self.snake_outline = outline
        self.show_customization_screen()

    def set_eye_color(self, color):
        self.eye_color = color
        self.show_customization_screen()

    # --- ЭКРАН 3: ВЫБОР СЛОЖНОСТИ ---
    def show_modes_screen(self):
        self.canvas.delete("all")
        btn_back_menu = tk.Button(self.root, text="← Назад", font=("Arial", 10), bg="#4a5568", fg="white",
                                  command=self.show_menu)
        self.canvas.create_window(60, 25, window=btn_back_menu, width=90)

        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 60, text="ВЫБЕРИТЕ СЛОЖНОСТЬ ИГРЫ", fill="white",
                                font=("Arial", 18, "bold"))

        btn_easy = tk.Button(self.root, text="Обычный", font=("Arial", 12, "bold"), bg="#4299e1", fg="white",
                             command=lambda: self.start_game("easy"))
        self.canvas.create_window(WIDTH // 2, HEIGHT // 2, window=btn_easy, width=180, height=35)

        btn_medium = tk.Button(self.root, text="Средний", font=("Arial", 12, "bold"), bg="#ecc94b", fg="black",
                               command=lambda: self.start_game("medium"))
        self.canvas.create_window(WIDTH // 2, HEIGHT // 2 + 50, window=btn_medium, width=180, height=35)

        btn_hard = tk.Button(self.root, text="Сложный", font=("Arial", 12, "bold"), bg="#f56565", fg="white",
                             command=lambda: self.start_game("hard"))
        self.canvas.create_window(WIDTH // 2, HEIGHT // 2 + 100, window=btn_hard, width=180, height=35)

    # --- ТАБЛИЦА ЛИДЕРОВ (ОКНО) ---
    def show_leaderboard_window(self):
        top_win = tk.Toplevel(self.root)
        top_win.title("Таблица лидеров")
        top_win.geometry("360x500")
        top_win.configure(bg="#2d3748")

        title_label = tk.Label(top_win, text=f"ТОП 100 — {self.mode.upper()}", font=("Arial", 14, "bold"), bg="#2d3748",
                               fg="#ecc94b")
        title_label.pack(pady=5)

        btn_frame = tk.Frame(top_win, bg="#2d3748")
        btn_frame.pack(pady=5)

        text_area = tk.Text(top_win, font=("Courier", 11, "bold"), bg="#1a202c", fg="white", bd=0, padx=15)
        text_area.pack(expand=True, fill="both", padx=15, pady=10)

        def refresh_leaderboard_content(target_mode):
            self.mode = target_mode
            title_label.config(text=f"ТОП 100 — {target_mode.upper()}")
            text_area.config(state=tk.NORMAL)
            text_area.delete("1.0", tk.END)

            leaders = self.db.get_leaderboard(target_mode, limit=100)
            if not leaders:
                text_area.insert(tk.END, f"{'№':<4}{'Игрок':<18}{'Рекорд':<6}\n")
                text_area.insert(tk.END, "-" * 30 + "\n")
                text_area.insert(tk.END, "\n      Записей пока нет...")
            else:
                text_area.insert(tk.END, f"{'№':<4}{'Игрок':<18}{'Рекорд':<6}\n")
                text_area.insert(tk.END, "-" * 30 + "\n")
                for i, row in enumerate(leaders, 1):
                    text_area.insert(tk.END, f"{i:<4}{row[0]:<18}{row[1]:<6}\n")
            text_area.config(state=tk.DISABLED)

        tk.Button(btn_frame, text="Обычный", font=("Arial", 9, "bold"), bg="#4299e1", fg="white",
                  command=lambda: refresh_leaderboard_content("easy")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Средний", font=("Arial", 9, "bold"), bg="#ecc94b", fg="black",
                  command=lambda: refresh_leaderboard_content("medium")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Сложный", font=("Arial", 9, "bold"), bg="#f56565", fg="white",
                  command=lambda: refresh_leaderboard_content("hard")).pack(side=tk.LEFT, padx=5)

        refresh_leaderboard_content(self.mode)

    # --- ЭКРАН 4: АВТОРИЗАЦИЯ ---
    def show_auth_screen(self):
        self.canvas.delete("all")
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 120, text="ВХОД В АККАУНТ", fill="#48bb78",
                                font=("Arial", 20, "bold"))
        self.canvas.create_text(WIDTH // 2 - 100, HEIGHT // 2 - 50, text="Логин:", fill="white", font=("Arial", 11))
        self.username_entry = tk.Entry(self.root, font=("Arial", 11))
        self.canvas.create_window(WIDTH // 2 + 30, HEIGHT // 2 - 50, window=self.username_entry, width=160)

        self.canvas.create_text(WIDTH // 2 - 100, HEIGHT // 2 - 10, text="Пароль:", fill="white", font=("Arial", 11))
        self.password_entry = tk.Entry(self.root, font=("Arial", 11), show="*")
        self.canvas.create_window(WIDTH // 2 + 30, HEIGHT // 2 - 10, window=self.password_entry, width=160)

        btn_login = tk.Button(self.root, text="Войти", font=("Arial", 11, "bold"), bg="#48bb78", fg="white",
                              command=self.handle_login)
        self.canvas.create_window(WIDTH // 2 - 80, HEIGHT // 2 + 40, window=btn_login, width=90)
        btn_register = tk.Button(self.root, text="Регистрация", font=("Arial", 11), bg="#4a5568", fg="white",
                                 command=self.handle_register)
        self.canvas.create_window(WIDTH // 2 + 20, HEIGHT // 2 + 40, window=btn_register, width=100)
        btn_back = tk.Button(self.root, text="Назад", font=("Arial", 11), bg="#718096", fg="white",
                             command=self.show_menu)
        self.canvas.create_window(WIDTH // 2 + 115, HEIGHT // 2 + 40, window=btn_back, width=60)

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        user_id = self.db.login_user(username, password)
        if user_id:
            self.user_id = user_id
            self.username = username
            self.show_menu()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def handle_register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        success = self.db.register_user(username, password)
        if success:
            messagebox.showinfo("У缺х", "Регистрация успешна! Войдите.")
        else:
            messagebox.showerror("Ошибка", "Имя уже занято")

    def toggle_pause(self, event):
        if not hasattr(self, 'game_over') or self.game_over:
            return
        if not hasattr(self, 'snake') or not self.snake:
            return

        self.is_paused = not self.is_paused

        if self.is_paused:
            rect = self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#1a202c", stipple="gray50")
            t1 = self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 30, text="ПАУЗА", fill="#ecc94b",
                                         font=("Arial", 32, "bold"))
            t2 = self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 20, text="Нажми ESC, чтобы продолжить", fill="white",
                                         font=("Arial", 12))

            btn_menu = tk.Button(self.root, text="Выйти в меню", font=("Arial", 11), bg="#f56565", fg="white",
                                 command=self.show_menu)
            b_win = self.canvas.create_window(WIDTH // 2, HEIGHT // 2 + 70, window=btn_menu, width=140)

            self.pause_elements = [rect, t1, t2, b_win]
        else:
            for el in self.pause_elements:
                self.canvas.delete(el)
            self.pause_elements = []
            self.move_snake()

    def start_game(self, mode):
        for bomb in self.bombs:
            self.canvas.delete(bomb)
        self.bombs = []

        self.mode = mode
        self.canvas.delete("all")
        self.direction = "Right"
        self.game_over = False
        self.is_paused = False
        self.pause_elements = []
        self.score = 0
        self.direction_locked = False

        if self.mode == "hard":
            self.speed = 100
        else:
            self.speed = 150

        self.create_objects()
        self.move_snake()

    def create_objects(self):
        self.snake = [
            self.canvas.create_rectangle(100, 100, 120, 120, fill=self.snake_color, outline=self.snake_outline),
            self.canvas.create_rectangle(80, 100, 100, 120, fill=self.snake_color, outline=self.snake_outline),
            self.canvas.create_rectangle(60, 100, 80, 120, fill=self.snake_color, outline=self.snake_outline)
        ]
        head_coords = self.canvas.coords(self.snake[0])
        self.eye1 = self.canvas.create_oval(head_coords[2] - 6, head_coords[1] + 3, head_coords[2] - 2,
                                            head_coords[1] + 7, fill=self.eye_color)
        self.eye2 = self.canvas.create_oval(head_coords[2] - 6, head_coords[3] - 7, head_coords[2] - 2,
                                            head_coords[3] - 3, fill=self.eye_color)

        self.apple = self.canvas.create_oval(300, 200, 320, 220, fill="#f56565", outline="#e53e3e")
        self.score_text = self.canvas.create_text(50, 20, text=f"Очки: {self.score}", fill="white",
                                                  font=("Arial", 14, "bold"))

    def change_direction(self, event):
        key = event.keysym
        if self.game_over and key == "space":
            self.start_game(self.mode)
            return

        if self.is_paused or self.direction_locked:
            return

        if key == "Left" and self.direction != "Right":
            self.direction = "Left";
            self.direction_locked = True
        elif key == "Right" and self.direction != "Left":
            self.direction = "Right";
            self.direction_locked = True
        elif key == "Up" and self.direction != "Down":
            self.direction = "Up";
            self.direction_locked = True
        elif key == "Down" and self.direction != "Up":
            self.direction = "Down";
            self.direction_locked = True

    def repaint_apple(self):
        random_x = random.randint(0, (WIDTH - BODY_SIZE) // BODY_SIZE) * BODY_SIZE
        random_y = random.randint(0, (HEIGHT - BODY_SIZE) // BODY_SIZE) * BODY_SIZE
        self.canvas.coords(self.apple, random_x, random_y, random_x + BODY_SIZE, random_y + BODY_SIZE)

    def spawn_bomb(self):
        random_x = random.randint(0, (WIDTH - BODY_SIZE) // BODY_SIZE) * BODY_SIZE
        random_y = random.randint(0, (HEIGHT - BODY_SIZE) // BODY_SIZE) * BODY_SIZE
        bomb = self.canvas.create_oval(random_x, random_y, random_x + BODY_SIZE, random_y + BODY_SIZE, fill="#1a202c",
                                       outline="#4a5568")
        self.bombs.append(bomb)

    def check_collisions(self, x1, y1):
        if self.mode != "easy":
            if x1 < 0 or x1 >= WIDTH or y1 < 0 or y1 >= HEIGHT: return True
        for segment in self.snake[1:]:
            seg_coords = self.canvas.coords(segment)
            if x1 == seg_coords[0] and y1 == seg_coords[1]: return True
        return False

    def move_snake(self):
        if self.game_over or self.is_paused:
            return

        self.direction_locked = False

        head_coords = self.canvas.coords(self.snake[0])
        x1, y1, x2, y2 = head_coords

        if self.direction == "Right":
            x1 += BODY_SIZE; x2 += BODY_SIZE
        elif self.direction == "Left":
            x1 -= BODY_SIZE; x2 -= BODY_SIZE
        elif self.direction == "Up":
            y1 -= BODY_SIZE; y2 -= BODY_SIZE
        elif self.direction == "Down":
            y1 += BODY_SIZE; y2 += BODY_SIZE

        if self.mode == "easy":
            if x1 < 0:
                x1 = WIDTH - BODY_SIZE; x2 = WIDTH
            elif x1 >= WIDTH:
                x1 = 0; x2 = BODY_SIZE
            elif y1 < 0:
                y1 = HEIGHT - BODY_SIZE; y2 = HEIGHT
            elif y1 >= HEIGHT:
                y1 = 0; y2 = BODY_SIZE

        if self.check_collisions(x1, y1):
            self.game_over = True
            if self.user_id:
                self.db.save_score(self.user_id, self.mode, self.score)

            self.canvas.delete(self.eye1)
            self.canvas.delete(self.eye2)

            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 40, text="GAME OVER", fill="#fc8181",
                                    font=("Arial", 30, "bold"))
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Нажми ПРОБЕЛ, чтобы повторить режим", fill="white",
                                    font=("Arial", 12))

            btn_menu = tk.Button(self.root, text="К Выбору Режима", font=("Arial", 11, "bold"), bg="#4a5568",
                                 fg="white", command=self.show_modes_screen)
            self.canvas.create_window(WIDTH // 2, HEIGHT // 2 + 50, window=btn_menu, width=160)
            return

        # --- КЛЮЧЕВОЙ МОМЕНТ 1: НАСТУПИЛИ НА БОМБУ ---
        hit_bomb = False
        for bomb in self.bombs:
            bomb_coords = self.canvas.coords(bomb)
            if x1 == bomb_coords[0] and y1 == bomb_coords[1]:
                hit_bomb = True
                self.canvas.delete(bomb)  # Удаляем с экрана
                self.bombs.remove(bomb)  # Удаляем только её из списка
                self.spawn_bomb()  # Пересоздаем только эту ОДНУ бомбу взамен съеденной
                break

        if hit_bomb:
            if self.score > 0: self.score -= 1
            self.canvas.itemconfig(self.score_text, text=f"Очки: {self.score}")
            if len(self.snake) > 1:
                last_segment = self.snake.pop()
                self.canvas.delete(last_segment)
            last_segment = self.snake.pop()
            self.canvas.coords(last_segment, x1, y1, x2, y2)
            self.snake.insert(0, last_segment)
        else:
            apple_coords = self.canvas.coords(self.apple)
            if x1 == apple_coords[0] and y1 == apple_coords[1]:
                new_head = self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.snake_color,
                                                        outline=self.snake_outline)
                self.snake.insert(0, new_head)
                self.repaint_apple()
                self.score += 1
                self.canvas.itemconfig(self.score_text, text=f"Очки: {self.score}")
                if self.mode != "easy" and self.speed > 50: self.speed -= 5

                # --- КЛЮЧЕВОЙ МОМЕНТ 2: СЪЕЛИ КРАСНЫЙ ФРУКТ ---
                # Запоминаем текущее количество бомб
                current_bombs_count = len(self.bombs)
                # Если на сложном режиме бомб еще нет, базово добавляем одну при первом яблоке
                if self.mode == "hard" and current_bombs_count == 0:
                    current_bombs_count = 1

                # Удаляем все старые бомбы с экрана
                for bomb in self.bombs:
                    self.canvas.delete(bomb)
                self.bombs = []

                # Спавним новые бомбы в том же количестве, но на новых местах (максимум 3 для сложного режима)
                if self.mode == "hard" and current_bombs_count < 3:
                    current_bombs_count += 1  # Постепенно увеличиваем число бомб до 3, как было в прошлой версии

                # На среднем режиме спавним 1, на сложном — сколько заслужили
                bombs_to_spawn = current_bombs_count if self.mode == "hard" else (1 if self.mode == "medium" else 0)
                for _ in range(bombs_to_spawn):
                    self.spawn_bomb()

            else:
                last_segment = self.snake.pop()
                self.canvas.coords(last_segment, x1, y1, x2, y2)
                self.snake.insert(0, last_segment)

        h_coords = self.canvas.coords(self.snake[0])
        if self.direction in ["Right", "Left"]:
            self.canvas.coords(self.eye1, h_coords[0] + 8, h_coords[1] + 3, h_coords[0] + 12, h_coords[1] + 7)
            self.canvas.coords(self.eye2, h_coords[0] + 8, h_coords[3] - 7, h_coords[0] + 12, h_coords[3] - 3)
        else:
            self.canvas.coords(self.eye1, h_coords[0] + 3, h_coords[1] + 8, h_coords[0] + 7, h_coords[1] + 12)
            self.canvas.coords(self.eye2, h_coords[2] - 7, h_coords[1] + 8, h_coords[2] - 3, h_coords[1] + 12)

        self.root.after(self.speed, self.move_snake)


if __name__ == "__main__":
    window = tk.Tk()
    game = SnakeGame(window)
    window.mainloop()