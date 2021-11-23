from sqlalchemy import sql, Column, BigInteger, String, DateTime
from asyncpg import UniqueViolationError
from datetime import datetime

from modules.db import database as db


class ExpectedCountries(db.BaseModel):
    """
    Класс модели таблицы стран, которые ждут люди (статистика)
    """

    __tablename__ = 'ExpectedCountries'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    country = Column(String(100))
    count = Column(BigInteger)
    updated_at = Column(DateTime)

    query: sql.Select


async def select_all() -> list:
    """
    Возвращает список со всеми странами и кол-вом ждущих людей
    """

    all_countries = await ExpectedCountries.query.gino.all()
    return all_countries


async def add(country: str, count: int = None):
    """
    Функция для добавления страны в бд

    `country`: Страна\n
    `count`: Кол-во людей, которые ждут страну
    """

    try:
        expected_country = ExpectedCountries(
            country=country, count=count, updated_at=datetime.now())
        await expected_country.create()
    except UniqueViolationError:
        pass


async def select(country: int) -> ExpectedCountries:
    """
    Возвращает страну, которую находит по аргументу country

    `country`: Страна
    """

    expected_country = await ExpectedCountries.query.where(ExpectedCountries.country == country).gino.first()
    return expected_country


async def update(country: str, count: int = None) -> None:
    """
    Функция для обновления записи о стране в бд

    `country`: Страна\n
    `count`: Кол-во людей, которые ждут страну
    """

    expected_country = await ExpectedCountries.query.where(ExpectedCountries.country == country).gino.first()
    if count is not None:
        await expected_country.update(count=count, updated_at=datetime.now()).apply()


async def delete(country: str) -> None:
    """
    Функция удаления страны из бд

    `country`: Страна
    """

    expected_country = await ExpectedCountries.query.where(ExpectedCountries.country == country).gino.first()
    await expected_country.delete()
