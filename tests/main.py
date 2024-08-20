from datetime import datetime
import os
import logging
import asyncio
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.database.models import Base

from src.database.models import User, Wallet, RegularWallet, SavingWallet

load_dotenv()

async def main() -> None:
    database_url = 'sqlite+aiosqlite:///test.sqlite'

    engine = create_async_engine(database_url)
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        user = User(id=123)
        user.wallets.append(SavingWallet(name='123', currency='$', balance=0.0, type='saving_wallet', goal_date=datetime.today()))
        session.add(user)
        await session.commit()

        print(user.wallets)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())