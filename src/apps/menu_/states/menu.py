from aiogram.dispatcher.filters.state import State, StatesGroup


class MenuStates(StatesGroup):
    country = State()
    operator = State()
    service = State()
    deleting_number = State()
    requesting_sms = State()
    end_activation = State()
