from typing import Iterable
from aiohttp import web
from aiohttp.web_routedef import AbstractRouteDef
from databases import Database
from aiohttp_swagger3 import SwaggerFile, SwaggerUiSettings

from db.db_connection import database
from settings import settings
from purchases.routes import router as purchase


class App:
    def __init__(self, db: Database, routes: Iterable[AbstractRouteDef]):
        self._db = db
        self._app = web.Application()
        # self._app.router.add_routes(routes)
        self.setup_swagger(routes)

    def __call__(
        self, host: str = settings.API_HOST, port: int = settings.API_PORT
    ):
        self._app.on_startup.append(self.start_connection)
        self._app.on_cleanup.append(self.close_connection)

        web.run_app(self._app, host=host, port=port)

    async def start_connection(self, app):
        await self._db.connect()

    async def close_connection(self, app):
        await self._db.disconnect()

    def setup_swagger(self, routes: Iterable[AbstractRouteDef]):
        swagger =  SwaggerFile(
            self._app,
            swagger_ui_settings=SwaggerUiSettings(path="/docs"),
            spec_file="./purchases/purchases.yaml",
        )
        swagger.add_routes(routes)


app = App(db=database, routes=purchase)
app()
