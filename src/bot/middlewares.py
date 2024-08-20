from typing import Callable, Awaitable, Any, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker


class SessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker: async_sessionmaker):
        self.session_maker = session_maker

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: dict[str, Any]
    ) -> Awaitable:
        async with self.session_maker() as session:
            data['session'] = session
            # data['db_manager'] = DatabaseManager(session)
            return await handler(event, data)