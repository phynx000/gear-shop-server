# models/order.py

from django.db import models
from ..models.products import Product
from ..models.user import CustomUser


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Delivered', 'Delivered')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField(null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=100)
    vnp_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    shipping_address = models.TextField(null=True)
    phone = models.CharField(max_length=15, null=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.username}'s order"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}  (Order {self.order.id})"
