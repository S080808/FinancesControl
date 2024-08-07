import datetime
from sqlalchemy import Integer, String, Float, ForeignKey, Date, func, select
from sqlalchemy.orm import mapped_column, relationship, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = mapped_column(Integer, nullable=False, primary_key=True)

    wallets = relationship("Wallet", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


class Transaction(Base):
    __tablename__ = 'transactions'

    transaction_id = mapped_column(Integer, primary_key=True)

    amount = mapped_column(Float, nullable=False)
    date = mapped_column(Date, server_default=func.now())
    description = mapped_column(String, nullable=False)

    user_id = mapped_column(Integer, ForeignKey('users.user_id'))
    wallet_id = mapped_column(Integer, ForeignKey('wallets.wallet_id'))

    user = relationship("User", back_populates="transactions")
    wallet = relationship("Wallet", back_populates="transactions")


class Wallet(Base):
    __tablename__ = 'wallets'

    wallet_id = mapped_column(Integer, primary_key=True)

    balance = mapped_column(Float, default=0.0)
    type = mapped_column(String, nullable=False)

    user_id = mapped_column(Integer, ForeignKey('users.user_id'))

    user = relationship("User", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet")

    __mapper_args__ = {
        'polymorphic_identity': 'wallet',
        'polymorphic_on': type
    }


class RegularWallet(Wallet):
    __tablename__ = 'regular_wallets'

    wallet_id = mapped_column(Integer, ForeignKey('wallets.wallet_id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'regular_wallet',
    }


class SavingWallet(Wallet):
    __tablename__ = 'saving_wallets'

    wallet_id = mapped_column(Integer, ForeignKey('wallets.wallet_id'), primary_key=True)

    goal_balance = mapped_column(Float, default=0.0)
    interest_rate = mapped_column(Float, default=0.0)

    __mapper_args__ = {
        'polymorphic_identity': 'saving_wallet',
    }


class DatabaseManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int) -> User:
        result = await self.session.execute(select(User).filter_by(user_id=user_id))
        return result.scalar_one_or_none()

    async def set_user(self, user_id: int) -> User:
        user = await self.get_user(user_id)
        if user is not None:
            return user

        user = User(user_id=user_id)
        self.session.add(user)
        await self.session.commit()
        return user

    async def set_regular_wallet(
            self,
            user_id: int,
            initial_balance: float = 0.0,
    ) -> Wallet:
        wallet = RegularWallet(
            balance=initial_balance,
            type='regular_wallet',
            user_id=user_id
        )
        self.session.add(wallet)
        await self.session.commit()
        return wallet

    async def set_saving_wallet(
            self,
            user: User,
            initial_balance: float = 0.0,
            goal_balance: float = 0.0,
            interest_rate: float = 0.0
    ) -> Wallet:
        wallet = SavingWallet(
            balance=initial_balance,
            user_id=user.user_id,
            type='saving_wallet',
            goal_balance=goal_balance,
            interest_rate=interest_rate
        )
        self.session.add(wallet)
        await self.session.commit()
        return wallet

    async def set_transaction(
            self,
            wallet: Wallet,
            amount: float,
            date: datetime.date,
            description: str
    ) -> Transaction:
        new_transaction = Transaction(
            amount=amount,
            date=date,
            description=description,
            user_id=wallet.user.user_id,
            wallet_id=wallet.wallet_id
        )
        self.session.add(new_transaction)
        await self.session.commit()
        return new_transaction
