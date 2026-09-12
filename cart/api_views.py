from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer


class CartDetailAPIView(APIView):
    """GET /api/cart/ — the logged-in customer's cart."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(customer=request.user)
        return Response(CartSerializer(cart).data)


class CartItemCreateAPIView(APIView):
    """POST /api/cart/items/ — add a product to the cart."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(customer=request.user)
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data.get('quantity', 1)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
        if not created:
            item.quantity += quantity
            item.save()
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)


class CartItemDetailAPIView(APIView):
    """PATCH/DELETE /api/cart/items/<id>/ — update quantity or remove an item."""
    permission_classes = [permissions.IsAuthenticated]

    def get_item(self, request, item_id):
        return CartItem.objects.filter(id=item_id, cart__customer=request.user).first()

    def patch(self, request, item_id):
        item = self.get_item(request, item_id)
        if not item:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        quantity = request.data.get('quantity')
        if quantity is None or int(quantity) < 1:
            return Response({'detail': 'quantity must be a positive integer.'}, status=status.HTTP_400_BAD_REQUEST)
        item.quantity = int(quantity)
        item.save()
        return Response(CartItemSerializer(item).data)

    def delete(self, request, item_id):
        item = self.get_item(request, item_id)
        if not item:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
