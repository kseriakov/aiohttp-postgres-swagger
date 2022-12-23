import asyncio
from typing import Callable, Type
import pytest_asyncio, pytest
from pytest_factoryboy import register
from sqlalchemy.ext.asyncio import AsyncConnection
from aiohttp import web

from tests.db.db_test_connection import metadata_test, engine
from tests.factory import Purchase
from purchases.models import purchase_table
from tests.routes.purchases import purchase_routes


register(Purchase)


@pytest.fixture(scope="session")
def event_loop():
    """
    Необходимая фикстура для работы pytest_asyncio
    """

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def connection():
    """
    Фикстура предоставляет единый экземпляр соединения с БД для тестов в рамках одного модуля
    В начале создаем тестовую таблицу, в конце - удаляем
    """
    async with engine.begin() as conn:
        await conn.run_sync(metadata_test.drop_all)
        await conn.run_sync(metadata_test.create_all)

    async with engine.connect() as conn:
        yield conn
        await conn.close()

    async with engine.begin() as conn:
        await conn.run_sync(metadata_test.drop_all)

    # Уничтожает весь пул подключений к БД
    await engine.dispose()


@pytest_asyncio.fixture
async def connection_one_trans(connection):
    """
    В рамках одной функции работаем в одной транзакции, по окончанию делаем откат
    Возвращаем экземпляр connection и transaction - чтобы сделать коммит внутри async with.
    Иначе из БД в рамках другого соединения мы не получим данных
    """

    async with connection.begin() as trans:
        yield connection, trans
        await trans.rollback()


@pytest_asyncio.fixture
async def insert_purchases(
    connection, purchase: Type[Purchase]
) -> Callable[[int, AsyncConnection], None]:
    """
    Фикстура для добавления произвольного числа объектов в БД
    """

    async def inner(
        count: int,
    ) -> None:
        list_data = purchase.build_batch(size=count)
        query = purchase_table.insert().values([i.dict() for i in list_data])
        await connection.execute(query)
        await connection.commit()

    return inner


@pytest.fixture(scope="session")
def get_app():
    """
    Инициализация приложения
    """
    app = web.Application()
    app.router.add_routes(purchase_routes)
    return app


@pytest.fixture
def client(event_loop, aiohttp_client, get_app):
    """
    Клиент для отправки HTTP запросов
    """

    return event_loop.run_until_complete(aiohttp_client(get_app))
