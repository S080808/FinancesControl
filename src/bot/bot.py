import logging

from aiogram import Router, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ErrorEvent, ReplyKeyboardRemove
from aiogram_dialog import DialogManager, setup_dialogs, StartMode, ShowMode
from aiogram_dialog.api.exceptions import UnknownIntent

from .bot_dialogs import states
from .bot_dialogs.main import main_dialog
from .bot_dialogs.wallets import wallets_dialog, adding_dialog
from .middlewares import SessionMiddleware
from .bot_dialogs.session import session_maker
from ..database.models import User

async def start(message: Message, dialog_manager: DialogManager):
    async with session_maker() as session:
        user = await User.get_by_id(session, message.from_user.id)
        if user is None:
            user = User(id=message.from_user.id)
            session.add(user)
        await session.commit()
    await dialog_manager.start(state=states.Main.MAIN, mode=StartMode.RESET_STACK)

async def on_unknown_intent(event: ErrorEvent, dialog_manager: DialogManager):
    logging.error("Restarting dialog: %s", event.exception)
    if event.update.callback_query:
        await event.update.callback_query.answer(
            "Bot process was restarted due to maintenance.\n"
            "Redirecting to main menu.",
        )
        if event.update.callback_query.message:
            try:
                await event.update.callback_query.message.delete()
            except TelegramBadRequest:
                pass  # whatever
    elif event.update.message:
        await event.update.message.answer(
            "Bot process was restarted due to maintenance.\n"
            "Redirecting to main menu.",
            reply_markup=ReplyKeyboardRemove(),
        )
    await dialog_manager.start(
        states.Main.MAIN,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )

dialog_router = Router()
dialog_router.include_routers(
    main_dialog,
    wallets_dialog,
    adding_dialog
)


def setup_dispatcher() -> Dispatcher:
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)
    dp.message.register(start, F.text == "/start")
    dp.message.middleware(SessionMiddleware(session_maker))
    dp.errors.register(
        on_unknown_intent,
        ExceptionTypeFilter(UnknownIntent),
    )

    dp.include_router(dialog_router)
    setup_dialogs(dp)

    return dp