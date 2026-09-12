from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from products.models import Product


class Cart(models.Model):
    """One cart per logged-in customer. Guests use the session (see cart/session_cart.py)."""
    customer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.customer}"

    @property
    def subtotal(self):
        return sum((item.line_total for item in self.items.all()), Decimal('0.00'))

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def delivery_fee(self):
        if self.subtotal == 0 or self.subtotal >= settings.FREE_DELIVERY_THRESHOLD:
            return Decimal('0.00')
        return Decimal(settings.DELIVERY_FEE)

    @property
    def grand_total(self):
        return self.subtotal + self.delivery_fee


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def line_total(self):
        return self.product.price * self.quantity
