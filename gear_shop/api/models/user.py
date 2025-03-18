from django.contrib.auth.models import AbstractUser ,Group, Permission
from django.db import models

#models cho user
class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    address = models.CharField(blank=True, null=True)
    is_admin = models.BooleanField(default=False)

    # Thêm related_name để tránh xung đột với auth.User
    groups = models.ManyToManyField(Group, related_name="customuser_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True)

    def __str__(self):
        return self.username