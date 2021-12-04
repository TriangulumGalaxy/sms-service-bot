from aiogram import executor
from apps import dp, db
from apps import _filters
from apps.root import sub
import asyncio


async def flush_all():
    print('Очистка базы...')
    await db.gino.drop_all()
    print('Готово')
    print('Создание таблиц...')
    await db.gino.create_all()
    print('Готово')


async def connect_db():
    from modules.db import database

    print('Подключение к базе данных...')
    await database.on_startup(dp)
    print('Подключение установлено')
    # await flush_all()


async def on_startup(dp):
    print("bot has started")
    await connect_db()
    # Creating background processes
    asyncio.create_task(sub.run_countries_monitoring())


def bind_filters(dp, *args):
    """
    `args`: фильтры
    `dp`: Dispatcher
    """

    filters = args[0]
    for fltr in filters:
        dp.bind_filter(fltr)


if __name__ == '__main__':
    bind_filters(dp, _filters)
    executor.start_polling(dp, on_startup=on_startup, skip_updates=False)
