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
    user_name = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id', 'user_name', 'total_price', 'status', 'payment_method',
                  'payment_status', 'created_at', 'shipping_address',
                   ]
        depth = 1
    def get_total_quantity(self, obj):
        return sum(item.quantity for item in obj.items.all())

    def get_user_name(self, obj):
        return obj.user.first_name if obj.user else None


        return obj.get_payment_status_display()


class OrderItemProductSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id','name', 'brand_name', 'original_price', 'version']

class GetOrderItemSerializer2(serializers.ModelSerializer):
    product = OrderItemProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = GetOrderItemSerializer2(many=True, read_only=True)
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    total_quantity = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    payment_status_display = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'user_name', 'user_email', 'total_price', 'email',
            'status', 'status_display', 'payment_method', 'vnp_transaction_id',
            'is_paid', 'payment_status', 'payment_status_display',
            'shipping_address', 'phone', 'note', 'created_at',
            'items', 'total_quantity'
        ]

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() if obj.user else None

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None

    def get_total_quantity(self, obj):
        return sum(item.quantity for item in obj.items.all())

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_payment_status_display(self, obj):
        return obj.get_payment_status_display()



class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status', 'payment_status']

    def validate_status(self, value):
        valid_statuses = [status[0] for status in Order.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Choose from: {', '.join(valid_statuses)}")
        return value

    def validate_payment_status(self, value):
        valid_payment_statuses = [status[0] for status in Order.PAYMENT_STATUS_CHOICES]
        if value not in valid_payment_statuses:
            raise serializers.ValidationError(
                f"Invalid payment status. Choose from: {', '.join(valid_payment_statuses)}")
        return value