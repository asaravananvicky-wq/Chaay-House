from django.db import transaction
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderStatusUpdateSerializer


class IsStaffOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.customer_id == request.user.id


class MyOrdersAPIView(APIView):
    """GET /api/orders/ — the logged-in customer's own orders. POST creates an order from their current cart."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(customer=request.user).prefetch_related('items')
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        cart = Cart.objects.filter(customer=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'detail': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            order = Order.objects.create(
                customer=request.user,
                subtotal=cart.subtotal,
                delivery_fee=cart.delivery_fee,
                total=cart.grand_total,
                **serializer.validated_data,
            )
            for item in cart.items.select_related('product').all():
                OrderItem.objects.create(
                    order=order, product=item.product, product_name=item.product.name,
                    price=item.product.price, quantity=item.quantity,
                )
            cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailAPIView(APIView):
    """GET /api/orders/<id>/ — order detail, owner or staff only."""
    permission_classes = [permissions.IsAuthenticated, IsStaffOrOwner]

    def get_order(self, request, order_id):
        order = Order.objects.filter(id=order_id).prefetch_related('items').first()
        if order:
            self.check_object_permissions(request, order)
        return order

    def get(self, request, order_id):
        order = self.get_order(request, order_id)
        if not order:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderSerializer(order).data)


class AdminOrderListAPIView(APIView):
    """GET /api/admin/orders/ — all orders, staff only."""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        orders = Order.objects.select_related('customer').prefetch_related('items')
        status_filter = request.query_params.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)
        return Response(OrderSerializer(orders, many=True).data)


class AdminOrderStatusAPIView(APIView):
    """PATCH /api/admin/orders/<id>/status/ — update order status, staff only."""
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, order_id):
        order = Order.objects.filter(id=order_id).first()
        if not order:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)
