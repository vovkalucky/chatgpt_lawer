import sqlite3 as sq
from aiogram import types
from bot.config_data.config import load_config
from datetime import datetime, timedelta
config = load_config()


async def sql_add_user(message):
    conn = sq.connect('chatgpt.db')
    cur = conn.cursor()
    # if conn:
    #     print('Database connect OK')
    cur.execute("""CREATE TABLE IF NOT EXISTS users(user_id PRIMARY KEY, username TEXT, date_enter DATETIME, request_count INTEGER, premium BOOLEAN, date_of_pay DATETIME, subscribe BOOLEAN)""")
    conn.commit()
    try:
        user_id = message.chat.id
        username = message.chat.username
        date_enter = message.date.strftime('%Y-%m-%d')
        request_count = config.tg_bot.request_count #на текущий момент 8 запросов
        premium = message.from_user.is_premium
        date_of_pay = None
        subscribe = True
        # Проверка наличия пользователя
        cur.execute('SELECT * FROM users WHERE user_id == ?', (user_id,))
        result = cur.fetchone()
        if result is None:
            cur.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?)', (user_id, username, date_enter, request_count, premium, date_of_pay, subscribe))
            conn.commit()
            #print('Новый пользователь добавлен в базу')
        # else:
        #     print("Пользователь уже существует в таблице.")

    except sq.Error as error:
        print("Error:", error)
    finally:
        if conn:
            conn.close()


async def sql_group_add_user(message):
    conn = sq.connect('chatgpt.db')
    cur = conn.cursor()
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        date_enter = message.date
        request_count = config.tg_bot.request_count #на текущий момент 8 запросов
        premium = message.from_user.is_premium

        # Проверка наличия пользователя
        cur.execute('SELECT * FROM users WHERE user_id == ?', (user_id,))
        result = cur.fetchone()
        if result is None:
            cur.execute('INSERT INTO users VALUES (?,?,?,?,?)', (user_id, username, date_enter, request_count, premium))
            conn.commit()
            #print('Новый пользователь добавлен в базу')
        # else:
        #     print("Значение user_id уже существует в таблице.")

    except sq.Error as error:
        print("Error:", error)
    finally:
        if conn:
            conn.close()


async def remove_user_from_database(user_id: int):
    conn = sq.connect('chatgpt.db')
    cur = conn.cursor()
    try:
        query = "DELETE FROM users WHERE user_id = ?"
        cur.execute(query, (user_id,))
        conn.commit()
        #print('Пользователь удален из базы')
    except sq.Error as error:
        print("Error:", error)
    finally:
        if conn:
            conn.close()


async def minus_request_count(message: types.Message | types.CallbackQuery):
    conn = sq.connect('chatgpt.db')
    cur = conn.cursor()
    try:
        user_id = message.from_user.id
        cur.execute("""UPDATE users SET request_count = request_count - 1 WHERE user_id = ?""", (user_id,))
        conn.commit()
    except sq.Error as error:
        print("Error:", error)
    finally:
        if conn:
            conn.close()


async def check_user_request_count(message: types.Message | types.CallbackQuery):
    conn = sq.connect('chatgpt.db')
    cur = conn.cursor()
    try:
        user_id = message.from_user.id
        request_count_tuple = cur.execute("SELECT request_count FROM users WHERE user_id = ?", (user_id,)).fetchone()
        request_count = request_count_tuple[0]
        return request_count
    except sq.Error as error:
        print("Error:", error)
    finally:
        if conn:
            conn.close()


async def get_users():
    conn = sq.connect('chatgpt.db')
    cur = conn.cursor()
    try:
        count_users = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        all_users = cur.execute("SELECT * FROM users").fetchall()
        return count_users, all_users
    except sq.Error as error:
        print("Error:", error)
    finally:
        if conn:
            conn.close()


async def count_user_for_period(days: int):
    conn = sq.connect('chatgpt.db')
    cur = conn.cursor()
    # Определяем начало и конец последней недели
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Преобразовываем даты к нужному формату для SQLite (YYYY-MM-DD)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    try:
        count_users = cur.execute("SELECT COUNT(*) FROM users WHERE date_enter BETWEEN ? AND ?", (start_date_str, end_date_str)).fetchone()[0]
        return count_users
    except sq.Error as error:
        print("Error:", error)
    finally:
        if conn:
            conn.close()


async def count_premium_users():
    conn = sq.connect('chatgpt.db')
    cur = conn.cursor()

    try:
        count_premium_users = cur.execute("SELECT COUNT(*) FROM users WHERE premium NOT NULL").fetchone()[0]
        return count_premium_users
    except sq.Error as error:
        print("Error:", error)
    finally:
        if conn:
            conn.close()


async def check_subscribe(message: types.Message | types.CallbackQuery):
    conn = sq.connect('chatgpt.db')
    cur = conn.cursor()

    try:
        user_id = message.from_user.id
        request_count_tuple = cur.execute("SELECT subscribe FROM users WHERE user_id = ?", (user_id,)).fetchone()
        subscribe_status = request_count_tuple[0]
        print(f"в chech_subscribe {subscribe_status}")
        return subscribe_status
    except sq.Error as error:
        print("Error:", error)
    finally:
        if conn:
            conn.close()

async def edit_subscribe(user_id: int):
    conn = sq.connect('chatgpt.db')
    cur = conn.cursor()

    try:
        request_count_tuple = cur.execute("SELECT subscribe FROM users WHERE user_id = ?", (user_id,)).fetchone()
        subscribe_status = request_count_tuple[0]
        if subscribe_status:
            cur.execute("""UPDATE users SET subscribe = False WHERE user_id = ?""", (user_id,))
            conn.commit()
        else:
            cur.execute("""UPDATE users SET subscribe = True WHERE user_id = ?""", (user_id,))
            conn.commit()
    except sq.Error as error:
        print("Error:", error)
    finally:
        if conn:
            conn.close()




