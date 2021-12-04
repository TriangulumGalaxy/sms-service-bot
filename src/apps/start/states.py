from aiogram.dispatcher.filters.state import State, StatesGroup

class AcceptingRegistration(StatesGroup):
    """
    Этап, на котором пользователь должен отправить API ключ
    """
    
    accepting_reg = State()
    language = State()
    register_email = State()
    register_name = State()
    email_verification = State()
