from django.db import models


class Ware(models.Model):
    COST_METHOD_CHOICES = [
        ("weighted_mean", "Weighted Mean"),
        ("fifo", "FIFO"),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    cost_method = models.CharField(max_length=50, choices=COST_METHOD_CHOICES)

    def __str__(self):
        return self.name


class Factor(models.Model):
    FACTOR_TYPE_CHOICES = [
        ("input", "Input (Restock)"),
        ("output", "Output (Fulfillment)"),
    ]

    id = models.AutoField(primary_key=True)
    ware = models.ForeignKey(Ware, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=FACTOR_TYPE_CHOICES)
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return f"{self.type.capitalize()} - {self.ware.name} ({self.quantity})"
