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

        # Слушаем стрелочки для управления и Пробел для перезапуска
        self.root.bind_all("<KeyPress>", self.change_direction)

        # Запускаем игру в первый раз
        self.start_game()

    # --- СБРОС И ЗАПУСК ИГРЫ ---
    def start_game(self):
        # Очищаем холст от старых надписей, змейки и яблок
        self.canvas.delete("all")

        # Сбрасываем настройки к начальным
        self.direction = "Right"
        self.game_over = False
        self.score = 0
        self.speed = 150

        # Пересоздаем объекты
        self.create_objects()

        # Запускаем цикл движения
        self.move_snake()

    def create_objects(self):
        self.snake = [
            self.canvas.create_rectangle(100, 100, 120, 120, fill="#48bb78", outline="#38a169"),
            self.canvas.create_rectangle(80, 100, 100, 120, fill="#38a169", outline="#2f855a"),
            self.canvas.create_rectangle(60, 100, 80, 120, fill="#38a169", outline="#2f855a")
        ]
        self.apple = self.canvas.create_oval(300, 200, 320, 220, fill="#f56565", outline="#e53e3e")

        self.score_text = self.canvas.create_text(
            50, 20,
            text=f"Очки: {self.score}",
            fill="white",
            font=("Arial", 14, "bold")
        )

    def change_direction(self, event):
        key = event.keysym

        # Если игра окончена и нажат Пробел — перезапускаем
        if self.game_over and key == "space":
            self.start_game()
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

    def check_collisions(self, x1, y1):
        if x1 < 0 or x1 >= WIDTH or y1 < 0 or y1 >= HEIGHT:
            return True
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

        if self.check_collisions(x1, y1):
            self.game_over = True
            self.canvas.create_text(
                WIDTH // 2, HEIGHT // 2 - 20,
                text="GAME OVER",
                fill="#fc8181",
                font=("Arial", 30, "bold")
            )
            # Добавляем подсказку для игрока
            self.canvas.create_text(
                WIDTH // 2, HEIGHT // 2 + 20,
                text="Нажми ПРОБЕЛ, чтобы начать заново",
                fill="white",
                font=("Arial", 14)
            )
            return

        apple_coords = self.canvas.coords(self.apple)
        if x1 == apple_coords[0] and y1 == apple_coords[1]:
            new_head = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#48bb78", outline="#38a169")
            self.snake.insert(0, new_head)
            self.repaint_apple()

            self.score += 1
            self.canvas.itemconfig(self.score_text, text=f"Очки: {self.score}")

            if self.speed > 50:
                self.speed -= 5
        else:
            last_segment = self.snake.pop()
            self.canvas.coords(last_segment, x1, y1, x2, y2)
            self.snake.insert(0, last_segment)

        self.root.after(self.speed, self.move_snake)


if __name__ == "__main__":
    window = tk.Tk()
    game = SnakeGame(window)
    window.mainloop()