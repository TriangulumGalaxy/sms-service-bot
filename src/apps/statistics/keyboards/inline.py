from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

choose_stats_keyboard = InlineKeyboardMarkup(row_width=1)
choose_stats_keyboard.insert(InlineKeyboardButton('Общая статистика', callback_data='general_stats'))
choose_stats_keyboard.insert(InlineKeyboardButton('Статистика по проданным номерам', callback_data='numbers_stats'))
choose_stats_keyboard.insert(InlineKeyboardButton('Статистика по ожидаемым странам', callback_data='countries_stats'))
choose_stats_keyboard.insert(InlineKeyboardButton('Вернуться в меню', callback_data='back_to_menu'))

dates_callback = CallbackData('dates', 'time')

choose_numbers_stats_keyboard = InlineKeyboardMarkup(row_width=1)
choose_numbers_stats_keyboard.insert(InlineKeyboardButton('За сегодня', callback_data=dates_callback.new(time='За сегодня')))
choose_numbers_stats_keyboard.insert(InlineKeyboardButton('Вчера', callback_data=dates_callback.new(time='Вчера')))
choose_numbers_stats_keyboard.insert(InlineKeyboardButton('Прошлая неделя ( пн-вс)', callback_data=dates_callback.new(time='Прошлая неделя ( пн-вс)')))
choose_numbers_stats_keyboard.insert(InlineKeyboardButton('Последние 14 дней', callback_data=dates_callback.new(time='Последние 14 дней')))
choose_numbers_stats_keyboard.insert(InlineKeyboardButton('Последние 30 дней', callback_data=dates_callback.new(time='Последние 30 дней')))
choose_numbers_stats_keyboard.insert(InlineKeyboardButton('Прошлый месяц', callback_data=dates_callback.new(time='Прошлый месяц')))
choose_numbers_stats_keyboard.insert(InlineKeyboardButton('Все время', callback_data=dates_callback.new(time='Все время')))
