import aiohttp
from aiogram.dispatcher.storage import FSMContext
from apps.root import dp
from aiogram.types import Message, CallbackQuery
from .keyboards import lang_keyboard, boolean_keyboard, langs
from .states import AcceptingRegistration


@dp.message_handler(commands=['start'])
async def start_cmd(message: Message, state: FSMContext):
    await message.answer("Choose your language (Выберите язык):", reply_markup=lang_keyboard)
    
@dp.message_handler()
async def choose_lang(message: Message, state: FSMContext):
    if message.text in langs:
        await message.answer(f"Вы выбрали {message.text.lower()[:-3]} язык")
        # Здесь должно быть добавление в бд языка пользователя
        await message.answer("Зарегистрированы ли вы на смс сервисе?", reply_markup=boolean_keyboard)

@dp.callback_query_handler(text_contains='answer_y', state='*')
async def reg_check_y(call: CallbackQuery, state: FSMContext):
        await call.message.answer(f"Пожалуйста, отправьте ваш API ключ (API ключ Вы можете получить в разделе: https://sms-service-online.com/ru/user/profile/)")
        await AcceptingRegistration.accepting_reg.set()

@dp.callback_query_handler(text_contains='answer_n', state='*')
async def reg_check_n(call: CallbackQuery, state: FSMContext):
        await call.message.answer(f"Чтобы использовать бота, вам необходимо зарегестрироваться на сервисе: https://sms-service-online.com/")

@dp.message_handler(state=AcceptingRegistration.accepting_reg)
async def check_api_key(message: Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://sms-service-online.com/stubs/handler_api?api_key={message.text.strip()}&action=getBalance&lang=ru') as resp:
            if resp.text == "BAD_KEY":
                await message.answer(f"Неправильный ключ. Попробуйте снова или используйте другой ключ")
            elif resp.status != 200:
                await message.answer(f"Ошибка")
            else:
                await message.answer(f'API ключ подключен. Ваш баланс: {await resp.text()}')
    