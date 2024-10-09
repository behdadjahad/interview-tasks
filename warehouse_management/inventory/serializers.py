from rest_framework import serializers
from .models import Ware, Factor


class WareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ware
        fields = ["id", "name", "cost_method"]


class FactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factor
        fields = [
            "id",
            "ware",
            "quantity",
            "purchase_price",
            "created_at",
            "type",
            "total_cost",
        ]
