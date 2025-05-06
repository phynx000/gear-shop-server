from  django.db import models

from ..models.branch import Branch
from ..models.products import Product

class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    color = models.CharField(max_length=10, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'branch', 'color')

