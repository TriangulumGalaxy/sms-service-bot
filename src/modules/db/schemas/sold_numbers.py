from sqlalchemy import sql, Column, BigInteger, String, DateTime, Boolean
from asyncpg import UniqueViolationError
import datetime
from dateutil.relativedelta import *
from modules.db import database as db


class SoldNumbers(db.BaseModel):
    """
    Класс модели таблицы проданных номеров
    """

    __tablename__ = 'SoldNumbers'

    id = Column(BigInteger, primary_key=True)
    number = Column(String(100))
    user_id = Column(BigInteger)
    cost = Column(BigInteger)
    country = Column(String(100))
    active = Column(Boolean)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)

    query: sql.Select


async def select_all() -> list:
    """
    Возвращает список со всеми проданными номерами
    """

    all_numbers = await SoldNumbers.query.gino.all()
    return all_numbers


async def select_by_days(time: str):
    """
    Возвращает список со всеми проданными номерами в промежутке времени `time`

    `time`: Промежуток времени в строковом формате
    """

    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    last_week_start = today - \
        datetime.timedelta(days=today.weekday()) - relativedelta(weeks=1)
    last_week_end = last_week_start + datetime.timedelta(days=6)
    last_fourteen_days = today - datetime.timedelta(days=14)
    last_thirty_days = today - datetime.timedelta(days=30)
    last_month_start = today.replace(day=1) - relativedelta(months=1)
    last_month_end = last_month_start + \
        relativedelta(months=1) - datetime.timedelta(days=1)

    numbers = {
        'За сегодня': (await SoldNumbers.query.where(SoldNumbers.created_at >= today).order_by(SoldNumbers.country).gino.all()),
        'Вчера': (await SoldNumbers.query.where((SoldNumbers.created_at >= yesterday) & (SoldNumbers.created_at <= today)).order_by(SoldNumbers.country).gino.all()),
        'Прошлая неделя ( пн-вс)': (await SoldNumbers.query.where((SoldNumbers.created_at >= last_week_start) & (SoldNumbers.created_at <= last_week_end)).order_by(SoldNumbers.country).gino.all()),
        'Последние 14 дней': (await SoldNumbers.query.where(SoldNumbers.created_at >= last_fourteen_days).order_by(SoldNumbers.country).gino.all()),
        'Последние 30 дней': (await SoldNumbers.query.where(SoldNumbers.created_at >= last_thirty_days).order_by(SoldNumbers.country).gino.all()),
        'Прошлый месяц': (await SoldNumbers.query.where((SoldNumbers.created_at >= last_month_start) & (SoldNumbers.created_at <= last_month_end)).order_by(SoldNumbers.country).gino.all()),
        'Все время': (await SoldNumbers.query.order_by(SoldNumbers.country).gino.all())
    }
    return numbers[time]


async def add(id: int, number: str, user_id: int, cost: int, country: str, active: bool=True):
    """
    Функция для добавления проданного номера в бд

    `id`: ID заказа номера\n
    `number`: Проданный номер\n
    `user_id`: ID пользователя, купившего номер\n
    `cost`: Стоимость проданного номера\n
    `country`: Страна номера\n
    `active`: Активен ли номер
    """

    try:
        sold_number = SoldNumbers(
            id=id, number=number, user_id=user_id, cost=cost, country=country, active=active, updated_at=datetime.datetime.now(), created_at=datetime.datetime.now())
        await sold_number.create()
    except UniqueViolationError:
        pass


async def select(id: int) -> SoldNumbers:
    """
    Возвращает запись, которую находит по ID заказа телефонного номера

    `id`: ID заказа номера
    """

    sold_number = await SoldNumbers.query.where(SoldNumbers.id == id).gino.first()
    return sold_number


async def get_number_id(number: str) -> SoldNumbers:
    """
    Возвращает запись, которую находит по телефонному номеру

    `number`: Проданный номер
    """

    sold_number = await SoldNumbers.query.where(SoldNumbers.number == number).gino.first()
    return sold_number


async def get_numbers_by_user(user_id: int) -> list:
    """
    Возвращает записи о купленных номерах одного пользователя

    `user_id`: ID пользователя
    """

    sold_numbers = await SoldNumbers.query.where(SoldNumbers.user_id == user_id).gino.all()
    return sold_numbers


async def update(id: int, number: str = None, user_id: int = None, cost: int = None, country: str = None, active: bool = None) -> None:
    """
    Функция для обновления записи о номере в бд

    `id`: ID заказа номера\n
    `number`: Проданный номер\n
    `user_id`: ID пользователя, купившего номер\n
    `cost`: Стоимость проданного номера\n
    `country`: Страна номера\n
    `active`: Активен ли номер
    """

    sold_number = await SoldNumbers.query.where(SoldNumbers.id == id).gino.first()
    if number is not None:
        await sold_number.update(number=number, updated_at=datetime.datetime.now()).apply()
    if user_id is not None:
        await sold_number.update(user_id=user_id, updated_at=datetime.datetime.now()).apply()
    if cost is not None:
        await sold_number.update(cost=cost, updated_at=datetime.datetime.now()).apply()
    if country is not None:
        await sold_number.update(country=country, updated_at=datetime.datetime.now()).apply()
    if active is not None:
        await sold_number.update(active=active, updated_at=datetime.datetime.now()).apply()
