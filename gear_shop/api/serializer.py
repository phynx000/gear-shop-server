from logging.config import valid_ident

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models.coupon import Coupon
from .models.flash_sale import FlashSale
from .models.order import OrderItem, Order
from .models.products import Product, Category, Brand, ProductImage
from .models.specification import Specification
from .models.stock import Stock
from .models.branch import Branch
from .models.user import CustomUser
from .models.cart import Cart, CartItem
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ["id", "name", "description", "original_price", "category", "images", "product_group" , "slug", "box_content"]



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

# class CartItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.CharField(source='product.name', read_only=True)
#     product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
#
#     class Meta:
#         model = CartItem
#         fields = ['id', 'product', 'product_name', 'product_price', 'quantity']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

# class OrderItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = '__all__'
#
# class OrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = '__all__'

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"

class FlashSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashSale
        fields = "__all__"

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'address', 'phone']


class StockSerializer(serializers.ModelSerializer):
    branch = BranchSerializer(read_only=True)
    branch_id = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(), write_only=True, source='branch'
    )
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, source='product'
    )

    class Meta:
        model = Stock
        fields = ['id', 'product_id', 'branch_id', 'branch', 'quantity']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'phone', 'address']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Không trả mật khẩu ra ngoài

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'first_name','last_name', 'phone', 'address']

    def create(self, validated_data):
        # Sử dụng set_password để lưu mật khẩu dạng hash
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username = username, password = password)

        if user:
            refresh = RefreshToken.for_user(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name' : user.last_name,
                    'phone': user.phone,
                    'address': user.address,
                }
            }
        raise serializers.ValidationError("Sai tài khoản hoặc mật khẩu!")

