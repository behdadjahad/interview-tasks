from django.db.models import QuerySet
from inventory.models import Factor


def factor_detail(id: int) -> Factor:
    return Factor.objects.get(id=id)


def factor_list() -> QuerySet[Factor]:
    return Factor.objects.all()
