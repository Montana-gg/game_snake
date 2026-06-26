import tkinter as tk
import random

WIDTH = 600
HEIGHT = 400
BODY_SIZE = 20


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Игра Змейка")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#2d3748")
        self.canvas.pack()

        self.root.bind_all("<KeyPress>", self.change_direction)

        # Список для хранения ID объектов-бомб на холсте
        self.bombs = []

        self.show_menu()

    def show_menu(self):
        self.canvas.delete("all")
        self.bombs = []  # Очищаем список бомб при выходе в меню

        self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 - 100,
            text="ЗМЕЙКА: ВЫБЕРИТЕ СЛОЖНОСТЬ",
            fill="#48bb78",
            font=("Arial", 20, "bold")
        )

        btn_easy = tk.Button(
            self.root, text="Обычный", font=("Arial", 12, "bold"), bg="#4299e1", fg="white",
            command=lambda: self.start_game("easy")
        )
        self.canvas.create_window(WIDTH // 2, HEIGHT // 2 - 30, window=btn_easy, width=150)

        btn_medium = tk.Button(
            self.root, text="Средний", font=("Arial", 12, "bold"), bg="#ecc94b", fg="black",
            command=lambda: self.start_game("medium")
        )
        self.canvas.create_window(WIDTH // 2, HEIGHT // 2 + 20, window=btn_medium, width=150)

        btn_hard = tk.Button(
            self.root, text="Сложный", font=("Arial", 12, "bold"), bg="#f56565", fg="white",
            command=lambda: self.start_game("hard")
        )
        self.canvas.create_window(WIDTH // 2, HEIGHT // 2 + 70, window=btn_hard, width=150)

    def start_game(self, mode):
        # Удаляем старые бомбы из памяти холста перед перезапуском
        for bomb in self.bombs:
            self.canvas.delete(bomb)
        self.bombs = []

        self.mode = mode
        self.canvas.delete("all")

        self.direction = "Right"
        self.game_over = False
        self.score = 0

        if self.mode == "hard":
            self.speed = 100
        else:
            self.speed = 150

        self.create_objects()
        self.move_snake()

    def create_objects(self):
        self.snake = [
            self.canvas.create_rectangle(100, 100, 120, 120, fill="#48bb78", outline="#38a169"),
            self.canvas.create_rectangle(80, 100, 100, 120, fill="#38a169", outline="#2f855a"),
            self.canvas.create_rectangle(60, 100, 80, 120, fill="#38a169", outline="#2f855a")
        ]
        self.apple = self.canvas.create_oval(300, 200, 320, 220, fill="#f56565", outline="#e53e3e")

        self.score_text = self.canvas.create_text(
            50, 20, text=f"Очки: {self.score}", fill="white", font=("Arial", 14, "bold")
        )

    def change_direction(self, event):
        key = event.keysym

        # Если игра окончена и нажат Пробел — перезапускаем ТОТ ЖЕ режим
        if self.game_over and key == "space":
            self.start_game(self.mode)
            return

        if key == "Left" and self.direction != "Right":
            self.direction = "Left"
        elif key == "Right" and self.direction != "Left":
            self.direction = "Right"
        elif key == "Up" and self.direction != "Down":
            self.direction = "Up"
        elif key == "Down" and self.direction != "Up":
            self.direction = "Down"

    def repaint_apple(self):
        random_x = random.randint(0, (WIDTH - BODY_SIZE) // BODY_SIZE) * BODY_SIZE
        random_y = random.randint(0, (HEIGHT - BODY_SIZE) // BODY_SIZE) * BODY_SIZE
        self.canvas.coords(self.apple, random_x, random_y, random_x + BODY_SIZE, random_y + BODY_SIZE)

    # --- МЕХАНИКА СЛОЖНОГО РЕЖИМА: СПАВН БОМБЫ ---
    def spawn_bomb(self):
        # Генерируем координаты так, чтобы они не накладывались на голову змейки напрямую
        random_x = random.randint(0, (WIDTH - BODY_SIZE) // BODY_SIZE) * BODY_SIZE
        random_y = random.randint(0, (HEIGHT - BODY_SIZE) // BODY_SIZE) * BODY_SIZE

        # Создаем черную ягоду-бомбу
        bomb = self.canvas.create_oval(
            random_x, random_y, random_x + BODY_SIZE, random_y + BODY_SIZE,
            fill="#1a202c", outline="#4a5568"
        )
        self.bombs.append(bomb)

    def check_collisions(self, x1, y1):
        # В Обычном режиме (easy) столкновение со стенами НЕ убивает
        if self.mode != "easy":
            if x1 < 0 or x1 >= WIDTH or y1 < 0 or y1 >= HEIGHT:
                return True

        # Столкновение со своим телом всегда смертельно
        for segment in self.snake[1:]:
            seg_coords = self.canvas.coords(segment)
            if x1 == seg_coords[0] and y1 == seg_coords[1]:
                return True
        return False

    def move_snake(self):
        if self.game_over:
            return

        head_coords = self.canvas.coords(self.snake[0])
        x1, y1, x2, y2 = head_coords

        if self.direction == "Right":
            x1 += BODY_SIZE;
            x2 += BODY_SIZE
        elif self.direction == "Left":
            x1 -= BODY_SIZE;
            x2 -= BODY_SIZE
        elif self.direction == "Up":
            y1 -= BODY_SIZE;
            y2 -= BODY_SIZE
        elif self.direction == "Down":
            y1 += BODY_SIZE;
            y2 += BODY_SIZE

        # --- МЕХАНИКА ОБЫЧНОГО РЕЖИМА: ТЕЛЕПОРТАЦИЯ СКВОЗЬ СТЕНЫ ---
        if self.mode == "easy":
            if x1 < 0:
                x1 = WIDTH - BODY_SIZE;
                x2 = WIDTH
            elif x1 >= WIDTH:
                x1 = 0;
                x2 = BODY_SIZE
            elif y1 < 0:
                y1 = HEIGHT - BODY_SIZE;
                y2 = HEIGHT
            elif y1 >= HEIGHT:
                y1 = 0;
                y2 = BODY_SIZE

        # Проверка на проигрыш
        if self.check_collisions(x1, y1):
            self.game_over = True
            self.canvas.create_text(
                WIDTH // 2, HEIGHT // 2 - 40, text="GAME OVER", fill="#fc8181", font=("Arial", 30, "bold")
            )
            self.canvas.create_text(
                WIDTH // 2, HEIGHT // 2, text="Нажми ПРОБЕЛ, чтобы повторить режим", fill="white", font=("Arial", 12)
            )

            # Кнопка возврата в главное меню поверх холста
            btn_menu = tk.Button(
                self.root, text="В Главное Меню", font=("Arial", 11, "bold"), bg="#4a5568", fg="white",
                command=self.show_menu
            )
            self.canvas.create_window(WIDTH // 2, HEIGHT // 2 + 50, window=btn_menu, width=160)
            return

        # --- МЕХАНИКА СЛОЖНОГО РЕЖИМА: ПРОВЕРКА НА БОМБЫ ---
        hit_bomb = False
        for bomb in self.bombs:
            bomb_coords = self.canvas.coords(bomb)
            if x1 == bomb_coords[0] and y1 == bomb_coords[1]:
                hit_bomb = True
                # Удаляем съеденную бомбу с экрана и из списка
                self.canvas.delete(bomb)
                self.bombs.remove(bomb)
                break

        if hit_bomb:
            # Если поймали бомбу: отнимаем очко (но не уходим в минус)
            if self.score > 0:
                self.score -= 1
            self.canvas.itemconfig(self.score_text, text=f"Очки: {self.score}")

            # Уменьшаем длину: удаляем хвост с экрана и из списка
            if len(self.snake) > 1:
                last_segment = self.snake.pop()
                self.canvas.delete(last_segment)

            # Двигаем оставшуюся змейку вперед обычным образом
            last_segment = self.snake.pop()
            self.canvas.coords(last_segment, x1, y1, x2, y2)
            self.snake.insert(0, last_segment)

        else:
            # Логика поедания обычного яблока
            apple_coords = self.canvas.coords(self.apple)
            if x1 == apple_coords[0] and y1 == apple_coords[1]:
                new_head = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#48bb78", outline="#38a169")
                self.snake.insert(0, new_head)
                self.repaint_apple()

                self.score += 1
                self.canvas.itemconfig(self.score_text, text=f"Очки: {self.score}")

                if self.mode != "easy" and self.speed > 50:
                    self.speed -= 5

                # В сложном режиме спавним бомбу по мере роста змейки (если бомб меньше 3)
                if self.mode == "hard" and len(self.bombs) < 3:
                    self.spawn_bomb()
            else:
                last_segment = self.snake.pop()
                self.canvas.coords(last_segment, x1, y1, x2, y2)
                self.snake.insert(0, last_segment)

        self.root.after(self.speed, self.move_snake)


if __name__ == "__main__":
    window = tk.Tk()
    game = SnakeGame(window)
    window.mainloop()