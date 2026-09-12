from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from cart.models import Cart
from .forms import CheckoutForm
from .models import Order, OrderItem


@login_required
def checkout_view(request):
    cart = Cart.objects.filter(customer=request.user).first()
    if not cart or not cart.items.exists():
        messages.warning(request, "Your cart is empty. Add some items before checking out.")
        return redirect('products:menu')

    # Guard against a product going out of stock/unavailable between add-to-cart and checkout
    unavailable = [item for item in cart.items.all() if not item.product.is_available]
    if unavailable:
        names = ', '.join(i.product.name for i in unavailable)
        messages.error(request, f"These items are no longer available: {names}. Please update your cart.")
        return redirect('cart:cart')

    initial = {
        'full_name': request.user.get_full_name(),
        'email': request.user.email,
    }
    if hasattr(request.user, 'profile'):
        profile = request.user.profile
        initial.update({'phone': profile.phone, 'address': profile.address, 'city': profile.city, 'pincode': profile.pincode})

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                data = form.cleaned_data
                order = Order.objects.create(
                    customer=request.user,
                    full_name=data['full_name'],
                    phone=data['phone'],
                    email=data['email'],
                    address=data['address'],
                    city=data['city'],
                    pincode=data['pincode'],
                    notes=data['notes'],
                    subtotal=cart.subtotal,
                    delivery_fee=cart.delivery_fee,
                    total=cart.grand_total,
                )
                for item in cart.items.select_related('product').all():
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        price=item.product.price,
                        quantity=item.quantity,
                    )
                cart.items.all().delete()

            messages.success(request, f"Order #{order.id} placed successfully! Pay at your doorstep.")
            return redirect('orders:confirmation', order_id=order.id)
    else:
        form = CheckoutForm(initial=initial)

    return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})


@login_required
def confirmation_view(request, order_id):
    order = Order.objects.filter(id=order_id, customer=request.user).prefetch_related('items').first()
    if not order:
        messages.error(request, "Order not found.")
        return redirect('home')
    return render(request, 'orders/confirmation.html', {'order': order})
