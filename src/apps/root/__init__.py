from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from modules.config.env_config import TOKEN
from modules.db.database import db
from modules.subscription.country import CountrySubscription

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

sub = CountrySubscription(bot=bot)
