import operator
from typing import Dict, Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Window, SubManager, DialogManager, Dialog
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.kbd import ScrollingGroup, ListGroup, Checkbox, Row, Button, ManagedCheckbox, Group, Radio, \
    Select, Multiselect, SwitchTo, Column, ManagedRadio, Back, Start, Next
from aiogram_dialog.widgets.text import Const, Format, Jinja

from .common import MAIN_MENU_BUTTON
from . import states

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
            text=Format("{item[text]}"),
            items="products",
            item_id_getter=operator.itemgetter('id'),
            id="lg",
            on_click=on_item_selected,
        ),
        id="sg",
        width=1,
        height=5,
    ),
    MAIN_MENU_BUTTON,

    getter=product_getter,
    preview_data=product_getter,
    state=states.MyWallets.PAGINATED
)

async def get_selected(dialog_manager: DialogManager, **kwargs):
    return {
        "selected": dialog_manager.dialog_data["selected"],
        "wallet": {
            'name': 'Мой кошелек 1',
            'balance': 100.0,
            'type': 'regular_wallet',
            'initial_balance': None,
            'goal_balance': None,
            'interest_rate': None
        }
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
{% if wallet.initial_balance is not none %}
     ├── 🎇 Initial: ${{ wallet.initial_balance }}
{% endif %}
{% if wallet.goal_balance is not none %}
     ├── 🎯 Goal: ${{ wallet.goal_balance }}
{% endif %}
{% if wallet.interest_rate is not none %}
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
    dialog_manager.dialog_data["products"] = [{'text': f"Product {i}", 'id': i} for i in range(1, 30)]


wallets_dialog = Dialog(
    wallets_paginated,
    show_wallet,
    edit_wallet,
    on_start=on_start
)
