from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APITestCase

from inventory.models import Ware, Factor


class WareModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.ware = Ware.objects.create(name="test", cost_method="fifo")

    def test_ware_content(self):
        self.assertEqual(self.ware.name, "test")
        self.assertEqual(self.ware.cost_method, "fifo")


class FactorModelTest(TestCase):
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


class FactorApiTest(APITestCase):
    def setUp(self) -> None:
        self.ware_weighted = Ware.objects.create(
            name="test2", cost_method="weighted_mean"
        )
        self.ware_fifo = Ware.objects.create(name="test1", cost_method="fifo")

    def test_create_input_success(self):
        url = "/api/inventory/input/"
        data = {
            "ware_id": self.ware_weighted.id,
            "quantity": 10,
            "purchase_price": Decimal("100.00"),
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Factor.objects.count(), 1)
        self.assertEqual(Factor.objects.get().quantity, 10)

    def test_create_output_success(self):
        url_input = "/api/inventory/input/"
        data_input = {
            "ware_id": self.ware_fifo.id,
            "quantity": 10,
            "purchase_price": Decimal("100.00"),
        }
        self.client.post(url_input, data_input, format="json")
        url = "/api/inventory/output/"
        data = {
            "ware_id": self.ware_fifo.id,
            "quantity": 10,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Factor.objects.count(), 2)
        self.assertEqual(Factor.objects.get(id=response.json()["id"]).quantity, 10)

    def test_insufficient_stock_output(self):
        url = "/api/inventory/output/"
        data = {
            "ware_id": self.ware_fifo.id,
            "quantity": 10,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["detail"], "Database Error - Insufficient Stock."
        )
        self.assertEqual(Factor.objects.count(), 0)

    def test_fifo_calculation(self):
        url_input_1 = "/api/inventory/input/"
        data_input_1 = {
            "ware_id": self.ware_fifo.id,
            "quantity": 10,
            "purchase_price": Decimal("100.00"),
        }
        self.client.post(url_input_1, data_input_1, format="json")

        url_input_2 = "/api/inventory/input/"
        data_input_2 = {
            "ware_id": self.ware_fifo.id,
            "quantity": 10,
            "purchase_price": Decimal("200.00"),
        }
        self.client.post(url_input_2, data_input_2, format="json")
        url = "/api/inventory/output/"
        data = {
            "ware_id": self.ware_fifo.id,
            "quantity": 15,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Factor.objects.count(), 3)
        self.assertEqual(
            Factor.objects.get(id=response.json()["id"]).total_cost, Decimal(2000)
        )

    def test_weighted_mean_calculation(self):
        url_input_1 = "/api/inventory/input/"
        data_input_1 = {
            "ware_id": self.ware_weighted.id,
            "quantity": 10,
            "purchase_price": Decimal("100.00"),
        }
        self.client.post(url_input_1, data_input_1, format="json")

        url_input_2 = "/api/inventory/input/"
        data_input_2 = {
            "ware_id": self.ware_weighted.id,
            "quantity": 10,
            "purchase_price": Decimal("200.00"),
        }
        self.client.post(url_input_2, data_input_2, format="json")
        url = "/api/inventory/output/"
        data = {
            "ware_id": self.ware_weighted.id,
            "quantity": 15,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Factor.objects.count(), 3)
        self.assertEqual(
            Factor.objects.get(id=response.json()["id"]).total_cost, Decimal(2250)
        )

    def test_valuation(self):
        url_input_1 = "/api/inventory/input/"
        data_input_1 = {
            "ware_id": self.ware_weighted.id,
            "quantity": 10,
            "purchase_price": Decimal("100.00"),
        }
        self.client.post(url_input_1, data_input_1, format="json")

        url_input_2 = "/api/inventory/input/"
        data_input_2 = {
            "ware_id": self.ware_weighted.id,
            "quantity": 10,
            "purchase_price": Decimal("200.00"),
        }
        self.client.post(url_input_2, data_input_2, format="json")

        url = f"/api/inventory/inventory/valuation/{self.ware_weighted.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["ware"], self.ware_weighted.id)
        self.assertEqual(response.json()["quantity_in_stock"], 20)
        self.assertEqual(response.json()["total_inventory_value"], Decimal(3000))


class WareApiTest(APITestCase):
    def setUp(self) -> None:
        self.ware = Ware.objects.create(name="test", cost_method="fifo")

    def test_create_ware_success(self):
        url = "/api/inventory/inventory/output/"
