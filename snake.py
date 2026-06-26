import tkinter as tk
import random

# --- НАСТРОЙКИ ИГРЫ ---
WIDTH = 600
HEIGHT = 400
BODY_SIZE = 20


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Игра Змейка")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#2d3748")
        self.canvas.pack()

        self.direction = "Right"

        # Переменная, которая следит, идет игра или уже закончена
        self.game_over = False

        self.create_objects()

        self.root.bind_all("<KeyPress>", self.change_direction)
        self.move_snake()

    def create_objects(self):
        self.snake = [
            self.canvas.create_rectangle(100, 100, 120, 120, fill="#48bb78", outline="#38a169"),
            self.canvas.create_rectangle(80, 100, 100, 120, fill="#38a169", outline="#2f855a"),
            self.canvas.create_rectangle(60, 100, 80, 120, fill="#38a169", outline="#2f855a")
        ]
        self.apple = self.canvas.create_oval(300, 200, 320, 220, fill="#f56565", outline="#e53e3e")

    def change_direction(self, event):
        key = event.keysym
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

    # --- НОВАЯ ФУНКЦИЯ: ПРОВЕРКА СТОЛКНОВЕНИЙ ---
    def check_collisions(self, x1, y1):
        # 1. Проверяем столкновение со стенами
        if x1 < 0 or x1 >= WIDTH or y1 < 0 or y1 >= HEIGHT:
            return True

        # 2. Проверяем столкновение со своим телом
        # Мы перебираем все сегменты змейки, кроме головы (начиная с индекса 1)
        for segment in self.snake[1:]:
            seg_coords = self.canvas.coords(segment)
            if x1 == seg_coords[0] and y1 == seg_coords[1]:
                return True

        return False

    def move_snake(self):
        # Если игра уже завершена, останавливаем цикл анимации
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

        # --- ОБНОВЛЕНИЕ: ПРОВЕРЯЕМ НА ПРОИГРЫШ ---
        if self.check_collisions(x1, y1):
            self.game_over = True
            # Рисуем текст по центру экрана
            self.canvas.create_text(
                WIDTH // 2, HEIGHT // 2,
                text="GAME OVER",
                fill="#fc8181",
                font=("Arial", 30, "bold")
            )
            return  # Выходим из функции, движение прекращается

        # Логика поедания яблока (осталась прежней)
        apple_coords = self.canvas.coords(self.apple)
        if x1 == apple_coords[0] and y1 == apple_coords[1]:
            new_head = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#48bb78", outline="#38a169")
            self.snake.insert(0, new_head)
            self.repaint_apple()
        else:
            last_segment = self.snake.pop()
            self.canvas.coords(last_segment, x1, y1, x2, y2)
            self.snake.insert(0, last_segment)

        self.root.after(150, self.move_snake)


if __name__ == "__main__":
    window = tk.Tk()
    game = SnakeGame(window)
    window.mainloop()