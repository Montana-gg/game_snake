import hashlib
import os  # Нужен для чтения переменных из системы
import psycopg2
from dotenv import load_dotenv  # Импортируем загрузчик .env

# Загружаем переменные из файла .env в систему
load_dotenv()


class DBManager:

    def __init__(self):
        # Теперь вместо строк мы используем os.getenv(), который берет данные из скрытого файла .env
        self.conn_params = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
        }
        self.create_tables()

    def get_connect(self):
        conn = psycopg2.connect(**self.conn_params)
        cursor = conn.cursor()
        return conn, cursor

    def create_tables(self):
        """Создание таблиц"""
        conn, cursor = self.get_connect()
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS scores (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                mode VARCHAR(20) NOT NULL,
                score INTEGER NOT NULL,
                CONSTRAINT unique_user_mode UNIQUE (user_id, mode)
            );
            """,
        ]
        try:
            for query in queries:
                cursor.execute(query)
            conn.commit()
            print("База данных успешно инициализирована.")
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    # --- НОВЫЙ МЕТОД: ХЭШИРОВАНИЕ ПАРОЛЯ ---
    def _hash_password(self, password):
        """Превращает строку-пароль в безопасный SHA-256 хэш"""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    # --- НОВЫЙ МЕТОД: РЕГИСТРАЦИЯ ---
    def register_user(self, username, password):
        """Регистрирует нового пользователя. Возвращает True, если успешно"""
        conn, cursor = self.get_connect()
        hashed_password = self._hash_password(password)

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s);",
                (username, hashed_password),
            )
            conn.commit()
            return True
        except psycopg2.errors.UniqueViolation:
            # Если такой username уже есть в базе (сработало ограничение UNIQUE)
            print("Пользователь с таким именем уже существует.")
            conn.rollback()
            return False
        except Exception as e:
            print(f"Ошибка при регистрации: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    # --- НОВЫЙ МЕТОД: ВХОД (АВТОРИЗАЦИЯ) ---
    def login_user(self, username, password):
        """Проверяет логин и пароль. Возвращает user_id, если всё ок, или None"""
        conn, cursor = self.get_connect()
        hashed_password = self._hash_password(password)

        try:
            cursor.execute(
                "SELECT id, password FROM users WHERE username = %s;",
                (username,),
            )
            user_data = cursor.fetchone()  # Получаем одну строку из результата

            if user_data:
                db_user_id, db_hashed_password = user_data
                # Сравниваем хэш введенного пароля с хэшем из базы данных
                if hashed_password == db_hashed_password:
                    return db_user_id  # Пароль совпал, возвращаем ID пользователя

            return None  # Пользователь не найден или пароль неверный
        except Exception as e:
            print(f"Ошибка при входе: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def save_score(self, user_id, mode, score):
        """Сохраняет или обновляет рекорд пользователя для конкретного режима"""
        conn, cursor = self.get_connect()
        try:
            # Используем UPSERT (INSERT ... ON CONFLICT DO UPDATE)
            cursor.execute("""
                INSERT INTO scores (user_id, mode, score) 
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, mode) 
                DO UPDATE SET score = GREATEST(scores.score, EXCLUDED.score);
            """, (user_id, mode, score))
            conn.commit()
        except Exception as e:
            print(f"Ошибка при сохранении рекорда: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def get_leaderboard(self, mode, limit=100):
        """Возвращает список кортежей (username, score) для указанного режима, отсортированный по убыванию"""
        conn, cursor = self.get_connect()
        try:
            cursor.execute("""
                SELECT u.username, s.score 
                FROM scores s
                JOIN users u ON s.user_id = u.id
                WHERE s.mode = %s
                ORDER BY s.score DESC
                LIMIT %s;
            """, (mode, limit))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении таблицы лидеров: {e}")
            return []
        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    db = DBManager()
