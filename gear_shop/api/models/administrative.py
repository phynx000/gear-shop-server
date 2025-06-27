# models/administrative.py
from django.db import models


class Province(models.Model):
    """Tỉnh/Thành phố trực thuộc Trung ương"""
    code = models.CharField(max_length=10, unique=True)  # Mã tỉnh
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)  # "Thành phố", "Tỉnh"

    class Meta:
        verbose_name = "Tỉnh/Thành phố"
        verbose_name_plural = "Tỉnh/Thành phố"

    def __str__(self):
        return self.name


class District(models.Model):
    """Quận/Huyện/Thị xã"""
    code = models.CharField(max_length=10, unique=True)  # Mã quận/huyện
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)  # "Quận", "Huyện", "Thị xã", "Thành phố"
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='districts')

    class Meta:
        verbose_name = "Quận/Huyện"
        verbose_name_plural = "Quận/Huyện"

    def __str__(self):
        return f"{self.name}, {self.province.name}"


class Ward(models.Model):
    """Phường/Xã/Thị trấn"""
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)  # "Phường", "Xã", "Thị trấn"
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='wards')

    class Meta:
        verbose_name = "Phường/Xã"
        verbose_name_plural = "Phường/Xã"

    def __str__(self):
        return f"{self.name}, {self.district.name}"