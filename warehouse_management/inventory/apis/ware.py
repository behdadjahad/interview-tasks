from rest_framework import status, views
from rest_framework.response import Response
from inventory.models import Ware
from django.db.models import Sum

from rest_framework import serializers
from drf_spectacular.utils import extend_schema

from inventory.services.ware import create_ware, delete_ware, update_ware
from inventory.selectors.ware import ware_list, ware_detail


class WareApi(views.APIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255)
        cost_method = serializers.CharField(max_length=50)

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Ware
            fields = "__all__"

    @extend_schema(
        responses=OutputSerializer,
        request=InputSerializer,
    )
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            query = create_ware(
                name=serializer.validated_data.get("name"),
                cost_method=serializer.validated_data.get("cost_method"),
            )
        except Exception as ex:
            return Response(
                {"detail": "Database Error - " + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(responses=OutputSerializer)
    def get(self, request):

        try:
            query = ware_list()
        except Exception as ex:
            return Response(
                {"detail": "Filter Error - " + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(self.OutputSerializer(query, many=True).data)


class WareDetailApi(views.APIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255, required=False)
        cost_method = serializers.CharField(max_length=50, required=False)

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Ware
            fields = "__all__"

    @extend_schema(
        responses=OutputSerializer,
    )
    def get(self, request, id):
        try:
            query = ware_detail(id)
        except Exception as ex:
            return Response(
                {"detail": "Filter Error - " + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(self.OutputSerializer(query).data)

    def delete(self, request, id):

        try:
            delete_ware(id)
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
            update_ware(id, **serializer.validated_data)
        except Exception as ex:
            return Response(
                {"detail": "Filter Error - " + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_200_OK)
