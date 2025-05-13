from django.db import models
from ..models.products import Product
from ..models.user import CustomUser
from django.conf import settings

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Giỏ hàng của {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('cart', 'product')

    def serialize(self):
        return {
            "id": self.id,
            "product": {
                "id": self.product.id,
                "name": self.product.name,
                "original_price": self.product.original_price,
            },
            "quantity": self.quantity,
        }

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


