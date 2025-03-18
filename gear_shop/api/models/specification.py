from django.db import models

from ..models.products import Product


class Specification(models.Model):
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.key}: {self.value}"