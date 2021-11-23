from sqlalchemy import sql, Column, BigInteger, String, DateTime, Integer
from asyncpg import UniqueViolationError
import datetime
from dateutil.relativedelta import *
from modules.db import database as db


class SoldNumbers(db.BaseModel):
    """
    Класс модели таблицы проданных номеров
    """

    __tablename__ = 'SoldNumbers'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    number = Column(String(100))
    cost = Column(BigInteger)
    country = Column(String(100))
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
    last_week_start = today - datetime.timedelta(days=today.weekday()) - relativedelta(weeks=1)
    last_week_end = last_week_start + datetime.timedelta(days=6)
    last_fourteen_days = today - datetime.timedelta(days=14)
    last_thirty_days = today - datetime.timedelta(days=30)
    last_month_start = today.replace(day=1) - relativedelta(months=1)
    last_month_end = last_month_start + relativedelta(months=1) - datetime.timedelta(days=1)

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


async def add(number: str, cost: int, country: str):
    """
    Функция для добавления проданного номера в бд

    `number`: Проданный номер\n
    `cost`: Стоимость проданного номера\n
    `country`: Страна номера
    """

    try:
        sold_number = SoldNumbers(
            number=number, cost=cost, country=country, created_at=datetime.datetime.now())
        await sold_number.create()
    except UniqueViolationError:
        pass


async def select(number: int) -> SoldNumbers:
    """
    Возвращает запись, которую находит по телефонному номеру

    `number`: Проданный номер
    """

    sold_number = await SoldNumbers.query.where(SoldNumbers.country == number).gino.first()
    return sold_number
