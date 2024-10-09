from django.db.models import QuerySet
from django.db import transaction
from decimal import Decimal

from inventory.models import Factor, Ware


@transaction.atomic
def create_input(
    *, ware_id: int, quantity: int, purchase_price: Decimal
) -> QuerySet[Factor]:
    ware = Ware.objects.get(id=ware_id)
    input_ware = Factor.objects.create(
        ware=ware,
        quantity=quantity,
        purchase_price=purchase_price,
        type=Factor.FACTOR_TYPE_CHOICES.index(0),
    )
    return input_ware


@transaction.atomic
def create_output(*, ware_id: int, quantity: int) -> QuerySet[Factor]:
    ware = Ware.objects.get(id=ware_id)
    if ware.cost_method == "fifo":
        total_price = calculate_total_cost_fifo(ware_id=ware_id, quantity=quantity)
    else:
        total_price = calculate_total_cost_weighted(ware_id=ware_id, quantity=quantity)

    output_ware = Factor.objects.create(
        ware=ware,
        quantity=quantity,
        type=Factor.FACTOR_TYPE_CHOICES.index(1),
        total_price=total_price,
    )
    return output_ware


@transaction.atomic
def create_factor(
    *, ware_id: int, quantity: int, purchase_price: Decimal, type: str, total_cost: str
):
    ware = Ware.objects.get(id=ware_id)
    Factor.objects.create(
        ware=ware,
        quantity=quantity,
        purchase_price=purchase_price,
        type=type,
        total_cost=total_cost,
    )


def update_factor(
    id: int,
    ware_id: int = None,
    quantity: int = None,
    purchase_price: Decimal = None,
    type: str = None,
    total_cost: str = None,
):
    factor = Factor.objects.get(id=id)
    if ware_id is not None:
        ware = Ware.objects.get(id=ware_id)
        factor.ware = ware
    if quantity is not None:
        factor.quantity = quantity
    if purchase_price is not None:
        factor.purchase_price = purchase_price
    if type is not None:
        factor.type = type
    if total_cost is not None:
        factor.total_cost = total_cost

    factor.save()


def delete_factor(id: int):
    Factor.objects.filter(id=id).delete()


def calculate_total_cost_fifo(*, ware_id: int, quantity: int) -> Decimal:
    factors = (
        Factor.objects.filter(type=Factor.FACTOR_TYPE_CHOICES.index(0))
        .filter(ware_id=ware_id)
        .order_by("-created_at")
    )

    total_cost = Decimal(0)
    for factor in factors:
        if quantity == 0:
            break
        quantity -= 1
        total_cost += factor.purchase_price

    return total_cost


# TODO
def calculate_total_cost_weighted(*, ware_id: int, quantity: int) -> Decimal:
    factors = (
        Factor.objects.filter(type=Factor.FACTOR_TYPE_CHOICES.index(0))
        .filter(ware_id=ware_id)
        .order_by("-created_at")
    )

    prices = dict()
    for factor in factors:
        if not factor.purchase_price in prices.keys:
            prices[factor.purchase_price] = 1
        else:
            prices[factor.purchase_price] += 1
    sum_of_price = Decimal(0)
    total_num = 0
    for key in prices:
        sum_of_price += key * prices[key]
        total_num += prices[key]

    return sum_of_price / total_num
