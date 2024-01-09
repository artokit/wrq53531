from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import HELPER_URL

start = InlineKeyboardBuilder()
start.row(InlineKeyboardButton(text='Табыс табу жайлы ?', callback_data='about_money'))
start.row(InlineKeyboardButton(text='Ұтыс отзывтары !', callback_data='comments'))
start.row(InlineKeyboardButton(text='Тоғызбайға жазып Бастау ↗', url=HELPER_URL))

comment_button = InlineKeyboardBuilder()
comment_button.row(InlineKeyboardButton(text='Отзывтарды карау ↗', callback_data='comments'))

help_button = InlineKeyboardBuilder()
help_button.row(InlineKeyboardButton(text='МЕНIМЕН ХАБАРЛАСЫҢЫЗ 🤝', url=HELPER_URL))

more_comments = InlineKeyboardBuilder()
more_comments.row(InlineKeyboardButton(text='Көбірек шолулар!', callback_data='more_comments'))

admins = InlineKeyboardBuilder()
admins.row(InlineKeyboardButton(text="Начать рассылку", callback_data='start_sender'))
admins.row(InlineKeyboardButton(text="Получить статистику", callback_data='get_stat'))


note_or_video = InlineKeyboardBuilder()
note_or_video.row(InlineKeyboardButton(text="Видео", callback_data="admin_sender_choice:video"))
note_or_video.row(InlineKeyboardButton(text="Кружок", callback_data="admin_sender_choice:video_note"))


start_sender_or_not = InlineKeyboardBuilder()
start_sender_or_not.row(InlineKeyboardButton(text="✅", callback_data="sender_start:yes"))
start_sender_or_not.row(InlineKeyboardButton(text="❌", callback_data="sender_start:no"))


type_of_push = InlineKeyboardBuilder()
type_of_push.row(InlineKeyboardButton(text="Мгновенный пуш", callback_data="instant_push"))
type_of_push.row(InlineKeyboardButton(text="Ежедневный пуш", callback_data="every_day_push"))
type_of_push.row(InlineKeyboardButton(text="Отложенный пуш", callback_data="time_push"))


sender_example_urls = InlineKeyboardBuilder()
sender_example_urls.row(InlineKeyboardButton(text="🔥 Стратегия 🔥", url='https://example.com'))
sender_example_urls.row(InlineKeyboardButton(text="💰 Лучшие выигрыши 💰", url='https://example1.com'))


no_buttons = InlineKeyboardBuilder()
no_buttons.row(InlineKeyboardButton(text="В этой рассылке не нужны кнопки", callback_data="no_buttons"))
