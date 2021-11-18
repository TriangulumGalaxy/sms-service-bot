from sqlalchemy import sql, Column, BigInteger, String, DateTime
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
    api_key = Column(String(100), unique=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    query: sql.Select


async def select_all() -> list:
    """
    Возвращает список со всеми пользователями
    """

    all_users = await User.query.gino.all()
    return all_users
