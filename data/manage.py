import sqlite3
import random

class UserDatabase:
    def __init__(self, db_name="Mikelangelo.sqlite"):
        self.db_name = db_name

    def __enter__(self):
        # Автоматически открываем соединение с базой данных при использовании with
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Автоматически закрываем соединение по завершении работы
        self.conn.close()

    def create_table(self):
        # Создание таблицы, если она не существует
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                telegram_id INTEGER UNIQUE NOT NULL,
                                username TEXT,
                                first_name TEXT,
                                last_name TEXT,
                                phone_number TEXT,
                                photo_id TEXT,
                                description TEXT,
                                city TEXT,
                                interests TEXT,
                                age INTEGER,
                                gender TEXT,
                                who_interest TEXT)''')
        self.conn.commit()

    def add_user(self, telegram_id, **kwargs):
        # Добавление нового пользователя (требуется только telegram_id, остальные поля опциональны)
        columns = "telegram_id" + (", " + ", ".join(kwargs.keys()) if kwargs else "")
        placeholders = "?" + (", " + ", ".join("?" for _ in kwargs) if kwargs else "")
        values = [telegram_id] + list(kwargs.values())
        
        query = f"INSERT INTO users ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()

    def update_user(self, telegram_id, **kwargs):
        # Обновление данных пользователя по telegram_id (требуется только telegram_id, остальные поля опциональны)
        if not kwargs:
            return  # Нечего обновлять
        fields = ", ".join(f"{key} = ?" for key in kwargs)
        values = list(kwargs.values()) + [telegram_id]
        query = f"UPDATE users SET {fields} WHERE telegram_id = ?"
        self.cursor.execute(query, values)
        self.conn.commit()

    def get_users_by_city(self, city):
        # Получение всех пользователей по городу
        self.cursor.execute("SELECT * FROM users WHERE city = ?", (city,))
        return self.cursor.fetchall()

    def get_users_by_age_range(self, min_age, max_age):
        # Получение всех пользователей в возрастном диапазоне
        self.cursor.execute("SELECT * FROM users WHERE age BETWEEN ? AND ?", (min_age, max_age))
        return self.cursor.fetchall()

    def get_user_by_telegram_id(self, telegram_id):
        # Получение пользователя по telegram_id
        self.cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        return self.cursor.fetchone()

    def delete_user(self, telegram_id):
        # Удаление пользователя по telegram_id
        self.cursor.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
        self.conn.commit()

    def get_all_users(self):
        # Получение всех пользователей
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()
    def save_photo(self, telegram_id, photo_data):
        # Сохранение фотографии пользователя по telegram_id
        self.cursor.execute('''
            UPDATE users SET photo = ? WHERE telegram_id = ?
        ''', (photo_data, telegram_id))
        self.conn.commit()
    def drop_table(self):
        # DROP TABLE BE CARFULE
        self.cursor.execute('DROP TABLE users')
        self.conn.commit()
        
class LikesDatabase:
    def __init__(self, db_name="Mikelangelo.sqlite"):
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS likes (
                                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                user_id_from INTEGER NOT NULL,
                                user_id_to INTEGER NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (user_id_from) REFERENCES users (telegram_id),
                                FOREIGN KEY (user_id_to) REFERENCES users (telegram_id))''')
        self.conn.commit()

    def add_like(self, user_id_from, user_id_to):
        self.cursor.execute('''
            INSERT INTO likes (user_id_from, user_id_to) VALUES (?, ?)
        ''', (user_id_from, user_id_to))
        self.conn.commit()
        
        self.cursor.execute('''
            SELECT 1 FROM likes WHERE user_id_from = ? AND user_id_to = ?
        ''', (user_id_to, user_id_from))
        mutual_like = self.cursor.fetchone()
        return mutual_like is not None

    def get_likes(self, user_id):
        self.cursor.execute('''
            SELECT user_id_to FROM likes WHERE user_id_from = ?
        ''', (user_id,))
        return self.cursor.fetchall()

    def get_mutual_likes(self, user_id):
        self.cursor.execute('''
            SELECT l1.user_id_to FROM likes l1
            JOIN likes l2 ON l1.user_id_to = l2.user_id_from
            WHERE l1.user_id_from = ? AND l2.user_id_to = ?
        ''', (user_id, user_id))
        return self.cursor.fetchall()

    def get_liked_users(self, user_id):
        self.cursor.execute('''
            SELECT user_id_to FROM likes WHERE user_id_from = ?
        ''', (user_id,))
        return self.cursor.fetchall()

    def get_users_who_liked(self, user_id):
        self.cursor.execute('''
            SELECT user_id_from FROM likes WHERE user_id_to = ?
        ''', (user_id,))
        return self.cursor.fetchall()


class RecommendationSystem:
    def __init__(self, user_db, likes_db):
        self.user_db = user_db
        self.likes_db = likes_db

    def get_recommendations(self, user_id, limit=10):
        user = self.user_db.get_user_by_telegram_id(user_id)
        if not user:
            return []

        city = user[8]  # city field
        age = user[10]  # age field
        gender = user[11]  # gender field
        who_interest = user[12]  # who_interest field

        # Получаем всех пользователей, соответствующих предпочтениям
        candidates = self.user_db.cursor.execute('''
            SELECT * FROM users
            WHERE city = ? AND age BETWEEN ? AND ? AND gender = ?
            AND telegram_id != ?
        ''', (city, age - 5, age + 5, who_interest, user_id)).fetchall()

        # Получаем пользователей, которых уже лайкнули
        liked_users = set(like[0] for like in self.likes_db.get_likes(user_id))

        # Исключаем уже лайкнутых пользователей
        recommendations = [candidate for candidate in candidates if candidate[1] not in liked_users]

        # Перемешиваем рекомендации и ограничиваем их количество
        random.shuffle(recommendations)
        return recommendations[:limit]


# with UserDatabase('Mikelangelo.sqlite') as db:
#     db.create_table()
    
# conn = sqlite3.connect('Mikelangelo.sqlite')
# cursor = conn.cursor()
# cursor.execute('DROP TABLE users')
# conn.commit()
# conn.close()