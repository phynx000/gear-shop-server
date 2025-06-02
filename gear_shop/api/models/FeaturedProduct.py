from django.db import models

from .products import Product


class FeaturedGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Ví dụ: "home", "summer-sale"
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def is_active(self):
        from django.utils import timezone
        now = timezone.now()
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True


class FeaturedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    group = models.ForeignKey(FeaturedGroup, on_delete=models.CASCADE, related_name='featured_products')
    priority = models.PositiveIntegerField(default=0)  # Thứ tự hiển thị

    class Meta:
        unique_together = ('product', 'group')
        ordering = ['priority']

    def __str__(self):
        return f"{self.product.name} in {self.group.name}" # Thứ tự hiển thị