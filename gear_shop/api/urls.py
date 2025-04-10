from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from .views.brand_view import BrandListView
from .views.coupon_view import ApplyCouponView
from .views.flash_sale_view import FlashSaleListView
from .views.product_view import ProductListView, ProductImageListView, ProductByCategoryListView
from .views.category_view import CategoryListView
from .views.register_view import RegisterView, LoginView, LogoutView
from .views.brand_view import BrandListView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    # path()
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('brands/', BrandListView.as_view(), name='brand-list'),
    path('apply-coupon/', ApplyCouponView.as_view(), name="apply-coupon"),
    path('flash-sales/', FlashSaleListView.as_view(), name="flash-sales"),
    path('product-image/', ProductImageListView.as_view(), name="product-image"),
    path('products/category/<int:category_id>/', ProductByCategoryListView.as_view(), name='product-list-by-category'),
    path("brands/<int:category_id>/", BrandListView.get_brands_by_category, name="get_brands_by_category"),

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]