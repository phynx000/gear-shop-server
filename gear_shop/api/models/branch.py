from .administrative import Province, District, Ward
from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=255, unique=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Giữ lại các trường cũ để tương thích ngược (có thể xóa sau)
    city = models.CharField(max_length=255, null=True, blank=True)
    district_old = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def full_address(self):
        """Địa chỉ đầy đủ"""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.ward:
            parts.append(str(self.ward))
        if self.district:
            parts.append(str(self.district))
        if self.province:
            parts.append(str(self.province))
        return ", ".join(parts)