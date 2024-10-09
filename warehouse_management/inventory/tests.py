from django.urls import reverse
from rest_framework.test import APITestCase


class WarehouseAPITest(APITestCase):

    def test_create_ware(self):
        url = reverse("create_ware")
        data = {"name": "Widget A", "cost_method": "fifo"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_input_transaction(self):
        url = reverse("add_ware")
        data = {"ware_id": 1, "quantity": 100, "purchase_price": 20.00}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_output_transaction(self):
        url = reverse("remove_ware")
        data = {"ware_id": 1, "quantity": 50}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_inventory_valuation(self):
        url = reverse("inventory_valuation")
        response = self.client.get(url, {"ware_id": 1})
        self.assertEqual(response.status_code, 200)
