import datetime
import os
from typing import Any

from aiogram_dialog import Dialog, Window, DialogManager, LaunchMode
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Jinja, Const, Format
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.database.models import User, Wallet, RegularWallet, SavingWallet, get_wallets

from . import states
from .session import session_maker

async def getter(dialog_manager: DialogManager, **kwargs):
    async with session_maker() as session:
        event = dialog_manager.event
        wallets = await get_wallets(session, event.from_user.id)
        if wallets is None:
            return

        wallets_info = []
        for wallet in wallets[0:3]:
            wallet_ = vars(wallet)
            if wallet_['type'] == 'regular_wallet':
                wallet_['type'] = 'Basic'
            else:
                wallet_['type'] = 'Saving'
            wallets_info.append(wallet_)

        total_balance = format(0.0, '.2f')
        transactions_info = [
            {
                'amount': 100.0,
                'date': '7 August, 2024',
                'description': 'some description',
                'wallet_name': 'Мой кошелек 2'
            }
        ]

        return {
            'total_balance': total_balance,
            'wallets_info': wallets_info,
            'transactions_info': transactions_info
        }

main_dialog = Dialog(
    Window(
        Jinja("""<b>💰 Total balance:</b> <code>${{ total_balance }}</code>\n
<pre><code class="language-🗂️ My wallets:">
{% for wallet in wallets_info %}
{% if loop.last %}
 └── 👜 {{ wallet.name }}
      ├── 💸 <b>Balance: </b>${{ wallet.balance }}
{% if wallet.type == 'Basic' %}
      └── 🧩 Type: {{ wallet.type }}
{% else %}
      ├── 🧩 Type: {{ wallet.type }}
{% endif %}
{% if wallet.type == 'Saving' %}
      ├── 🎯 Goal: ${{ wallet.goal_balance }}
      └── 📈 Interest rate: {{ wallet.interest_rate }}
{% endif %}
{% else %}
 ├── 👜 {{ wallet.name }}
 │    ├── 💸 <b> Balance: </b>${{ wallet.balance }}
{% if wallet.type == 'Basic' %}
 │    └── 🧩 Type: {{ wallet.type }}
 |
{% else %}
 │    ├── 🧩 Type: {{ wallet.type }}
{% endif %}
{% if wallet.type == 'Saving' %}
 │    ├── 🎯 Goal: ${{ wallet.goal_balance }}
 │    └── 📈 Interest rate: {{ wallet.interest_rate }}
 │
{% endif %}
{% endif %}
        {% endfor %}
        </code></pre>
        <pre><code class="language-🧾 Recent transactions:">
        {% for transaction in transactions_info %}
{% if loop.last %}
 └── 💳 <b>{{ transaction.wallet_name }}</b> - ${{ transaction.amount }}
      └── 🗓 Date: {{ transaction.date }}
{% else %}
 ├── 💳 <b>{{ transaction.wallet_name }}:</b> {{ transaction.amount }} - {{ transaction.date }}\n
      └── 🗓 Date: {{ transaction.date }}
{% endif %}
        {% endfor %}
        </code></pre>

<b>⬇️ Choose option ⬇️</b>️"""),
        Start(
            text=Const('My wallets'),
            id="my_wallets",
            state=states.MyWallets.PAGINATED,
        ),
        parse_mode="HTML",
        state=states.Main.MAIN,
        getter=getter
    ),
    launch_mode=LaunchMode.ROOT,
)
