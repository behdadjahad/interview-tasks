from django.test import TestCase
from django.urls import reverse
from decimal import Decimal

from inventory.models import Ware, Factor


class WareTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.ware = Ware.objects.create(name="test", cost_method="fifo")

    def test_ware_content(self):
        self.assertEqual(self.ware.name, "test")
        self.assertEqual(self.ware.cost_method, "fifo")


class FactorTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.ware = Ware.objects.create(name="test", cost_method="fifo")
        cls.factor = Factor.objects.create(
            ware=cls.ware, quantity=10, purchase_price=Decimal(1000), type="input"
        )

    def test_factor_content(self):
        self.assertEqual(self.factor.ware, self.ware)
        self.assertEqual(self.factor.quantity, 10)
        self.assertEqual(self.factor.purchase_price, Decimal(1000))
        self.assertEqual(self.factor.type, "input")
