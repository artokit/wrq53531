from dataclasses import dataclass
from database import db_api

BLOCKED_USERS = []


@dataclass
class User:
    user_id: int
    username: str

    @staticmethod
    def add_user(user_id: int, username: str):
        return db_api.add_user(user_id, username)

    @staticmethod
    def get_users():
        return [User(*i) for i in db_api.get_users()]


@dataclass
class Stat:
    date: str
    add_user_count: int
    block_user_count: int

    @staticmethod
    def increment_stat():
        db_api.add_new_user_stat()

    @staticmethod
    def stat_today():
        return Stat(*db_api.get_today_stat())

    @staticmethod
    def add_block_user(user_id: int):
        if user_id not in BLOCKED_USERS:
            print(user_id)
            BLOCKED_USERS.append(user_id)
            db_api.add_new_blocked_stat()

    @staticmethod
    def get_all_users_count():
        return sum([i[0] for i in db_api.get_all_stat()])


@dataclass
class Sender:
    date: str
    type: str
    data: dict

    # @staticmethod
    # def get_senders():
    #     return [Sender(date=i[0], type=i[1], data=) for i in db_api.get_senders()]
