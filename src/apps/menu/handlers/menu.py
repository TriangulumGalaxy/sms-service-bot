from aiogram.dispatcher.storage import FSMContext
from aiogram.types import CallbackQuery, Message
from apps.root import dp
from apps.start.keyboards import (get_countries_and_operators_keyboard,
                                  get_operators_keyboard)
from modules.api.services import get_country_and_operators, get_number, exceptions

from ..keyboards.inline import (
    get_services_and_costs_keyboard, bool_keyboard)
from ..keyboards.inline import menu as menu_keyboard
from ..keyboards.inline import back_to_menu_keyboard
from ..keyboards.inline import page_callback, service_callback
from modules.db.schemas import user as user_db
from ..states.menu import MenuStates


@dp.callback_query_handler(lambda c: ("back_to_menu" in c.data) or (c.data == "bool:no"), state="*")
async def menu_callback_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('Menu', reply_markup=menu_keyboard)
    await state.finish()


@dp.message_handler(commands=['menu'], state="*")
async def menu_cmd(message: Message, state: FSMContext):
    await message.answer('Menu', reply_markup=menu_keyboard)


@dp.callback_query_handler(lambda c: c.data and c.data == "choose_country")
async def country_choose(call: CallbackQuery):
    await call.message.edit_text('Выберите страну', reply_markup=(await get_countries_and_operators_keyboard(page=1)))
    await MenuStates.country.set()


@dp.callback_query_handler(text_contains="country_name", state=MenuStates.country)
async def country_choose_and_save_callback(call: CallbackQuery, state: FSMContext):
    # TEST !!!!
    country = call.data.split(':')[1]
    country_id = [d['id'] for d in (await get_country_and_operators()) if d['name'] == country][0]
    await user_db.update(call.message.chat.id, country=country, operator=None, service=None, country_id=country_id)
    await call.message.edit_text('Вы поменяли страну. Не забудьте выбрать оператора и сервис перед тем как заказать номер!', reply_markup=back_to_menu_keyboard)
    await state.finish()


@dp.callback_query_handler(lambda c: c.data and c.data == "choose_operator", state="*")
async def operator_choose(call: CallbackQuery):
    # Здесь название страны из БД
    country = (await user_db.select(call.message.chat.id)).country  # TEST !!!!
    await call.message.edit_text('Operator', reply_markup=(await get_operators_keyboard(country_name='Россия', page=1)))
    await MenuStates.operator.set()


@dp.callback_query_handler(text_contains='operator_name', state=MenuStates.operator)
async def operator_choose_and_save_callback(call: CallbackQuery, state: FSMContext):
    operator = call.data.split(':')[1]
    await user_db.update(call.message.chat.id, operator=operator)  # TEST!!!!
    await call.message.edit_text(f'Вы выбрали оператора: {operator}', reply_markup=back_to_menu_keyboard)


@dp.callback_query_handler(lambda c: c.data and c.data == "choose_service")
async def service_choose(call: CallbackQuery):
    await call.message.edit_text('Service', reply_markup=(await get_services_and_costs_keyboard()))
    await MenuStates.service.set()


@dp.callback_query_handler(service_callback.filter(), state=MenuStates.service)
async def set_service_callback(call: CallbackQuery, state: FSMContext, callback_data: dict):
    operator = (await user_db.select(call.message.chat.id)).operator
    if not operator:
        await call.message.edit_text('Пожалуйста, выберите оператора!')
        return
    service = callback_data['name']
    price = callback_data['price']
    await call.message.edit_text(f'Вы хотите заказать номер со следующими настройками?\nOperator:{operator}\nService:{service}\nPrice:{price}\n', reply_markup=bool_keyboard)


@dp.callback_query_handler(page_callback.filter(), state='*')
async def page_callback_handler(call: CallbackQuery, state: FSMContext, callback_data: dict):
    if callback_data['action'] == "back" and int(callback_data['page']) - 1 > 0:
        await call.message.edit_reply_markup((await get_services_and_costs_keyboard(page=int(callback_data['page']) - 1)))
    elif callback_data['action'] == "next":
        await call.message.edit_reply_markup((await get_services_and_costs_keyboard(page=int(callback_data['page']) + 1)))


@dp.callback_query_handler(text='order_number', state='*')
async def order_number_callbak(call: CallbackQuery, state: FSMContext):
    user_id = call.message.chat.id
    user = await user_db.select(user_id)
    country = user.country_id
    operator = user.operator
    service = user.service
    if not all((country, operator, service)):
        await call.message.edit_text('Вы выбрали не все параметры!', reply_markup=back_to_menu_keyboard)
        await state.finish()
        return
    res = await get_number(service, operator, country)
    if res in exceptions:
        await call.message.edit_text(f'Произошла ошибка: {res}', reply_markup=back_to_menu_keyboard)
