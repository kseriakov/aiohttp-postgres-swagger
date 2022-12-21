from aiohttp.web import (
    RouteTableDef,
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

from db.db_connection import engine
from .models import purchase_table
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


router = RouteTableDef()

service = Service(engine=engine, table_obj=purchase_table)


@router.get("/purchases/search")
async def search_purchases(request: Request) -> Response:
    try:
        search_params = PurchaseSearch(**request.query)
    except ValidationError as err:
        raise HTTPBadRequest(text=err.errors()[0]["msg"])

    data = await service.search(**search_params.dict())
    expenses = await service.get_expenses(**search_params.dict())
    return Response(
        body=PurchaseSearchList(purchases=data, expenses=expenses).json(),
        content_type="application/json",
    )


@router.get("/purchases")
async def get_all(request: Request) -> Response:
    data = await service.fetch_all()
    return Response(
        body=PurchaseList(purchases=data).json(),
        content_type="application/json",
    )


@router.get("/purchases/{id}")
async def get_one(request: Request) -> Response:
    id = get_id_from_request(request)
    data = await service.fetch_one(id)

    if not data:
        raise HTTPNotFound(
            text=f"Purchase with id = {id} does not exists",
        )

    return Response(body=PurchaseShow(**data).json(), content_type="application/json")


@router.post("/purchases")
async def create(request: Request) -> Response:
    data = await request.json()
    purchase_schema = PurchaseCreate(**data)
    purchase_id = await service.create_one(purchase_schema)
    return json_response(purchase_id, status=HTTPCreated.status_code)


@router.patch("/purchases/{id}")
async def update(request: Request) -> Response:
    id = get_id_from_request(request)
    data = await request.json()
    updated = await service.update_one(id, PurchaseUpdate(**data))

    if not updated:
        raise HTTPNotFound(
            text=f"Purchase with id = {id} does not exists",
        )

    return Response(status=HTTPOk.status_code)


@router.delete("/purchases/{id}")
async def delete(request: Request) -> Response:
    id = get_id_from_request(request)
    deleted = await service.delete_one(id)
    if not deleted:
        raise HTTPNotFound(
            text=f"Purchase with id = {id} does not exists",
        )

    return Response(status=HTTPNoContent.status_code)
