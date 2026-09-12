from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity', 'line_total']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'full_name', 'phone', 'email', 'address', 'city', 'pincode', 'notes',
            'subtotal', 'delivery_fee', 'total', 'payment_method', 'status', 'status_display',
            'items', 'created_at', 'updated_at',
        ]
        read_only_fields = ['subtotal', 'delivery_fee', 'total', 'status', 'created_at', 'updated_at']


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
