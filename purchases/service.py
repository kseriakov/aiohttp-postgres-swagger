from sqlalchemy import delete, select, update
from sqlalchemy.sql import func

from db.db_connection import database
from .utils import checkout_dates, get_dict_not_none_values
from .schemas import PurchaseCreate, PurchaseUpdate
from .models import purchase_table


async def fetch_all_purchases():
    query = select(purchase_table)
    return await database.fetch_all(query)


async def create_purchase(data: PurchaseCreate) -> int:
    query = purchase_table.insert().values(data.dict())
    return await database.execute(query)


async def fetch_purchase(id: int):
    query = select(purchase_table).where(purchase_table.c.id == id)
    return await database.fetch_one(query)


async def update_purchase(id: int, data: PurchaseUpdate):
    not_none_data = get_dict_not_none_values(data.dict())
    query = (
        update(purchase_table)
        .where(purchase_table.c.id == id)
        .values(**not_none_data)
    )
    return await database.execute(query)


async def delete_purchase(id: int):
    query = delete(purchase_table).where(purchase_table.c.id == id)
    return await database.execute(query)


@checkout_dates
async def search_purchases(query_start, query_end):
    query = select(purchase_table).where(query_start, query_end)
    return await database.fetch_all(query)


@checkout_dates
async def get_expenses(query_start, query_end):
    query = select(
        func.sum(purchase_table.c.price * purchase_table.c.amount)
    ).where(query_start, query_end)
    return await database.fetch_val(query)
