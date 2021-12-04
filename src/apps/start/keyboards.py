from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.callback_data import CallbackData
from modules.api.services import get_country_and_operators, get_services_and_cost

langs = (
    "Английский 🇺🇸",
    "Португальский 🇵🇹",
    "Русский 🇷🇺",
    "Китайский(упрощенный) 🇨🇳",
    "Турецкий 🇹🇷",
    "Германский 🇩🇪",
    "Испанский 🇪🇸",
    "Французский 🇫🇷",
    "Корейский 🇰🇷",
    "Польский 🇵🇱",
    "Индонезийский 🇮🇩",
    "Нидерландский 🇳🇱",
    "Vietnamese 🇻🇳",
    "Тайский 🇹🇭",
    "Чешский 🇨🇿",
    "Итальянский 🇮🇹",
    "Японский 🇯🇵",
    "Швейцарский 🇨🇭",
)

lang_keyboard = InlineKeyboardMarkup(row_width=1)
for lang in langs:
    lang_keyboard.insert(InlineKeyboardButton(lang, callback_data=lang))

boolean_keyboard = InlineKeyboardMarkup(row_width=2)
boolean_keyboard.insert(InlineKeyboardButton("Да", callback_data="answer_y"))
boolean_keyboard.insert(InlineKeyboardButton("Нет", callback_data="answer_n"))

pagination_callback = CallbackData(
    "btn", "page", "action", "country", "operator", "country_id")
services_callback = CallbackData('services', 'name', 'price', 'quantity')


async def get_countries_and_operators_keyboard(page: int):
    countries_and_operators = await get_country_and_operators()
    pages = {}
    for p in range(12, len(countries_and_operators) + 1, 12):
        pages[p] = countries_and_operators[p - 12:p]
    countries_keyboard = InlineKeyboardMarkup(row_width=3)

    if page * 12 in pages:
        for country in pages[page * 12]:
            countries_keyboard.insert(InlineKeyboardButton(
                country["name"], callback_data=f'country_name:{country["name"]}'))
        countries_keyboard.add(InlineKeyboardButton(
            '<', callback_data=pagination_callback.new(page=page, action='back', country='', operator='', country_id='')))
        countries_keyboard.insert(
            InlineKeyboardButton(str(page), callback_data='0'))
        countries_keyboard.insert(InlineKeyboardButton(
            '>', callback_data=pagination_callback.new(page=page, action='next', country='', operator='', country_id='')))

        return countries_keyboard


async def get_operators_keyboard(country_name: str, page: int):
    operators_keyboard = InlineKeyboardMarkup(row_width=3)

    countries_and_operators = await get_country_and_operators()
    operators = []
    for country in countries_and_operators:
        if country["name"] == country_name:
            operators = list(country["operators"].keys())
            break

    pages = {}
    if len(operators) < 12:
        pages[12] = operators
    else:
        for p in range(12, len(operators) + 1, 12):
            pages[p] = operators[p - 12:p]

    if page * 12 in pages:
        for op in pages[page * 12]:
            operators_keyboard.insert(InlineKeyboardButton(
                op, callback_data=f'operator_name:{op}'))
        operators_keyboard.add(InlineKeyboardButton('<', callback_data=pagination_callback.new(
            page=page, action='op_back', country=country_name, operator='', country_id='')))
        operators_keyboard.insert(
            InlineKeyboardButton(str(page), callback_data='0'))
        operators_keyboard.insert(InlineKeyboardButton('>', callback_data=pagination_callback.new(
            page=page, action='op_next', country=country_name, operator='', country_id='')))

        return operators_keyboard


def chunks(lst: list, chunk_size: int) -> list:
    res = []
    for i in range(0, len(lst), chunk_size):
        res.append(lst[i:i + chunk_size])
    return res


async def get_services_keyboard(operator: str, country: int, page: int = 1) -> InlineKeyboardMarkup:
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
        keyboard.add(InlineKeyboardButton(f"{response.get('name')} [{response.get('price')}] RUB - {response.get('quantity')} шт.", callback_data=services_callback.new(
            name=response.get('name'),
            price=response.get('price'),
            quantity=response.get('quantity')
        )))

    keyboard.add(InlineKeyboardButton(
        '<', callback_data=pagination_callback.new(page=page, action='s_back', country='', operator=operator, country_id=country)))
    keyboard.insert(InlineKeyboardButton(str(page), callback_data='0'))
    keyboard.insert(InlineKeyboardButton(
        '>', callback_data=pagination_callback.new(page=page, action='s_next', country='', operator=operator, country_id=country)))
    return keyboard
