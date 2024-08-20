from aiogram import Router, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram_dialog import DialogManager, setup_dialogs, StartMode
from sqlalchemy.ext.asyncio import async_sessionmaker

from .bot_dialogs import states
from .bot_dialogs.main import main_dialog

async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=states.Main.MAIN, mode=StartMode.RESET_STACK)


dialog_router = Router()
dialog_router.include_routers(
    main_dialog
)


def setup_dispatcher(session_maker: async_sessionmaker) -> Dispatcher:
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)
    dp.message.register(start, F.text == "/start")
    # dp.message.middleware(SessionMiddleware(session_maker))
    dp.include_router(dialog_router)
    setup_dialogs(dp)

    return dp