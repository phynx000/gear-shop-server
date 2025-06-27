# api/serializers/branch_serializers.py
from rest_framework import serializers
from api.models.branch import Branch
from api.models.stock import Stock
from api.models.products import Product


class ProductInStockSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id')
    product_name = serializers.CharField(source='product.name')
    image_url = serializers.SerializerMethodField()
    stock_id = serializers.IntegerField(source='id')  # Add stock_id field


    class Meta:
        model = Stock
        fields = ['stock_id','product_id', 'product_name', 'color', 'quantity', 'image_url']

    def get_image_url(self, obj):
        # Get the first image of the product if it exists
        product_image = obj.product.images.first()
        if product_image and product_image.image:
            return product_image.image.url
        return None

class StaffBranchWithStockSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    branch_id = serializers.IntegerField(source='id')
    branch_name = serializers.CharField(source='name')
    address = serializers.CharField(source='full_address')


    class Meta:
        model = Branch
        fields = ['branch_id', 'branch_name', 'address', 'phone', 'products']

    def get_products(self, branch):
        stocks = Stock.objects.filter(
            branch=branch,
            quantity__gt=0
        ).select_related('product')

        serializer = ProductInStockSerializer(stocks, many=True)
        return serializer.data


class StockUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['color', 'quantity']

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value


