from datetime import date
import json
from typing import Type
import pytest
from aiohttp import ClientResponse
from aiohttp.test_utils import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from purchases.models import purchase_table
from tests.factory import Purchase
from tests.routes.purchases import handlers


@pytest.mark.asyncio
async def test_get_all(
    client: TestClient, connection: AsyncConnection, insert_purchases
):
    await insert_purchases(3)
    response: ClientResponse = await client.get("/purchases")
    assert response.status == 200

    purchases = await response.json()
    res = await connection.execute(select(purchase_table))
    correct_result = res.all()
    assert len(purchases["purchases"]) == len(correct_result)


@pytest.mark.asyncio
async def test_search_purchases(client: TestClient, connection: AsyncConnection):
    response: ClientResponse = await client.get(
        f"/purchases/search?start_date={date.today()}"
    )
    assert response.status == 200

    searched_purchases = await response.json()
    res = await connection.execute(select(purchase_table))
    correct_result = res.all()
    assert len(searched_purchases["purchases"]) == len(correct_result)


@pytest.mark.asyncio
async def test_uncorrect_search_purchases(client: TestClient):
    response: ClientResponse = await client.get(f"/purchases/search")
    assert response.status == 400


@pytest.mark.asyncio
async def test_get_one(client: TestClient):
    id = 1
    response: ClientResponse = await client.get(f"/purchases/{id}")
    assert response.status == 200
    purchase = await response.json()
    assert purchase["id"] == id


@pytest.mark.asyncio
async def test_uncorrect_get_one(client: TestClient):
    response: ClientResponse = await client.get("/purchases/111")
    assert response.status == 404


@pytest.mark.asyncio
async def test_create(client: TestClient, purchase: Type[Purchase]):
    response: ClientResponse = await client.post(
        "/purchases", data=json.dumps(purchase().dict(), default=str)
    )
    created_id = await response.json()
    assert response.status == 201
    assert type(created_id) is int


@pytest.mark.asyncio
async def test_update(
    client: TestClient, purchase: Type[Purchase], connection: AsyncConnection
):
    id = 1
    payload = purchase()

    response: ClientResponse = await client.patch(
        f"/purchases/{id}", data=json.dumps(payload.dict(), default=str)
    )

    assert response.status == 200

    res = await connection.execute(
        select(purchase_table).where(purchase_table.c.id == id)
    )
    updated_purchase = res.one()

    assert updated_purchase.name == payload.name
    assert updated_purchase.price == payload.price
    assert updated_purchase.amount == payload.amount


@pytest.mark.asyncio
async def test_uncorrect_update(client: TestClient):
    response: ClientResponse = await client.patch("/purchases/111", data=json.dumps({}))
    assert response.status == 404


@pytest.mark.asyncio
async def test_delete(client: TestClient, connection: AsyncConnection):
    id = 1
    response: ClientResponse = await client.delete(f"/purchases/{id}")
    assert response.status == 204

    res = await connection.execute(
        select(purchase_table).where(purchase_table.c.id == id)
    )
    assert res.one_or_none() is None

@pytest.mark.asyncio
async def test_uncorrect_delete(client: TestClient):
    response: ClientResponse = await client.delete("/purchases/111")
    assert response.status == 404