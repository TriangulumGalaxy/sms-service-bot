import aiohttp
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import CallbackQuery, Message
from apps.root import dp
from modules.api.services import get_country_and_operators
from modules.db.schemas import user
from modules.statistics import json_stats

from .keyboards import (boolean_keyboard, get_countries_and_operators_keyboard,
                        get_operators_keyboard, get_services_keyboard,
                        lang_keyboard, langs, pagination_callback,
                        services_callback)
from .states import AcceptingRegistration


@dp.message_handler(commands=['start'])
async def start_cmd(message: Message, state: FSMContext):
    await message.answer("Choose your language (Выберите язык):", reply_markup=lang_keyboard)
    await json_stats.update_param('Запустили бота')
    await AcceptingRegistration.language.set()


@dp.message_handler(lambda msg: not msg.text.startswith('/'), state=AcceptingRegistration.language)
async def choose_lang(message: Message, state: FSMContext):
    if message.text in langs:
        await message.answer(f"Вы выбрали {message.text.lower()[:-3]} язык")
        await user.add(message.chat.id, message.text[:-3])
        await message.answer("Зарегистрированы ли вы на смс сервисе?", reply_markup=boolean_keyboard)


@dp.callback_query_handler(text_contains='answer_y', state=AcceptingRegistration)
async def reg_check_y(call: CallbackQuery, state: FSMContext):
    await call.message.answer(f"Пожалуйста, отправьте ваш API ключ (API ключ Вы можете получить в разделе: https://sms-service-online.com/ru/user/profile/)")
    await AcceptingRegistration.accepting_reg.set()


@dp.callback_query_handler(text_contains='answer_n', state=AcceptingRegistration)
async def reg_check_n(call: CallbackQuery, state: FSMContext):
    await call.message.answer(f"Чтобы использовать бота, вам необходимо зарегестрироваться на сервисе. Выберите страну номера:", reply_markup=(await get_countries_and_operators_keyboard(1)))
    await json_stats.update_param('Этап выбора страны')


@dp.callback_query_handler(pagination_callback.filter(), state='*')
async def change_page(query: CallbackQuery, callback_data: dict):
    if callback_data["action"] == "back":
        kybrd = await get_countries_and_operators_keyboard(int(callback_data["page"]) - 1)
        if kybrd:
            await query.message.edit_reply_markup(kybrd)
    elif callback_data["action"] == "next":
        kybrd = await get_countries_and_operators_keyboard(int(callback_data["page"]) + 1)
        if kybrd:
            await query.message.edit_reply_markup(kybrd)
    elif callback_data["action"] == "op_back":
        kybrd = await get_operators_keyboard(callback_data["country"], int(callback_data["page"]) - 1, api_key=((await user.select(query.message.chat.id)).api_key))
        if kybrd:
            await query.message.edit_reply_markup(kybrd)
    elif callback_data["action"] == "op_next":
        kybrd = await get_operators_keyboard(callback_data["country"], int(callback_data["page"]) + 1, api_key=((await user.select(query.message.chat.id)).api_key))
        if kybrd:
            await query.message.edit_reply_markup(kybrd)
    elif callback_data["action"] == "s_back" and int(callback_data['page']) - 1 > 0:
        kybrd = await get_services_keyboard(callback_data["operator"], callback_data["country_id"], int(callback_data["page"]) - 1)
        if kybrd:
            await query.message.edit_reply_markup(kybrd)
    elif callback_data["action"] == "s_next":
        kybrd = await get_services_keyboard(callback_data["operator"], callback_data["country_id"], int(callback_data["page"]) + 1)
        if kybrd:
            await query.message.edit_reply_markup(kybrd)


@dp.callback_query_handler(text_contains='country_name', state=AcceptingRegistration)
async def get_operators(call: CallbackQuery, state: FSMContext):
    await state.update_data(country=call.data[13:])
    await call.message.answer(f"Выберите оператора:", reply_markup=(await get_operators_keyboard(call.data[13:], 1, api_key=((await user.select(call.message.chat.id)).api_key))))


@dp.callback_query_handler(text_contains='operator_name', state=AcceptingRegistration)
async def get_services(call: CallbackQuery, state: FSMContext):
    await state.update_data(operator=call.data[14:])
    user_data = await state.get_data()
    country_id = [d['id'] for d in (await get_country_and_operators()) if d['name'] == user_data['country']][0]
    await call.message.answer(f"Выберите сервис:", reply_markup=(await get_services_keyboard(call.data[14:], country_id, 1)))
    await json_stats.update_param('Этап выбора сервиса')


@dp.callback_query_handler(services_callback.filter(), state=AcceptingRegistration)
async def answer_services(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Регистрируйтесь по ссылке: https://sms-service-online.com/ru/register/")
    await json_stats.update_param('Этап перехода на регистрацию')


@dp.message_handler(state=AcceptingRegistration.accepting_reg)
async def check_api_key(message: Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://sms-service-online.com/stubs/handler_api?api_key={message.text.strip()}&action=getBalance&lang=ru') as resp:
            if (await resp.text()) == "BAD_KEY":
                await message.answer(f"Неправильный ключ. Попробуйте снова или используйте другой ключ")
            elif resp.status != 200:
                await message.answer(f"Ошибка")
            else:
                await message.answer(f'API ключ подключен. Ваш баланс: {await resp.text()}. \nЧтобы вызвать меню действий, напишите /menu')
                await user.update(message.chat.id, api_key=message.text.strip())
                await state.finish()
