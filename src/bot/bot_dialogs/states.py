from aiogram.fsm.state import State, StatesGroup


class Main(StatesGroup):
    MAIN = State()


class MyWallets(StatesGroup):
    PAGINATED = State()
    SHOWING = State()
    EDITING = State()
    DELETING = State()

class AddWallet(StatesGroup):
    WAIT_FOR_TYPE = State()
    WAIT_FOR_NAME = State()
    WAIT_FOR_INFO = State()
    WAIT_FOR_ACCEPT = State()
    WAIT_FOR_GOAL_BALANCE = State()
    WAIT_FOR_GOAL_DATE = State()
    WAIT_FOR_INTEREST_RATE = State()