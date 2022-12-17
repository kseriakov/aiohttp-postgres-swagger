import databases
from sqlalchemy import MetaData

from settings import settings as s


DB_URL = f"postgresql+asyncpg://{s.DB_USER}:{s.DB_PASSWORD}@{s.DB_HOST}:{s.DB_PORT}/{s.DB_NAME}"

database = databases.Database(DB_URL)


metadata_obj = MetaData()
