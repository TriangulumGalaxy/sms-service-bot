from aiogram import executor
from apps import dp
# from apps import _filters

async def on_startup(dp):
    print("bot has started")

def bind_filters(dp, *args):
    """
    `args`: фильтры
    `dp`: Dispatcher
    """
    
    filters = args[0]
    for fltr in filters:
        dp.bind_filter(fltr)

if __name__ == '__main__':
    # bind_filters(dp, _filters)
    executor.start_polling(dp, on_startup=on_startup, skip_updates=False)
