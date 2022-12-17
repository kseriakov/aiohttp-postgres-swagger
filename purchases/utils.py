from datetime import date
from functools import wraps
import inspect
from typing import Any, Callable
from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp.web_request import Request
from pydantic import BaseModel

from .models import purchase_table


def get_id_from_request(request: Request) -> int:
    try:
        id = int(request.match_info['id'])
    except:
        raise HTTPBadRequest(text="Purchase id invalid")

    return id


def optional(class_: BaseModel, *fields) -> BaseModel:
    """Decorator function used to modify a pydantic model's fields to all be optional.
    Alternatively, you can  also pass the field names that should be made optional as arguments
    to the decorator.
    """

    def dec(_cls):
        for field in fields:
            _cls.__fields__[field].required = False
        return _cls

    if class_ and inspect.isclass(class_) and issubclass(class_, BaseModel):
        cls = class_
        fields = cls.__fields__
        return dec(cls)

    return dec


def get_dict_not_none_values(data: dict) -> dict:
    return {k: v for k, v in data.items() if v is not None}


def checkout_dates(func: Callable):
    """
    Проверяет даты на наличие None, строит условия для WHERE
    """

    @wraps(func)
    async def inner(start_date: date | None, end_date: date | None):
        query_start = (
            purchase_table.c.date >= start_date if start_date else True
        )
        query_end = purchase_table.c.date <= end_date if end_date else True
        return await func(query_start, query_end)

    return inner
