from django.db import models
from django.utils.timezone import now

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique= True)
    discount_type = models.CharField(max_length=10, choices=[('percent', 'percent'), ('amount', 'amount')]) # kiểu giảm giá ( theo % hoặc fixed cứng)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    expiration_date = models.DateTimeField()
    created_at = models.DateTimeField(default=now)

    def is_valid(self, order_amount):
        return self.is_active and self.expiration_date > now()

    def __str__(self):
        return "f{self.code} - {self.discount_value}{'%' if self.discount_type == 'percent' else ''}"

