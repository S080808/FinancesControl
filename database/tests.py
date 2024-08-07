import asyncio
import datetime

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from models import Base, DatabaseManager


async def main() -> None:
    DATABASE_URL = "sqlite+aiosqlite:///database/test_db.sqlite"
    engine = create_async_engine(DATABASE_URL, echo=True)
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        db_manager = DatabaseManager(session)

        new_user = await db_manager.set_user(123)

        assert (new_user.user_id == 123)

        regular_wallet = await db_manager.set_regular_wallet(123, 100.0)
        saving_wallet = await db_manager.set_saving_wallet(new_user, 100.0, 1000.0, 0.05)

        assert (regular_wallet.user_id == 123)
        assert (regular_wallet.balance == 100.0)

        assert (saving_wallet.user_id == 123)
        assert (saving_wallet.balance == 100.0)
        assert (saving_wallet.goal_balance == 1000.0)
        assert (saving_wallet.interest_rate == 0.05)

        new_transaction = await db_manager.set_transaction(saving_wallet, 100.0, datetime.date(2010, 10, 10), '123')

        await session.refresh(new_transaction)

        assert (new_transaction.user.user_id == 123)
        assert (new_transaction.wallet.wallet_id == saving_wallet.wallet_id)

        print(new_transaction.wallet.wallet_id)
        print(new_transaction.user.user_id)

if __name__ == '__main__':
    asyncio.run(main())
