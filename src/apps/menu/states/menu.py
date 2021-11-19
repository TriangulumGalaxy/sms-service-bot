from aiogram.dispatcher.filters.state import State, StatesGroup


class MenuStates(StatesGroup):
    country = State()
    operator = State()
    service = State()
