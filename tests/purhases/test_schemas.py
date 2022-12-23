from typing import Type
import pytest
from purchases.schemas import PurchaseCreate
from tests.factory import Purchase


def test_amount_less_then_zero(purchase: Type[Purchase]):
    payload = purchase(amount=-1)
    with pytest.raises(ValueError):
        obj = PurchaseCreate(**payload.dict())
