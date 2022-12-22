from datetime import date, datetime, timedelta
from typing import Type
import pytest
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import select

from purchases.schemas import PurchaseCreate, PurchaseSearch, PurchaseUpdate
from tests.db.db_test_connection import engine
from purchases.models import purchase_table
from purchases.service import Service
from tests.factory import Purchase


service = Service(engine=engine, table_obj=purchase_table)


@pytest.mark.asyncio
async def test_fetch_all_purchases(insert_purchases):
    await insert_purchases(3)
    purchases = await service.fetch_all()
    assert len(purchases) == 3


@pytest.mark.asyncio
async def test_create_purchase(purchase: Type[Purchase]):
    obj = PurchaseCreate(**purchase().dict())
    id = await service.create_one(obj)
    assert id is not None


@pytest.mark.asyncio
async def test_fetch_purchase():
    purchase = await service.fetch_one(id=1)
    assert purchase is not None
    assert purchase["id"] == 1


@pytest.mark.asyncio
async def test_update_purchase(purchase: Type[Purchase], connection: AsyncConnection):

    prchs = purchase()
    new_data = PurchaseUpdate(name=prchs.name, price=prchs.price, amount=prchs.amount)
    updated_id = await service.update_one(id=1, data=new_data)

    query = select(purchase_table).where(purchase_table.c.id == updated_id)
    res = await connection.execute(query)
    updated_purchase = res.one_or_none()

    assert updated_id == 1
    assert updated_purchase.name == prchs.name
    assert updated_purchase.price == prchs.price
    assert updated_purchase.amount == prchs.amount


@pytest.mark.asyncio
async def test_wrong_update_purchase():
    updated_id_not_exists = await service.update_one(id=100, data={"name": ""})
    assert updated_id_not_exists is None


@pytest.mark.asyncio
async def test_get_expenses(connection: AsyncConnection):
    expenses = await service.get_expenses(
        **PurchaseSearch(start_date="1970-01-01").dict()
    )
    res = await connection.execute(select(purchase_table))
    all = res.all()
    correct_expenses = 0

    for p in all:
        correct_expenses += p.amount * p.price

    assert expenses == correct_expenses


@pytest.mark.asyncio
async def test_search_purchases(connection: AsyncConnection):
    searched = await service.search(**PurchaseSearch(start_date="1970-01-01").dict())
    correct = await connection.execute(select(purchase_table))
    assert searched == correct.all()

    not_data = await service.search(
        **PurchaseSearch(start_date=date.today() + timedelta(days=1)).dict()
    )
    assert not_data == []


@pytest.mark.asyncio
async def test_delete_purchase(connection: AsyncConnection):
    deleted_id = await service.delete_one(id=1)
    assert deleted_id == 1

    not_object = await connection.execute(
        select(purchase_table).where(purchase_table.c.id == 1)
    )
    assert not_object.scalar() is None
