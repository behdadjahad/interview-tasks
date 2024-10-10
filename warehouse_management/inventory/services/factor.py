from django.db import transaction
from decimal import Decimal

from inventory.models import Factor, Ware


@transaction.atomic
def create_input(*, ware_id: int, quantity: int, purchase_price: Decimal) -> Factor:
    ware = Ware.objects.get(id=ware_id)
    input_ware = Factor.objects.create(
        ware=ware, quantity=quantity, purchase_price=purchase_price, type="input"
    )
    return input_ware


@transaction.atomic
def create_output(*, ware_id: int, quantity: int) -> Factor:

    ware = Ware.objects.get(id=ware_id)

    factors = Factor.objects.filter(type="input").filter(ware=ware)
    available = 0
    for factor in factors:
        available += factor.quantity

    if available < quantity:
        raise ValueError("Insufficient Stock.")

    if ware.cost_method == "fifo":
        total_cost = calculate_total_cost_fifo(ware_id=ware_id, quantity=quantity)
    else:
        total_cost = calculate_total_cost_weighted(ware_id=ware_id, quantity=quantity)

    output_ware = Factor.objects.create(
        ware=ware,
        quantity=quantity,
        type="output",
        total_cost=total_cost,
        purchase_price=0,
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
    ware = Ware.objects.get(id=ware_id)
    factors = (
        Factor.objects.filter(type="input").filter(ware=ware).order_by("created_at")
    )

    total_cost = Decimal(0)

    for factor in factors:
        factor_quantity = factor.quantity
        while factor_quantity > 0:
            if quantity == 0:
                return total_cost
            quantity -= 1
            factor_quantity -= 1
            total_cost += factor.purchase_price

    return total_cost


def calculate_total_cost_weighted(*, ware_id: int, quantity: int) -> Decimal:
    ware = Ware.objects.get(id=ware_id)
    factors = Factor.objects.filter(type="input").filter(ware=ware)
    if factors.count() == 0:
        raise ValueError("No factor for this item.")
    total_quantity = 0
    total_cost = 0
    for factor in factors:
        total_cost += factor.purchase_price * factor.quantity
        total_quantity += factor.quantity
    price_per_each = total_cost / total_quantity
    return quantity * price_per_each
