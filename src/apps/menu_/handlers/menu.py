import asyncio

from aiogram.dispatcher.storage import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from apps.root import bot, dp, sub
from apps.start.keyboards import (get_countries_and_operators_keyboard,
                                  get_operators_keyboard)
from apps.menu_.keyboards.inline import (after_order_menu, back_to_menu_keyboard,
                                         change_balance_limit_keyboard,
                                         get_limits_keyboard,
                                         get_services_and_costs_keyboard, menu_callback,
                                         menu_keyboard, ok_and_delete_keyboard,
                                         page_callback, service_callback, get_current_numbers_keyboard)
from modules.api.check_sms import pending_sms
from modules.api.services import (exceptions, get_balance,
                                  get_country_and_operators, get_number,
                                  get_services_and_cost, set_status)
from modules.db.schemas import sold_numbers as sold_numbers_db
from modules.db.schemas import user as user_db
from modules.statistics import json_stats
from apps.menu_.states.menu import MenuStates


async def get_menu_text(user_id: int) -> str:
    menu_body = 'Баланс: {balance}\n' \
        'Номер телефона: {phone}\n' \
        'Сервис: {service}\n' \
        'Страна: {country}\n' \
        'Цена: {price}\n'
    user = await user_db.select(user_id)
    balance = await get_balance(user.api_key)
    return menu_body.format(balance=balance, phone=user.phone_number, service=user.service, country=user.country, price=user.number_price)


@dp.callback_query_handler(lambda c: ("back_to_menu" in c.data) or (c.data == "bool:no"), state="*")
async def menu_callback_handler(call: CallbackQuery, state: FSMContext):
    kybrd = menu_keyboard
    if (await user_db.select(call.message.chat.id)).is_admin:
        kybrd.add(InlineKeyboardButton(
            "Посмотреть статистику", callback_data="get_statistics"))
    await call.message.edit_text((await get_menu_text(call.message.chat.id)), reply_markup=kybrd)
    await state.finish()


@dp.message_handler(commands=['menu'], state="*")
async def menu_cmd(message: Message, state: FSMContext):
    await message.answer((await get_menu_text(message.chat.id)), reply_markup=menu_keyboard)


@dp.callback_query_handler(menu_callback.filter(action="buy_number"))
async def buy_number_callback(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text((await get_menu_text(call.message.chat.id)), reply_markup=(await get_countries_and_operators_keyboard(page=1)))
    api_key = (await user_db.select(call.message.chat.id)).api_key
    await state.update_data({'api_key': api_key})
    await MenuStates.country.set()
    await json_stats.update_param('Этап выбора страны (уже зарегистрирован)')


@dp.callback_query_handler(text_contains="country_name", state=MenuStates.country)
async def country_callback(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    country = call.data.split(':')[1]
    country_id = [d['id'] for d in (await get_country_and_operators(api_key=data.get('api_key'))) if d['name'] == country][0]
    await user_db.update(call.message.chat.id, country=country, operator=None, service=None, country_id=country_id)
    await call.message.edit_text((await get_menu_text(call.message.chat.id)), reply_markup=(await get_operators_keyboard(country_name=country, page=1, api_key=data.get('api_key'))))
    data.update({'country_id': country_id})
    await state.update_data(data)
    await MenuStates.operator.set()


@dp.callback_query_handler(text_contains='operator_name', state=MenuStates.operator)
async def operator_callback(call: CallbackQuery, state: FSMContext):
    operator = call.data.split(':')[1]
    data = await state.get_data()
    await user_db.update(call.message.chat.id, operator=operator)
    await call.message.edit_text((await get_menu_text(call.message.chat.id)), reply_markup=(await get_services_and_costs_keyboard(operator=operator, country=data.get('country_id'), api_key=data.get('api_key'))))
    data.update({"operator": operator})
    await state.update_data(data)
    await MenuStates.service.set()
    await json_stats.update_param('Этап выбора сервиса (уже зарегистрирован)')


@dp.callback_query_handler(service_callback.filter(), state=MenuStates.service)
async def choose_service_callback(call: CallbackQuery, state: FSMContext, callback_data: dict):
    user = await user_db.select(call.message.chat.id)
    data = await state.get_data()
    service = callback_data['name']
    price = callback_data['price']
    svs = list(filter(lambda x: x['name'] == service, await get_services_and_cost(operator=data.get('operator'), country=data.get('country_id'), api_key=data.get('api_key'))))
    current_balance = await get_balance(api_key=data.get('api_key'))
    balance_limit = user.balance_limit
    if balance_limit > current_balance:
        await call.message.answer(f"Ваш баланс ниже {balance_limit} и составляет {current_balance}", reply_markup=ok_and_delete_keyboard)
    await user_db.update(call.message.chat.id, service=svs[0]['id'], number_price=float(price))

    res = await get_number(
        api_key=data.get('api_key'),
        country=data.get('country_id'),
        operator=data.get('operator'),
        service=svs[0]['id']
    )
    if res in exceptions:
        await call.message.edit_text(f'Произошла ошибка: {res}')
        await state.finish()
        await user_db.update(
            user_id=call.message.chat.id,
            country='',
            number_price=0.0,
            phone_number='',
            service=''
        )
        return
    current_balance = await get_balance(api_key=user.api_key)
    balance_limit = user.balance_limit
    if balance_limit > current_balance:
        await call.message.answer(f"Ваш баланс ниже {balance_limit} и составляет {current_balance}", reply_markup=ok_and_delete_keyboard)
    await user_db.update(call.message.chat.id, order_id=int(res.split(":")[1]), phone_number=res.split(":")[2])
    await call.message.edit_text((await get_menu_text(call.message.chat.id)), reply_markup=after_order_menu)
    task = asyncio.create_task(pending_sms(call.message.chat.id, int(
        res.split(":")[1]), api_key=data.get("api_key"), bot=bot))
    sold_number_user = await user_db.select(call.message.chat.id)
    await sold_numbers_db.add(sold_number_user.order_id, sold_number_user.phone_number, sold_number_user.user_id, sold_number_user.number_price, sold_number_user.country)
    await json_stats.update_param('Получил номер  (уже зарегистрирован)')
    await task
    
    await state.finish()


@dp.callback_query_handler(page_callback.filter(), state='*')
async def page_callback_handler(call: CallbackQuery, state: FSMContext, callback_data: dict):
    user_id = call.message.chat.id
    user = await user_db.select(user_id)
    if callback_data['action'] == "back" and int(callback_data['page']) - 1 > 0:
        await call.message.edit_reply_markup((await get_services_and_costs_keyboard(page=int(callback_data['page']) - 1, country=user.country_id, operator=user.operator, api_key=user.api_key)))
    elif callback_data['action'] == "next":
        await call.message.edit_reply_markup((await get_services_and_costs_keyboard(page=int(callback_data['page']) + 1, country=user.country_id, operator=user.operator, api_key=user.api_key)))


@dp.callback_query_handler(text_contains='save_to_favourite', state='*')
async def save_to_favourite_callback(call: CallbackQuery, state: FSMContext):
    user_id = call.message.chat.id
    user = await user_db.select(user_id)
    fav_operator = user.operator
    fav_country = user.country_id
    fav_service = user.service
    await user_db.update(user_id, fav_service=fav_service, fav_country=str(fav_country), fav_operator=fav_operator)
    await call.message.edit_text(f"Вы сохранили следующие настройки:\nСтрана: {user.country}\nОператор: {fav_operator}\nСервис: {fav_service}", reply_markup=back_to_menu_keyboard)


@dp.callback_query_handler(menu_callback.filter(action='buy_from_saved'))
async def order_from_favourite_number_callback(call: CallbackQuery, state: FSMContext):
    user_id = call.message.chat.id
    user = await user_db.select(user_id)
    country = user.fav_country
    operator = user.fav_operator
    service = user.fav_service

    current_balance = await get_balance(api_key=user.api_key)
    balance_limit = user.balance_limit
    if balance_limit > current_balance:
        await call.message.answer(f"Ваш баланс ниже {balance_limit} и составляет {current_balance}", reply_markup=ok_and_delete_keyboard)
    # await user_db.update(call.message.chat.id, service=svs[0]['id'], number_price=float(user.number_price))

    res = await get_number(
        api_key=user.api_key,
        country=country,
        operator=operator,
        service=service
    )
    if res in exceptions:
        await call.message.edit_text(f'Произошла ошибка: {res}', reply_markup=back_to_menu_keyboard)
        await state.finish()
        await user_db.update(
            user_id=call.message.chat.id,
            country='',
            number_price=0.0,
            phone_number='',
            service=''
        )
        return
    current_balance = await get_balance(api_key=user.api_key)
    balance_limit = user.balance_limit
    if balance_limit > current_balance:
        await call.message.answer(f"Ваш баланс ниже {balance_limit} и составляет {current_balance}", reply_markup=ok_and_delete_keyboard)
    await user_db.update(call.message.chat.id, order_id=int(res.split(":")[1]), phone_number=res.split(":")[2])
    await call.message.edit_text((await get_menu_text(call.message.chat.id)), reply_markup=after_order_menu)
    task = asyncio.create_task(pending_sms(call.message.chat.id, int(
        res.split(":")[1]), api_key=user.api_key, bot=bot))
    sold_number_user = await user_db.select(call.message.chat.id)
    await sold_numbers_db.add(sold_number_user.order_id, sold_number_user.phone_number, sold_number_user.user_id, sold_number_user.number_price, sold_number_user.country, active=True)
    await state.finish()
    await json_stats.update_param('Получил номер  (уже зарегистрирован)')
    await task



@dp.callback_query_handler(menu_callback.filter(action='cancel_number'))
async def cancel_number_ordering_callback(call: CallbackQuery, state: FSMContext):
    order_id = (await user_db.select(call.message.chat.id)).order_id
    if not order_id:
        await call.message.edit_text('Вы еще не купили номер!', reply_markup=back_to_menu_keyboard)
        return
    numbers = [i.number for i in await sold_numbers_db.get_numbers_by_user(call.message.chat.id)]
    await call.message.edit_text('Выберите номер, который хотите отменить', reply_markup=get_current_numbers_keyboard(numbers))
    await MenuStates.deleting_number.set()
    # await set_status(id_=order_id, status=8)
    # await user_db.update(
    #     user_id=call.message.chat.id,
    #     country='',
    #     number_price=0.0,
    #     phone_number='',
    #     service=''
    # )
    # await call.message.edit_text('Отменено', reply_markup=back_to_menu_keyboard)
    await json_stats.update_param('Отменил номер (уже зарегистрирован)')


@dp.callback_query_handler(lambda c: c.data.startswith('number:'), state=MenuStates.deleting_number)
async def number_canceling_callback(call: CallbackQuery, state: FSMContext):
    number = call.data.strip('numbers:')
    order_id = (await sold_numbers_db.get_number_id(number)).id
    await set_status(id_=order_id, status=8)
    await user_db.update(
        user_id=call.message.chat.id,
        country='',
        number_price=0.0,
        phone_number='',
        service=''
    )
    await sold_numbers_db.update(order_id, active=False)
    await call.message.edit_text('Номер отменен', reply_markup=back_to_menu_keyboard)
    await state.finish()


@dp.callback_query_handler(menu_callback.filter(action='request_new_sms'))
async def request_new_sms_callback(call: CallbackQuery, state: FSMContext):
    numbers = [i.number for i in await sold_numbers_db.get_numbers_by_user(call.message.chat.id)]
    await call.message.edit_text('Выберите номер, с которого хотите запросить СМС повторно', reply_markup=get_current_numbers_keyboard(numbers=numbers))
    await MenuStates.requesting_sms.set()


@dp.callback_query_handler(lambda c: c.data.startswith('number:'), state=MenuStates.requesting_sms)
async def requesting_sms_callback(call: CallbackQuery, state: FSMContext):
    user = await user_db.select(call.message.chat.id)
    order_id = user.order_id
    await set_status(id_=order_id, status=3, api_key=user.api_key)
    await call.message.edit_text('СМС повторно отправлено', reply_markup=back_to_menu_keyboard)
    order_id = (await sold_numbers_db.get_number_id(call.data.strip('number:'))).id

    task = asyncio.create_task(pending_sms(
        call.message.chat.id, order_id, api_key=user.api_key, bot=bot))
    await task
    await state.finish()


@dp.callback_query_handler(menu_callback.filter(action='end_activation'))
async def end_activation_number_choose_callback(call: CallbackQuery, state: FSMContext):
    numbers = [i.number for i in await sold_numbers_db.get_numbers_by_user(call.message.chat.id)]
    await call.message.edit_text('Выберите номер, на котором нужно завершить регистрацию', reply_markup=get_current_numbers_keyboard(numbers))
    await MenuStates.end_activation.set()


@dp.callback_query_handler(lambda c: c.data.startswith('number:'), state=MenuStates.end_activation)
async def end_activation_callback(call: CallbackQuery, state: FSMContext):
    user = await user_db.select(call.message.chat.id)
    order_id = (await sold_numbers_db.get_number_id(call.data.strip("numbers:"))).id
    if not order_id:
        await call.message.edit_text('Вы еще не купили номер!', reply_markup=back_to_menu_keyboard)
        return
    res = await set_status(id_=order_id, status=6, api_key=user.api_key)
    if res not in exceptions:
        await user_db.update(
            user_id=call.message.chat.id,
            country='',
            number_price=0.0,
            phone_number='',
            service=''
        )
        await call.message.edit_text('Активация завершена', reply_markup=back_to_menu_keyboard)
    await state.finish()


@dp.callback_query_handler(text_contains="ok_and_delete", state="*")
async def ok_and_delete_callback(call: CallbackQuery, state: FSMContext):
    await call.message.delete()


@dp.callback_query_handler(menu_callback.filter(action='pay_balance'), state="*")
async def deposit_money_callbeck(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Пополнить баланс можно на сайте: https://sms-service-online.com/ru/pay/')


@dp.callback_query_handler(menu_callback.filter(action='balance_notifications'))
async def balance_limit_notification_callback(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"У вас стоит лимит: {(await user_db.select(call.message.chat.id)).balance_limit}", reply_markup=change_balance_limit_keyboard)


@dp.callback_query_handler(text_contains="change_balance_limit")
async def change_balance_limit_callback(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Выберите сумму, при балансе ниже которой Вам придет уведомление", reply_markup=(await get_limits_keyboard()))


@dp.callback_query_handler(text_contains="set_limit")
async def set_limit_callback(call: CallbackQuery, state: FSMContext):
    await user_db.update(call.message.chat.id, balance_limit=int(call.data.split(":")[1]))
    await call.message.edit_text(f"Теперь Вам будут приходить уведомления, когда баланс упадет ниже {call.data.split(':')[1]}", reply_markup=back_to_menu_keyboard)


@dp.callback_query_handler(menu_callback.filter(action='countries_notifications'))
async def countries_notifications_callback(call: CallbackQuery, state: FSMContext):
    users = await sub.get_users()
    if call.message.chat.id not in users:
        await sub.add_user(call.message.chat.id)
        await call.message.edit_text('Уведомления о новых странах включены', reply_markup=back_to_menu_keyboard)
    else:
        await sub.delete_user(call.message.chat.id)
        await call.message.edit_text('Уведомления о новых странах выключены', reply_markup=back_to_menu_keyboard)
