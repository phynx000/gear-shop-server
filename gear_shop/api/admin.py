from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models.user import CustomUser
from .models.order import Order, OrderItem
from .models.products import Product, Category, Brand, ProductImage
from .models.specification import Specification
from .forms.product_form import ProductForm

# Register your models here.

class SpecificationInline(admin.TabularInline):  # Hoặc admin.StackedInline nếu thích giao diện dọc
    model = Specification
    extra = 3  # Số ô nhập thông số mặc định

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # Hiển thị 3 ô nhập ảnh mặc định
    def delete_model(self, request, obj):
        """Xóa ảnh trên S3 trước khi xóa trong database"""
        obj.delete()  # Gọi delete() trong model để xóa ảnh trên S


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    form = ProductForm
    # Gắn Specification vào ProductAdmin
    inlines = [SpecificationInline, ProductImageInline]
    def delete_queryset(self, request, queryset):
        """Xóa tất cả ảnh trên S3 trước khi xóa nhiều sản phẩm"""
        for product in queryset:
            for image in product.images.all():
                image.delete()  # Xóa ảnh trên S3
            product.delete()  # Xóa sản phẩm


class ProductImageAdmin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        """Xóa ảnh trên S3 trước khi xóa nhiều ảnh"""
        for image in queryset:
            image.delete()  # Gọi delete() của model


class CustomUserAdmin(UserAdmin):
    # Hiển thị các trường của CustomUser trong Admin
    fieldsets = UserAdmin.fieldsets + (
        ("Thông tin bổ sung", {"fields": ("full_name", "phone", "address", "is_admin")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Thông tin bổ sung", {"fields": ("full_name", "phone", "address")}),
    )

admin.site.register(ProductImage, ProductImageAdmin)

#
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Order)
admin.site.register(Product, ProductAdmin, )
admin.site.register(OrderItem)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.site_header = "Quản lý cửa hàng phụ kiện máy tính"
admin.site.site_title = "Admin - Phụ kiện PC"
admin.site.index_title = "Trang quản trị hệ thống"


