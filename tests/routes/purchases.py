from aiohttp import web

from purchases.service import Service
from purchases.models import purchase_table
from purchases.routes import PurchaseRouter
from tests.db.db_test_connection import engine


service = Service(engine=engine, table_obj=purchase_table)
handlers = PurchaseRouter(service_db=service)


purchase_routes = [
    web.get("/purchases/search", handlers.search_purchases),
    web.get("/purchases", handlers.get_all),
    web.get("/purchases/{id}", handlers.get_one),
    web.post("/purchases", handlers.create),
    web.patch("/purchases/{id}", handlers.update),
    web.delete("/purchases/{id}", handlers.delete),
]

