from aiogram.dispatcher.storage import FSMContext
from aiogram.types import CallbackQuery, Message
from apps.root import dp
from apps.statistics.filters import IsAdmin
from apps.statistics.keyboards.inline import choose_stats_keyboard, choose_numbers_stats_keyboard, dates_callback
from modules.statistics.json_stats import get_params
from modules.db.schemas.sold_numbers import select_by_days


@dp.callback_query_handler(IsAdmin(), text_contains="get_statistics", state="*")
async def get_stats(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(choose_stats_keyboard)


@dp.callback_query_handler(IsAdmin(), text_contains="general_stats", state="*")
async def general_stats(call: CallbackQuery, state: FSMContext):
    await call.message.answer(await get_params())


@dp.callback_query_handler(IsAdmin(), text_contains="numbers_stats", state="*")
async def numbers_stats(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(choose_numbers_stats_keyboard)


@dp.callback_query_handler(IsAdmin(), dates_callback.filter(), state="*")
async def numbers_stats(call: CallbackQuery, callback_data: dict, state: FSMContext):
    answer = f'Статистика по проданным номерам\n\n{callback_data["time"]}:\n\n'
    country = None
    cost = 0
    count = 0
    for number in (await select_by_days(callback_data["time"])):
        print(number.country)
        if not country:
            country = number.country
        elif country != number.country:
            country = number.country
            answer += f'{number.country}: {count} номеров. Общая стоимость: {cost}\n'
            count = 0
            cost = 0
        else:
            cost += number.cost
            count += 1
    if answer == f'Статистика по проданным номерам\n\n{callback_data["time"]}:\n\n':
        answer += 'Нет проданных номеров'
    await call.message.answer(answer)


@dp.callback_query_handler(IsAdmin(), text_contains="countries_stats", state="*")
async def countries_stats(call: CallbackQuery, state: FSMContext):
    await call.message.answer('В разработке...')
