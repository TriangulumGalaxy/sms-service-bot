from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


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
