import datetime
import sqlite3
from sqlite3 import IntegrityError
import os

connect = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'db.sqlite'), check_same_thread=False)
cursor = connect.cursor()


def add_user(user_id: int, username: str) -> bool:
    try:
        add_new_sender_id(user_id)
        cursor.execute('INSERT INTO USERS VALUES(?, ?)', (user_id, username))
        connect.commit()
        return True
    except IntegrityError:
        return False


def add_new_user_stat():
    stat = get_today_stat()
    cursor.execute('UPDATE stats set add_user_count=? where date=?', (stat[1]+1, stat[0]))
    connect.commit()


def get_today_stat():
    date = datetime.datetime.now().strftime('%D')
    res = cursor.execute('SELECT * FROM stats where date=?', (date, )).fetchone()

    if not res:
        cursor.execute('INSERT INTO stats VALUES(?, ?, ?)', (date, 0, 0))
        connect.commit()
        return get_today_stat()

    return res


def add_new_blocked_stat():
    stat = get_today_stat()
    cursor.execute('UPDATE stats set block_user_count=? where date=?', (stat[2] + 1, stat[0]))
    connect.commit()


def get_all_stat():
    return cursor.execute("SELECT add_user_count FROM STATS").fetchall()


def get_users():
    return cursor.execute("SELECT * FROM USERS").fetchall()


def get_senders():
    return cursor.execute("SELECT * FROM SENDERS").fetchall()


def add_new_sender_id(user_id: int):
    con = sqlite3.connect('sender.sqlite')
    curs = con.cursor()
    try:
        curs.execute('INSERT INTO sender_ids VALUES(?)', (user_id,))
        con.commit()
    except sqlite3.IntegrityError:
        pass
    curs.close()
    con.close()
