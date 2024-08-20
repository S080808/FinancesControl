from __future__ import annotations

import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, declarative_base, mapped_column, Mapped

Base = declarative_base()

class User(Base):
    __tablename__ = 'user_table'

    id: Mapped[int] = mapped_column(primary_key=True)

    wallets: Mapped[List[Wallet]] = relationship(back_populates="user", lazy="selectin")

    def __repr__(self):
        return f"User(id={self.id!r})"

    @classmethod
    async def get_by_id(cls, session: AsyncSession, user_id: int) -> Optional[User]:
        return await session.get(cls, user_id)


class Wallet(Base):
    __tablename__ = 'wallets_table'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(nullable=False)
    balance: Mapped[float] = mapped_column(default=0.0)
    type: Mapped[str] = mapped_column(default='regular_wallet')

    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    user: Mapped[User] = relationship(back_populates="wallets")

    __mapper_args__ = {
        "polymorphic_identity": "wallet",
        "polymorphic_on": "type",
    }

    def __repr__(self):
        return (f"Wallet(id={self.id!r}, name={self.name!r}, currency={self.currency!r}, "
                f"balance={self.balance!r}, type={self.type}, user_id={self.user_id!r})")

    @classmethod
    async def get_by_id(cls, session: AsyncSession, wallet_id: int) -> Optional[Wallet]:
        return await session.get(cls, wallet_id)


class RegularWallet(Wallet):
    __tablename__ = 'regular_wallets_table'

    id: Mapped[int] = mapped_column(ForeignKey("wallets_table.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "regular_wallet",
    }


class SavingWallet(Wallet):
    __tablename__ = 'saving_wallets_table'

    id: Mapped[int] = mapped_column(ForeignKey("wallets_table.id"), primary_key=True)
    initial_balance: Mapped[float] = mapped_column(default=0.0)
    goal_balance: Mapped[float] = mapped_column(default=0.0)
    goal_date: Mapped[datetime.datetime] = mapped_column(nullable=False)
    interest_rate: Mapped[float] = mapped_column(nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "saving_wallet",
    }

    def __repr__(self):
        return (f"SavingWallet(id={self.id!r}, name={self.name!r}, currency={self.currency!r}, "
                f"balance={self.balance!r}, type={self.type}, user_id={self.user_id!r}, "
                f"goal_balance={self.goal_balance!r}, goal_date={self.goal_date.strftime('%d %B, %Y')})")

