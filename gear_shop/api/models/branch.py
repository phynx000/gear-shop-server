# models.py
from django.db import models

class Branch(models.Model):
    name = models.CharField(max_length=255, unique=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name