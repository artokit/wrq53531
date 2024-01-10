import threading
import time
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
import keyboards
from database.models import Stat, User
from config import ADMINS
import moviepy.editor as mp
from states import SendSenderMessage

router = Router()


@router.message(Command('admin'))
async def admin_start(message: Message):
    if message.chat.id in ADMINS:
        await message.answer("Выберите действие", reply_markup=keyboards.admins.as_markup())


@router.callback_query(F.data == 'get_stat')
async def get_stat(call: CallbackQuery):
    stat = Stat.stat_today()
    await call.message.edit_text(
        f"➕ Пользователей за сегодня: `{stat.add_user_count}`\n"
        f"❌ Заблокировали бота за сегодня: `{stat.block_user_count}`\n\n"
        f"⏳ Людей за всё время: `{stat.get_all_users_count()}`",
        parse_mode='markdown',
        reply_markup=keyboards.admins.as_markup()
    )


@router.callback_query(F.data == 'start_sender')
async def get_message(call: CallbackQuery, state: FSMContext):
    await state.set_state(SendSenderMessage.send_message)
    await call.message.answer("Отправьте сообщение, которые хотели бы использовать для рассылки")


@router.message(SendSenderMessage.send_message, F.video)
async def ask_admin(message: Message, state: FSMContext):
    file_id = message.video.file_id
    file = await message.bot.get_file(file_id)
    await message.bot.download_file(file.file_path, 'video.mp4')
    await state.update_data({'message_id': message.message_id, 'video': FSInputFile('video.mp4'), 'caption': message.caption})
    if not message.caption:
        await message.answer(
            "Вы хотели бы отправить это сообщение как видео или кружок?",
            reply_markup=keyboards.note_or_video.as_markup()
        )


@router.callback_query(SendSenderMessage.send_message, F.data.startswith('admin_sender_choice'))
async def admin_sender_choice(call: CallbackQuery, state: FSMContext):
    choice = call.data.split(':')[1]

    if choice == 'video_note':
        await call.message.answer("Ожидайте конвертации видео в кружочек")
        input_video = mp.VideoFileClip("video.mp4")
        w, h = input_video.size
        circle_size = 360
        aspect_ratio = float(w) / float(h)

        if w > h:
            new_w = int(circle_size * aspect_ratio)
            new_h = circle_size
        else:
            new_w = circle_size
            new_h = int(circle_size / aspect_ratio)

        resized_video = input_video.resize((new_w, new_h))
        output_video = resized_video.crop(x_center=resized_video.w / 2, y_center=resized_video.h / 2, width=circle_size,
                                          height=circle_size)

        output_video.write_videofile("output_video.mp4", codec="libx264", audio_codec="aac", bitrate="1M", fps=25,
                                     threads=4)

        await state.update_data({'video_note': FSInputFile('output_video.mp4'), 'video': None})

    await state.set_state(SendSenderMessage.enter_urls)

    await call.message.answer(
        "Введите кнопки с ссылками",
        reply_markup=keyboards.no_buttons.as_markup()
    )
    await call.message.answer(
        "Например:\n"
        "🔥 Стратегия 🔥 - https://example.com\n"
        "💰 Лучшие выигрыши 💰 - https://example1.com",
        reply_markup=keyboards.sender_example_urls.as_markup()
    )


@router.callback_query(F.data == 'no_buttons')
async def no_buttons(call: CallbackQuery, state: FSMContext):
    await start_sender(await state.get_data(), call.bot, [call.message.chat.id])
    await call.message.answer(
        "Выберите тип пуша",
        reply_markup=keyboards.type_of_push.as_markup(),
    )


@router.message(SendSenderMessage.enter_urls, F.text)
async def get_urls(message: Message, state: FSMContext):
    reply_markup = InlineKeyboardBuilder()
    for i in message.text.split('\n'):
        text, url = [i.strip() for i in i.split('-', maxsplit=1)]
        reply_markup.row(InlineKeyboardButton(text=text, url=url))

        if not url.startswith('http') or not text:
            return await message.answer("Неправильно введены кнопки\nПопробуйте ещё раз по примеру выше")

    await state.update_data({'reply_markup': reply_markup.as_markup()})
    await start_sender(await state.get_data(), message.bot, [message.chat.id])
    await message.answer(
        "Выберите тип пуша",
        reply_markup=keyboards.type_of_push.as_markup(),
    )


@router.callback_query(F.data == 'instant_push')
async def instant_push(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await call.message.answer("Рассылка началась")
    await start_sender(data, call.message.bot, [i.user_id for i in User.get_users()])


@router.callback_query(F.data == 'time_push')
async def enter_time_for_push(call: CallbackQuery, state: FSMContext):
    await state.set_state(SendSenderMessage.time_for_push)
    await call.message.answer(
        "Если хотите начать рассылку сейчас, то нажмите кнопку начать\n"
        "Иначе напишите время когда вы хотите сделать рассылку в формата ДД.ММ.ГГГГ ЧЧ:ММ "
        "(Например: 09.01.2024 05:41)\nВНИМАНИЕ! Часовой пояс на сервере: UTC"
    )


@router.message(SendSenderMessage.time_for_push, F.text)
async def get_time_for_push(message: Message, state: FSMContext):
    try:
        d, m = message.text.split(' ')
        _, _, _ = [int(i) for i in d.split('.')]
        _, _ = [int(i) for i in m.split(':')]
        data = await state.get_data()
        await state.clear()
        await message.answer("Ожидаем нужное время для рассылки")
    except Exception as e:
        str(e)
        return await message.answer("Дата введена неправильно\nПосмотри на образец ещё раз")


async def start_sender(data: dict, bot: Bot, users_id: list[int]):
    print(data)
    if data.get('video_note'):
        video_note = data['video_note']
        for user_id in users_id:
            try:
                msg = await bot.send_video_note(user_id, video_note, reply_markup=data.get('reply_markup'))
                video_note = msg.video_note.file_id
            except Exception as e:
                print(str(e))

    if data.get('video'):
        video = data['video']
        for user_id in users_id:
            try:
                msg = await bot.send_video(user_id, video, reply_markup=data.get('reply_markup'))
                video = msg.video.file_id
            except Exception as e:
                print(str(e))
