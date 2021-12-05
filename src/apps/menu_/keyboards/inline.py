from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from modules.api.services import get_services_and_cost

menu_callback = CallbackData('menu', 'action')
menu_buttons = {
    "Купить номер": "buy_number",
    "Отменить номер": "cancel_number",
    "Заказать из избранного": "buy_from_saved",
    "Пополнить баланс": "pay_balance",
    "Уведомления о балансе": "balance_notifications",
    "Уведомления о новых сервисах": "services_notifications",
    "Уведомления о новых странах": "countries_notifications",
    "Запросить ещё одну СМС": "request_new_sms",
    # "Мои номера": "my_numbers",
    "Посмотреть статистику": "statistics",
    "Завершить активацию": "end_activation",
}

menu_keyboard = InlineKeyboardMarkup(row_width=2)
for button_text, action in menu_buttons.items():
    menu_keyboard.insert(InlineKeyboardButton(
        button_text, callback_data=menu_callback.new(action=action)))


ok_and_delete_keyboard = InlineKeyboardMarkup(row_width=1).insert(
    InlineKeyboardButton('Ок', callback_data="ok_and_delete"))

back_to_menu_button = InlineKeyboardButton(
    'Назад в меню', callback_data="back_to_menu")


back_to_menu_keyboard = InlineKeyboardMarkup()
back_to_menu_keyboard.insert(back_to_menu_button)

after_order_menu = InlineKeyboardMarkup()
after_order_menu.insert(back_to_menu_button)
after_order_menu.add(InlineKeyboardButton(
    'Сохранить настройки в избранное', callback_data="save_to_favourite"))


def chunks(lst: list, chunk_size: int) -> list:
    res = []
    for i in range(0, len(lst), chunk_size):
        res.append(lst[i:i + chunk_size])
    return res


page_callback = CallbackData('pagination', 'page', 'action')
service_callback = CallbackData('services', 'name', 'price', 'quantity')


async def get_services_and_costs_keyboard(operator: str, country: int, api_key: str, page: int = 1, ) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=3)
    data = chunks(
        list(filter(lambda x: int(x.get('quantity')) != 0,
                    await get_services_and_cost(operator=operator, country=country, api_key=api_key))),
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
    return keyboard


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


def get_current_numbers_keyboard(numbers: list) -> InlineKeyboardMarkup:
    """Returns an inline keyboard with all numbers

    Args:
        numbers (list): list of numbers for buttons

    Returns:
        InlineKeyboardMarkup with Inline
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    print(numbers)
    keyboard.add(*[InlineKeyboardButton(str(number),
                                        callback_data=f"number:{str(number)}") for number in numbers])
    return keyboard
