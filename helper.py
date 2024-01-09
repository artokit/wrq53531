from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters

app = Client('anon', 28470956, 'ffc72a348f21e61c9c3d2be46d991856')


@app.on_message()
async def my_handler(client: Client, message: Message):
    print(message)
    res = await client.download_media(message)
    print(res)
    await client.send_video_note(message.chat.id, res)

app.run()
