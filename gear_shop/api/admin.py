from dal import autocomplete
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms

# from .models import FeaturedProduct
from .models.FeaturedProduct import FeaturedGroup, FeaturedProduct
from .models.branch import Branch
from .models.user import CustomUser
from .models.order import Order, OrderItem
from .models.products import Product, Category, Brand, ProductImage
from .models.specification import Specification
from .forms.product_form import ProductForm
from .models.stock import Stock
from .models.cart import Cart, CartItem

# Register your models here.

class SpecificationInline(admin.TabularInline):  # Hoặc admin_site.StackedInline nếu thích giao diện dọc
    model = Specification
    extra = 3  # Số ô nhập thông số mặc định

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # Hiển thị 3 ô nhập ảnh mặc định
    def delete_model(self, request, obj):
        """Xóa ảnh trên S3 trước khi xóa trong database"""
        obj.delete()  # Gọi delete() trong model để xóa ảnh trên S


class BranchAdminForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = '__all__'
        widgets = {
            'district': autocomplete.ModelSelect2(
                url='district-autocomplete',
                forward=['province']  # forward province_id để lọc
            ),
            'ward': autocomplete.ModelSelect2(
                url='ward-autocomplete',
                forward=['district']  # forward district_id để lọc
            )
        }

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    form = BranchAdminForm
    list_display = ('name', 'address')
    search_fields = ['name', 'address']

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'branch', 'quantity', 'color')


class StockInline(admin.TabularInline):
    model = Stock
    extra = 1
    autocomplete_fields = ['branch']
    verbose_name = "Tồn kho tại chi nhánh"
    verbose_name_plural = "Thông tin tồn kho"

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'original_price')
    form = ProductForm
    search_fields = ['name', 'brand__name']  # thêm dòng này
    # Gắn Specification vào ProductAdmin
    inlines = [SpecificationInline, ProductImageInline, StockInline]

    def changelist_view(self, request, extra_context=None):
        """Thêm nút Upload Excel vào trang danh sách sản phẩm"""
        extra_context = extra_context or {}
        extra_context['custom_buttons'] = [
            {
                'url': '/api/admin_site/products/upload-excel/',
                'title': 'Upload Excel',
                'class': 'addlink',
                'icon': 'icon-upload'
            },
            {
                'url': '/api/admin_site/products/download-template/',
                'title': 'Tải Template Excel',
                'class': 'addlink',
                'icon': 'icon-download'
            }
        ]
        return super().changelist_view(request, extra_context)

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


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0  # Không thêm hàng trống mặc định

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')
    list_filter = ('cart', 'product')


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'address')}),
        ('Permissions', {'fields': ('role', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_active'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

# admin_site.site.register(CustomUser, CustomUserAdmin)

class FeaturedProductInline(admin.TabularInline):
    model = FeaturedProduct
    extra = 1  # Số dòng thêm mới hiển thị sẵn
    autocomplete_fields = ['product']
    ordering = ['priority']


@admin.register(FeaturedGroup)
class FeaturedGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date']
    inlines = [FeaturedProductInline]
    search_fields = ['name']
    list_filter = ['start_date', 'end_date']


@admin.register(FeaturedProduct)
class FeaturedProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'group', 'priority']
    list_filter = ['group']
    autocomplete_fields = ['product', 'group']
    ordering = ['group', 'priority']


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
