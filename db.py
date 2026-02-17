import mysql.connector as mysql
import hashlib

class MYSQL_Connection:
    def __init__(self, host, user, password, database):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }

    def get_connection(self):
        return mysql.connect(**self.config)

    def create_db_and_table(self):
        conn = mysql.connect(
            host=self.config["host"],
            user=self.config["user"],
            password=self.config["password"]
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS chatbot_results")
        conn.close()

        self.config["database"] = "chatbot_results"
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE,
                password VARCHAR(64)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                role VARCHAR(20),
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_info(id)
                ON DELETE CASCADE
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
            query = """
                INSERT INTO user_info (username, password)
                VALUES (%s, %s)
            """
            cursor.execute(query, (username, self.hash_password(password)))
            conn.commit()
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            conn.close()

    def login_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT id FROM user_info
            WHERE username = %s AND password = %s
        """
        cursor.execute(query, (username, self.hash_password(password)))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def reset_password (self , username , new_password):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "UPDATE user_info SET password = %s WHERE username = %s"
        cursor.execute(query,(self.hash_password(new_password),username))
        conn.commit()

        updated = cursor.rowcount
        conn.close()
        return updated>0

    def insert_message(self, user_id, role, message):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO chat_info (user_id, role, message)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (user_id, role, message))
        conn.commit()
        conn.close()

    def fetch_history(self, user_id, limit=20):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT role, message
            FROM chat_info
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT %s
        """
        cursor.execute(query, (user_id, limit))
        data = cursor.fetchall()
        conn.close()
        return data

    def clear_chat(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM chat_info WHERE user_id = %s",
            (user_id,)
        )
        conn.commit()
        conn.close()
