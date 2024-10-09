from rest_framework import status, views
from rest_framework.response import Response
from .models import Ware, Factor
from .serializers import WareSerializer, FactorSerializer
from django.db.models import Sum


class WareViewSet(views.APIView):
    def post(self, request):
        serializer = WareSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InputTransactionView(views.APIView):
    def post(self, request):
        ware_id = request.data.get("ware_id")
        quantity = request.data.get("quantity")
        purchase_price = request.data.get("purchase_price")

        try:
            ware = Ware.objects.get(id=ware_id)
        except Ware.DoesNotExist:
            return Response(
                {"error": "Ware not found"}, status=status.HTTP_404_NOT_FOUND
            )

        factor = Factor.objects.create(
            ware=ware,
            quantity=quantity,
            purchase_price=purchase_price,
            type="input",
            total_cost=quantity * purchase_price,
        )

        serializer = FactorSerializer(factor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OutputTransactionView(views.APIView):
    def post(self, request):
        ware_id = request.data.get("ware_id")
        quantity = request.data.get("quantity")

        try:
            ware = Ware.objects.get(id=ware_id)
        except Ware.DoesNotExist:
            return Response(
                {"error": "Ware not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check stock level
        total_stock = Factor.objects.filter(ware=ware, type="input").aggregate(
            Sum("quantity")
        )["quantity__sum"]
        if total_stock is None or total_stock < quantity:
            return Response(
                {"error": "Insufficient stock"}, status=status.HTTP_400_BAD_REQUEST
            )

        total_cost = self.calculate_fifo_cost(ware, quantity)
        factor = Factor.objects.create(
            ware=ware, quantity=quantity, type="output", total_cost=total_cost
        )

        serializer = FactorSerializer(factor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def calculate_fifo_cost(self, ware, quantity):
        factors = Factor.objects.filter(ware=ware, type="input").order_by("created_at")
        remaining_quantity = quantity
        total_cost = 0

        for factor in factors:
            if remaining_quantity == 0:
                break

            if factor.quantity <= remaining_quantity:
                total_cost += factor.quantity * factor.purchase_price
                remaining_quantity -= factor.quantity
            else:
                total_cost += remaining_quantity * factor.purchase_price
                remaining_quantity = 0

        return total_cost


class InventoryValuationView(views.APIView):
    def get(self, request):
        ware_id = request.query_params.get("ware_id")

        try:
            ware = Ware.objects.get(id=ware_id)
        except Ware.DoesNotExist:
            return Response(
                {"error": "Ware not found"}, status=status.HTTP_404_NOT_FOUND
            )

        total_quantity = Factor.objects.filter(ware=ware, type="input").aggregate(
            Sum("quantity")
        )["quantity__sum"]
        total_cost = Factor.objects.filter(ware=ware, type="input").aggregate(
            Sum("total_cost")
        )["total_cost__sum"]

        if total_quantity and total_cost:
            return Response(
                {
                    "ware_id": ware.id,
                    "quantity_in_stock": total_quantity,
                    "total_inventory_value": total_cost,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "No stock available"}, status=status.HTTP_404_NOT_FOUND
            )
