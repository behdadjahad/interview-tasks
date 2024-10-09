from django.db.models import QuerySet
from inventory.models import Ware


def ware_detail(id: int) -> Ware:
    return Ware.objects.get(id=id)


def ware_list() -> QuerySet[Ware]:
    return Ware.objects.all()
