import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from routers import user, admins


async def main():
    bot = Bot(TOKEN)
    print(await bot.get_me())
    dp = Dispatcher()
    dp.include_routers(user.router, admins.router)
    await dp.start_polling(bot)


asyncio.run(main())
