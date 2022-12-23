from aiohttp import web

from .service import Service
from .models import purchase_table
from .routes import PurchaseRouter
from db.db_connection import engine


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
