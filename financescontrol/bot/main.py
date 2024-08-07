from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Jinja

from bot import states


main_dialog = Dialog(
    Window(
        Jinja("123"),
        parse_mode="HTML",
        state=states.Main.MAIN,
    )
)
