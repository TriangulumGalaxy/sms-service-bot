from sqlalchemy import sql, Column, BigInteger, String, DateTime, Integer
from asyncpg import UniqueViolationError
from datetime import datetime

from modules.db import database as db


class User(db.BaseModel):
    """
    Класс модели таблицы пользователей бота
    """

    __tablename__ = 'Users'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True)
    lang = Column(String(100))
    api_key = Column(String(100))
    country_id = Column(Integer)
    country = Column(String(100))
    operator = Column(String(100))
    service = Column(String(100))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    query: sql.Select


async def select_all() -> list:
    """
    Возвращает список со всеми пользователями
    """

    all_users = await User.query.gino.all()
    return all_users


async def add(user_id: int, lang: str, api_key: str = None, country_id: int = None, country: str = None, operator: str = None, service: str = None):
    """
    Функция для добавления пользователя в бд

    `user_id`: ID пользователя в Telegram\n
    `lang`: Язык, который выбрал пользователь\n
    `api_key`: API ключ пользователя, который он вводил при регистрации\n
    `country_id`: ID страны, которую выбрал пользователь\n
    `country`: Страна, которую выбрал пользователь\n
    `operator`: Оператор связи, которого выбрал пользователь\n
    `service`: Сервис, который выбрал пользователь
    """

    try:
        user = User(user_id=user_id, lang=lang, api_key=api_key, country_id=country_id, country=country,
                    operator=operator, service=service, created_at=datetime.now(), updated_at=datetime.now())
        await user.create()
    except UniqueViolationError:
        pass


async def select(user_id: int) -> User:
    """
    Возвращает пользователя, которого находит по аргументу user_id

    `user_id`: ID пользователя в Telegram
    """

    user = await User.query.where(User.user_id == user_id).gino.first()
    return user


async def update(id: int, user_id: int, lang: str, api_key: str, country_id: int, country: str, operator: str, service: str) -> None:
    """
    Функция для обновления записи о пользователе в бд

    `id`: ID пользователя в БД\n
    `lang`: Язык, который выбрал пользователь\n
    `api_key`: API ключ пользователя, который он вводил при регистрации\n
    `country_id`: ID страны, которую выбрал пользователь\n
    `country`: Страна, которую выбрал пользователь\n
    `operator`: Оператор связи, которого выбрал пользователь\n
    `service`: Сервис, который выбрал пользователь
    """

    user = await User.get(id)
    if user_id is not None:
        await user.update(user_id=user_id, updated_at=datetime.now()).apply()
    if lang is not None:
        await user.update(lang=lang, updated_at=datetime.now()).apply()
    if api_key is not None:
        await user.update(api_key=api_key, updated_at=datetime.now()).apply()
    if country_id is not None:
        await user.update(country_id=country_id, updated_at=datetime.now()).apply()
    if country is not None:
        await user.update(country=country, updated_at=datetime.now()).apply()
    if operator is not None:
        await user.update(operator=operator, updated_at=datetime.now()).apply()
    if service is not None:
        await user.update(service=service, updated_at=datetime.now()).apply()


async def delete(user_id: int) -> None:
    """
    Функция удаления пользователя из бд

    `user_id`: ID пользователя в Telegram
    """
    user = await User.query.where(User.user_id == user_id).gino.first()
    await user.delete()
