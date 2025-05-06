from django.db import models
from django.utils.timezone import now

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique= True) # mã giảm giá mà người dùng nhập vào
    discount_type = models.CharField(max_length=10, choices=[('percent', 'percent'), ('amount', 'amount')]) # kiểu giảm giá ( theo % hoặc fixed cứng)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2) # giá trị giảm
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0) # giá trị đơn hàng tối thiểu để áp dụng mã
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # số tiền giảm tối nế type là %
    is_active = models.BooleanField(default=True) # trạng thái hoạt động của mã
    expiration_date = models.DateTimeField() # ngày hết hạn của mã
    created_at = models.DateTimeField(default=now)

    def is_valid(self, order_amount):
        return self.is_active and self.expiration_date > now()

    def __str__(self):
        return "f{self.code} - {self.discount_value}{'%' if self.discount_type == 'percent' else ''}"

