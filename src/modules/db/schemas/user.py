from sqlalchemy import sql, Column, BigInteger, String, DateTime, Integer, Float, Boolean
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
    is_admin = Column(Boolean)
    api_key = Column(String(100))
    country_id = Column(Integer)
    country = Column(String(100))
    operator = Column(String(100))
    service = Column(String(100))
    order_id = Column(BigInteger)
    phone_number = Column(String(100))
    number_price = Column(Float)
    balance_limit = Column(BigInteger, default=0, nullable=False)
    fav_country = Column(String(100))
    fav_operator = Column(String(100))
    fav_service = Column(String(100))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    query: sql.Select


async def select_all() -> list:
    """
    Возвращает список со всеми пользователями
    """

    all_users = await User.query.gino.all()
    return all_users


async def add(user_id: int, lang: str, is_admin: bool = False, api_key: str = None, country_id: int = None, country: str = None, operator: str = None, service: str = None, order_id: int = None, phone_number: str = None, number_price: float = None, balance_limit: int = 0, fav_country: str = None, fav_operator: str = None, fav_service: str = None):
    """
    Функция для добавления пользователя в бд

    `user_id`: ID пользователя в Telegram\n
    `lang`: Язык, который выбрал пользователь\n
    `is_admin`: Определяет, является ли пользователь админом\n
    `api_key`: API ключ пользователя, который он вводил при регистрации\n
    `country_id`: ID страны, которую выбрал пользователь\n
    `country`: Страна, которую выбрал пользователь\n
    `operator`: Оператор связи, которого выбрал пользователь\n
    `service`: Сервис, который выбрал пользователь\n
    `order_id`: ID заказа номера телефона\n
    `phone_number`: Заказанный номер телефона\n
    `number_price`: Цена заказанного номера\n
    `balance_limit`: Лимит баланса номера\n
    `fav_country`: Любимая страна номера\n
    `fav_operator`: Любимый оператор\n
    `fav_service`: Любимый сервис
    """

    try:
        user = User(user_id=user_id, lang=lang, is_admin=is_admin, api_key=api_key, country_id=country_id, country=country,
                    operator=operator, service=service, order_id=order_id, phone_number=phone_number, number_price=number_price, balance_limit=balance_limit, fav_country=fav_country, fav_operator=fav_operator, fav_service=fav_service, created_at=datetime.now(), updated_at=datetime.now())
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


async def update(user_id: int, lang: str = None, is_admin: bool = None, api_key: str = None, country_id: int = None, country: str = None, operator: str = None, service: str = None, order_id: int = None, phone_number: str = None, number_price: float = None, balance_limit: int = None, fav_country: str = None, fav_operator: str = None, fav_service: str = None) -> None:
    """
    Функция для обновления записи о пользователе в бд

    `user_id`: ID пользователя в Telegram\n
    `lang`: Язык, который выбрал пользователь\n
    `is_admin`: Определяет, является ли пользователь админом\n
    `api_key`: API ключ пользователя, который он вводил при регистрации\n
    `country_id`: ID страны, которую выбрал пользователь\n
    `country`: Страна, которую выбрал пользователь\n
    `operator`: Оператор связи, которого выбрал пользователь\n
    `service`: Сервис, который выбрал пользователь\n
    `order_id`: ID заказа номера телефона\n
    `phone_number`: Заказанный номер телефона\n
    `number_price`: Цена заказанного номера\n
    `balance_limit`: Лимит баланса номера\n
    `fav_country`: Любимая страна номера\n
    `fav_operator`: Любимый оператор\n
    `fav_service`: Любимый сервис
    """

    user = await User.query.where(User.user_id == user_id).gino.first()
    if lang is not None:
        await user.update(lang=lang, updated_at=datetime.now()).apply()
    if is_admin is not None:
        await user.update(is_admin=is_admin, updated_at=datetime.now()).apply()
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
    if order_id is not None:
        await user.update(order_id=order_id, updated_at=datetime.now()).apply()
    if phone_number is not None:
        await user.update(phone_number=phone_number, updated_at=datetime.now()).apply()
    if number_price is not None:
        await user.update(number_price=number_price, updated_at=datetime.now()).apply()
    if balance_limit is not None:
        await user.update(balance_limit=balance_limit, updated_at=datetime.now()).apply()
    if fav_country is not None:
        await user.update(fav_country=fav_country, updated_at=datetime.now()).apply()
    if fav_operator is not None:
        await user.update(fav_operator=fav_operator, updated_at=datetime.now()).apply()
    if fav_service is not None:
        await user.update(fav_service=fav_service, updated_at=datetime.now()).apply()


async def delete(user_id: int) -> None:
    """
    Функция удаления пользователя из бд

    `user_id`: ID пользователя в Telegram
    """

    user = await User.query.where(User.user_id == user_id).gino.first()
    await user.delete()
