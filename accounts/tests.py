from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class RegistrationLoginTests(TestCase):
    def test_register_creates_user_and_profile(self):
        response = self.client.post(reverse('accounts:register'), {
            'name': 'Jane Doe', 'email': 'jane@example.com', 'phone': '9998887777',
            'password': 'strongpass123', 'confirm_password': 'strongpass123',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email='jane@example.com')
        self.assertTrue(hasattr(user, 'profile'))

    def test_register_password_mismatch_fails(self):
        response = self.client.post(reverse('accounts:register'), {
            'name': 'Jane Doe', 'email': 'jane2@example.com', 'phone': '9998887777',
            'password': 'strongpass123', 'confirm_password': 'different',
        })
        self.assertEqual(response.status_code, 200)  # re-renders form with error
        self.assertFalse(User.objects.filter(email='jane2@example.com').exists())

    def test_login_with_correct_credentials(self):
        User.objects.create_user(username='jane@example.com', email='jane@example.com', password='strongpass123')
        response = self.client.post(reverse('accounts:login'), {
            'username': 'jane@example.com', 'password': 'strongpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_with_wrong_password_fails(self):
        User.objects.create_user(username='jane@example.com', email='jane@example.com', password='strongpass123')
        response = self.client.post(reverse('accounts:login'), {
            'username': 'jane@example.com', 'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
