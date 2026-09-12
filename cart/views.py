from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product
from .models import Cart, CartItem


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(customer=request.user)
    items = cart.items.select_related('product').all()
    return render(request, 'cart/cart.html', {'cart': cart, 'items': items})


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    quantity = int(request.POST.get('quantity', 1) or 1)
    quantity = max(1, quantity)

    cart, _ = Cart.objects.get_or_create(customer=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
    if not created:
        item.quantity += quantity
        item.save()

    messages.success(request, f"{product.name} added to your cart.")
    next_url = request.POST.get('next') or 'cart:cart'
    return redirect(next_url)


@login_required
@require_POST
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    action = request.POST.get('action')

    if action == 'increase':
        item.quantity += 1
        item.save()
    elif action == 'decrease':
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
        else:
            item.save()
    return redirect('cart:cart')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    product_name = item.product.name
    item.delete()
    messages.info(request, f"{product_name} removed from cart.")
    return redirect('cart:cart')
