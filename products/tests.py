from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class ProductTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Tea')
        self.product = Product.objects.create(
            category=self.category, name='Masala Chai', price=25, is_available=True,
        )

    def test_product_list_shows_available_products(self):
        response = self.client.get(reverse('products:menu'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Masala Chai')

    def test_product_detail_page(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Masala Chai')

    def test_search_filters_products(self):
        Product.objects.create(category=self.category, name='Filter Coffee', price=35, is_available=True)
        response = self.client.get(reverse('products:menu'), {'q': 'chai'})
        self.assertContains(response, 'Masala Chai')
        self.assertNotContains(response, 'Filter Coffee')

    def test_unavailable_product_hidden_from_menu(self):
        Product.objects.create(category=self.category, name='Sold Out Item', price=10, is_available=False)
        response = self.client.get(reverse('products:menu'))
        self.assertNotContains(response, 'Sold Out Item')
