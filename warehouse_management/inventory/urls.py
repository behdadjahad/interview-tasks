from django.urls import path

from inventory.apis.factor import (
    InputApi,
    OutputApi,
    FactorApi,
    FactorDetailApi,
    ValuationApi,
)
from inventory.apis.ware import WareApi, WareDetailApi

urlpatterns = [
    path("wares/", WareApi.as_view(), name="ware api"),
    path("factor/", FactorApi.as_view(), name="factor api"),
    path("wares/<int:id>/", WareDetailApi.as_view(), name="ware detail api"),
    path("factor/<int:id>/", FactorDetailApi.as_view(), name="factor detail api"),
    path("input/", InputApi.as_view(), name="add_ware"),
    path("output/", OutputApi.as_view(), name="remove_ware"),
    path(
        "inventory/valuation/<int:id>/",
        ValuationApi.as_view(),
        name="inventory_valuation",
    ),
]
