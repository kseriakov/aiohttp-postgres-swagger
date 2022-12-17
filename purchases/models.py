from sqlalchemy import Table, Column, Integer, String, DateTime, DECIMAL
from sqlalchemy.sql import func

from db.db_connection import metadata_obj


purchase_table = Table(
    "purchase",
    metadata_obj,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, index=True, nullable=False),
    Column("price", DECIMAL(precision=5, scale=2), nullable=False),
    Column("amount", Integer, nullable=False),
    Column("date", DateTime, server_default=func.now()),
)
