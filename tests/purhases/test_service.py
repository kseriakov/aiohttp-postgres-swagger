import pytest
from purchases.schemas import PurchaseCreate

from tests.db.db_test_connection import engine
from purchases.models import purchase_table
from purchases.service import Service


service = Service(engine=engine, table_obj=purchase_table)


@pytest.mark.asyncio
async def test_fetch_all_purchases(insert_purchases):
    await insert_purchases(3)
    purchases = await service.fetch_all()
    assert len(purchases) == 3


@pytest.mark.asyncio
async def test_create_purchase(purchase):
    obj = PurchaseCreate(**purchase().dict())
    id = await service.create_one(obj)
    assert type(id) == int


@pytest.mark.asyncio
async def test_fetch_purchase():
    purchase = await service.fetch_one(id=1)
    assert purchase is not None
    assert purchase["id"] == 1
