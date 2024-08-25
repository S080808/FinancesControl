import operator
from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Window, DialogManager, Dialog, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Row, Button, Select, SwitchTo, Back, Radio, Next, Cancel, Start, \
    Calendar, Column
from aiogram_dialog.widgets.text import Const, Format, Jinja
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from datetime import datetime

from . import states
from ...database.models import User, Wallet, RegularWallet, SavingWallet, get_wallet_by_id
from .common import MAIN_MENU_BUTTON
from .session import session_maker

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
    Start(Const("Add"), id="add_wallet", state=states.AddWallet.WAIT_FOR_TYPE),
    MAIN_MENU_BUTTON,

    getter=product_getter,
    preview_data=product_getter,
    state=states.MyWallets.PAGINATED
)


async def get_selected(dialog_manager: DialogManager, **kwargs):
    selected = dialog_manager.dialog_data["selected"]
    session = dialog_manager.dialog_data["session"]

    wallet = await get_wallet_by_id(session, selected)
    wallet_ = vars(wallet)
    if wallet_['type'] == 'regular_wallet':
        wallet_['type'] = 'Basic'
    else:
        wallet_['type'] = 'Saving'

    return {
        "selected": selected,
        "wallet": wallet_
    }


async def on_delete_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    selected = dialog_manager.dialog_data["selected"]
    session: AsyncSession = dialog_manager.dialog_data["session"]
    await Wallet.delete_by_id(session, selected)

    dialog_manager.dialog_data["products"] = [
        product for product in dialog_manager.dialog_data["products"] if int(product['id']) != int(selected)
    ]


show_wallet = Window(
    Jinja("""<pre><code class="language-🗂️ Wallet:">
 │   
 └── 👜 Name: {{ wallet.name }}
      ├── 💸 Balance: ${{ wallet.balance }}
{% if wallet.type == 'Basic' %}
      └── 🧩 Type: {{ wallet.type }}
{% else %}
      ├── 🧩 Type: {{ wallet.type }}
{% endif %}
{% if wallet.type == 'Saving' %}
      ├── 🎇 Initial: ${{ wallet.initial_balance }}
      ├── 🎯 Goal: ${{ wallet.goal_balance }}
      └── 📈 Interest rate: {{ wallet.interest_rate }}
{% endif %}
        </code></pre>
<b>⬇️ Choose option ⬇️</b>️
"""
          ),
    Column(
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
        try:
            wallets = [vars(wallet) for wallet in user.wallets]
        except AttributeError:
            pass

        dialog_manager.dialog_data["products"] = wallets


wallets_dialog = Dialog(
    wallets_paginated,
    show_wallet,
    edit_wallet,
    on_start=on_start,
    launch_mode=LaunchMode.SINGLE_TOP
)


async def on_input_name(message: Message, dialog: MessageInput, manager: DialogManager):
    manager.dialog_data["name"] = message.text


async def on_input_balance(message: Message, dialog: MessageInput, manager: DialogManager):
    if message.text.isdigit():
        manager.dialog_data["balance"] = int(message.text)
    else:
        manager.dialog_data["balance"] = None


async def on_input_goal_balance(message: Message, dialog: MessageInput, manager: DialogManager):
    if message.text.isdigit():
        manager.dialog_data["goal_balance"] = float(message.text)
    else:
        manager.dialog_data["goal_balance"] = None


async def on_date_selected(callback: CallbackQuery, widget: Calendar, manager: DialogManager, selected_date: datetime):
    manager.dialog_data['goal_date'] = selected_date
    await manager.switch_to(states.AddWallet.WAIT_FOR_INTEREST_RATE)


async def on_input_interest_rate(message: Message, dialog: MessageInput, manager: DialogManager):
    try:
        manager.dialog_data["interest_rate"] = float(message.text)
    except ValueError:
        manager.dialog_data["interest_rate"] = None


async def on_type_changed(callback: CallbackQuery, widget: Radio, manager: DialogManager, item_id: str):
    manager.dialog_data['type'] = item_id


async def getter(dialog_manager: DialogManager, **kwargs):
    return {
        'type': dialog_manager.dialog_data.get('type', None),
        'name': dialog_manager.dialog_data.get('name', None),
        'not name': not dialog_manager.dialog_data.get('name', False),
        'balance': dialog_manager.dialog_data.get('balance', None),
        'not balance': not dialog_manager.dialog_data.get('balance', False),
        'goal_balance': dialog_manager.dialog_data.get('goal_balance', None),
        'goal_date': dialog_manager.dialog_data.get('goal_date', None),
        'interest_rate': dialog_manager.dialog_data.get('interest_rate', None),
    }


async def create_wallet(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    async with session_maker() as session:
        user = await User.get_by_id(session, dialog_manager.event.from_user.id)

        wallet_type = dialog_manager.dialog_data['type']
        if wallet_type == 'Basic':
            wallet = RegularWallet(
                name=dialog_manager.dialog_data['name'],
                currency='$',
                balance=dialog_manager.dialog_data['balance'],
                user_id=dialog_manager.event.from_user.id
            )
        else:  # SavingWallet
            wallet = SavingWallet(
                name=dialog_manager.dialog_data['name'],
                currency='$',
                balance=dialog_manager.dialog_data['balance'],
                user_id=dialog_manager.event.from_user.id,
                goal_balance=dialog_manager.dialog_data['goal_balance'],
                goal_date=dialog_manager.dialog_data['goal_date'],
                interest_rate=dialog_manager.dialog_data['interest_rate'],
            )
        user.wallets.append(wallet)
        session.add(user)
        await session.commit()

        await callback.answer(f"{dialog_manager.dialog_data['name']} was created")


async def on_balance_next(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if dialog_manager.dialog_data['type'] == 'Basic':
        await dialog_manager.switch_to(states.AddWallet.WAIT_FOR_ACCEPT)
    else:
        await dialog_manager.next()


adding_dialog = Dialog(
    Window(
        Const("Выберите тип кошелька"),
        Radio(
            checked_text=Format('🔘 {item}'),
            unchecked_text=Format('⚪️ {item}'),
            id='choose_type',
            item_id_getter=str,
            items=['Basic', 'Saving'],
            on_state_changed=on_type_changed
        ),
        Column(
            Next(when='type'),
            Cancel(),
        ),
        state=states.AddWallet.WAIT_FOR_TYPE,
        getter=getter
    ),

    Window(
        Const("Введите имя кошелька"),
        Format("Name: {name}", when='name'),
        MessageInput(on_input_name),
        Column(
            Back(),
            Next(when='name'),
            Cancel(when='not name'),
        ),
        state=states.AddWallet.WAIT_FOR_NAME,
        getter=getter
    ),

    Window(
        Const('Введите начальный баланс'),
        Format('Ваш баланс: {balance}', when='balance'),
        MessageInput(on_input_balance),
        Column(
            Back(),
            Button(Const("Next"), id="balance_next", on_click=on_balance_next, when='balance'),
            Cancel(when='not balance'),
        ),
        state=states.AddWallet.WAIT_FOR_INFO,
        getter=getter
    ),

    Window(
        Const("Введите целевой баланс"),
        Format("Goal Balance: {goal_balance}", when='goal_balance'),
        MessageInput(on_input_goal_balance),
        Column(
            Back(),
            Next(when='goal_balance'),
            Cancel(when='not goal_balance'),
        ),
        state=states.AddWallet.WAIT_FOR_GOAL_BALANCE,
        getter=getter,
    ),

    Window(
        Const("Выберите целевую дату"),
        Calendar(
            id="goal_date",
            on_click=on_date_selected
        ),
        state=states.AddWallet.WAIT_FOR_GOAL_DATE,
        getter=getter,
    ),

    Window(
        Const("Введите процентную ставку"),
        Format("Interest Rate: {interest_rate}", when='interest_rate'),
        MessageInput(on_input_interest_rate),
        Column(
            Back(),
            Next(when='interest_rate'),
            Cancel(when='not interest_rate'),
        ),
        state=states.AddWallet.WAIT_FOR_INTEREST_RATE,
        getter=getter,
    ),

    Window(
        Jinja(
"""<pre><code class="language-🗂️ Wallet:">\n
👜 Name: {{ name }}
 ├── 💸 Balance: ${{ balance }}
{% if type == 'Basic' %}
 └── 🧩 Type: {{ type }}
{% else %}
 ├── 🧩 Type: {{ type }}
 ├── 🎇 Goal Balance: ${{ goal_balance }}
 ├── 🎯 Goal Date: {{ goal_date.strftime('%d %B, %Y') }}
 └── 📈 Interest Rate: {{ interest_rate }}%
{% endif %}
        </code></pre> <b>⬇️ Choose option ⬇️</b>️
"""
        ),
        Start(text=Format('Confirm'), on_click=create_wallet, state=states.MyWallets.PAGINATED, id='back_to_paginated'),
        Column(
            Back(),
            Cancel(),
        ),

        parse_mode='HTML',
        getter=getter,
        state=states.AddWallet.WAIT_FOR_ACCEPT
    ),
)