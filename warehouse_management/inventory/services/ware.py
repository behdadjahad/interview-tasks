from django.db.models import QuerySet
from django.db import transaction

from inventory.models import Ware


@transaction.atomic
def create_ware(*, name: str, cost_method: str) -> QuerySet[Ware]:
    ware = Ware.objects.create(name=name, cost_method=cost_method)
    return ware


def delete_ware(id: int):
    Ware.objects.filter(id=id).delete()


def update_ware(id: int, name: str = None, cost_method: str = None):
    ware = Ware.objects.get(id=id)
    if name is not None:
        ware.name = name
    if cost_method is not None:
        ware.cost_method = cost_method
    ware.save()
