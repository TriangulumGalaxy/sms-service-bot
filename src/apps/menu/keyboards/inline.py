from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# from aiogram.utils import callback_data
from modules.api.services import get_country_and_operators, get_services_and_cost
from aiogram.utils.callback_data import CallbackData


bool_keyboard = InlineKeyboardMarkup(row_width=2)
bool_keyboard.insert(InlineKeyboardButton(
    'Да', callback_data='bool:yes:order_number'))
bool_keyboard.insert(InlineKeyboardButton('Нет', callback_data='bool:no'))

back_to_menu_button = InlineKeyboardButton(
    'Назад в меню', callback_data="back_to_menu")


back_to_menu_keyboard = InlineKeyboardMarkup()
back_to_menu_keyboard.insert(back_to_menu_button)

change_balance_limit_keyboard = InlineKeyboardMarkup(row_width=2)
change_balance_limit_keyboard.insert(InlineKeyboardButton(
    'Изменить', callback_data="change_balance_limit"))
change_balance_limit_keyboard.insert(back_to_menu_button)


async def get_limits_keyboard(limits: list = [
    100,
    500,
    1000,
    5000,
    10000,
    20000,
    0,
]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for i in limits:
        keyboard.insert(InlineKeyboardButton(
            f"{i} RUB", callback_data=f"set_limit:{i}"))
    return keyboard

menu = InlineKeyboardMarkup(row_width=2)
menu.insert(InlineKeyboardButton(
    "Выбрать страну", callback_data="choose_country"))
menu.insert(InlineKeyboardButton(
    "Завершить активацию", callback_data="end_activation"))
menu.insert(InlineKeyboardButton(
    "Выбрать оператора", callback_data="choose_operator"))
menu.insert(
    InlineKeyboardButton("Заказать номер", callback_data="order_number")
)
menu.insert(InlineKeyboardButton(
    'Проверить баланс', callback_data="check_balance"))
menu.insert(InlineKeyboardButton("Запросить еще одну смс",
                                 callback_data="retry_sms_sending"))
menu.insert(InlineKeyboardButton('Просмотреть СМС', callback_data="check_sms"))
menu.insert(InlineKeyboardButton(
    "Выбрать сервис", callback_data="choose_service"))
menu.insert(InlineKeyboardButton(
    "Отменить заказ", callback_data="cancel_order"))
menu.add(
    InlineKeyboardButton("Настроить уведомления о балансе",
                         callback_data="balance_limit_notification")
)


async def get_countries_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=3)
    data = await get_country_and_operators()
    callback = CallbackData('countries', 'country_name', 'country_id')
    for response in data:
        keyboard.insert(InlineKeyboardButton(response.get('name'), callback_data=callback.new(
            country_name=response.get('name'), country_id=response.get('id'))))
    keyboard.add(back_to_menu_button)
    return keyboard


def chunks(lst: list, chunk_size: int) -> list:
    res = []
    for i in range(0, len(lst), chunk_size):
        res.append(lst[i:i + chunk_size])
    return res


page_callback = CallbackData('pageination', 'page', 'action')
service_callback = CallbackData('services', 'name', 'price', 'quantity')


async def get_services_and_costs_keyboard(operator: str, country: int, page: int = 1) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup(row_width=3)
    # data = await get_services_and_cost(operator='tele2', country=0)
    # data = list(filter(lambda x: int(x.get('quantity')) != 0, await get_services_and_cost(operator='tele2', country=0)))
    data = chunks(
        list(filter(lambda x: int(x.get('quantity')) != 0,
                    await get_services_and_cost(operator=operator, country=country))),  # Получение оператора и страны из БД
        10)

    if len(data) <= page - 1:
        # Поменять на page = len(data), чтобы убрать бесконечное пролистывание
        page = 1

    for response in data[page - 1]:
        keyboard.add(InlineKeyboardButton(f"{response.get('name')} [{response.get('price')}] RUB - {response.get('quantity')} шт.", callback_data=service_callback.new(
            name=response.get('name'),
            price=response.get('price'),
            quantity=response.get('quantity')
        )))

    keyboard.add(InlineKeyboardButton(
        '<', callback_data=page_callback.new(page=page, action='back')))
    keyboard.insert(InlineKeyboardButton(str(page), callback_data='0'))
    keyboard.insert(InlineKeyboardButton(
        '>', callback_data=page_callback.new(page=page, action='next')))
    keyboard.add(back_to_menu_button)
    return keyboard
