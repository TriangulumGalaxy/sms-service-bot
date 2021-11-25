from aiogram.dispatcher.storage import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from apps.root import dp
from apps.start.keyboards import (get_countries_and_operators_keyboard,
                                  get_operators_keyboard)
from modules.api.services import (exceptions, get_balance,
                                  get_country_and_operators, get_number,
                                  get_services_and_cost, get_status,
                                  set_status)
from modules.db.schemas import sold_numbers as sold_numbers_db
from modules.db.schemas import user as user_db
from modules.statistics import json_stats

from ..keyboards.inline import (after_order_menu, back_to_menu_keyboard,
                                bool_keyboard, change_balance_limit_keyboard,
                                get_limits_keyboard,
                                get_services_and_costs_keyboard)
from ..keyboards.inline import menu as menu_keyboard
from ..keyboards.inline import (ok_and_delete_keyboard, page_callback,
                                service_callback)
from ..states.menu import MenuStates


@dp.callback_query_handler(lambda c: ("back_to_menu" in c.data) or (c.data == "bool:no"), state="*")
async def menu_callback_handler(call: CallbackQuery, state: FSMContext):
    kybrd = menu_keyboard
    if (await user_db.select(call.message.chat.id)).is_admin:
        kybrd.add(InlineKeyboardButton(
            "Посмотреть статистику", callback_data="get_statistics"))
    await call.message.edit_text('Menu', reply_markup=kybrd)
    await state.finish()


@dp.message_handler(commands=['menu'], state="*")
async def menu_cmd(message: Message, state: FSMContext):
    kybrd = menu_keyboard
    if (await user_db.select(message.chat.id)).is_admin:
        kybrd.add(InlineKeyboardButton(
            "Посмотреть статистику", callback_data="get_statistics"))
    await message.answer('Menu', reply_markup=kybrd)


@dp.callback_query_handler(lambda c: c.data and c.data == "choose_country")
async def country_choose(call: CallbackQuery):
    await call.message.edit_text('Выберите страну', reply_markup=(await get_countries_and_operators_keyboard(page=1)))
    await json_stats.update_param('Этап выбора страны (уже зарегистрирован)')
    await MenuStates.country.set()


@dp.callback_query_handler(text_contains="country_name", state=MenuStates.country)
async def country_choose_and_save_callback(call: CallbackQuery, state: FSMContext):
    country = call.data.split(':')[1]
    country_id = [d['id'] for d in (await get_country_and_operators()) if d['name'] == country][0]
    await user_db.update(call.message.chat.id, country=country, operator=None, service=None, country_id=country_id)
    await call.message.edit_text('Вы поменяли страну. Не забудьте выбрать оператора и сервис перед тем как заказать номер!', reply_markup=back_to_menu_keyboard)
    await state.finish()


@dp.callback_query_handler(lambda c: c.data and c.data == "choose_operator", state="*")
async def operator_choose(call: CallbackQuery):
    country = (await user_db.select(call.message.chat.id)).country
    await call.message.edit_text('Operator', reply_markup=(await get_operators_keyboard(country_name=country, page=1)))
    await MenuStates.operator.set()


@dp.callback_query_handler(text_contains='operator_name', state=MenuStates.operator)
async def operator_choose_and_save_callback(call: CallbackQuery, state: FSMContext):
    operator = call.data.split(':')[1]
    await user_db.update(call.message.chat.id, operator=operator)
    await call.message.edit_text(f'Вы выбрали оператора: {operator}', reply_markup=back_to_menu_keyboard)


@dp.callback_query_handler(lambda c: c.data and c.data == "choose_service")
async def service_choose(call: CallbackQuery):
    user_id = call.message.chat.id
    user = await user_db.select(user_id)
    if not user.operator:
        await call.message.edit_text('Сначала выберите оператора', reply_markup=back_to_menu_keyboard)
        return
    if not user.country or user.country_id is None:
        await call.message.edit_text('Сначала выберите срану', reply_markup=back_to_menu_keyboard)
        return
    await call.message.edit_text('Service', reply_markup=(await get_services_and_costs_keyboard(country=user.country_id, operator=user.operator)))
    await json_stats.update_param('Этап выбора сервиса (уже зарегистрирован)')
    await MenuStates.service.set()


@dp.callback_query_handler(service_callback.filter(), state=MenuStates.service)
async def set_service_callback(call: CallbackQuery, state: FSMContext, callback_data: dict):
    user_id = call.message.chat.id
    operator = (await user_db.select(user_id)).operator
    if not operator:
        await call.message.edit_text('Пожалуйста, выберите оператора!')
        return
    service = callback_data['name']
    price = callback_data['price']
    svs = list(filter(lambda x: x['name'] == service, await get_services_and_cost(operator=operator, country=(await user_db.select(user_id)).country_id)))
    # print(svs)
    current_balance = await get_balance()
    balance_limit = (await user_db.select(user_id)).balance_limit
    if balance_limit > current_balance:
        await call.message.answer(f"Ваш баланс ниже {balance_limit} и составляет {current_balance}", reply_markup=ok_and_delete_keyboard)
    await user_db.update(user_id, service=svs[0]['id'], number_price=float(price))
    await call.message.edit_text(f'Вы хотите заказать номер со следующими настройками?\nOperator:{operator}\nService:{service}\nPrice:{price}\n', reply_markup=bool_keyboard)


@dp.callback_query_handler(page_callback.filter(), state='*')
async def page_callback_handler(call: CallbackQuery, state: FSMContext, callback_data: dict):
    user_id = call.message.chat.id
    user = await user_db.select(user_id)
    if callback_data['action'] == "back" and int(callback_data['page']) - 1 > 0:
        await call.message.edit_reply_markup((await get_services_and_costs_keyboard(page=int(callback_data['page']) - 1, country=user.country_id, operator=user.operator)))
    elif callback_data['action'] == "next":
        await call.message.edit_reply_markup((await get_services_and_costs_keyboard(page=int(callback_data['page']) + 1, country=user.country_id, operator=user.operator)))


@dp.callback_query_handler(text_contains='order_number', state='*')
async def order_number_callback(call: CallbackQuery, state: FSMContext):
    user_id = call.message.chat.id
    user = await user_db.select(user_id)
    country = user.country_id
    operator = user.operator
    service = user.service
    if country is None or not operator or not service:
        await call.message.edit_text('Вы выбрали не все параметры!', reply_markup=back_to_menu_keyboard)
        await state.finish()
        return
    res = await get_number(service, operator, country)
    if res in exceptions:
        await call.message.edit_text(f'Произошла ошибка: {res}', reply_markup=back_to_menu_keyboard)
        return
    current_balance = await get_balance()
    balance_limit = (await user_db.select(user_id)).balance_limit
    if balance_limit > current_balance:
        await call.message.answer(f"Ваш баланс ниже {balance_limit} и составляет {current_balance}", reply_markup=ok_and_delete_keyboard)
    await user_db.update(user_id, order_id=int(res.split(":")[1]), phone_number=res.split(":")[2])
    await call.message.edit_text(f'Данные вашего заказа:\nНомер:{res.split(":")[2]}', reply_markup=after_order_menu)
    await state.finish()
    await json_stats.update_param('Получил номер  (уже зарегистрирован)')

    # Добавление проданного номера в бд
    sold_number_user = await user_db.select(user_id)
    await sold_numbers_db.add(sold_number_user.phone_number, sold_number_user.number_price, sold_number_user.country)


@dp.callback_query_handler(text_contains='save_to_favourite')
async def save_to_favourite_callback(call: CallbackQuery, state: FSMContext):
    user_id = call.message.chat.id
    user = await user_db.select(user_id)
    fav_operator = user.operator
    fav_country = user.country_id
    fav_service = user.service
    await user_db.update(user_id, fav_service=fav_service, fav_country=str(fav_country), fav_operator=fav_operator)
    await call.message.edit_text(f"Вы сохранили следующие настройки:\nСтрана: {user.country}\nОператор: {fav_operator}\nСервис: {fav_service}", reply_markup=back_to_menu_keyboard)


@dp.callback_query_handler(text="order_from_favourite_number")
async def order_from_favourite_number_callback(call: CallbackQuery, state: FSMContext):
    user_id = call.message.chat.id
    user = await user_db.select(user_id)
    country = user.fav_country
    operator = user.fav_operator
    service = user.fav_service
    if country is None or not operator or not service:
        await call.message.edit_text('Избранное не найдено!', reply_markup=back_to_menu_keyboard)
        return
    res = await get_number(service, operator, country)
    if res in exceptions:
        await call.message.edit_text(f'Произошла ошибка: {res}', reply_markup=back_to_menu_keyboard)
        return
    current_balance = await get_balance()
    balance_limit = (await user_db.select(user_id)).balance_limit
    if balance_limit > current_balance:
        await call.message.answer(f"Ваш баланс ниже {balance_limit} и составляет {current_balance}", reply_markup=ok_and_delete_keyboard)
    await user_db.update(user_id, order_id=int(res.split(":")[1]), phone_number=res.split(":")[2])
    await call.message.edit_text(f'Данные вашего заказа:\nНомер:{res.split(":")[2]}', reply_markup=after_order_menu)
    await state.finish()

    await json_stats.update_param('Получил номер  (уже зарегистрирован)')

    # Добавление проданного номера в бд
    sold_number_user = await user_db.select(user_id)
    await sold_numbers_db.add(sold_number_user.phone_number, sold_number_user.number_price, sold_number_user.country)


@dp.callback_query_handler(text="cancel_order")
async def cancel_number_ordering_callback(call: CallbackQuery, state: FSMContext):
    order_id = (await user_db.select(call.message.chat.id)).order_id
    if not order_id:
        await call.message.edit_text('Вы еще не купили номер!', reply_markup=back_to_menu_keyboard)
        return
    await set_status(id_=order_id, status=8)
    await call.message.edit_text('Отменено', reply_markup=back_to_menu_keyboard)
    await json_stats.update_param('Отменил номер (уже зарегистрирован)')


@dp.callback_query_handler(text="end_activation")
async def end_activation_callback(call: CallbackQuery, state: FSMContext):
    order_id = (await user_db.select(call.message.chat.id)).order_id
    if not order_id:
        await call.message.edit_text('Вы еще не купили номер!', reply_markup=back_to_menu_keyboard)
        return
    res = await set_status(id_=order_id, status=6)
    # print(res)
    if res not in exceptions:
        await user_db.update(call.message.chat.id, country=None, country_id=None, operator=None, number_price=None, phone_number=None, order_id=None, service=None)
        await call.message.edit_text('Активация завершена', reply_markup=back_to_menu_keyboard)


@dp.callback_query_handler(text='retry_sms_sending')
async def retry_sms_sending_callback(call: CallbackQuery, state: FSMContext):
    order_id = (await user_db.select(call.message.chat.id)).order_id
    if not order_id:
        await call.message.edit_text('Вы еще не купили номер!', reply_markup=back_to_menu_keyboard)
        return
    await set_status(id_=order_id, status=3)
    await call.message.edit_text('СМС повторно отправлено', reply_markup=back_to_menu_keyboard)


@dp.callback_query_handler(text_contains='check_sms')
async def check_sms_handler(call: CallbackQuery, state: FSMContext):
    # print(await get_balance())
    order_id = (await user_db.select(call.message.chat.id)).order_id
    if not order_id:
        await call.message.edit_text('Вы еще не купили номер!', reply_markup=back_to_menu_keyboard)
        return
    res = await get_status(id_=order_id)
    if 'STATUS_WAIT_CODE' in res:
        await call.message.edit_text("Ожидаем смс, попробуйте позже!", reply_markup=back_to_menu_keyboard)
    elif "STATUS_OK" in res:
        await call.message.edit_text(f'Код: {res.split(":")[1]}', reply_markup=back_to_menu_keyboard)
        await json_stats.update_param('Получил смс (уже зарегистрирован)')
    else:
        # print(res)
        await call.message.edit_text('Нет смс', reply_markup=back_to_menu_keyboard)


@dp.callback_query_handler(text_contains="balance_limit_notification")
async def balance_limit_notification_callback(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"У вас стоит лимит: {(await user_db.select(call.message.chat.id)).balance_limit}", reply_markup=change_balance_limit_keyboard)


@dp.callback_query_handler(text_contains="change_balance_limit")
async def change_balance_limit_callback(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Выберите сумму, при балансе ниже которой Вам придет уведомление", reply_markup=(await get_limits_keyboard()))


@dp.callback_query_handler(text_contains="set_limit")
async def set_limit_callback(call: CallbackQuery, state: FSMContext):
    await user_db.update(call.message.chat.id, balance_limit=int(call.data.split(":")[1]))
    await call.message.edit_text(f"Теперь Вам будут приходить уведомления, когда баланс упадет ниже {call.data.split(':')[1]}", reply_markup=back_to_menu_keyboard)


@dp.callback_query_handler(text_contains="check_balance")
async def check_balance_callback(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"Ваш баланс: {await get_balance()}", reply_markup=back_to_menu_keyboard)


@dp.callback_query_handler(text_contains="ok_and_delete", state="*")
async def ok_and_delete_callback(call: CallbackQuery, state: FSMContext):
    await call.message.delete()


@dp.callback_query_handler(text_contains="deposit_money", state="*")
async def deposit_money_callbeck(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Поплнить баланс можно на сайте: https://sms-service-online.com/ru/pay/')
