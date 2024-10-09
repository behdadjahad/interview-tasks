from rest_framework import status, views
from rest_framework.response import Response
from inventory.models import Factor
from django.db.models import Sum

from rest_framework import serializers
from drf_spectacular.utils import extend_schema

from inventory.services.factor import (
    create_input,
    create_output,
    create_factor,
    update_factor,
    delete_factor,
)

from inventory.selectors.factor import factor_list, factor_detail


class InputApi(views.APIView):
    class InputSerializer(serializers.Serializer):
        ware_id = serializers.IntegerField()
        quantity = serializers.IntegerField()
        purchase_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Factor
            fields = [
                "factor_id",
                "ware_id",
                "quantity",
                "purchase_price",
                "created_at",
                "type",
            ]

    @extend_schema(
        responses=OutputSerializer,
        request=InputSerializer,
    )
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            query = create_input(
                ware_id=serializer.validated_data.get("ware_id"),
                quantity=serializer.validated_data.get("quantity"),
                purchase_price=serializer.validated_data.get("purchase_price"),
            )
        except Exception as ex:
            return Response(
                {"detail": "Database Error - " + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(self.OutPutSerializer(query, context={"request": request}).data)


class OutputApi(views.APIView):
    class InputSerializer(serializers.Serializer):
        ware_id = serializers.IntegerField()
        quantity = serializers.IntegerField()

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Factor
            fields = [
                "factor_id",
                "ware_id",
                "quantity",
                "total_cost",
                "created_at",
                "type",
            ]

    @extend_schema(
        responses=OutputSerializer,
        request=InputSerializer,
    )
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            query = create_output(
                ware_id=serializer.validated_data.get("ware_id"),
                quantity=serializer.validated_data.get("quantity"),
            )
        except Exception as ex:
            return Response(
                {"detail": "Database Error - " + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(self.OutPutSerializer(query, context={"request": request}).data)


class FactorApi(views.APIView):
    class InputSerializer(serializers.Serializer):
        ware_id = serializers.IntegerField()
        quantity = serializers.IntegerField()
        purchase_price = serializers.DecimalField(max_digits=10, decimal_places=2)
        type = serializers.CharField(max_length=10)
        total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Factor
            fields = "__all__"

    @extend_schema(
        responses=OutputSerializer,
        request=InputSerializer,
    )
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            create_factor(**serializer.validated_data)
        except Exception as ex:
            return Response(
                {"detail": "Filter Error - " + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(
        responses=OutputSerializer,
    )
    def get(self, request):
        try:
            query = factor_list()
        except Exception as ex:
            return Response(
                {"detail": "Filter Error - " + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(self.OutputSerializer(query, many=True).data)


class FactorDetailApi(views.APIView):
    class InputSerializer(serializers.Serializer):
        ware_id = serializers.IntegerField(required=False)
        quantity = serializers.IntegerField(required=False)
        purchase_price = serializers.DecimalField(
            max_digits=10, decimal_places=2, required=False
        )
        type = serializers.CharField(max_length=10, required=False)
        total_cost = serializers.DecimalField(
            max_digits=10, decimal_places=2, required=False
        )

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Factor
            fields = "__all__"

    @extend_schema(
        responses=OutputSerializer,
    )
    def get(self, request, id):
        try:
            query = factor_detail(id)
        except Exception as ex:
            return Response(
                {"detail": "Filter Error - " + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(self.OutputSerializer(query).data)

    def delete(self, request, id):
        try:
            delete_factor(id)
        except Exception as ex:
            return Response(
                {"detail": "Filter Error - " + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=InputSerializer,
    )
    def put(self, request, id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            update_factor(id, **serializer.validated_data)
        except Exception as ex:
            return Response(
                {"detail": "Filter Error - " + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_200_OK)
