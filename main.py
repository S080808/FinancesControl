import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot

from src.bot.bot import setup_dispatcher

load_dotenv()

async def main() -> None:
    bot_token = os.getenv('BOT_TOKEN')
    database_url = os.getenv('DATABASE_URL')

    bot = Bot(token=bot_token)
    dp = setup_dispatcher()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())