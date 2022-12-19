from typing import NoReturn
from sqlalchemy import delete, select, update
from sqlalchemy.sql import func
from sqlalchemy.engine.row import Row
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.sql.dml import Update

from db.db_connection import engine
from .utils import checkout_dates, get_dict_not_none_values
from .schemas import PurchaseCreate, PurchaseShow, PurchaseUpdate
from .models import purchase_table


async def fetch_all_purchases():
    """
    Возвращает список всех данных в таблице
    await conn.execute(query) - возвращает объект CursorResult
    engine.begin() - выполняет операции в рамках одной транзакции
    (по окончании - commit, если была ошибка - rollback)
    """

    async with engine.begin() as connection:
        query = select(purchase_table)
        result = await connection.execute(query)
        return result.all()


async def create_purchase(data: PurchaseCreate) -> int:
    """
    Создает объект, возвращает первичный ключ
    """

    async with engine.begin() as connection:
        query = purchase_table.insert().values(data.dict())
        result = await connection.execute(query)
        return result.inserted_primary_key[0]


async def fetch_purchase(id: int) -> Row | None:
    """
    Возвращает объект Row или None, если запись с переданным id не существует
    """

    async with engine.begin() as connection:
        query = select(purchase_table).where(purchase_table.c.id == id)
        result = await connection.execute(query)
        return result.one_or_none()


async def update_purchase(id: int, data: PurchaseUpdate) -> int | None:
    """
    Проверяем, что объект с заданным id существует, т.к.
    connection.execute не выбрасывает ошибку
    """

    async with engine.begin() as connection:
        if not await fetch_purchase(id):
            return None

        not_none_data = get_dict_not_none_values(data.dict())
        query: Update = (
            update(purchase_table)
            .where(purchase_table.c.id == id)
            .values(**not_none_data)
        )

        await connection.execute(query)
        return id


# async def delete_purchase(id: int):
#     query = delete(purchase_table).where(purchase_table.c.id == id)
#     return await database.execute(query)


# @checkout_dates
# async def search_purchases(query_start, query_end):
#     query = select(purchase_table).where(query_start, query_end)
#     return await database.fetch_all(query)


# @checkout_dates
# async def get_expenses(query_start, query_end):
#     query = select(
#         func.sum(purchase_table.c.price * purchase_table.c.amount)
#     ).where(query_start, query_end)
#     return await database.fetch_val(query)
