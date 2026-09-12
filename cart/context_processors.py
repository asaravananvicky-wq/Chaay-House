from .models import Cart


def cart_summary(request):
    """Exposes cart item count in every template, for the navbar cart badge."""
    count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(customer=request.user).first()
        if cart:
            count = cart.total_items
    return {'cart_item_count': count}
