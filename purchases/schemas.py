from datetime import datetime, date
from pydantic import BaseModel, condecimal, ValidationError, validator
from pydantic.error_wrappers import ErrorWrapper
from functools import reduce

from .utils import optional


class PurchaseBase(BaseModel):
    name: str
    price: condecimal(max_digits=5, decimal_places=2)
    amount: int

    @validator("amount")
    def amount_gt_zero(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Amount must be greater then zero")
        return value


@optional
class PurchaseUpdate(PurchaseBase):
    """
    Class PurchaseBase with optional field for HTTP method patch
    """

    date: datetime


class PurchaseCreate(PurchaseBase):
    pass


class PurchaseShow(PurchaseBase):
    id: int
    date: datetime


class PurchaseList(BaseModel):
    purchases: list[PurchaseShow] = []


class PurchaseSearchList(PurchaseList):
    expenses: condecimal(max_digits=15, decimal_places=2) | None


class PurchaseSearch(BaseModel):
    start_date: date | None
    end_date: date | None

    def __init__(self, **data):
        super().__init__(**data)

        field_values_not_none = reduce(lambda x, y: x or y, self.dict().values())

        if not field_values_not_none:
            raise ValidationError(
                errors=[
                    ErrorWrapper(ValueError("Both field values is None"), loc=None)
                ],
                model=self.__class__,
            )
