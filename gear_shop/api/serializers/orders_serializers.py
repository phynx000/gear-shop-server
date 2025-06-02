# serializers/order.py

from rest_framework import serializers
from ..models.order import Order, OrderItem
from ..models.products import Product
from ..serializer import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity', 'price']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['total_price', 'payment_method', 'vnp_transaction_id', 'shipping_address', 'phone', 'note', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user

        order = Order.objects.create(user=user, **validated_data)

        for item in items_data:
            product = Product.objects.get(id=item['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=item['price']
            )

        return order


class GetOrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']


class GetOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_quantity = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'status', 'status_display'
                  , 'shipping_address', 'items', 'total_price', 'total_quantity', 'phone', 'note']
    def get_total_quantity(self, obj):
        return sum(item.quantity for item in obj.items.all())