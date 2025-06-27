from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from .admin_site.view.branches_view import StaffBranchesWithStockView, StaffStockUpdateView
from .admin_site.view.dashboard_view import DashboardOverviewView, OrderStatsView, LowStockProductsView
from .admin_site.view.product_upload_view import ProductExcelUploadView, download_product_template
from .autocomplete import DistrictAutocomplete, WardAutocomplete
from .views import checkout_view, search_view, product_view, stock_view, register_view
from .views.branch_view import ProvinceListView, DistrictListView, WardListView, branches_with_stock, \
    available_colors_by_location
from .views.brand_view import BrandListView
from .views.coupon_view import ApplyCouponView
from .views.featured_products_view import FeaturedGroupAPIView
from .views.flash_sale_view import FlashSaleListView
from .views.order_view import CreateOrderView, OrderHistoryView, AdminOrderListView, StaffOrderStatusUpdateView, \
    OrderDetailView
from .views.product_view import ProductListView, ProductImageListView, ProductByCategoryListView, ProductDetailView, \
    ProductColorsView, ProductBySlugView
from .views.category_view import CategoryListCreateView, CategoryDetailView, CategoryBySlugView
from .views.register_view import RegisterView, LoginView, LogoutView, CheckUserRoleView
from .views.brand_view import BrandListView
from .views.search_view import search_products_strict


from .views.cart_view import AddToCartView, GetCartItemsView, UpdateQuantityCart, RemoveCartItemView
from .views.user_view import UserProfileView
from .views.vnpay_payment_return import VNPAYReturnView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'), # api trả về danh sách tất cả sản phẩm
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('brands/', BrandListView.as_view(), name='brand-list'),
    path('apply-coupon/', ApplyCouponView.as_view(), name="apply-coupon"),
    path('flash-sales/', FlashSaleListView.as_view(), name="flash-sales"),
    path('product-image/', ProductImageListView.as_view(), name="product-image"),
    # path('products/category/<int:category_id>/', ProductByCategoryListView.as_view(), name='product-list-by-category'),
    path('products/<slug:slug>/', ProductByCategoryListView.as_view() ,name='product-list-by-category'),
    path("brands/<int:category_id>/", BrandListView.get_brands_by_category, name="get_brands_by_category"),

    path("cart/add/", AddToCartView.as_view(), name="add-to-cart"),
    path('cart/update/', UpdateQuantityCart.as_view(), name='update-cart-quantity'),
# Add this to the urlpatterns list
    path('cart/remove/<int:item_id>/', RemoveCartItemView.as_view(), name='remove-cart-item'),
    path('cart/items/', GetCartItemsView.as_view(), name='get_cart_items'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),


    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('orders/create/', CreateOrderView.as_view(), name='create-order'),
    path('orders/detail/<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),

    path('payment/vnpay-return/', VNPAYReturnView.as_view(), name='vnpay-return'),

    # Add this to gear_shop/api/urls.py


    # Add this to the urlpatterns list

    # API tìm kiếm chính
    path('search/', search_view.search_products, name='search_products'),

    # API gợi ý tìm kiếm
    path('search/suggestions/', search_view.search_suggestions, name='search_suggestions'),

    path('search/strict/', search_products_strict, name='search_products_strict'),
    # API lấy bộ lọc
    path('search/filters/', search_view.get_search_filters, name='search_filters'),

    path('products/<int:product_id>/versions/', product_view.get_product_versions, name='get_product_versions'),
    path('products/colors/', ProductColorsView.as_view(), name='product-colors'),
    path('products/<int:product_id>/colors/', ProductColorsView.as_view(), name='product-specific-colors'),

    # Add these to your urlpatterns in urls.py

    # Product CRUD endpoints
    path('admin_site/products/', ProductListView.as_view(), name='admin_site-product-list-create'),
    path('admin_site/products/<int:pk>/', ProductDetailView.as_view(), name='admin_site-product-detail'),
    path('admin_site/products/slug/<slug:slug>/', ProductBySlugView.as_view(), name='admin_site-product-by-slug'),

    # Product image management
    # path('admin_site/products/<int:product_id>/images/', ProductImageView.as_view(), name='admin_site-product-images'),
    # path('admin_site/products/<int:product_id>/images/<int:image_id>/', ProductImageView.as_view(),
    #      name='admin_site-product-image-delete'),

    # New category endpoints
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/slug/<slug:slug>/', CategoryBySlugView.as_view(), name='category-by-slug'),

    path('featured/<str:group_name>/', FeaturedGroupAPIView.as_view(), name='featured-group'),
    path('orders/history/', OrderHistoryView.as_view(), name='order-history'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('user/change-password/', register_view.ChangePasswordView.as_view(), name='change-password'),
    path('provinces/', ProvinceListView.as_view(), name='province-list'),
    path('districts/', DistrictListView.as_view(), name='district-list'),
    path('wards/', WardListView.as_view(), name='ward-list'),

    path('user/check-role/', CheckUserRoleView.as_view(), name='check-user-role'),
    path('admin_site/autocomplete/district/', DistrictAutocomplete.as_view(), name='district-autocomplete'),
    path('admin_site/autocomplete/ward/', WardAutocomplete.as_view(), name='ward-autocomplete'),


    # Stock and branch data
    path('branches-with-stock/', branches_with_stock, name='branches-with-stock'),
    path('available-colors/', available_colors_by_location, name='available-colors'),

#     only staff url
    path('staff/orders/', AdminOrderListView.as_view(), name='admin_site-order-list'),
    path('staff/orders/<int:order_id>/update-status/', StaffOrderStatusUpdateView.as_view(), name='admin_site-order-status-update'),
    path('staff/branches-with-stock/', StaffBranchesWithStockView.as_view(), name='staff-branches-with-stock'),
    path('staff/stock/<int:stock_id>/', StaffStockUpdateView.as_view(), name='staff-stock-update'),
    path('dashboard/overview/', DashboardOverviewView.as_view(), name='dashboard-overview'),

path('dashboard/orders/stats/', OrderStatsView.as_view(), name='dashboard-order-stats'),
path('dashboard/products/low-stock/', LowStockProductsView.as_view(), name='dashboard-low-stock'),


    path('admin_site/products/upload-excel/', ProductExcelUploadView.as_view(), name='admin_site-product-upload-excel'),
    path('admin_site/products/download-template/', download_product_template, name='admin_site-download-product-template'),

]