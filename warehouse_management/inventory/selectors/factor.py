from django.db.models import QuerySet
from inventory.models import Factor, Ware


def factor_detail(id: int) -> Factor:
    return Factor.objects.get(id=id)


def factor_list() -> QuerySet[Factor]:
    return Factor.objects.all()


def valuation_stock(ware_id: int):
    ware = Ware.objects.get(id=ware_id)
    factors = Factor.objects.filter(ware=ware)

    total_quantity = 0
    total_value = 0

    for factor in factors:
        if factor.type == "input":
            total_quantity += factor.quantity
            total_value += factor.quantity * factor.purchase_price
        elif factor.type == "output":
            total_quantity -= factor.quantity
            total_value -= factor.quantity * factor.purchase_price

    result = {
        "ware": ware_id,
        "quantity_in_stock": total_quantity,
        "total_inventory_value": total_value,
    }
    return result
