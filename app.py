import asyncio
import os
import logging


from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

from dotenv import load_dotenv

load_dotenv()

from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker
from handlers.user_private import user_private_router


async def on_startup(bot):

    await drop_db()

    await create_db()


async def on_shutdown(bot):
    print("Stop the bot")


async def main():

    dp = Dispatcher()
    dp.include_router(user_private_router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') 

    bot = Bot(
        token=os.getenv("TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    bot.my_admins_list = []
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
