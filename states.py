from aiogram.fsm.state import StatesGroup, State


class SendPhoto(StatesGroup):
    send_photos = State()


class SendSenderMessage(StatesGroup):
    send_message = State()
    enter_urls = State()
    time_for_push = State()
