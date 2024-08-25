import os
import logging
import asyncio
from aiogram import Bot
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.bot.bot import setup_dispatcher
from src.database.models import Base

load_dotenv()

async def main() -> None:
    bot_token = os.getenv('BOT_TOKEN')
    database_url = os.getenv('DATABASE_URL')

    engine = create_async_engine(database_url)
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)

    bot = Bot(token=bot_token)
    dp = setup_dispatcher()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except TypeError and KeyboardInterrupt:
        logging.info('Bot stopped')
