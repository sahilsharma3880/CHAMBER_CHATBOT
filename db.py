import sqlite3
import hashlib


class MYSQL_Connection:
    def __init__(self, database="chatbot_results.db"):
        self.database = database
        self.create_db_and_table()

    def get_connection(self):
        return sqlite3.connect(self.database)

    def create_db_and_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_info(id)
            )
        """)

        conn.commit()
        conn.close()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO user_info (username, password) VALUES (?, ?)",
                (username, self.hash_password(password))
            )
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()

    def login_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM user_info WHERE username = ? AND password = ?",
            (username, self.hash_password(password))
        )
        result = cursor.fetchone()
        conn.close()
        return result

    def reset_password(self, username, new_password):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE user_info SET password = ? WHERE username = ?",
            (self.hash_password(new_password), username)
        )
        conn.commit()
        updated = cursor.rowcount
        conn.close()
        return updated > 0

    def insert_message(self, user_id, role, message):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_info (user_id, role, message) VALUES (?, ?, ?)",
            (user_id, role, message)
        )
        conn.commit()
        conn.close()

    def fetch_history(self, user_id, limit=20):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, message FROM chat_info WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit)
        )
        data = cursor.fetchall()
        conn.close()
        return data

    def clear_chat(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM chat_info WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()
        conn.close()
