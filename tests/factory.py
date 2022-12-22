from typing import Any
import factory
from faker import Faker

fake = Faker()


class PurchaseTestBase:
    """
    Базовый класс представления
    """

    def __init__(self, name: str, price: str, amount: int):
        self.name = name
        self.price = price
        self.amount = amount

    def dict(self) -> dict[str, Any]:
        fields = {}
        fields["name"] = self.name
        fields["price"] = self.price
        fields["amount"] = self.amount
        return fields


class Purchase(factory.Factory):
    name = factory.LazyFunction(lambda: fake.word())
    price = factory.LazyFunction(lambda: fake.pydecimal(left_digits=3, right_digits=2, positive=True))
    amount = factory.LazyFunction(lambda: fake.pyint(min_value=1, max_value=10))

    class Meta:
        model = PurchaseTestBase
        strategy = factory.BUILD_STRATEGY
