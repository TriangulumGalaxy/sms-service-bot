from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)
from aiogram.utils.callback_data import CallbackData
from modules.api.services import get_country_and_operators

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

lang_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
for lang in langs:
    lang_keyboard.insert(KeyboardButton(lang))

boolean_keyboard = InlineKeyboardMarkup(row_width=2)
boolean_keyboard.insert(InlineKeyboardButton("Да", callback_data="answer_y"))
boolean_keyboard.insert(InlineKeyboardButton("Нет", callback_data="answer_n"))

pagination_callback = CallbackData("btn", "page", "action", "country")

async def get_countries_and_operators_keyboard(page: int):
    countries_and_operators = await get_country_and_operators()
    pages = {}
    for p in range(6, len(countries_and_operators) + 1, 6):
        pages[p] = countries_and_operators[p - 6:p]
    countries_keyboard = InlineKeyboardMarkup(row_width=3)
    
    if page * 6 in pages:
        for country in pages[page * 6]:
            countries_keyboard.insert(InlineKeyboardButton(country["name"], callback_data=f'country_name:{country["name"]}'))
        countries_keyboard.add(InlineKeyboardButton('<', callback_data=pagination_callback.new(page=page, action='back', country='')))
        countries_keyboard.insert(InlineKeyboardButton(str(page), callback_data='0'))
        countries_keyboard.insert(InlineKeyboardButton('>', callback_data=pagination_callback.new(page=page, action='next', country='')))
        
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
    if len(operators) < 6:
        pages[6] = operators
    else:
        for p in range(6, len(operators) + 1, 6):
            pages[p] = operators[p - 6:p]
    
    if page * 6 in pages:
        for op in pages[page * 6]:
            operators_keyboard.insert(InlineKeyboardButton(op, callback_data=f'operator_name:{op}'))
        operators_keyboard.add(InlineKeyboardButton('<', callback_data=pagination_callback.new(page=page, action='op_back', country=country_name)))
        operators_keyboard.insert(InlineKeyboardButton(str(page), callback_data='0'))
        operators_keyboard.insert(InlineKeyboardButton('>', callback_data=pagination_callback.new(page=page, action='op_next', country=country_name)))
        
        return operators_keyboard
    