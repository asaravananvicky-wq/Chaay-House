from django.urls import include, path
from rest_framework.routers import DefaultRouter

from products.api_views import CategoryViewSet, ProductViewSet
from cart.api_views import CartDetailAPIView, CartItemCreateAPIView, CartItemDetailAPIView
from orders.api_views import (
    AdminOrderListAPIView, AdminOrderStatusAPIView, MyOrdersAPIView, OrderDetailAPIView,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='api-category')
router.register('products', ProductViewSet, basename='api-product')

urlpatterns = [
    path('', include(router.urls)),

    path('cart/', CartDetailAPIView.as_view(), name='api-cart-detail'),
    path('cart/items/', CartItemCreateAPIView.as_view(), name='api-cart-item-create'),
    path('cart/items/<int:item_id>/', CartItemDetailAPIView.as_view(), name='api-cart-item-detail'),

    path('orders/', MyOrdersAPIView.as_view(), name='api-my-orders'),
    path('orders/<int:order_id>/', OrderDetailAPIView.as_view(), name='api-order-detail'),

    path('admin/orders/', AdminOrderListAPIView.as_view(), name='api-admin-orders'),
    path('admin/orders/<int:order_id>/status/', AdminOrderStatusAPIView.as_view(), name='api-admin-order-status'),

    path('auth/', include('rest_framework.urls')),
]
