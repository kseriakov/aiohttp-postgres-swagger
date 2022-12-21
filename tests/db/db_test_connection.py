from sqlalchemy.ext.asyncio import create_async_engine

from db.db_connection import metadata_obj
from settings import settings as s


DB_URL = f"postgresql+asyncpg://{s.DB_USER}:{s.DB_PASSWORD}@{s.DB_HOST}:{s.DB_PORT}/{s.DB_TEST_NAME}"

engine = create_async_engine(DB_URL)

metadata_test = metadata_obj
