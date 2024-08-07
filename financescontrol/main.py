import os
import logging
import asyncio
from dotenv import load_dotenv

from aiogram import Bot
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.bot import setup_dispatcher

load_dotenv()


async def main() -> None:
    bot_token = os.getenv('BOT_TOKEN')
    database_url = os.getenv('DATABASE_URL')

    engine = create_async_engine(database_url)
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

    bot = Bot(token=bot_token)
    dp = setup_dispatcher(session_maker)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
