from logging.config import valid_ident

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models.coupon import Coupon
from .models.flash_sale import FlashSale
from .models.order import OrderItem, Order
from .models.products import Product, Category, Brand, ProductImage
from .models.specification import Specification
from .models.user import CustomUser
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
        fields = ["id", "name", "description", "price", "category", "images", "product_group"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'phone', 'address']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Không trả mật khẩu ra ngoài

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'full_name', 'phone', 'address']

    def create(self, validated_data):
        # Sử dụng set_password để lưu mật khẩu dạng hash
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            full_name=validated_data.get('full_name', ''),
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', '')
        )
        user.set_password(validated_data['password'])  # Băm (hash) mật khẩu đúng cách
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
                    'full_name': user.full_name,
                    'phone': user.phone,
                    'address': user.address,
                }
            }
        raise serializers.ValidationError("Sai tài khoản hoặc mật khẩu!")