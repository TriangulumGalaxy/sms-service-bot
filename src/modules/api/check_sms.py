from aiogram.bot.bot import Bot
from .services import get_status


async def wait_for_sms(order_id: int, api_key: str) -> str:
    while True:
        res = await get_status(id_=order_id, api_key=api_key)
        if "STATUS_CANCEL" in res:
            return "STATUS_CANCEL"
        elif "STATUS_OK" in res:
            return res.strip("STATUS_OK:")
        elif "STATUS_WAIT_CODE" in res:
            continue
        else:
            return res


async def pending_sms(user_id: int, order_id: int, api_key: str, bot: Bot):
    res = await wait_for_sms(order_id, api_key)
    if res == "ERROR_API":
        await bot.send_message(user_id, 'Произошла ошибка на сервере, или вы отменили номер, попробуйте еще раз!')
    elif not res == "STATUS_CANCEL":
        await bot.send_message(user_id, res)