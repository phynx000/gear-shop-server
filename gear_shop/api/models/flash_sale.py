from django.db import models
from django.utils.timezone import now
from ..models import Product


class FlashSale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2) # giá sale
    start_time = models.DateTimeField() # ngày bắt đầu
    end_time = models.DateTimeField() # ngày kết thúc
    quantity = models.PositiveIntegerField() # số lượng tối đa có thể mua
    is_active = models.BooleanField(default=True) # trạng thái

    def is_valid(self, product_quantity):
        return self.is_active and self.start_time <= now() <= self.end_time

    def __str__(self):
        return f"{self.product.name} - {self.sale_price}"