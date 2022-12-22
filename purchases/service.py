from functools import wraps
from typing import Callable, Concatenate, ParamSpec, Self, TypeVar
from sqlalchemy import delete, select, update, Table
from sqlalchemy.sql import func
from sqlalchemy.engine.row import Row
from sqlalchemy.sql.dml import Update
from sqlalchemy.engine import Engine

from .utils import checkout_dates, get_dict_not_none_values
from .schemas import PurchaseCreate, PurchaseUpdate


P = ParamSpec("P")
R = TypeVar("R")


class Service:
    def __init__(self, engine: Engine, table_obj: Table):
        self.engine = engine
        self.table = table_obj

    @staticmethod
    def is_exists(func: Callable[Concatenate[Self, P], R]) -> Callable[P, R]:
        """
        Декоратор для проверки, что объект с переданным id есть в БД
        """

        @wraps(func)
        async def inner(self: Self, *args: P.args, **kwargs: P.kwargs) -> R:
            if not await Service.fetch_one(self, kwargs["id"]):
                return None
            return await func(self, *args, **kwargs)

        return inner

    async def fetch_all(self):
        """
        Возвращает список всех данных в таблице
        await conn.execute(query) - возвращает объект CursorResult
        engine.begin() - выполняет операции в рамках одной транзакции
        (по окончании - commit, если была ошибка - rollback)
        """

        async with self.engine.begin() as connection:
            query = select(self.table)
            result = await connection.execute(query)
            return result.all()

    async def create_one(self, data: PurchaseCreate) -> int:
        """
        Создает объект, возвращает первичный ключ
        """

        async with self.engine.begin() as connection:
            query = self.table.insert().values(data.dict())
            result = await connection.execute(query)
            return result.inserted_primary_key[0]

    async def fetch_one(self, id: int) -> Row | None:
        """
        Возвращает объект Row или None, если запись с переданным id не существует
        """

        async with self.engine.begin() as connection:
            query = select(self.table).where(self.table.c.id == id)
            result = await connection.execute(query)
            return result.one_or_none()

    @is_exists
    async def update_one(self, *, id: int, data: PurchaseUpdate) -> int | None:
        """
        Проверяем в декораторе, что объект для обновления с заданным id существует
        """

        async with self.engine.begin() as connection:
            not_none_data = get_dict_not_none_values(data.dict())
            query: Update = (
                update(self.table).where(self.table.c.id == id).values(**not_none_data)
            )

            await connection.execute(query)
            return id

    @is_exists
    async def delete_one(self, *, id: int) -> int | None:
        async with self.engine.begin() as connection:
            query = delete(self.table).where(self.table.c.id == id)
            await connection.execute(query)
            return id

    @checkout_dates
    async def search(self, *, start_date, end_date) -> list:
        """
        Выводим список покупок по датам создания
        """

        async with self.engine.begin() as connection:
            query = select(self.table).where(start_date, end_date)
            result = await connection.execute(query)
            return result.all()

    @checkout_dates
    async def get_expenses(self, *, start_date, end_date) -> float:
        """
        Считаем стоимость покупок во временном диапазоне
        """

        async with self.engine.begin() as connection:
            query = select(func.sum(self.table.c.price * self.table.c.amount)).where(
                start_date, end_date
            )

            result = await connection.execute(query)
            return result.scalar_one()
