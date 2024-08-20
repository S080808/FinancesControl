from __future__ import annotations

import datetime
from typing import List

from sqlalchemy import func, select
from sqlalchemy import Integer, String, Float, ForeignKey, Date, CHAR
from sqlalchemy.orm import relationship, declarative_base, mapped_column, Mapped
from sqlalchemy.ext.asyncio import AsyncSession

Base = declarative_base()


class User(Base):
    __tablename__ = 'user_table'

    id: Mapped[int] = mapped_column(primary_key=True)

    wallets: Mapped[List[Wallet]] = relationship(back_populates="user", lazy="selectin")

    def __repr__(self):
        return f"User(id={self.id!r})"


class Wallet(Base):
    __tablename__ = 'wallets_table'

    id: Mapped[int] = mapped_column(primary_key=True)
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
        return f"Address(id={self.id!r}, user_id={self.user_id!r})"


class RegularWallet(Wallet):
    __tablename__ = 'regular_wallets_table'

    id: Mapped[int] = mapped_column(ForeignKey("wallets_table.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "regular_wallet",
    }


class SavingWallet(Wallet):
    __tablename__ = 'saving_wallets_table'

    id: Mapped[int] = mapped_column(ForeignKey("wallets_table.id"), primary_key=True)
    goal_balance: Mapped[float] = mapped_column(default=0.0)

    __mapper_args__ = {
        "polymorphic_identity": "saving_wallet",
    }