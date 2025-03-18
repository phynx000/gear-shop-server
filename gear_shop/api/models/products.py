import boto3
from django.db import models
import random
import string
from django.conf import settings


def product_image_upload_path(instance, filename):
    """Tạo thư mục theo category khi lưu ảnh lên S3"""
    category_name = instance.product.category.name.replace(" ", "_").lower()
    product_name = instance.product.name.replace(" ", "_").lower()
    return f"product_images/{category_name}/{product_name}/{filename}"

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=20, unique=True,default="GEAR_000")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    sku = models.CharField(max_length=20, unique=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)  # Liên kết Brand
    name = models.CharField(max_length=255)
    description = models.JSONField(default=dict,null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def generate_sku(self):
        """Tạo SKU tự động nếu chưa có, theo format: CATEGORY_CODE + 4 ký tự ngẫu nhiên"""
        category_code = self.category.name[:3].upper()  # Lấy 3 chữ cái đầu của danh mục
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))  # 4 ký tự ngẫu nhiên
        return f"{category_code}{random_part}"

    def save(self, *args, **kwargs):
        if not self.sku:  # Nếu SKU để trống thì tự động tạo
            self.sku = self.generate_sku()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Xóa tất cả ảnh của sản phẩm khi xóa sản phẩm"""
        for image in self.images.all():
            image.delete()  # Gọi phương thức delete() của ProductImage

        # Xóa sản phẩm khỏi database
        super().delete(*args, **kwargs)


    def __str__(self):
        return f"{self.sku} - {self.name}"



class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=product_image_upload_path)

    def __str__(self):
        return f"Image for {self.product.name}"

    def delete(self, *args, **kwargs):
        """Xóa ảnh khỏi S3 khi xóa đối tượng"""
        if self.image:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )

            try:
                s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=self.image.name)
                print(f"✅ Đã xóa ảnh: {self.image.name} khỏi S3")
            except Exception as e:
                print(f"❌ Lỗi khi xóa ảnh trên S3: {e}")

        super().delete(*args, **kwargs)





