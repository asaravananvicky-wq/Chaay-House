from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product
from .models import Cart


class CartTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cust@example.com', password='pass12345')
        self.client.login(username='cust@example.com', password='pass12345')
        self.category = Category.objects.create(name='Tea')
        self.product = Product.objects.create(category=self.category, name='Masala Chai', price=25, is_available=True)

    def test_add_to_cart_creates_item(self):
        response = self.client.post(reverse('cart:add', args=[self.product.id]), {'quantity': 2})
        self.assertEqual(response.status_code, 302)
        cart = Cart.objects.get(customer=self.user)
        self.assertEqual(cart.total_items, 2)
        self.assertEqual(cart.subtotal, 50)

    def test_update_quantity_increase_decrease(self):
        self.client.post(reverse('cart:add', args=[self.product.id]), {'quantity': 1})
        item = Cart.objects.get(customer=self.user).items.first()
        self.client.post(reverse('cart:update', args=[item.id]), {'action': 'increase'})
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)
        self.client.post(reverse('cart:update', args=[item.id]), {'action': 'decrease'})
        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)

    def test_remove_item_deletes_it(self):
        self.client.post(reverse('cart:add', args=[self.product.id]), {'quantity': 1})
        item = Cart.objects.get(customer=self.user).items.first()
        self.client.post(reverse('cart:remove', args=[item.id]))
        self.assertEqual(Cart.objects.get(customer=self.user).items.count(), 0)

    def test_cart_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('cart:cart'))
        self.assertEqual(response.status_code, 302)  # redirected to login
