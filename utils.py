import os
from aiogram import Bot
from aiogram.types import FSInputFile

HASHED_MEDIA = {

}
MEDIA_PATH = os.path.join(os.path.dirname(__file__), 'media')


async def send_video(bot: Bot, video_name: str, **kwargs):
    if video_name not in HASHED_MEDIA:
        file = FSInputFile(os.path.join(MEDIA_PATH, video_name))
        msg = await bot.send_video(video=file, **kwargs)
        HASHED_MEDIA[video_name] = msg.video.file_id
        return

    await bot.send_video(video=HASHED_MEDIA[video_name], **kwargs)


async def send_photo(bot: Bot, photo_name: str, **kwargs):
    if photo_name not in HASHED_MEDIA:
        file = FSInputFile(os.path.join(MEDIA_PATH, photo_name))
        msg = await bot.send_photo(photo=file, **kwargs)
        HASHED_MEDIA[photo_name] = msg.photo[-1].file_id
        return msg

    return await bot.send_photo(photo=HASHED_MEDIA[photo_name], **kwargs)


async def safe_delete_media(bot: Bot, chat_id: int, messages_ids: list[int]):
    await bot.delete_messages(chat_id=chat_id, message_ids=messages_ids)
