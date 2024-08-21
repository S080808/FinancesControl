import operator
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager, Dialog, LaunchMode
from aiogram_dialog.widgets.kbd import ScrollingGroup, Row, Button, Select, SwitchTo, Back
from aiogram_dialog.widgets.text import Const, Format, Jinja
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from . import states
from .session import session_maker
from .common import MAIN_MENU_BUTTON
from ...database.models import User, Wallet


async def product_getter(dialog_manager: DialogManager, **kwargs):
    return {
        "products": dialog_manager.dialog_data["products"],
    }

async def on_item_selected(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    selected_item: str,
):
    dialog_manager.dialog_data["selected"] = selected_item
    await dialog_manager.switch_to(state=states.MyWallets.SHOWING)


wallets_paginated = Window(
    Const("Scrolling group with default pager (legacy mode)"),
    ScrollingGroup(
        Select(
            text=Format("👜 {item[name]}"),
            items="products",
            item_id_getter=operator.itemgetter('id'),
            id="lg",
            on_click=on_item_selected,
        ),
        id="sg",
        width=2,
        height=5,
    ),
    MAIN_MENU_BUTTON,

    getter=product_getter,
    preview_data=product_getter,
    state=states.MyWallets.PAGINATED
)

async def get_selected(dialog_manager: DialogManager, **kwargs):
    selected = dialog_manager.dialog_data["selected"]
    session = dialog_manager.dialog_data["session"]

    wallet = await Wallet.get_by_id(session, selected)
    print(wallet)
    return {
        "selected": selected,
        "wallet": vars(wallet)
    }

async def on_delete_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    selected = dialog_manager.dialog_data["selected"]
    dialog_manager.dialog_data["products"] = [
        product for product in dialog_manager.dialog_data["products"] if int(product['id']) != int(selected)
    ]

show_wallet = Window(
    Jinja("""<pre><code class="language-🗂️ Wallet:">
└── 👜 <b>{{ wallet.name }}:</b> ${{ wallet.balance }}
{% if wallet.type == 'regular_wallet' %}
     └── 🧩 Type: {{ wallet.type }}
{% else %}
     ├── 🧩 Type: {{ wallet.type }}
{% endif %}
{% if 'initial_balance' in wallet %}
     ├── 🎇 Initial: ${{ wallet.initial_balance }}
{% endif %}
{% if 'goal_balance' in wallet %}
     ├── 🎯 Goal: ${{ wallet.goal_balance }}
{% endif %}
{% if 'interest_rate' in wallet %}
     └── 📈 Interest rate: {{ wallet.interest_rate }}
{% endif %}
</code></pre>
"""
    ),
    Row(
        SwitchTo(text=Const('Edit'), id='edit_wallet', state=states.MyWallets.EDITING),
        Back(text=Const('Delete'), id='delete_wallet', on_click=on_delete_clicked),
    ),
    Back(),
    state=states.MyWallets.SHOWING,
    getter=get_selected,
    parse_mode="HTML"
)

edit_wallet = Window(
    Format("{selected}"),
    SwitchTo(text=Const('Back'), id='back_to_wallets', state=states.MyWallets.PAGINATED),
    state=states.MyWallets.EDITING,
    getter=get_selected
)

async def on_start(start_data: Any, dialog_manager: DialogManager):
    async with session_maker() as session:
        dialog_manager.dialog_data["session"] = session
        user = await User.get_by_id(session, dialog_manager.event.from_user.id)
        wallets = [vars(wallet) for wallet in user.wallets]
        print(wallets)

        dialog_manager.dialog_data["products"] = [{'name': '123', 'type': 'regular_wallet', 'initial_balance': 0.0, 'id': 1}]

wallets_dialog = Dialog(
    wallets_paginated,
    show_wallet,
    edit_wallet,
    on_start=on_start,
    launch_mode=LaunchMode.SINGLE_TOP
)
