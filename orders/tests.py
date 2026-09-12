from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from cart.models import Cart, CartItem
from products.models import Category, Product
from .models import Order


class CheckoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cust@example.com', password='pass12345')
        self.client.login(username='cust@example.com', password='pass12345')
        self.category = Category.objects.create(name='Tea')
        self.product = Product.objects.create(category=self.category, name='Masala Chai', price=25, is_available=True)
        self.cart = Cart.objects.create(customer=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_checkout_creates_order_and_clears_cart(self):
        response = self.client.post(reverse('orders:checkout'), {
            'full_name': 'Test User', 'phone': '9998887777', 'email': 'cust@example.com',
            'address': '123 Street', 'city': 'Chennai', 'pincode': '600001', 'notes': '',
        })
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(customer=self.user)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total, order.subtotal + order.delivery_fee)
        self.assertEqual(self.cart.items.count(), 0)

    def test_checkout_blocked_with_empty_cart(self):
        self.cart.items.all().delete()
        response = self.client.post(reverse('orders:checkout'), {
            'full_name': 'Test User', 'phone': '9998887777', 'email': 'cust@example.com',
            'address': '123 Street', 'city': 'Chennai', 'pincode': '600001',
        })
        self.assertRedirects(response, reverse('products:menu'))
        self.assertEqual(Order.objects.count(), 0)

    def test_order_status_default_pending(self):
        self.client.post(reverse('orders:checkout'), {
            'full_name': 'Test User', 'phone': '9998887777', 'email': 'cust@example.com',
            'address': '123 Street', 'city': 'Chennai', 'pincode': '600001',
        })
        order = Order.objects.get(customer=self.user)
        self.assertEqual(order.status, Order.Status.PENDING)


class AdminOrderPermissionTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username='staff@example.com', password='pass12345', is_staff=True)
        self.customer = User.objects.create_user(username='cust2@example.com', password='pass12345')

    def test_non_staff_cannot_access_dashboard(self):
        self.client.login(username='cust2@example.com', password='pass12345')
        response = self.client.get(reverse('dashboard:overview'))
        self.assertEqual(response.status_code, 302)  # redirected away

    def test_staff_can_access_dashboard(self):
        self.client.login(username='staff@example.com', password='pass12345')
        response = self.client.get(reverse('dashboard:overview'))
        self.assertEqual(response.status_code, 200)
