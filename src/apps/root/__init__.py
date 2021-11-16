from aiogram import Dispatcher, Bot
from modules.config.env_config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
