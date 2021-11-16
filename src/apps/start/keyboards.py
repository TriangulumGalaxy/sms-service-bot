from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup


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
for i in langs:
    lang_keyboard.insert(KeyboardButton(i))

boolean_keyboard = InlineKeyboardMarkup(row_width=2)
boolean_keyboard.insert(InlineKeyboardButton("Да", callback_data="answer_y"))
boolean_keyboard.insert(InlineKeyboardButton("Нет", callback_data="answer_n"))
