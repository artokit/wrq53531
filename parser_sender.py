import sqlite3
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pyrogram import Client
from pyrogram import types, filters
from aiogram import Bot
import os
from aiogram.types import InlineKeyboardButton, FSInputFile, Message
from pyrogram.enums import MessageEntityType
from config import TOKEN, HELPER_URL

# Ключ - откуда копируем, значение - куда копируем.
CHANNELS = {
    6386656575: [6606885505]
}

api_id = 11325071
api_hash = '8b7bd8121748973fcc1341afb5935b3b'
app = Client('anon', api_id=api_id, api_hash=api_hash)
bot = Bot(token=TOKEN)
DOWNLOADS = {}


async def edit_keyboard(msg, kb):
    await bot.edit_message_reply_markup(msg.chat.id, msg.id, reply_markup=kb)


def get_users_id():
    connect = sqlite3.connect('sender.sqlite')
    cursor = connect.cursor()
    res = [i[0] for i in cursor.execute('SELECT * FROM SENDER_IDS').fetchall()]
    cursor.close()
    connect.close()
    return res


def replace_sender(txt):
    if txt:
        return txt.replace('Toguzbay_manager1', 'Toguzbay_Official').replace('https://share.kz/gcjV', 'https://t.me/Toguzbay_Official')
        # return txt.replace('https://t.me/Toguzbay_manager1', HELPER_URL).replace('tg://resolve?domain=Toguzbay_manager1', HELPER_URL)
    return txt


def replace_entities(ent):
    if not ent:
        return

    for i in ent:
        if i.type == MessageEntityType.TEXT_LINK:
            i.url = replace_sender(i.url)


def get_edit_copy_keyboard(keyboard):
    kb = InlineKeyboardBuilder()
    if keyboard:
        reply_markup = keyboard.inline_keyboard
        for i in reply_markup:
            button = i[0]
            if button.url:
                kb.row(InlineKeyboardButton(text=button.text, url='https://t.me/Toguzbay_Official'))

            if button.callback_data:
                kb.row(InlineKeyboardButton(text=button.text, callback_data=button.callback_data))

            print(button.url)
    return kb.as_markup()


@app.on_message(filters=filters.chat(list(CHANNELS.keys())) & filters.text)
async def post_text_handler(client: Client, message: types.Message):
    replace_entities(message.entities)
    kb = get_edit_copy_keyboard(message.reply_markup)
    await send_in_groups(bot.send_message, message.chat.id, text=replace_sender(message.text), kb=kb)


@app.on_message(filters=filters.chat(list(CHANNELS.keys())) & filters.media_group)
async def post_media_handler(client: Client, message: types.Message):
    length = len((await message.get_media_group()))
    res = await client.download_media(message)
    prev_res = DOWNLOADS.get(message.media_group_id, {}).get('res', [])
    prev_res.append([res, message.caption])
    DOWNLOADS[message.media_group_id] = {'length': length, 'res': prev_res}

    if DOWNLOADS[message.media_group_id]['length'] == len(prev_res):
        groups = []
        for i in DOWNLOADS[message.media_group_id]['res']:
            frmt = i[0][::-1].split('.')[0][::-1].lower()
            replace_entities(message.caption_entities)

            if frmt in ('jpg', 'png'):
                groups.append(types.InputMediaPhoto(i[0], caption=replace_sender(i[1])))

            if frmt in ('mp4', 'avi'):
                groups.append(types.InputMediaVideo(i[0], caption=replace_sender(i[1])))

        await send_in_groups(bot.send_media_group, message.chat.id, kb=False, media=groups)

        for i in DOWNLOADS[message.media_group_id]['res']:
            os.remove(i[0])

            del DOWNLOADS[message.media_group_id]


@app.on_message(filters=filters.chat(list(CHANNELS.keys())) & filters.photo)
async def post_photo_handler(client: Client, message: types.Message):
    res = await client.download_media(message)
    kb = get_edit_copy_keyboard(message.reply_markup)
    replace_entities(message.caption_entities)
    await send_in_groups(bot.send_photo, message.chat.id, photo=FSInputFile(res), caption=replace_sender(message.caption), kb=kb)

    os.remove(res)


@app.on_message(filters=filters.chat(list(CHANNELS.keys())) & filters.video)
async def post_video_handler(client: Client, message: types.Message):
    res = await client.download_media(message)
    kb = get_edit_copy_keyboard(message.reply_markup)
    dst = await client.download_media(message.video.thumbs[-1].file_id)
    replace_entities(message.caption_entities)
    await send_in_groups(bot.send_video, message.chat.id, kb=kb,
                         video=FSInputFile(res), caption=replace_sender(message.caption), width=message.video.width,
                         height=message.video.height, supports_streaming=message.video.supports_streaming)
    os.remove(dst)
    os.remove(res)


@app.on_message(filters=filters.chat(list(CHANNELS.keys())) & filters.video_note)
async def post_video_note_handler(client: Client, message: types.Message):
    res = await client.download_media(message)
    kb = get_edit_copy_keyboard(message.reply_markup)
    await send_in_groups(bot.send_video_note, message.chat.id, kb=kb, video_note=FSInputFile(res))

    os.remove(res)


@app.on_message(filters=filters.chat(list(CHANNELS.keys())) & filters.document)
async def post_document_handler(client: Client, message: types.Message):
    replace_entities(message.caption_entities)
    res = await client.download_media(message)
    kb = get_edit_copy_keyboard(message.reply_markup)
    await send_in_groups(bot.send_document, message.chat.id, document=FSInputFile(res), kb=kb,
                         caption=replace_sender(message.caption))
    os.remove(res)


@app.on_message(filters=filters.chat(list(CHANNELS.keys())) & filters.animation)
async def post_animation_handler(client: Client, message: types.Message):
    replace_entities(message.caption_entities)
    res = await client.download_media(message)
    kb = get_edit_copy_keyboard(message.reply_markup)

    await send_in_groups(bot.send_animation, message.chat.id, animation=FSInputFile(res), kb=kb,
                         caption=replace_sender(message.caption))
    os.remove(res)


@app.on_message(filters=filters.chat(list(CHANNELS.keys())) & filters.voice)
async def post_voice_handler(client: Client, message: types.Message):
    res = await client.download_media(message)
    kb = get_edit_copy_keyboard(message.reply_markup)
    await send_in_groups(bot.send_voice, message.chat.id, voice=FSInputFile(res), kb=kb,
                         caption=replace_sender(message.caption))
    os.remove(res)


@app.on_message(filters=filters.chat(list(CHANNELS.keys())) & filters.sticker)
async def post_sticker_handler(client: Client, message: types.Message):
    res = await client.download_media(message)
    kb = get_edit_copy_keyboard(message.reply_markup)
    await send_in_groups(bot.send_sticker, message.chat.id, sticker=FSInputFile(res), kb=kb)
    os.remove(res)


@app.on_message(filters=filters.chat(list(CHANNELS.keys())) & filters.audio)
async def post_audio_handler(client: Client, message: types.Message):
    res = await client.download_media(message)
    replace_entities(message.caption_entities)
    kb = get_edit_copy_keyboard(message.reply_markup)
    await send_in_groups(bot.send_audio, message.chat.id, kb=kb, audio=FSInputFile(res), caption=replace_sender(message.caption),)
    os.remove(res)


@app.on_message(filters=filters.chat(list(CHANNELS.keys())))
async def f(client: Client, message: types.Message):
    await client.send_message('@DenisErmoshin', 'что-то пошло по пизде :(')


async def send_in_groups(func, chat_copy_id, kb=True, **kwargs):
    first = True
    for i in get_users_id():
        try:
            msg: Message
            msg = await func(
                i,
                reply_markup=kb,
                **kwargs
            )

            if first:
                if msg.video:
                    video_file_id = msg.video.file_id
                    kwargs['video'] = video_file_id

                if msg.photo:
                    photo_id = msg.photo[-1].file_id
                    kwargs['photo'] = photo_id

                if msg.video_note:
                    kwargs['video_note'] = msg.video_note.file_id

                first = False

        except Exception as e:
            print(f'Исключение в канале {i}\n{str(e)}')


app.run()
