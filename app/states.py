from aiogram.fsm.state import StatesGroup, State

class MainMenu(StatesGroup):
    screen = State()

class NotifSettings(StatesGroup):
    screen = State()
    fav_menu = State()
    input = State()
    fav_remove = State()