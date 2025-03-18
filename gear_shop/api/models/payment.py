from django.db import models

from ..models.order import Order
from ..models.products import Product
from ..models.user import CustomUser


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_status = models.CharField(max_length=255)
    transaction_id = models.CharField(max_length=255)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.id} - {self.payment_status}"

