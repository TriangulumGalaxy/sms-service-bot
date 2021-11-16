from aiogram.dispatcher.storage import FSMContext
from apps.root import dp
from aiogram.types import Message
from .keyboards import lang_keyboard


@dp.message_handler(commands=['start'])
async def start_cmd(message: Message, state: FSMContext):
    await message.answer("Choose your language (Выберите язык):", reply_markup=lang_keyboard)
