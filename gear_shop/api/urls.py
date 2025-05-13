from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from .views import checkout_view
from .views.brand_view import BrandListView
from .views.coupon_view import ApplyCouponView
from .views.flash_sale_view import FlashSaleListView
from .views.order_view import CreateOrderView
from .views.product_view import ProductListView, ProductImageListView, ProductByCategoryListView, ProductDetailView
from .views.category_view import CategoryListView
from .views.register_view import RegisterView, LoginView, LogoutView
from .views.brand_view import BrandListView
from .views.stock_view import StockListCreateView,StockByProductView
from .views.cart_view import AddToCartView, GetCartItemsView, UpdateQuantityCart
from .views.vnpay_payment_return import VNPAYReturnView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'), # api trả về danh sách tất cả sản phẩm
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('brands/', BrandListView.as_view(), name='brand-list'),
    path('apply-coupon/', ApplyCouponView.as_view(), name="apply-coupon"),
    path('flash-sales/', FlashSaleListView.as_view(), name="flash-sales"),
    path('product-image/', ProductImageListView.as_view(), name="product-image"),
    # path('products/category/<int:category_id>/', ProductByCategoryListView.as_view(), name='product-list-by-category'),
    path('products/<slug:slug>/', ProductByCategoryListView.as_view() ,name='product-list-by-category'),
    path("brands/<int:category_id>/", BrandListView.get_brands_by_category, name="get_brands_by_category"),
    path("stocks/", StockListCreateView.as_view(), name="stock-list-create"),
    path("stocks/product/<int:product_id>/", StockByProductView.as_view(), name="stock-by-product"),
    path("cart/add/", AddToCartView.as_view(), name="add-to-cart"),
    path('cart/update/', UpdateQuantityCart.as_view(), name='update-cart-quantity'),
    path('cart/items/', GetCartItemsView.as_view(), name='get_cart_items'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),


    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('orders/create/', CreateOrderView.as_view(), name='create-order'),
    path('payment/vnpay-return/', VNPAYReturnView.as_view(), name='vnpay-return'),



]