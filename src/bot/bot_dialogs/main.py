from aiogram_dialog import Dialog, Window, DialogManager, LaunchMode
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Jinja, Const
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Wallet, RegularWallet, SavingWallet

from . import states

async def getter(dialog_manager: DialogManager, **kwargs):
    session: AsyncSession = dialog_manager.middleware_data["session"]
    event = dialog_manager.event

    # user = User(id=1089328715)
    # user.wallets.append(RegularWallet(name='Cash', currency='$', balance=0.0, user_id=user.id))
    # session.add(user)
    # await session.commit()

    user: User = await User.get_by_id(session, event.from_user.id)
    wallets = user.wallets[0:3]

    wallets_info = []
    for wallet in wallets:
        wallets_info.append(vars(wallet))

    print(wallets_info)
    total_balance = format(0.0, '.2f')
    # wallets_info = [
    #     {
    #         'name': 'Мой кошелек 1',
    #         'balance': 100.0,
    #         'type': 'regular_wallet',
    #         'goal_balance': None,
    #         'interest_rate': None
    #     },
    #     {
    #         'name': 'Мой кошелек 2',
    #         'balance': 1000.0,
    #         'type': 'saving_wallet',
    #         'goal_balance': '10000.0',
    #         'interest_rate': '5%'
    #     }
    # ]
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
        Jinja("""
<b>💰 Total balance:</b> <code>${{ total_balance }}</code>\n
<pre><code class="language-🗂️ My wallets:">
{% for wallet in wallets_info %}
{% if loop.last %}
└── 👜 <b>{{ wallet.name }}:</b> ${{ wallet.balance }}
{% else %}
├── 👜 <b>{{ wallet.name }}:</b> ${{ wallet.balance }}
{% endif %}
{% if wallet.type == 'regular_wallet' %}
     └── 🧩 Type: {{ wallet.type }}
{% else %}
     ├── 🧩 Type: {{ wallet.type }}
{% endif %}
{% if 'goal_balance' in wallet %}
     ├── 🎯 Goal: ${{ wallet.goal_balance }}
{% endif %}
{% if 'interest_rate' in wallet %}
     └── 📈 Interest rate: {{ wallet.interest_rate }}
{% endif %}

        {% endfor %}
        </code></pre>
        <pre><code class="language-🧾 Recent transactions:">
        {% for transaction in transactions_info %}
{% if loop.last %}
└── 💳 <b>{{ transaction.wallet_name }}:</b> ${{ transaction.amount }}
     └── 🗓 Date: {{ transaction.date }}
{% else %}
├── 💳 <b>{{ transaction.wallet_name }}:</b> {{ transaction.amount }} - {{ transaction.date }}\n
    └── 🗓 Date: {{ transaction.date }}
{% endif %}
        {% endfor %}
        </code></pre>

<b>⬇️ Choose option ⬇️</b>️
        """),
        Start(
            text=Const('My wallets'),
            id="my_wallets",
            state=states.MyWallets.PAGINATED
        ),
        parse_mode="HTML",
        state=states.Main.MAIN,
        getter=getter
    ),
    launch_mode=LaunchMode.ROOT
)
