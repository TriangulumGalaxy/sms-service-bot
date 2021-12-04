import json
from aiohttp import ClientSession

REG_URL = "https://sms-service-online.com/register-with-confirm?email={EMAIL}"
EMAIL_URL = "https://sms-service-online.com/register-email-confirm?token={TOKEN}"
AUTH_URL = "https://sms-service-online.com/auth-post?email={EMAIL}&password={PASSWORD}"

async def register(email: str, name: str = None):
    """
    Регистрация с подтверждением пользователя
    """
    
    async with ClientSession() as session:
        if name:
            url = REG_URL + '&name={NAME}'
            async with session.get(url.format(EMAIL=email, NAME=name)) as res:
                response = await res.text()
                print(response)
        else:
            async with session.get(REG_URL.format(EMAIL=email)) as res:
                response = await res.text()
                print(response)
    return response


async def email(token: str):
    """
    Подтверждение почты
    """
    
    async with ClientSession() as session:
        async with session.get(EMAIL_URL.format(TOKEN=token)) as res:
            response = await res.text()
            print(response)
    return response


async def auth(email: str, password: str):
    """
    Авторизация
    """
    
    async with ClientSession() as session:
        async with session.get(EMAIL_URL.format(EMAIL=email, PASSWORD=password)) as res:
            response = await res.text()
            print(response)
    return response


