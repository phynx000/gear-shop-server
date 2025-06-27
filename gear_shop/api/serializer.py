from logging.config import valid_ident

from django.db import models
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


from .models.FeaturedProduct import FeaturedGroup,FeaturedProduct
from .models.coupon import Coupon
from .models.flash_sale import FlashSale
from .models.order import OrderItem, Order
from .models.products import Product, Category, Brand, ProductImage
from .models.specification import Specification
from .models.stock import Stock
from .models.branch import Branch
from .models.user import CustomUser
from .models.cart import Cart, CartItem
from .models.administrative import Province, District, Ward
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate


User = get_user_model()



class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    category = CategorySerializer()
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = SpecificationSerializer(many=True, read_only=True, source='specification_set')

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'sku', 'brand', 'description',
            'original_price', 'slug', 'product_group', 'version',
            'box_content', 'is_new', 'created_at', 'images', 'specifications'
        ]
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"

class FlashSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashSale
        fields = "__all__"





class FeaturedProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = FeaturedProduct
        fields = ['product', 'priority']


class FeaturedGroupSerializer(serializers.ModelSerializer):
    featured_products = FeaturedProductSerializer(many=True)

    class Meta:
        model = FeaturedGroup
        fields = ['name', 'description', 'featured_products']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Không trả mật khẩu ra ngoài

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'address']

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', ''),
            role=CustomUser.CUSTOMER  # Default role is customer
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
        user = authenticate(username=username, password=password)

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
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'address': user.address,
                    'role': user.role,
                }
            }
        raise serializers.ValidationError("Sai tài khoản hoặc mật khẩu!")

class ProductColorSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    colors = serializers.ListField(child=serializers.CharField())


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'code', 'name', 'type']


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'code', 'name', 'type', 'province']


class WardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ward
        fields = ['id', 'code', 'name', 'type', 'district']


class BranchSerializer(serializers.ModelSerializer):
    province_name = serializers.CharField(source='province.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    ward_name = serializers.CharField(source='ward.name', read_only=True)

    class Meta:
        model = Branch
        fields = ['id', 'name', 'province', 'district', 'ward', 'address',
                  'phone', 'province_name', 'district_name', 'ward_name', 'full_address']


class BranchWithStockSerializer(serializers.ModelSerializer):
    """Serializer cho chi nhánh có kèm thông tin tồn kho"""
    province_name = serializers.CharField(source='province.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    ward_name = serializers.CharField(source='ward.name', read_only=True)
    total_stock = serializers.SerializerMethodField()
    available_colors = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = ['id', 'name', 'province', 'district', 'ward', 'address',
                  'phone', 'province_name', 'district_name', 'ward_name',
                  'full_address', 'total_stock', 'available_colors']

    def get_total_stock(self, obj):
        """Tổng số lượng tồn kho của chi nhánh này"""
        product_id = self.context.get('product_id')
        if product_id:
            return Stock.objects.filter(
                branch=obj,
                product_id=product_id,
                quantity__gt=0
            ).aggregate(total=models.Sum('quantity'))['total'] or 0
        return 0

    def get_available_colors(self, obj):
        """Các màu có sẵn tại chi nhánh"""
        product_id = self.context.get('product_id')
        if product_id:
            colors = Stock.objects.filter(
                branch=obj,
                product_id=product_id,
                quantity__gt=0
            ).values('color').annotate(total_quantity=models.Sum('quantity'))
            # quantity_color = Stock.objects.filter(
            #     branch=obj,
            #     product_id=product_id,
            #     quantity__gt=0
            # ).values('color').annotate(total_quantity=models.Sum('quantity'))
            return list(colors)
        return []


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
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'address', 'role']
        read_only_fields = ['id', 'username', 'email']  # These fields shouldn't be updated via this serializer