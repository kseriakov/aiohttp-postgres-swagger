from aiohttp.web import (
    json_response,
    Response,
    HTTPNotFound,
    HTTPOk,
    HTTPCreated,
    HTTPNoContent,
    HTTPBadRequest,
)
from aiohttp.web_request import Request
from pydantic import ValidationError

from .utils import get_id_from_request
from .service import Service
from .schemas import (
    PurchaseCreate,
    PurchaseShow,
    PurchaseUpdate,
    PurchaseList,
    PurchaseSearch,
    PurchaseSearchList,
)


class PurchaseRouter:
    """
    Класс обработчиков запросов
    Реализован для возможности подключения к тестовой БД через service_db
    """

    def __init__(self, service_db: Service):
        self.service_db = service_db

    # @router.get("/purchases/search")
    async def search_purchases(self, request: Request) -> Response:
        try:
            search_params = PurchaseSearch(**request.query)
        except ValidationError as err:
            raise HTTPBadRequest(text=err.errors()[0]["msg"])

        data = await self.service_db.search(**search_params.dict())
        expenses = await self.service_db.get_expenses(**search_params.dict())
        return Response(
            body=PurchaseSearchList(purchases=data, expenses=expenses).json(),
            content_type="application/json",
        )

    # @router.get("/purchases")
    async def get_all(self, request: Request) -> Response:
        data = await self.service_db.fetch_all()
        return Response(
            body=PurchaseList(purchases=data).json(),
            content_type="application/json",
        )

    # @router.get("/purchases/{id}")
    async def get_one(self, request: Request) -> Response:
        id = get_id_from_request(request)
        data = await self.service_db.fetch_one(id)

        if not data:
            raise HTTPNotFound(
                text=f"Purchase with id = {id} does not exists",
            )

        return Response(
            body=PurchaseShow(**data).json(), content_type="application/json"
        )

    # @router.post("/purchases")
    async def create(self, request: Request) -> Response:
        data = await request.json()
        purchase_schema = PurchaseCreate(**data)
        purchase_id = await self.service_db.create_one(purchase_schema)
        return json_response(purchase_id, status=HTTPCreated.status_code)

    # @router.patch("/purchases/{id}")
    async def update(self, request: Request) -> Response:
        id = get_id_from_request(request)
        data = await request.json()
        updated = await self.service_db.update_one(id=id, data=PurchaseUpdate(**data))

        if not updated:
            raise HTTPNotFound(
                text=f"Purchase with id = {id} does not exists",
            )

        return Response(status=HTTPOk.status_code)

    # @router.delete("/purchases/{id}")
    async def delete(self, request: Request) -> Response:
        id = get_id_from_request(request)
        deleted = await self.service_db.delete_one(id=id)
        if not deleted:
            raise HTTPNotFound(
                text=f"Purchase with id = {id} does not exists",
            )

        return Response(status=HTTPNoContent.status_code)
