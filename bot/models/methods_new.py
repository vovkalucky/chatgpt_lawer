import sqlite3
from aiogram import types
from bot.config_data.config import load_config
from datetime import datetime, timedelta
config = load_config()


class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS users(user_id PRIMARY KEY, username TEXT, date_enter DATETIME, 
            request_count INTEGER, premium BOOLEAN, date_of_pay DATETIME, subscribe BOOLEAN)""")
        self.conn.commit()

    def sql_add_user(self, message: types.Message):
        try:
            user_id = message.chat.id
            username = message.chat.username
            date_enter = message.date.strftime('%Y-%m-%d')
            request_count = config.tg_bot.request_count #на текущий момент 8 запросов
            premium = message.from_user.is_premium
            date_of_pay = None
            subscribe = True
            # Проверка наличия пользователя
            self.cur.execute('SELECT * FROM users WHERE user_id == ?', (user_id,))
            result = self.cur.fetchone()
            if result is None:
                self.cur.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?)', (user_id, username, date_enter, request_count, premium, date_of_pay, subscribe))
                self.conn.commit()
        except sqlite3.Error as error:
            print("Error:", error)
        finally:
            if self.conn:
                self.conn.close()

    # async def sql_group_add_user(self, message: types.Message):
    #     try:
    #         user_id = message.from_user.id
    #         username = message.from_user.username
    #         date_enter = message.date
    #         request_count = config.tg_bot.request_count #на текущий момент 8 запросов
    #         premium = message.from_user.is_premium
    #
    #         # Проверка наличия пользователя
    #         self.cur.execute('SELECT * FROM users WHERE user_id == ?', (user_id,))
    #         result = self.cur.fetchone()
    #         if result is None:
    #             self.cur.execute('INSERT INTO users VALUES (?,?,?,?,?)', (user_id, username, date_enter, request_count, premium))
    #             self.conn.commit()
    #     except sqlite3.Error as error:
    #         print("Error:", error)
    #     finally:
    #         if self.conn:
    #             self.conn.close()

    async def remove_user_from_database(self, user_id: int):
        try:
            query = "DELETE FROM users WHERE user_id = ?"
            self.cur.execute(query, (user_id,))
            self.conn.commit()
        except sqlite3.Error as error:
            print("Error:", error)
        finally:
            if self.conn:
                self.conn.close()

    async def minus_request_count(self, message: types.Message | types.CallbackQuery):
        try:
            user_id = message.from_user.id
            self.cur.execute("""UPDATE users SET request_count = request_count - 1 WHERE user_id = ?""", (user_id,))
            self.conn.commit()
        except sqlite3.Error as error:
            print("Error:", error)
        finally:
            if self.conn:
                self.conn.close()

    async def check_user_request_count(self, message: types.Message | types.CallbackQuery):
        try:
            user_id = message.from_user.id
            request_count_tuple = self.cur.execute("SELECT request_count FROM users WHERE user_id = ?", (user_id,)).fetchone()
            request_count = request_count_tuple[0]
            return request_count
        except sqlite3.Error as error:
            print("Error:", error)
        finally:
            if self.conn:
                self.conn.close()

    async def get_users(self):
        try:
            count_users = self.cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            all_users = self.cur.execute("SELECT * FROM users").fetchall()
            return count_users, all_users
        except sqlite3.Error as error:
            print("Error:", error)
        finally:
            if self.conn:
                self.conn.close()

    async def count_user_for_period(self, days: int):
        # Определяем начало и конец последней недели
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Преобразовываем даты к нужному формату для SQLite (YYYY-MM-DD)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        try:
            count_users = self.cur.execute("SELECT COUNT(*) FROM users WHERE date_enter BETWEEN ? AND ?", (start_date_str, end_date_str)).fetchone()[0]
            return count_users
        except sqlite3.Error as error:
            print("Error:", error)
        finally:
            if self.conn:
                self.conn.close()

    async def count_premium_users(self):
        try:
            count_premium_users = self.cur.execute("SELECT COUNT(*) FROM users WHERE premium NOT NULL").fetchone()[0]
            return count_premium_users
        except sqlite3.Error as error:
            print("Error:", error)
        finally:
            if self.conn:
                self.conn.close()

    async def check_subscribe(self, message: types.Message | types.CallbackQuery):
        try:
            user_id = message.from_user.id
            request_count_tuple = self.cur.execute("SELECT subscribe FROM users WHERE user_id = ?", (user_id,)).fetchone()
            subscribe_status = request_count_tuple[0]
            return subscribe_status
        except sqlite3.Error as error:
            print("Error:", error)
        finally:
            if self.conn:
                self.conn.close()

    async def edit_subscribe(self, message: types.Message | types.CallbackQuery):
        try:
            user_id = message.from_user.id
            self.cur.execute("""UPDATE users SET subscribe = False WHERE user_id = ?""", (user_id,))
            self.conn.commit()
        except sqlite3.Error as error:
            print("Error:", error)
        finally:
            if self.conn:
                self.conn.close()




